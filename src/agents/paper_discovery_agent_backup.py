"""
Paper Discovery Agent - Searches and retrieves relevant academic papers.
"""
import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
import xml.etree.ElementTree as ET
from datetime import datetime
import re

from ..models.data_models import PaperMetadata, TopicMap
from .base_agent import BaseAgent


class PaperDiscoveryAgent(BaseAgent):
    """Agent responsible for discovering and retrieving academic papers."""
    
    def __init__(self, memory_store=None, max_papers_per_source: int = 50):
        super().__init__("PaperDiscoveryAgent", memory_store)
        self.max_papers_per_source = max_papers_per_source
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def process(self, topic_map: TopicMap) -> List[PaperMetadata]:
        """
        Discover papers based on the topic map.
        
        Args:
            topic_map: Structured topic information
            
        Returns:
            List of discovered papers with metadata
        """
        self.log_operation("paper_discovery_start", {
            "main_topic": topic_map.main_topic,
            "keywords_count": len(topic_map.keywords)
        })
        
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        # Search multiple sources
        all_papers = []
        
        # ArXiv search
        arxiv_papers = await self._search_arxiv(topic_map)
        all_papers.extend(arxiv_papers)
        
        # Semantic Scholar search (simulated - would need API key)
        semantic_papers = await self._search_semantic_scholar(topic_map)
        all_papers.extend(semantic_papers)
        
        # Remove duplicates and rank papers
        unique_papers = self._remove_duplicates(all_papers)
        ranked_papers = self._rank_papers(unique_papers, topic_map)
        
        # Store results
        await self.store_result("discovered_papers", ranked_papers)
        
        self.log_operation("paper_discovery_complete", {
            "total_papers": len(ranked_papers),
            "arxiv_papers": len(arxiv_papers),
            "semantic_papers": len(semantic_papers)
        })
        
        return ranked_papers
    
    async def _search_arxiv(self, topic_map: TopicMap) -> List[PaperMetadata]:
        """Search ArXiv for relevant papers."""
        papers = []
        
        # Construct search query
        query_terms = [topic_map.main_topic] + topic_map.keywords[:5]  # Limit keywords
        query = " AND ".join([f'"{term}"' for term in query_terms])
        
        url = "http://export.arxiv.org/api/query"
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": self.max_papers_per_source,
            "sortBy": "relevance",
            "sortOrder": "descending"
        }
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    content = await response.text()
                    papers = self._parse_arxiv_response(content)
                else:
                    self.logger.warning(f"ArXiv search failed with status {response.status}")
        except Exception as e:
            self.logger.error(f"ArXiv search error: {e}")
        
        return papers
    
    def _parse_arxiv_response(self, xml_content: str) -> List[PaperMetadata]:
        """Parse ArXiv API XML response."""
        papers = []
        
        try:
            root = ET.fromstring(xml_content)
            namespace = {"atom": "http://www.w3.org/2005/Atom"}
            
            for entry in root.findall("atom:entry", namespace):
                title_elem = entry.find("atom:title", namespace)
                summary_elem = entry.find("atom:summary", namespace)
                published_elem = entry.find("atom:published", namespace)
                id_elem = entry.find("atom:id", namespace)
                
                if title_elem is not None and summary_elem is not None:
                    title = title_elem.text.strip().replace('\n', ' ')
                    abstract = summary_elem.text.strip().replace('\n', ' ')
                    
                    # Extract authors
                    authors = []
                    for author in entry.findall("atom:author", namespace):
                        name_elem = author.find("atom:name", namespace)
                        if name_elem is not None:
                            authors.append(name_elem.text.strip())
                    
                    # Extract year
                    year = 2023  # Default
                    if published_elem is not None:
                        try:
                            date_str = published_elem.text
                            year = int(date_str[:4])
                        except (ValueError, IndexError):
                            pass
                    
                    # Extract ArXiv ID
                    arxiv_id = None
                    if id_elem is not None:
                        arxiv_match = re.search(r'(\d{4}\.\d{4,5})', id_elem.text)
                        if arxiv_match:
                            arxiv_id = arxiv_match.group(1)
                    
                    paper = PaperMetadata(
                        title=title,
                        authors=authors,
                        year=year,
                        venue="arXiv",
                        arxiv_id=arxiv_id,
                        abstract=abstract,
                        url=id_elem.text if id_elem is not None else None
                    )
                    papers.append(paper)
        
        except ET.ParseError as e:
            self.logger.error(f"Failed to parse ArXiv XML: {e}")
        
        return papers
    
    async def _search_semantic_scholar(self, topic_map: TopicMap) -> List[PaperMetadata]:
        """Search Semantic Scholar (simulated - would need actual API)."""
        # This is a placeholder implementation
        # In a real system, you would use the Semantic Scholar API
        papers = []
        
        # Simulate some papers based on topic
        if "graph neural network" in topic_map.main_topic.lower():
            papers.extend([
                PaperMetadata(
                    title="Semi-Supervised Classification with Graph Convolutional Networks",
                    authors=["Thomas N. Kipf", "Max Welling"],
                    year=2017,
                    venue="ICLR",
                    abstract="We present a scalable approach for semi-supervised learning on graph-structured data...",
                    relevance_score=0.95
                ),
                PaperMetadata(
                    title="Graph Attention Networks",
                    authors=["Petar Veličković", "Guillem Cucurull", "Arantxa Casanova"],
                    year=2018,
                    venue="ICLR",
                    abstract="We present graph attention networks (GATs), novel neural network architectures...",
                    relevance_score=0.92
                )
            ])
        
        if "drug discovery" in topic_map.main_topic.lower():
            papers.extend([
                PaperMetadata(
                    title="Molecular Graph Enhanced Transformer for Drug Design",
                    authors=["Kexin Huang", "Tianfan Fu", "Wenhao Gao"],
                    year=2021,
                    venue="Nature Machine Intelligence",
                    abstract="Drug design is a complex process that requires understanding molecular structures...",
                    relevance_score=0.88
                )
            ])
        
        return papers
    
    def _remove_duplicates(self, papers: List[PaperMetadata]) -> List[PaperMetadata]:
        """Remove duplicate papers based on title similarity."""
        unique_papers = []
        seen_titles = set()
        
        for paper in papers:
            # Normalize title for comparison
            normalized_title = re.sub(r'[^\w\s]', '', paper.title.lower()).strip()
            
            if normalized_title not in seen_titles:
                seen_titles.add(normalized_title)
                unique_papers.append(paper)
        
        return unique_papers
    
    def _rank_papers(self, papers: List[PaperMetadata], topic_map: TopicMap) -> List[PaperMetadata]:
        """Rank papers by relevance, impact, and recency."""
        
        def calculate_relevance_score(paper: PaperMetadata) -> float:
            score = 0.0
            title_lower = paper.title.lower()
            abstract_lower = paper.abstract.lower()
            
            # Main topic match
            if topic_map.main_topic.lower() in title_lower:
                score += 0.3
            if topic_map.main_topic.lower() in abstract_lower:
                score += 0.2
            
            # Keyword matches
            for keyword in topic_map.keywords:
                if keyword.lower() in title_lower:
                    score += 0.1
                if keyword.lower() in abstract_lower:
                    score += 0.05
            
            # Recency bonus (papers from last 5 years get bonus)
            current_year = datetime.now().year
            if current_year - paper.year <= 5:
                score += 0.1 * (6 - (current_year - paper.year)) / 5
            
            # Venue impact (simplified)
            high_impact_venues = ["Nature", "Science", "ICLR", "NeurIPS", "ICML", "AAAI"]
            if any(venue in paper.venue for venue in high_impact_venues):
                score += 0.2
            
            return min(score, 1.0)  # Cap at 1.0
        
        # Calculate relevance scores
        for paper in papers:
            if paper.relevance_score == 0.0:  # Only calculate if not already set
                paper.relevance_score = calculate_relevance_score(paper)
        
        # Sort by relevance score (descending)
        ranked_papers = sorted(papers, key=lambda p: p.relevance_score, reverse=True)
        
        return ranked_papers