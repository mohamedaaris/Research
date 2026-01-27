"""
Custom Citation Formatter - Creates citations in specific academic format.
"""
import re
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..models.data_models import PaperMetadata, Citation
from .base_agent import BaseAgent


class CustomCitationFormatter(BaseAgent):
    """Custom citation formatter with specific academic format."""
    
    def __init__(self, memory_store=None):
        super().__init__("CustomCitationFormatter", memory_store)
        self.proper_nouns = self._load_proper_nouns()
    
    def _load_proper_nouns(self) -> List[str]:
        """Load list of proper nouns that should be capitalized."""
        return [
            "wiener", "euler", "hamilton", "fibonacci", "pascal", "newton", "gauss",
            "fourier", "laplace", "bayes", "markov", "poisson", "bernoulli",
            "covid", "sars", "hiv", "aids", "dna", "rna", "pcr", "crispr",
            "python", "java", "matlab", "tensorflow", "pytorch", "keras",
            "ieee", "acm", "aaai", "icml", "neurips", "iclr", "cvpr", "iccv",
            "nature", "science", "cell", "lancet", "nejm", "pnas", "jacs",
            "american", "european", "british", "chinese", "japanese", "german",
            "google", "microsoft", "ibm", "facebook", "amazon", "apple",
            "stanford", "mit", "harvard", "cambridge", "oxford", "berkeley"
        ]
    
    async def process(self, papers: List[PaperMetadata]) -> List[Dict[str, Any]]:
        """
        Generate custom formatted citations for papers.
        
        Args:
            papers: List of papers to format
            
        Returns:
            List of formatted citations with metadata
        """
        self.log_operation("custom_citation_start", {"paper_count": len(papers)})
        
        formatted_citations = []
        
        for paper in papers:
            try:
                citation = await self._format_paper_citation(paper)
                formatted_citations.append(citation)
            except Exception as e:
                self.logger.warning(f"Failed to format citation for {paper.title}: {e}")
        
        # Store results
        await self.store_result("custom_citations", formatted_citations)
        
        self.log_operation("custom_citation_complete", {
            "citations_generated": len(formatted_citations)
        })
        
        return formatted_citations
    
    async def _format_paper_citation(self, paper: PaperMetadata) -> Dict[str, Any]:
        """Format a single paper citation in custom format."""
        
        # Generate bibitem key
        bibitem_key = self._generate_bibitem_key(paper)
        
        # Format authors
        formatted_authors = self._format_authors_custom(paper.authors)
        
        # Format title
        formatted_title = self._format_title_custom(paper.title)
        
        # Format journal/venue
        formatted_venue = self._format_venue_custom(paper.venue)
        
        # Format volume and article number
        volume_info = self._extract_volume_info(paper)
        
        # Format year
        year = paper.year
        
        # Format page numbers
        page_numbers = self._extract_page_numbers(paper)
        
        # Format DOI
        doi_link = self._format_doi(paper.doi, paper.url)
        
        # Create the full citation
        citation_parts = []
        citation_parts.append(formatted_authors)
        citation_parts.append(formatted_title)
        citation_parts.append(formatted_venue)
        
        if volume_info:
            citation_parts.append(volume_info)
        
        citation_parts.append(f"({year})")
        
        if page_numbers:
            citation_parts.append(page_numbers)
        
        if doi_link:
            citation_parts.append(doi_link)
        
        # Join parts appropriately
        full_citation = self._join_citation_parts(citation_parts)
        
        # Create bibitem format
        bibitem_citation = f"\\bibitem{{{bibitem_key}}} {full_citation}"
        
        return {
            "paper_id": self._generate_paper_id(paper),
            "bibitem_key": bibitem_key,
            "bibitem_citation": bibitem_citation,
            "formatted_authors": formatted_authors,
            "formatted_title": formatted_title,
            "formatted_venue": formatted_venue,
            "year": year,
            "volume_info": volume_info,
            "page_numbers": page_numbers,
            "doi_link": doi_link,
            "paper_url": self._get_paper_url(paper),
            "journal_name": paper.venue,
            "original_paper": paper
        }
    
    def _generate_bibitem_key(self, paper: PaperMetadata) -> str:
        """Generate bibitem key from first 2-3 authors and year."""
        if not paper.authors:
            return f"Unknown{paper.year % 100:02d}"
        
        # Get first 2-3 authors
        authors_for_key = paper.authors[:3] if len(paper.authors) >= 3 else paper.authors[:2]
        
        # Extract first two letters of last names
        key_parts = []
        for author in authors_for_key:
            last_name = self._extract_last_name(author)
            if len(last_name) >= 2:
                key_parts.append(last_name[:2].title())
            elif len(last_name) == 1:
                key_parts.append(last_name.upper())
        
        # Add year (last 2 digits)
        year_suffix = paper.year % 100
        
        key = "".join(key_parts) + f"{year_suffix:02d}"
        return key
    
    def _format_authors_custom(self, authors: List[str]) -> str:
        """Format authors with initials first, then last name."""
        if not authors:
            return "Unknown Author"
        
        formatted_authors = []
        
        for author in authors:
            formatted_author = self._format_single_author(author)
            formatted_authors.append(formatted_author)
        
        # Join authors with commas
        if len(formatted_authors) == 1:
            return formatted_authors[0]
        elif len(formatted_authors) == 2:
            return f"{formatted_authors[0]}, {formatted_authors[1]}"
        else:
            # For 3+ authors, list all
            return ", ".join(formatted_authors)
    
    def _format_single_author(self, author: str) -> str:
        """Format single author: F.M. Last (initials first)."""
        # Clean the author name
        author = author.strip()
        
        # Split into parts
        parts = author.split()
        if len(parts) < 2:
            return author  # Return as-is if can't parse
        
        # Check if author is already in correct format (e.g., "Y. Saad", "M.H. Schultz")
        if len(parts) == 2 and len(parts[0]) <= 4 and '.' in parts[0]:
            # Already in format like "Y. Saad" or "M.H. Schultz"
            return author
        
        # Last part is last name
        last_name = parts[-1]
        
        # Everything else is first/middle names
        first_middle = parts[:-1]
        
        # Create initials
        initials = []
        for name in first_middle:
            if name and name[0].isalpha():
                # Handle names that might already have periods
                if name.endswith('.'):
                    initials.append(name)
                else:
                    initials.append(f"{name[0].upper()}.")
        
        # Format as "F.M. Last" (initials first, then last name)
        if initials:
            return f"{''.join(initials)} {last_name}"
        else:
            return last_name
    
    def _extract_last_name(self, author: str) -> str:
        """Extract last name from author string."""
        parts = author.strip().split()
        return parts[-1] if parts else author
    
    def _format_title_custom(self, title: str) -> str:
        """Format title with only first letter capital, except proper nouns."""
        if not title:
            return ""
        
        # Clean title
        title = title.strip()
        if title.endswith('.'):
            title = title[:-1]
        
        # Convert to lowercase first
        title_lower = title.lower()
        
        # Capitalize first letter
        if title_lower:
            title_formatted = title_lower[0].upper() + title_lower[1:]
        else:
            title_formatted = title_lower
        
        # Capitalize proper nouns
        for proper_noun in self.proper_nouns:
            # Use word boundaries to match whole words
            pattern = r'\b' + re.escape(proper_noun.lower()) + r'\b'
            replacement = proper_noun.capitalize()
            title_formatted = re.sub(pattern, replacement, title_formatted, flags=re.IGNORECASE)
        
        # Capitalize after colons and question marks
        title_formatted = re.sub(r'([:\?])\s*([a-z])', 
                                lambda m: m.group(1) + ' ' + m.group(2).upper(), 
                                title_formatted)
        
        return title_formatted
    
    def _format_venue_custom(self, venue: str) -> str:
        """Format venue name."""
        if not venue:
            return ""
        
        # Clean venue name
        venue = venue.strip()
        
        # Handle common abbreviations
        venue_mappings = {
            "arXiv": "arXiv preprint",
            "arxiv": "arXiv preprint",
            "ICLR": "International Conference on Learning Representations",
            "NeurIPS": "Advances in Neural Information Processing Systems",
            "ICML": "International Conference on Machine Learning",
            "AAAI": "AAAI Conference on Artificial Intelligence"
        }
        
        return venue_mappings.get(venue, venue)
    
    def _extract_volume_info(self, paper: PaperMetadata) -> Optional[str]:
        """Extract volume and issue information."""
        # This would typically come from paper metadata
        # For now, we'll try to extract from venue or other fields
        
        # Look for volume patterns in venue or other fields
        volume_pattern = r'(\d+)\((\d+)\)'  # Volume(Issue)
        
        # Check if venue contains volume info
        if hasattr(paper, 'volume') and paper.volume:
            return f"\\textbf{{{paper.volume}}}"
        
        # Try to extract from venue string
        venue_match = re.search(volume_pattern, paper.venue)
        if venue_match:
            volume = venue_match.group(1)
            issue = venue_match.group(2)
            return f"\\textbf{{{volume}}}({issue})"
        
        # Default volume (would need to be enhanced with real data)
        return "\\textbf{1}(1)"
    
    def _extract_page_numbers(self, paper: PaperMetadata) -> Optional[str]:
        """Extract page numbers."""
        # This would typically come from paper metadata
        # For now, return a placeholder or try to extract from abstract/other fields
        
        if hasattr(paper, 'pages') and paper.pages:
            return paper.pages
        
        # Look for page patterns in abstract or other fields
        page_pattern = r'(\d+)--(\d+)'
        
        # For now, return a placeholder
        return "1--10"  # Would need real page data
    
    def _format_doi(self, doi: str, url: str) -> Optional[str]:
        """Format DOI link."""
        if doi:
            if doi.startswith('http'):
                return doi
            else:
                return f"https://doi.org/{doi}"
        elif url:
            return url
        else:
            return None
    
    def _get_paper_url(self, paper: PaperMetadata) -> str:
        """Get the best URL for the paper."""
        if paper.doi:
            if paper.doi.startswith('http'):
                return paper.doi
            else:
                return f"https://doi.org/{paper.doi}"
        elif paper.url:
            return paper.url
        elif paper.arxiv_id:
            return f"https://arxiv.org/abs/{paper.arxiv_id}"
        else:
            return ""
    
    def _join_citation_parts(self, parts: List[str]) -> str:
        """Join citation parts with appropriate punctuation."""
        if not parts:
            return ""
        
        result = parts[0]  # Authors
        
        for i, part in enumerate(parts[1:], 1):
            if not part:
                continue
                
            if i == 1:  # Title
                result += f", {part}"
            elif i == 2:  # Venue
                result += f", {part}"
            elif i == 3:  # Volume
                result += f" {part}"
            elif i == 4:  # Year
                result += f" {part}"
            elif i == 5:  # Pages
                result += f" {part}"
            elif i == 6:  # DOI
                result += f". {part}"
            else:
                result += f", {part}"
        
        return result
    
    def _generate_paper_id(self, paper: PaperMetadata) -> str:
        """Generate unique paper ID."""
        if paper.doi:
            return re.sub(r'[^\w]', '_', paper.doi)
        elif paper.arxiv_id:
            return f"arxiv_{paper.arxiv_id.replace('.', '_')}"
        else:
            title_words = re.findall(r'\w+', paper.title.lower())[:3]
            title_part = '_'.join(title_words)
            author_part = re.sub(r'[^\w]', '', paper.authors[0].split()[-1].lower()) if paper.authors else "unknown"
            return f"{author_part}_{title_part}_{paper.year}"
    
    def filter_citations(self, citations: List[Dict[str, Any]], 
                        journal_filter: str = None, 
                        year_filter: int = None,
                        year_range: tuple = None) -> List[Dict[str, Any]]:
        """Filter citations by journal and year."""
        filtered = citations
        
        if journal_filter:
            filtered = [c for c in filtered 
                       if journal_filter.lower() in c['journal_name'].lower()]
        
        if year_filter:
            filtered = [c for c in filtered if c['year'] == year_filter]
        
        if year_range:
            start_year, end_year = year_range
            filtered = [c for c in filtered 
                       if start_year <= c['year'] <= end_year]
        
        return filtered
    
    def generate_bibliography(self, citations: List[Dict[str, Any]]) -> str:
        """Generate complete bibliography in LaTeX format."""
        if not citations:
            return ""
        
        bibliography = "\\begin{thebibliography}{99}\n\n"
        
        for citation in citations:
            bibliography += citation['bibitem_citation'] + "\n\n"
        
        bibliography += "\\end{thebibliography}"
        
        return bibliography
    
    def get_citation_stats(self, citations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about citations."""
        if not citations:
            return {"total": 0}
        
        journals = {}
        years = {}
        
        for citation in citations:
            journal = citation['journal_name']
            year = citation['year']
            
            journals[journal] = journals.get(journal, 0) + 1
            years[year] = years.get(year, 0) + 1
        
        return {
            "total_citations": len(citations),
            "unique_journals": len(journals),
            "year_range": f"{min(years.keys())}-{max(years.keys())}",
            "top_journals": sorted(journals.items(), key=lambda x: x[1], reverse=True)[:5],
            "year_distribution": dict(sorted(years.items()))
        }