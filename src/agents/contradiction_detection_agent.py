"""
Contradiction Detection Agent - Identifies contradictions and agreements between claims.
"""
import re
from typing import List, Dict, Any, Optional, Tuple
from itertools import combinations
from datetime import datetime

from ..models.data_models import Claim, Contradiction
from .base_agent import BaseAgent


class ContradictionDetectionAgent(BaseAgent):
    """Agent responsible for detecting contradictions between claims."""
    
    def __init__(self, memory_store=None, similarity_threshold: float = 0.7):
        super().__init__("ContradictionDetectionAgent", memory_store)
        self.similarity_threshold = similarity_threshold
        self.contradiction_patterns = self._initialize_contradiction_patterns()
        self.semantic_similarity_cache = {}
    
    def _initialize_contradiction_patterns(self) -> Dict[str, Any]:
        """Initialize patterns for detecting contradictions."""
        return {
            "direct_opposites": [
                ("increases", "decreases"),
                ("improves", "worsens"),
                ("higher", "lower"),
                ("better", "worse"),
                ("outperforms", "underperforms"),
                ("superior", "inferior"),
                ("effective", "ineffective")
            ],
            "quantitative_thresholds": {
                "accuracy": 0.1,  # 10% difference threshold
                "precision": 0.1,
                "recall": 0.1,
                "f1_score": 0.1,
                "auc": 0.05,
                "rmse": 0.2,
                "mae": 0.2
            },
            "contradiction_indicators": [
                "however", "but", "although", "despite", "contrary to",
                "in contrast", "on the other hand", "nevertheless"
            ]
        }
    
    async def process(self, claims: List[Claim]) -> List[Contradiction]:
        """
        Detect contradictions between claims.
        
        Args:
            claims: List of claims to analyze
            
        Returns:
            List of detected contradictions
        """
        self.log_operation("contradiction_detection_start", {"claim_count": len(claims)})
        
        contradictions = []
        
        # Compare all pairs of claims
        for claim1, claim2 in combinations(claims, 2):
            contradiction = await self._detect_contradiction(claim1, claim2)
            if contradiction:
                contradictions.append(contradiction)
        
        # Store results
        await self.store_result("detected_contradictions", contradictions)
        
        self.log_operation("contradiction_detection_complete", {
            "contradictions_found": len(contradictions),
            "pairs_analyzed": len(list(combinations(claims, 2)))
        })
        
        return contradictions
    
    async def _detect_contradiction(self, claim1: Claim, claim2: Claim) -> Optional[Contradiction]:
        """Detect contradiction between two claims."""
        
        # Skip if claims are from the same paper (less likely to contradict)
        if claim1.paper_id == claim2.paper_id:
            return None
        
        # Check for direct contradictions
        direct_contradiction = self._check_direct_contradiction(claim1, claim2)
        if direct_contradiction:
            return direct_contradiction
        
        # Check for metric contradictions
        metric_contradiction = self._check_metric_contradiction(claim1, claim2)
        if metric_contradiction:
            return metric_contradiction
        
        # Check for conditional contradictions
        conditional_contradiction = self._check_conditional_contradiction(claim1, claim2)
        if conditional_contradiction:
            return conditional_contradiction
        
        return None
    
    def _check_direct_contradiction(self, claim1: Claim, claim2: Claim) -> Optional[Contradiction]:
        """Check for direct textual contradictions."""
        
        # Check if claims are about similar topics
        if not self._are_claims_related(claim1, claim2):
            return None
        
        statement1_lower = claim1.statement.lower()
        statement2_lower = claim2.statement.lower()
        
        # Check for opposite terms
        for positive, negative in self.contradiction_patterns["direct_opposites"]:
            if (positive in statement1_lower and negative in statement2_lower) or \
               (negative in statement1_lower and positive in statement2_lower):
                
                severity = self._calculate_contradiction_severity(claim1, claim2, "direct")
                
                return Contradiction(
                    claim1_id=claim1.id,
                    claim2_id=claim2.id,
                    contradiction_type="direct",
                    explanation=f"Claims contain opposite terms: '{positive}' vs '{negative}'",
                    severity=severity
                )
        
        return None
    
    def _check_metric_contradiction(self, claim1: Claim, claim2: Claim) -> Optional[Contradiction]:
        """Check for contradictions in reported metrics."""
        
        if not claim1.metrics or not claim2.metrics:
            return None
        
        # Find common metrics
        common_metrics = set(claim1.metrics.keys()) & set(claim2.metrics.keys())
        
        for metric in common_metrics:
            value1 = claim1.metrics[metric]
            value2 = claim2.metrics[metric]
            
            if isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
                threshold = self.contradiction_patterns["quantitative_thresholds"].get(metric, 0.15)
                
                if abs(value1 - value2) > threshold:
                    # Check if they're testing on similar conditions
                    if self._have_similar_conditions(claim1, claim2):
                        severity = self._calculate_contradiction_severity(claim1, claim2, "metric")
                        
                        return Contradiction(
                            claim1_id=claim1.id,
                            claim2_id=claim2.id,
                            contradiction_type="methodological",
                            explanation=f"Significant difference in {metric}: {value1:.3f} vs {value2:.3f}",
                            severity=severity
                        )
        
        return None
    
    def _check_conditional_contradiction(self, claim1: Claim, claim2: Claim) -> Optional[Contradiction]:
        """Check for contradictions under specific conditions."""
        
        # Check if claims have overlapping datasets
        common_datasets = set(claim1.datasets) & set(claim2.datasets)
        
        if common_datasets:
            # Look for contradictory statements about the same dataset
            for dataset in common_datasets:
                if self._statements_contradict_on_dataset(claim1, claim2, dataset):
                    severity = self._calculate_contradiction_severity(claim1, claim2, "conditional")
                    
                    return Contradiction(
                        claim1_id=claim1.id,
                        claim2_id=claim2.id,
                        contradiction_type="conditional",
                        explanation=f"Contradictory results on dataset {dataset}",
                        severity=severity
                    )
        
        return None
    
    def _are_claims_related(self, claim1: Claim, claim2: Claim) -> bool:
        """Check if two claims are related enough to potentially contradict."""
        
        # Check for common keywords
        words1 = set(re.findall(r'\b\w+\b', claim1.statement.lower()))
        words2 = set(re.findall(r'\b\w+\b', claim2.statement.lower()))
        
        common_words = words1 & words2
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        meaningful_common = common_words - stop_words
        
        # Claims are related if they share enough meaningful words
        return len(meaningful_common) >= 2
    
    def _have_similar_conditions(self, claim1: Claim, claim2: Claim) -> bool:
        """Check if claims were tested under similar conditions."""
        
        # Check for common datasets
        if set(claim1.datasets) & set(claim2.datasets):
            return True
        
        # Check for similar experimental conditions
        conditions1 = [c.lower() for c in claim1.conditions]
        conditions2 = [c.lower() for c in claim2.conditions]
        
        for c1 in conditions1:
            for c2 in conditions2:
                if self._conditions_similar(c1, c2):
                    return True
        
        return False
    
    def _conditions_similar(self, condition1: str, condition2: str) -> bool:
        """Check if two conditions are similar."""
        
        # Simple similarity check based on common words
        words1 = set(re.findall(r'\b\w+\b', condition1.lower()))
        words2 = set(re.findall(r'\b\w+\b', condition2.lower()))
        
        if not words1 or not words2:
            return False
        
        intersection = words1 & words2
        union = words1 | words2
        
        # Jaccard similarity
        similarity = len(intersection) / len(union) if union else 0
        
        return similarity > 0.3
    
    def _statements_contradict_on_dataset(self, claim1: Claim, claim2: Claim, dataset: str) -> bool:
        """Check if statements contradict each other regarding a specific dataset."""
        
        statement1 = claim1.statement.lower()
        statement2 = claim2.statement.lower()
        dataset_lower = dataset.lower()
        
        # Both statements should mention the dataset
        if dataset_lower not in statement1 or dataset_lower not in statement2:
            return False
        
        # Look for contradictory terms in the context of the dataset
        for positive, negative in self.contradiction_patterns["direct_opposites"]:
            if (positive in statement1 and negative in statement2) or \
               (negative in statement1 and positive in statement2):
                return True
        
        return False
    
    def _calculate_contradiction_severity(self, claim1: Claim, claim2: Claim, 
                                        contradiction_type: str) -> float:
        """Calculate the severity of a contradiction."""
        
        base_severity = {
            "direct": 0.8,
            "methodological": 0.6,
            "conditional": 0.4
        }.get(contradiction_type, 0.5)
        
        # Adjust based on claim confidence
        confidence_factor = (claim1.confidence + claim2.confidence) / 2
        
        # Adjust based on paper impact (if available)
        impact_factor = 1.0
        # This could be enhanced with actual paper impact scores
        
        severity = base_severity * confidence_factor * impact_factor
        
        return min(severity, 1.0)
    
    def get_contradiction_summary(self, contradictions: List[Contradiction]) -> Dict[str, Any]:
        """Get summary statistics about detected contradictions."""
        
        if not contradictions:
            return {"total": 0}
        
        by_type = {}
        severities = []
        
        for contradiction in contradictions:
            # Count by type
            if contradiction.contradiction_type not in by_type:
                by_type[contradiction.contradiction_type] = 0
            by_type[contradiction.contradiction_type] += 1
            
            severities.append(contradiction.severity)
        
        return {
            "total": len(contradictions),
            "by_type": by_type,
            "avg_severity": sum(severities) / len(severities),
            "high_severity": len([s for s in severities if s > 0.7]),
            "medium_severity": len([s for s in severities if 0.4 <= s <= 0.7]),
            "low_severity": len([s for s in severities if s < 0.4])
        }