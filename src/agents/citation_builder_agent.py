"""
Citation & Reference Builder Agent - Generates citations and references in multiple formats.
"""
import re
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..models.data_models import PaperMetadata, Citation
from .base_agent import BaseAgent


class CitationBuilderAgent(BaseAgent):
    """Agent responsible for building citations and references."""
    
    def __init__(self, memory_store=None):
        super().__init__("CitationBuilderAgent", memory_store)
        self.citation_styles = self._initialize_citation_styles()
    
    def _initialize_citation_styles(self) -> Dict[str, Any]:
        """Initialize citation style configurations."""
        return {
            "bibtex": {
                "article_template": "@article{{{id},\n  title={{{title}}},\n  author={{{authors}}},\n  journal={{{venue}}},\n  year={{{year}}}{doi_line}{url_line}\n}}",
                "inproceedings_template": "@inproceedings{{{id},\n  title={{{title}}},\n  author={{{authors}}},\n  booktitle={{{venue}}},\n  year={{{year}}}{doi_line}{url_line}\n}}",
                "arxiv_template": "@article{{{id},\n  title={{{title}}},\n  author={{{authors}}},\n  journal={{arXiv preprint arXiv:{arxiv_id}}},\n  year={{{year}}}{url_line}\n}}"
            },
            "apa": {
                "format": "{authors} ({year}). {title}. {venue_formatted}.",
                "venue_formats": {
                    "journal": "{venue}",
                    "conference": "In {venue}",
                    "arxiv": "arXiv preprint arXiv:{arxiv_id}"
                }
            },
            "ieee": {
                "format": "{authors}, \"{title},\" {venue_formatted}, {year}.",
                "venue_formats": {
                    "journal": "{venue}",
                    "conference": "in {venue}",
                    "arxiv": "arXiv preprint arXiv:{arxiv_id}"
                }
            },
            "mla": {
                "format": "{authors}. \"{title}.\" {venue_formatted}, {year}.",
                "venue_formats": {
                    "journal": "{venue}",
                    "conference": "{venue}",
                    "arxiv": "arXiv, {arxiv_id}"
                }
            }
        }
    
    async def process(self, papers: List[PaperMetadata]) -> List[Citation]:
        """
        Generate citations for a list of papers.
        
        Args:
            papers: List of papers to generate citations for
            
        Returns:
            List of citations in multiple formats
        """
        self.log_operation("citation_building_start", {"paper_count": len(papers)})
        
        citations = []
        
        for paper in papers:
            try:
                citation = await self._build_citation(paper)
                citations.append(citation)
            except Exception as e:
                self.logger.warning(f"Failed to build citation for paper {paper.title}: {e}")
        
        # Store results
        await self.store_result("citations", citations)
        
        self.log_operation("citation_building_complete", {
            "citations_generated": len(citations)
        })
        
        return citations
    
    async def _build_citation(self, paper: PaperMetadata) -> Citation:
        """Build citation for a single paper in multiple formats."""
        
        paper_id = self._generate_paper_id(paper)
        
        # Generate different citation formats
        bibtex = self._generate_bibtex(paper, paper_id)
        apa = self._generate_apa(paper)
        ieee = self._generate_ieee(paper)
        mla = self._generate_mla(paper)
        
        citation = Citation(
            paper_id=paper_id,
            bibtex=bibtex,
            apa=apa,
            ieee=ieee,
            mla=mla
        )
        
        return citation
    
    def _generate_bibtex(self, paper: PaperMetadata, paper_id: str) -> str:
        """Generate BibTeX citation."""
        
        # Format authors for BibTeX
        authors_str = " and ".join(paper.authors)
        
        # Determine entry type and template
        if paper.arxiv_id:
            template = self.citation_styles["bibtex"]["arxiv_template"]
            return template.format(
                id=paper_id,
                title=paper.title,
                authors=authors_str,
                arxiv_id=paper.arxiv_id,
                year=paper.year,
                url_line=f",\n  url={{{paper.url}}}" if paper.url else ""
            )
        elif self._is_conference_venue(paper.venue):
            template = self.citation_styles["bibtex"]["inproceedings_template"]
        else:
            template = self.citation_styles["bibtex"]["article_template"]
        
        # Format DOI and URL lines
        doi_line = f",\n  doi={{{paper.doi}}}" if paper.doi else ""
        url_line = f",\n  url={{{paper.url}}}" if paper.url else ""
        
        return template.format(
            id=paper_id,
            title=paper.title,
            authors=authors_str,
            venue=paper.venue,
            year=paper.year,
            doi_line=doi_line,
            url_line=url_line
        )
    
    def _generate_apa(self, paper: PaperMetadata) -> str:
        """Generate APA citation."""
        
        # Format authors for APA
        authors_str = self._format_authors_apa(paper.authors)
        
        # Format venue
        venue_formatted = self._format_venue_apa(paper)
        
        return self.citation_styles["apa"]["format"].format(
            authors=authors_str,
            year=paper.year,
            title=paper.title,
            venue_formatted=venue_formatted
        )
    
    def _generate_ieee(self, paper: PaperMetadata) -> str:
        """Generate IEEE citation."""
        
        # Format authors for IEEE
        authors_str = self._format_authors_ieee(paper.authors)
        
        # Format venue
        venue_formatted = self._format_venue_ieee(paper)
        
        return self.citation_styles["ieee"]["format"].format(
            authors=authors_str,
            title=paper.title,
            venue_formatted=venue_formatted,
            year=paper.year
        )
    
    def _generate_mla(self, paper: PaperMetadata) -> str:
        """Generate MLA citation."""
        
        # Format authors for MLA
        authors_str = self._format_authors_mla(paper.authors)
        
        # Format venue
        venue_formatted = self._format_venue_mla(paper)
        
        return self.citation_styles["mla"]["format"].format(
            authors=authors_str,
            title=paper.title,
            venue_formatted=venue_formatted,
            year=paper.year
        )
    
    def _format_authors_apa(self, authors: List[str]) -> str:
        """Format authors for APA style."""
        if not authors:
            return "Unknown Author"
        
        if len(authors) == 1:
            return self._format_author_last_first(authors[0])
        elif len(authors) == 2:
            return f"{self._format_author_last_first(authors[0])} & {self._format_author_last_first(authors[1])}"
        elif len(authors) <= 20:
            formatted_authors = [self._format_author_last_first(author) for author in authors[:-1]]
            return ", ".join(formatted_authors) + f", & {self._format_author_last_first(authors[-1])}"
        else:
            # For more than 20 authors, use et al.
            formatted_authors = [self._format_author_last_first(author) for author in authors[:19]]
            return ", ".join(formatted_authors) + f", ... {self._format_author_last_first(authors[-1])}"
    
    def _format_authors_ieee(self, authors: List[str]) -> str:
        """Format authors for IEEE style."""
        if not authors:
            return "Unknown Author"
        
        if len(authors) <= 3:
            return ", ".join(authors)
        else:
            return f"{authors[0]} et al."
    
    def _format_authors_mla(self, authors: List[str]) -> str:
        """Format authors for MLA style."""
        if not authors:
            return "Unknown Author"
        
        if len(authors) == 1:
            return self._format_author_last_first(authors[0])
        elif len(authors) == 2:
            return f"{self._format_author_last_first(authors[0])}, and {authors[1]}"
        else:
            return f"{self._format_author_last_first(authors[0])}, et al."
    
    def _format_author_last_first(self, author: str) -> str:
        """Format author name as 'Last, F. M.'"""
        parts = author.strip().split()
        if len(parts) < 2:
            return author
        
        last_name = parts[-1]
        first_names = parts[:-1]
        
        # Create initials
        initials = ". ".join([name[0].upper() for name in first_names if name]) + "."
        
        return f"{last_name}, {initials}"
    
    def _format_venue_apa(self, paper: PaperMetadata) -> str:
        """Format venue for APA style."""
        if paper.arxiv_id:
            return self.citation_styles["apa"]["venue_formats"]["arxiv"].format(arxiv_id=paper.arxiv_id)
        elif self._is_conference_venue(paper.venue):
            return self.citation_styles["apa"]["venue_formats"]["conference"].format(venue=paper.venue)
        else:
            return self.citation_styles["apa"]["venue_formats"]["journal"].format(venue=paper.venue)
    
    def _format_venue_ieee(self, paper: PaperMetadata) -> str:
        """Format venue for IEEE style."""
        if paper.arxiv_id:
            return self.citation_styles["ieee"]["venue_formats"]["arxiv"].format(arxiv_id=paper.arxiv_id)
        elif self._is_conference_venue(paper.venue):
            return self.citation_styles["ieee"]["venue_formats"]["conference"].format(venue=paper.venue)
        else:
            return self.citation_styles["ieee"]["venue_formats"]["journal"].format(venue=paper.venue)
    
    def _format_venue_mla(self, paper: PaperMetadata) -> str:
        """Format venue for MLA style."""
        if paper.arxiv_id:
            return self.citation_styles["mla"]["venue_formats"]["arxiv"].format(arxiv_id=paper.arxiv_id)
        else:
            return self.citation_styles["mla"]["venue_formats"]["journal"].format(venue=paper.venue)
    
    def _is_conference_venue(self, venue: str) -> bool:
        """Determine if venue is a conference."""
        conference_indicators = [
            "conference", "proceedings", "workshop", "symposium",
            "ICLR", "NeurIPS", "ICML", "AAAI", "IJCAI", "ACL", "EMNLP",
            "CVPR", "ICCV", "ECCV", "SIGIR", "WWW", "KDD", "ICDE"
        ]
        
        venue_lower = venue.lower()
        return any(indicator.lower() in venue_lower for indicator in conference_indicators)
    
    def _generate_paper_id(self, paper: PaperMetadata) -> str:
        """Generate a unique ID for a paper."""
        if paper.doi:
            return re.sub(r'[^\w]', '_', paper.doi)
        elif paper.arxiv_id:
            return f"arxiv_{paper.arxiv_id.replace('.', '_')}"
        else:
            # Create ID from title and year
            title_words = re.findall(r'\w+', paper.title.lower())[:3]
            title_part = '_'.join(title_words)
            author_part = re.sub(r'[^\w]', '', paper.authors[0].split()[-1].lower()) if paper.authors else "unknown"
            return f"{author_part}_{title_part}_{paper.year}"
    
    def generate_bibliography(self, citations: List[Citation], style: str = "apa") -> str:
        """Generate a formatted bibliography."""
        
        if style not in ["bibtex", "apa", "ieee", "mla"]:
            raise ValueError(f"Unsupported citation style: {style}")
        
        bibliography_lines = []
        
        for citation in citations:
            if style == "bibtex":
                bibliography_lines.append(citation.bibtex)
            elif style == "apa":
                bibliography_lines.append(citation.apa)
            elif style == "ieee":
                bibliography_lines.append(citation.ieee)
            elif style == "mla" and hasattr(citation, 'mla'):
                bibliography_lines.append(citation.mla)
        
        if style == "bibtex":
            return "\n\n".join(bibliography_lines)
        else:
            # For other styles, add numbering for IEEE or alphabetical sorting for APA/MLA
            if style == "ieee":
                numbered_lines = [f"[{i+1}] {line}" for i, line in enumerate(bibliography_lines)]
                return "\n".join(numbered_lines)
            else:
                # Sort alphabetically for APA/MLA
                sorted_lines = sorted(bibliography_lines)
                return "\n\n".join(sorted_lines)
    
    def get_citation_stats(self, citations: List[Citation]) -> Dict[str, Any]:
        """Get statistics about generated citations."""
        
        if not citations:
            return {"total": 0}
        
        # Analyze venue types
        venue_types = {"journal": 0, "conference": 0, "arxiv": 0, "other": 0}
        
        for citation in citations:
            # Extract venue info from BibTeX (simple heuristic)
            if "arXiv preprint" in citation.bibtex:
                venue_types["arxiv"] += 1
            elif "@inproceedings" in citation.bibtex:
                venue_types["conference"] += 1
            elif "@article" in citation.bibtex:
                venue_types["journal"] += 1
            else:
                venue_types["other"] += 1
        
        return {
            "total_citations": len(citations),
            "venue_distribution": venue_types,
            "formats_generated": ["bibtex", "apa", "ieee"]
        }