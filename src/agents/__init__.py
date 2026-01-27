"""
Agents package for the Autonomous Research Agent System.
"""

from .base_agent import BaseAgent
from .topic_expansion_agent import TopicExpansionAgent
from .paper_discovery_agent import PaperDiscoveryAgent
from .claim_extraction_agent import ClaimExtractionAgent
from .claim_normalization_agent import ClaimNormalizationAgent
from .contradiction_detection_agent import ContradictionDetectionAgent
from .research_gap_detection_agent import ResearchGapDetectionAgent
from .citation_builder_agent import CitationBuilderAgent

__all__ = [
    "BaseAgent",
    "TopicExpansionAgent",
    "PaperDiscoveryAgent", 
    "ClaimExtractionAgent",
    "ClaimNormalizationAgent",
    "ContradictionDetectionAgent",
    "ResearchGapDetectionAgent",
    "CitationBuilderAgent"
]