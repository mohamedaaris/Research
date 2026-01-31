"""
Data models for the Autonomous Research Agent System.
"""
from typing import List, Dict, Optional, Any, Set
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class CitationFormat(str, Enum):
    BIBTEX = "bibtex"
    APA = "apa"
    IEEE = "ieee"


class PaperMetadata(BaseModel):
    """Metadata for academic papers."""
    id: Optional[str] = Field(default_factory=lambda: f"paper_{datetime.now().timestamp()}")
    title: str
    authors: List[str]
    year: int
    venue: str
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None
    abstract: str
    url: Optional[str] = None
    relevance_score: float = 0.0
    impact_score: float = 0.0


class Claim(BaseModel):
    """Structured representation of a research claim."""
    id: str = Field(default_factory=lambda: f"claim_{datetime.now().timestamp()}")
    statement: str
    paper_id: str
    evidence: List[str] = []
    metrics: Dict[str, Any] = {}
    datasets: List[str] = []
    conditions: List[str] = []
    confidence: float = 0.0
    limitations: List[str] = []
    metadata: Dict[str, Any] = {}


class Contradiction(BaseModel):
    """Represents a contradiction between claims."""
    id: str = Field(default_factory=lambda: f"contradiction_{datetime.now().timestamp()}")
    claim1_id: str
    claim2_id: str
    contradiction_type: str  # "direct", "conditional", "methodological"
    explanation: str
    severity: float = 0.0  # 0-1 scale


class ResearchGap(BaseModel):
    """Represents an identified research gap."""
    id: str = Field(default_factory=lambda: f"gap_{datetime.now().timestamp()}")
    description: str
    gap_type: str  # "unexplored_topic", "missing_dataset", "conflicting_results", "underrepresented_condition"
    related_topics: List[str] = []
    potential_questions: List[str] = []
    priority: float = 0.0  # 0-1 scale


class TopicMap(BaseModel):
    """Hierarchical representation of research topics."""
    main_topic: str
    subtopics: List[str] = []
    methods: List[str] = []
    datasets: List[str] = []
    related_areas: List[str] = []
    keywords: List[str] = []


class Citation(BaseModel):
    """Citation information for a paper."""
    paper_id: str
    bibtex: str
    apa: str
    ieee: str
    mla: Optional[str] = None


class KnowledgeNode(BaseModel):
    """Node in the knowledge graph."""
    id: str
    type: str  # "paper", "claim", "method", "dataset", "topic"
    data: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.now)


class KnowledgeEdge(BaseModel):
    """Edge in the knowledge graph."""
    source_id: str
    target_id: str
    relationship: str  # "supports", "contradicts", "evaluates_on", "uses_method", "related_to"
    weight: float = 1.0
    metadata: Dict[str, Any] = {}


class ResearchResults(BaseModel):
    """Final output of the research system."""
    topic_map: TopicMap
    papers: List[PaperMetadata]
    claims: List[Claim]
    contradictions: List[Contradiction]
    research_gaps: List[ResearchGap]
    citations: List[Citation]
    generated_at: datetime = Field(default_factory=datetime.now)
    total_papers_analyzed: int = 0
    total_claims_extracted: int = 0


# Literature Builder Models
class QRanking(str, Enum):
    Q1 = "Q1"
    Q2 = "Q2"
    Q3 = "Q3"


class ClaimCluster(BaseModel):
    """Represents a cluster of related claims."""
    cluster_id: str
    theme: str
    method: Optional[str] = None
    dataset: Optional[str] = None
    task: Optional[str] = None
    research_objective: str
    claims: List[Claim]
    papers: List[PaperMetadata]
    contradictions: List[str] = []
    agreements: List[str] = []
    q_ranking: Dict[str, str] = {}  # paper_id -> Q1/Q2/Q3
    sa_papers: List[str] = []  # List of SA (Systematic Analysis) paper IDs


class LiteratureSection(BaseModel):
    """Represents a section of literature."""
    section_type: str  # introduction, related_work, comparative_analysis, trends
    title: str
    content: str
    citations: List[str] = []
    claim_ids: List[str] = []  # Traceability to original claims
    subsections: Optional[List['LiteratureSection']] = None
    word_count: int = 0
    
    def __init__(self, **data):
        super().__init__(**data)
        self.word_count = len(self.content.split())


class LiteratureOutline(BaseModel):
    """Represents the structure of the literature."""
    title: str
    sections: List[Dict[str, Any]]
    total_papers: int
    total_claims: int
    date_range: tuple
    estimated_word_count: int = 0


class LiteratureDocument(BaseModel):
    """Complete literature document."""
    outline: LiteratureOutline
    sections: List[LiteratureSection]
    bibliography: List[str]
    metadata: Dict[str, Any]
    generated_at: datetime = Field(default_factory=datetime.now)
    
    @property
    def total_word_count(self) -> int:
        return sum(section.word_count for section in self.sections)
    
    @property
    def total_citations(self) -> int:
        return len(set(citation for section in self.sections for citation in section.citations))


class LiteratureFilter(BaseModel):
    """Filter criteria for literature generation."""
    q_rankings: List[str] = ['Q1', 'Q2', 'Q3']
    include_sa_papers: bool = True
    min_year: Optional[int] = None
    max_year: Optional[int] = None
    methods: List[str] = []
    datasets: List[str] = []
    min_confidence: float = 0.0
    max_sections: int = 10