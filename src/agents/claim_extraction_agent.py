"""
Paper Reading & Claim Extraction Agent - Extracts structured claims from papers.
"""
import re
from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime

from ..models.data_models import PaperMetadata, Claim
from .base_agent import BaseAgent


class ClaimExtractionAgent(BaseAgent):
    """Agent responsible for reading papers and extracting structured claims."""
    
    def __init__(self, memory_store=None):
        super().__init__("ClaimExtractionAgent", memory_store)
        self.claim_patterns = self._initialize_claim_patterns()
        self.metric_patterns = self._initialize_metric_patterns()
    
    def _initialize_claim_patterns(self) -> List[Dict[str, Any]]:
        """Initialize patterns for identifying claims in text."""
        return [
            {
                "pattern": r"(improves?|increases?|reduces?|decreases?|achieves?|outperforms?)\s+.*?by\s+(\d+(?:\.\d+)?)\s*(%|percent|points?)",
                "type": "performance_improvement",
                "confidence": 0.9
            },
            {
                "pattern": r"(accuracy|precision|recall|f1-score|auc)\s+of\s+(\d+(?:\.\d+)?)\s*(%|percent)?",
                "type": "metric_achievement",
                "confidence": 0.8
            },
            {
                "pattern": r"(significantly|substantially|considerably)\s+(better|worse|higher|lower|improved)",
                "type": "comparative_claim",
                "confidence": 0.7
            },
            {
                "pattern": r"(state-of-the-art|sota|best|superior|novel|first)",
                "type": "novelty_claim",
                "confidence": 0.6
            }
        ]
    
    def _initialize_metric_patterns(self) -> List[Dict[str, str]]:
        """Initialize patterns for extracting metrics."""
        return [
            {"pattern": r"accuracy[:\s]+(\d+(?:\.\d+)?)\s*(%|percent)?", "metric": "accuracy"},
            {"pattern": r"precision[:\s]+(\d+(?:\.\d+)?)\s*(%|percent)?", "metric": "precision"},
            {"pattern": r"recall[:\s]+(\d+(?:\.\d+)?)\s*(%|percent)?", "metric": "recall"},
            {"pattern": r"f1[-\s]score[:\s]+(\d+(?:\.\d+)?)\s*(%|percent)?", "metric": "f1_score"},
            {"pattern": r"auc[:\s]+(\d+(?:\.\d+)?)", "metric": "auc"},
            {"pattern": r"rmse[:\s]+(\d+(?:\.\d+)?)", "metric": "rmse"},
            {"pattern": r"mae[:\s]+(\d+(?:\.\d+)?)", "metric": "mae"}
        ]
    
    async def process(self, papers: List[PaperMetadata]) -> List[Claim]:
        """
        Extract claims from a list of papers.
        
        Args:
            papers: List of papers to process
            
        Returns:
            List of extracted claims
        """
        self.log_operation("claim_extraction_start", {"paper_count": len(papers)})
        
        all_claims = []
        
        # Process papers concurrently (with limit to avoid overwhelming)
        semaphore = asyncio.Semaphore(5)  # Limit concurrent processing
        
        tasks = [self._extract_claims_from_paper(paper, semaphore) for paper in papers]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                all_claims.extend(result)
            elif isinstance(result, Exception):
                self.logger.error(f"Error processing paper: {result}")
        
        # Store results
        await self.store_result("extracted_claims", all_claims)
        
        self.log_operation("claim_extraction_complete", {
            "total_claims": len(all_claims),
            "papers_processed": len([r for r in results if isinstance(r, list)])
        })
        
        return all_claims
    
    async def _extract_claims_from_paper(self, paper: PaperMetadata, semaphore: asyncio.Semaphore) -> List[Claim]:
        """Extract claims from a single paper."""
        async with semaphore:
            claims = []
            paper_id = self._generate_paper_id(paper)
            
            # Extract claims from abstract (main source for now)
            abstract_claims = self._extract_claims_from_text(
                paper.abstract, 
                paper_id, 
                "abstract"
            )
            claims.extend(abstract_claims)
            
            # Extract claims from title
            title_claims = self._extract_claims_from_text(
                paper.title, 
                paper_id, 
                "title"
            )
            claims.extend(title_claims)
            
            # Add paper-level metadata to claims
            for claim in claims:
                claim.datasets = self._extract_datasets_from_text(paper.abstract)
                claim.conditions = self._extract_conditions_from_text(paper.abstract)
                claim.limitations = self._extract_limitations_from_text(paper.abstract)
            
            return claims
    
    def _extract_claims_from_text(self, text: str, paper_id: str, source: str) -> List[Claim]:
        """Extract claims from a text segment."""
        claims = []
        
        # Split text into sentences
        sentences = self._split_into_sentences(text)
        
        for sentence in sentences:
            # Check each claim pattern
            for pattern_info in self.claim_patterns:
                matches = re.finditer(pattern_info["pattern"], sentence, re.IGNORECASE)
                
                for match in matches:
                    claim = self._create_claim_from_match(
                        sentence, 
                        match, 
                        pattern_info, 
                        paper_id, 
                        source
                    )
                    if claim:
                        claims.append(claim)
        
        return claims
    
    def _create_claim_from_match(self, sentence: str, match: re.Match, 
                               pattern_info: Dict[str, Any], paper_id: str, 
                               source: str) -> Optional[Claim]:
        """Create a structured claim from a regex match."""
        
        # Extract metrics from the sentence
        metrics = self._extract_metrics_from_sentence(sentence)
        
        # Extract evidence (surrounding context)
        evidence = [sentence.strip()]
        
        # Generate claim ID
        claim_id = f"{paper_id}_{source}_{len(sentence)}_{datetime.now().timestamp()}"
        
        claim = Claim(
            id=claim_id,
            statement=sentence.strip(),
            paper_id=paper_id,
            evidence=evidence,
            metrics=metrics,
            confidence=pattern_info["confidence"]
        )
        
        return claim
    
    def _extract_metrics_from_sentence(self, sentence: str) -> Dict[str, Any]:
        """Extract numerical metrics from a sentence."""
        metrics = {}
        
        for pattern_info in self.metric_patterns:
            matches = re.finditer(pattern_info["pattern"], sentence, re.IGNORECASE)
            
            for match in matches:
                metric_name = pattern_info["metric"]
                try:
                    value = float(match.group(1))
                    metrics[metric_name] = value
                except (ValueError, IndexError):
                    continue
        
        return metrics
    
    def _extract_datasets_from_text(self, text: str) -> List[str]:
        """Extract dataset names from text."""
        datasets = []
        
        # Common dataset patterns
        dataset_patterns = [
            r"\b(MNIST|CIFAR-10|CIFAR-100|ImageNet|COCO|Pascal VOC)\b",
            r"\b(ChEMBL|PubChem|DrugBank|ZINC|QM9)\b",
            r"\b(Cora|CiteSeer|PubMed|Reddit|OGB)\b",
            r"\b(GLUE|SQuAD|CoNLL|WikiText)\b"
        ]
        
        for pattern in dataset_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                datasets.append(match.group(0))
        
        return list(set(datasets))
    
    def _extract_conditions_from_text(self, text: str) -> List[str]:
        """Extract experimental conditions from text."""
        conditions = []
        
        # Pattern for experimental conditions
        condition_patterns = [
            r"under\s+([^.]+?)(?:\.|,|;)",
            r"with\s+([^.]+?)(?:\.|,|;)",
            r"using\s+([^.]+?)(?:\.|,|;)",
            r"on\s+([^.]+?)(?:\.|,|;)"
        ]
        
        for pattern in condition_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                condition = match.group(1).strip()
                if len(condition) < 100:  # Avoid very long matches
                    conditions.append(condition)
        
        return conditions
    
    def _extract_limitations_from_text(self, text: str) -> List[str]:
        """Extract limitations mentioned in text."""
        limitations = []
        
        # Pattern for limitations
        limitation_keywords = [
            "limitation", "limited", "constraint", "drawback", 
            "weakness", "shortcoming", "challenge", "issue"
        ]
        
        sentences = self._split_into_sentences(text)
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in limitation_keywords):
                limitations.append(sentence.strip())
        
        return limitations
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting (could be improved with NLTK)
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _generate_paper_id(self, paper: PaperMetadata) -> str:
        """Generate a unique ID for a paper."""
        # Use DOI if available, otherwise create from title and year
        if paper.doi:
            return paper.doi.replace('/', '_').replace('.', '_')
        elif paper.arxiv_id:
            return f"arxiv_{paper.arxiv_id}"
        else:
            # Create ID from title and year
            title_words = re.findall(r'\w+', paper.title.lower())[:5]
            title_part = '_'.join(title_words)
            return f"{title_part}_{paper.year}"