"""
API Configuration for Enhanced Paper Discovery
"""
import os
from pathlib import Path

class APIConfig:
    """Configuration for academic database APIs."""
    
    # Free APIs (no key required)
    ARXIV_ENABLED = True
    SEMANTIC_SCHOLAR_ENABLED = True
    CROSSREF_ENABLED = True
    PUBMED_ENABLED = True
    
    # APIs requiring keys (set to True after adding keys)
    SPRINGER_ENABLED = False
    ELSEVIER_ENABLED = False
    WILEY_ENABLED = False
    
    # API Keys (get these from respective providers)
    SEMANTIC_SCHOLAR_API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY")  # Optional, increases rate limits
    SPRINGER_API_KEY = os.getenv("SPRINGER_API_KEY")  # Required for Springer
    ELSEVIER_API_KEY = os.getenv("ELSEVIER_API_KEY")  # Required for Elsevier
    ELSEVIER_INST_TOKEN = os.getenv("ELSEVIER_INST_TOKEN")  # Optional institution token
    WILEY_API_KEY = os.getenv("WILEY_API_KEY")  # Required for Wiley
    PUBMED_API_KEY = os.getenv("PUBMED_API_KEY")  # Optional, increases rate limits
    
    # Contact information (required for some APIs)
    CONTACT_EMAIL = "your-email@example.com"  # Required for CrossRef polite pool
    
    # Rate limiting
    MAX_PAPERS_PER_SOURCE = 50
    MAX_CONCURRENT_REQUESTS = 3
    
    @classmethod
    def get_enabled_sources(cls):
        """Get list of enabled sources."""
        sources = []
        
        if cls.ARXIV_ENABLED:
            sources.append("ArXiv")
        if cls.SEMANTIC_SCHOLAR_ENABLED:
            sources.append("Semantic Scholar")
        if cls.CROSSREF_ENABLED:
            sources.append("CrossRef")
        if cls.PUBMED_ENABLED:
            sources.append("PubMed")
        if cls.SPRINGER_ENABLED and cls.SPRINGER_API_KEY:
            sources.append("Springer Nature")
        if cls.ELSEVIER_ENABLED and cls.ELSEVIER_API_KEY:
            sources.append("Elsevier ScienceDirect")
        if cls.WILEY_ENABLED and cls.WILEY_API_KEY:
            sources.append("Wiley")
        
        return sources
    
    @classmethod
    def validate_config(cls):
        """Validate API configuration."""
        issues = []
        
        if cls.SPRINGER_ENABLED and not cls.SPRINGER_API_KEY:
            issues.append("Springer enabled but no API key provided")
        
        if cls.ELSEVIER_ENABLED and not cls.ELSEVIER_API_KEY:
            issues.append("Elsevier enabled but no API key provided")
        
        if cls.WILEY_ENABLED and not cls.WILEY_API_KEY:
            issues.append("Wiley enabled but no API key provided")
        
        if cls.CONTACT_EMAIL == "your-email@example.com":
            issues.append("Please set a real contact email for CrossRef")
        
        return issues


# Instructions for getting API keys
API_KEY_INSTRUCTIONS = {
    "semantic_scholar": {
        "url": "https://www.semanticscholar.org/product/api",
        "description": "Free API with optional key for higher rate limits",
        "cost": "Free"
    },
    "springer": {
        "url": "https://dev.springernature.com/",
        "description": "Access to Springer Nature journals and books",
        "cost": "Free tier available, paid plans for higher usage"
    },
    "elsevier": {
        "url": "https://dev.elsevier.com/",
        "description": "Access to ScienceDirect, Scopus, and other Elsevier databases",
        "cost": "Free tier available, institutional access recommended"
    },
    "wiley": {
        "url": "https://onlinelibrary.wiley.com/library-info/resources/text-and-datamining",
        "description": "Access to Wiley Online Library",
        "cost": "Varies, often requires institutional access"
    },
    "pubmed": {
        "url": "https://ncbi.nlm.nih.gov/books/NBK25497/",
        "description": "Optional API key for higher rate limits",
        "cost": "Free"
    }
}


def print_api_setup_guide():
    """Print guide for setting up API keys."""
    print("🔑 API Setup Guide for Enhanced Paper Discovery")
    print("=" * 60)
    
    print("\n📚 Currently Enabled (Free APIs):")
    free_sources = ["ArXiv", "Semantic Scholar", "CrossRef", "PubMed"]
    for source in free_sources:
        print(f"  ✅ {source}")
    
    print("\n🔐 Available with API Keys:")
    for api_name, info in API_KEY_INSTRUCTIONS.items():
        print(f"\n  📖 {api_name.upper()}:")
        print(f"     URL: {info['url']}")
        print(f"     Description: {info['description']}")
        print(f"     Cost: {info['cost']}")
    
    print("\n⚙️ Setup Instructions:")
    print("1. Get API keys from the URLs above")
    print("2. Set environment variables:")
    print("   export SPRINGER_API_KEY='your-key-here'")
    print("   export ELSEVIER_API_KEY='your-key-here'")
    print("   export WILEY_API_KEY='your-key-here'")
    print("3. Update api_config.py to enable the APIs")
    print("4. Restart the research system")
    
    print("\n💡 Pro Tips:")
    print("- Start with free APIs (ArXiv, Semantic Scholar, CrossRef)")
    print("- Institutional access often provides better API limits")
    print("- Some publishers require VPN/institutional network")
    print("- Always respect rate limits and terms of service")


if __name__ == "__main__":
    print_api_setup_guide()