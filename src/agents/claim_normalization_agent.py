"""
Claim Normalization & Verification Agent - Normalizes claims into comparable formats.
"""
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from ..models.data_models import Claim
from .base_agent import BaseAgent


class ClaimNormalizationAgent(BaseAgent):
    """Agent responsible for normalizing and verifying claims."""
    
    def __init__(self, memory_store=None):
        super().__init__("ClaimNormalizationAgent", memory_store)
        self.normalization_rules = self._initialize_normalization_rules()
        self.verification_patterns = self._initialize_verification_patterns()
    
    def _initialize_normalization_rules(self) -> Dict[str, Any]:
        """Initialize rules for claim normalization."""
        return {
            "metric_standardization": {
                "accuracy": ["acc", "accuracy", "correct rate"],
                "precision": ["prec", "precision"],
                "recall": ["rec", "recall", "sensitivity"],
                "f1_score": ["f1", "f-score", "f1-score", "f-measure"],
                "auc": ["auc", "area under curve", "auroc"],
                "rmse": ["rmse", "root mean square error"],
                "mae": ["mae", "mean absolute error"]
            },
            "unit_standardization": {
                "percentage": ["%", "percent", "percentage"],
                "decimal": ["decimal", "fraction"],
                "points": ["points", "pts"]
            },
            "condition_standardization": {
                "dataset_patterns": [
                    r"on\s+([A-Z][A-Za-z0-9\-]+)\s+dataset",
                    r"using\s+([A-Z][A-Za-z0-9\-]+)\s+data",
                    r"evaluated\s+on\s+([A-Z][A-Za-z0-9\-]+)"
                ],
                "method_patterns": [
                    r"using\s+([A-Z][A-Za-z\s]+)\s+method",
                    r"with\s+([A-Z][A-Za-z\s]+)\s+approach",
                    r"employing\s+([A-Z][A-Za-z\s]+)"
                ]
            }
        }
    
    def _initialize_verification_patterns(self) -> Dict[str, Any]:
        """Initialize patterns for claim verification."""
        return {
            "weak_indicators": [
                "might", "could", "possibly", "potentially", "seems",
                "appears", "suggests", "indicates", "preliminary"
            ],
            "strong_indicators": [
                "demonstrates", "proves", "shows", "achieves", "outperforms",
                "significantly", "substantially", "consistently"
            ],
            "uncertainty_markers": [
                "approximately", "around", "about", "roughly", "nearly"
            ],
            "statistical_indicators": [
                "p <", "p-value", "confidence interval", "standard deviation",
                "statistical significance", "t-test", "anova"
            ]
        }
    
    async def process(self, claims: List[Claim]) -> List[Claim]:
        """
        Normalize and verify claims.
        
        Args:
            claims: List of raw claims to normalize
            
        Returns:
            List of normalized and verified claims
        """
        self.log_operation("claim_normalization_start", {"claim_count": len(claims)})
        
        normalized_claims = []
        
        for claim in claims:
            try:
                normalized_claim = await self._normalize_claim(claim)
                verified_claim = await self._verify_claim(normalized_claim)
                normalized_claims.append(verified_claim)
            except Exception as e:
                self.logger.warning(f"Failed to normalize claim {claim.id}: {e}")
                # Keep original claim with reduced confidence
                claim.confidence *= 0.5
                normalized_claims.append(claim)
        
        # Store results
        await self.store_result("normalized_claims", normalized_claims)
        
        self.log_operation("claim_normalization_complete", {
            "normalized_count": len(normalized_claims),
            "avg_confidence": sum(c.confidence for c in normalized_claims) / len(normalized_claims) if normalized_claims else 0
        })
        
        return normalized_claims
    
    async def _normalize_claim(self, claim: Claim) -> Claim:
        """Normalize a single claim."""
        normalized_claim = claim.model_copy()
        
        # Normalize statement
        normalized_claim.statement = self._normalize_statement(claim.statement)
        
        # Normalize metrics
        normalized_claim.metrics = self._normalize_metrics(claim.metrics)
        
        # Normalize conditions
        normalized_claim.conditions = self._normalize_conditions(claim.conditions)
        
        # Extract and normalize datasets
        normalized_claim.datasets = self._normalize_datasets(claim.datasets, claim.statement)
        
        return normalized_claim
    
    def _normalize_statement(self, statement: str) -> str:
        """Normalize claim statement text."""
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', statement.strip())
        
        # Standardize metric names
        for standard_name, variants in self.normalization_rules["metric_standardization"].items():
            for variant in variants:
                pattern = rf'\b{re.escape(variant)}\b'
                normalized = re.sub(pattern, standard_name, normalized, flags=re.IGNORECASE)
        
        # Standardize units
        for standard_unit, variants in self.normalization_rules["unit_standardization"].items():
            for variant in variants:
                if variant == "%":
                    normalized = re.sub(r'(\d+(?:\.\d+)?)\s*%', r'\1 percent', normalized)
                else:
                    pattern = rf'\b{re.escape(variant)}\b'
                    normalized = re.sub(pattern, standard_unit, normalized, flags=re.IGNORECASE)
        
        return normalized
    
    def _normalize_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize metric names and values."""
        normalized_metrics = {}
        
        for metric_name, value in metrics.items():
            # Standardize metric name
            standard_name = metric_name.lower()
            for standard, variants in self.normalization_rules["metric_standardization"].items():
                if metric_name.lower() in [v.lower() for v in variants]:
                    standard_name = standard
                    break
            
            # Normalize value (convert percentages to decimals if needed)
            normalized_value = value
            if isinstance(value, (int, float)):
                if standard_name in ["accuracy", "precision", "recall", "f1_score"] and value > 1:
                    # Likely a percentage, convert to decimal
                    normalized_value = value / 100.0
            
            normalized_metrics[standard_name] = normalized_value
        
        return normalized_metrics
    
    def _normalize_conditions(self, conditions: List[str]) -> List[str]:
        """Normalize experimental conditions."""
        normalized_conditions = []
        
        for condition in conditions:
            # Extract datasets
            for pattern in self.normalization_rules["condition_standardization"]["dataset_patterns"]:
                matches = re.finditer(pattern, condition, re.IGNORECASE)
                for match in matches:
                    dataset = match.group(1)
                    normalized_conditions.append(f"dataset: {dataset}")
            
            # Extract methods
            for pattern in self.normalization_rules["condition_standardization"]["method_patterns"]:
                matches = re.finditer(pattern, condition, re.IGNORECASE)
                for match in matches:
                    method = match.group(1).strip()
                    normalized_conditions.append(f"method: {method}")
            
            # Keep original if no specific pattern matched
            if not any(nc.split(": ", 1)[1] in condition for nc in normalized_conditions):
                normalized_conditions.append(condition)
        
        return list(set(normalized_conditions))  # Remove duplicates
    
    def _normalize_datasets(self, datasets: List[str], statement: str) -> List[str]:
        """Normalize dataset names."""
        normalized_datasets = set(datasets)
        
        # Extract additional datasets from statement
        dataset_patterns = [
            r'\b(MNIST|CIFAR-10|CIFAR-100|ImageNet|COCO|Pascal VOC)\b',
            r'\b(ChEMBL|PubChem|DrugBank|ZINC|QM9)\b',
            r'\b(Cora|CiteSeer|PubMed|Reddit|OGB)\b',
            r'\b(GLUE|SQuAD|CoNLL|WikiText)\b'
        ]
        
        for pattern in dataset_patterns:
            matches = re.finditer(pattern, statement, re.IGNORECASE)
            for match in matches:
                normalized_datasets.add(match.group(0))
        
        return list(normalized_datasets)
    
    async def _verify_claim(self, claim: Claim) -> Claim:
        """Verify claim strength and adjust confidence."""
        verified_claim = claim.model_copy()
        
        # Calculate verification score
        verification_score = self._calculate_verification_score(claim.statement)
        
        # Adjust confidence based on verification
        verified_claim.confidence = min(claim.confidence * verification_score, 1.0)
        
        # Add verification metadata
        verified_claim.metadata = getattr(verified_claim, 'metadata', {})
        verified_claim.metadata['verification_score'] = verification_score
        verified_claim.metadata['verification_timestamp'] = datetime.now().isoformat()
        
        return verified_claim
    
    def _calculate_verification_score(self, statement: str) -> float:
        """Calculate verification score based on statement content."""
        score = 1.0
        statement_lower = statement.lower()
        
        # Check for weak indicators
        weak_count = sum(1 for indicator in self.verification_patterns["weak_indicators"] 
                        if indicator in statement_lower)
        score -= weak_count * 0.1
        
        # Check for strong indicators
        strong_count = sum(1 for indicator in self.verification_patterns["strong_indicators"] 
                          if indicator in statement_lower)
        score += strong_count * 0.1
        
        # Check for uncertainty markers
        uncertainty_count = sum(1 for marker in self.verification_patterns["uncertainty_markers"] 
                               if marker in statement_lower)
        score -= uncertainty_count * 0.05
        
        # Check for statistical indicators (positive)
        stats_count = sum(1 for indicator in self.verification_patterns["statistical_indicators"] 
                         if indicator in statement_lower)
        score += stats_count * 0.15
        
        # Check for numerical evidence
        if re.search(r'\d+(?:\.\d+)?', statement):
            score += 0.1
        
        # Ensure score is between 0.1 and 1.5
        return max(0.1, min(score, 1.5))
    
    def get_normalization_stats(self, claims: List[Claim]) -> Dict[str, Any]:
        """Get statistics about claim normalization."""
        if not claims:
            return {}
        
        return {
            "total_claims": len(claims),
            "avg_confidence": sum(c.confidence for c in claims) / len(claims),
            "claims_with_metrics": len([c for c in claims if c.metrics]),
            "claims_with_datasets": len([c for c in claims if c.datasets]),
            "claims_with_conditions": len([c for c in claims if c.conditions]),
            "unique_datasets": len(set(d for c in claims for d in c.datasets)),
            "confidence_distribution": {
                "high (>0.8)": len([c for c in claims if c.confidence > 0.8]),
                "medium (0.5-0.8)": len([c for c in claims if 0.5 <= c.confidence <= 0.8]),
                "low (<0.5)": len([c for c in claims if c.confidence < 0.5])
            }
        }