"""
Configuration settings for the Autonomous Research Agent System.
"""
import os
from pathlib import Path
from typing import Dict, Any


class Config:
    """Configuration class for the research system."""
    
    # Storage settings
    STORAGE_PATH = os.getenv("STORAGE_PATH", "data/memory")
    OUTPUT_PATH = os.getenv("OUTPUT_PATH", "output")
    
    # API settings (for future use)
    SEMANTIC_SCHOLAR_API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
    PUBMED_API_KEY = os.getenv("PUBMED_API_KEY")
    
    # Agent settings
    MAX_PAPERS_PER_SOURCE = int(os.getenv("MAX_PAPERS_PER_SOURCE", "50"))
    MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", "5"))
    
    # Processing settings
    CLAIM_CONFIDENCE_THRESHOLD = float(os.getenv("CLAIM_CONFIDENCE_THRESHOLD", "0.5"))
    CONTRADICTION_THRESHOLD = float(os.getenv("CONTRADICTION_THRESHOLD", "0.7"))
    
    # Logging settings
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "research_system.log")
    
    @classmethod
    def create_directories(cls):
        """Create necessary directories."""
        Path(cls.STORAGE_PATH).mkdir(parents=True, exist_ok=True)
        Path(cls.OUTPUT_PATH).mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_agent_config(cls) -> Dict[str, Any]:
        """Get configuration for agents."""
        return {
            "max_papers_per_source": cls.MAX_PAPERS_PER_SOURCE,
            "max_concurrent_requests": cls.MAX_CONCURRENT_REQUESTS,
            "claim_confidence_threshold": cls.CLAIM_CONFIDENCE_THRESHOLD,
            "contradiction_threshold": cls.CONTRADICTION_THRESHOLD
        }


# Create directories on import
Config.create_directories()