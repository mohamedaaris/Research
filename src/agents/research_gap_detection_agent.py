"""
Research Gap Detection Agent - Identifies unexplored research areas and opportunities.
"""
from typing import List, Dict, Any, Set
from collections import Counter, defaultdict
import re

from ..models.data_models import TopicMap, Claim, ResearchGap
from .base_agent import BaseAgent


class ResearchGapDetectionAgent(BaseAgent):
    """Agent responsible for identifying research gaps and opportunities."""
    
    def __init__(self, memory_store=None):
        super().__init__("ResearchGapDetectionAgent", memory_store)
        self.gap_detection_rules = self._initialize_gap_detection_rules()
    
    def _initialize_gap_detection_rules(self) -> Dict[str, Any]:
        """Initialize rules for detecting different types of research gaps."""
        return {
            "coverage_thresholds": {
                "subtopic_min_claims": 3,  # Minimum claims per subtopic
                "method_min_claims": 2,    # Minimum claims per method
                "dataset_min_papers": 2    # Minimum papers per dataset
            },
            "temporal_gaps": {
                "recent_years": 3,  # Consider papers from last 3 years as recent
                "min_recent_ratio": 0.3  # At least 30% of papers should be recent
            },
            "methodological_gaps": [
                "cross-validation", "ablation study", "statistical significance",
                "baseline comparison", "error analysis", "hyperparameter tuning"
            ],
            "evaluation_gaps": [
                "real-world evaluation", "user study", "clinical trial",
                "longitudinal study", "multi-domain evaluation"
            ]
        }
    
    async def process(self, topic_map: TopicMap, claims: List[Claim]) -> List[ResearchGap]:
        """
        Detect research gaps based on topic map and extracted claims.
        
        Args:
            topic_map: Structured topic information
            claims: List of extracted claims
            
        Returns:
            List of identified research gaps
        """
        self.log_operation("research_gap_detection_start", {
            "subtopics": len(topic_map.subtopics),
            "claims": len(claims)
        })
        
        gaps = []
        
        # Detect different types of gaps
        coverage_gaps = await self._detect_coverage_gaps(topic_map, claims)
        gaps.extend(coverage_gaps)
        
        methodological_gaps = await self._detect_methodological_gaps(claims)
        gaps.extend(methodological_gaps)
        
        dataset_gaps = await self._detect_dataset_gaps(topic_map, claims)
        gaps.extend(dataset_gaps)
        
        temporal_gaps = await self._detect_temporal_gaps(claims)
        gaps.extend(temporal_gaps)
        
        evaluation_gaps = await self._detect_evaluation_gaps(claims)
        gaps.extend(evaluation_gaps)
        
        # Rank gaps by priority
        ranked_gaps = self._rank_gaps(gaps)
        
        # Store results
        await self.store_result("research_gaps", ranked_gaps)
        
        self.log_operation("research_gap_detection_complete", {
            "total_gaps": len(ranked_gaps),
            "coverage_gaps": len(coverage_gaps),
            "methodological_gaps": len(methodological_gaps),
            "dataset_gaps": len(dataset_gaps)
        })
        
        return ranked_gaps
    
    async def _detect_coverage_gaps(self, topic_map: TopicMap, claims: List[Claim]) -> List[ResearchGap]:
        """Detect gaps in topic coverage."""
        gaps = []
        
        # Analyze subtopic coverage
        subtopic_claims = defaultdict(list)
        for claim in claims:
            for subtopic in topic_map.subtopics:
                if subtopic.lower() in claim.statement.lower():
                    subtopic_claims[subtopic].append(claim)
        
        # Identify underexplored subtopics
        min_claims = self.gap_detection_rules["coverage_thresholds"]["subtopic_min_claims"]
        for subtopic in topic_map.subtopics:
            claim_count = len(subtopic_claims[subtopic])
            if claim_count < min_claims:
                gap = ResearchGap(
                    description=f"Limited research on {subtopic}",
                    gap_type="unexplored_topic",
                    related_topics=[subtopic],
                    potential_questions=[
                        f"How does {subtopic} compare to other approaches?",
                        f"What are the limitations of current {subtopic} methods?",
                        f"Can {subtopic} be applied to new domains?"
                    ],
                    priority=self._calculate_priority(subtopic, claim_count, min_claims)
                )
                gaps.append(gap)
        
        # Analyze method coverage
        method_claims = defaultdict(list)
        for claim in claims:
            for method in topic_map.methods:
                if method.lower() in claim.statement.lower():
                    method_claims[method].append(claim)
        
        min_method_claims = self.gap_detection_rules["coverage_thresholds"]["method_min_claims"]
        for method in topic_map.methods:
            claim_count = len(method_claims[method])
            if claim_count < min_method_claims:
                gap = ResearchGap(
                    description=f"Insufficient evaluation of {method}",
                    gap_type="underrepresented_method",
                    related_topics=[method],
                    potential_questions=[
                        f"How effective is {method} compared to alternatives?",
                        f"What are the computational requirements of {method}?",
                        f"In which scenarios does {method} perform best?"
                    ],
                    priority=self._calculate_priority(method, claim_count, min_method_claims)
                )
                gaps.append(gap)
        
        return gaps
    
    async def _detect_methodological_gaps(self, claims: List[Claim]) -> List[ResearchGap]:
        """Detect gaps in research methodology."""
        gaps = []
        
        # Check for missing methodological practices
        methodology_coverage = {}
        for practice in self.gap_detection_rules["methodological_gaps"]:
            coverage_count = 0
            for claim in claims:
                if practice.lower() in claim.statement.lower():
                    coverage_count += 1
            methodology_coverage[practice] = coverage_count
        
        # Identify underrepresented practices
        total_claims = len(claims)
        for practice, count in methodology_coverage.items():
            coverage_ratio = count / total_claims if total_claims > 0 else 0
            
            if coverage_ratio < 0.2:  # Less than 20% coverage
                gap = ResearchGap(
                    description=f"Limited use of {practice} in research",
                    gap_type="methodological_gap",
                    related_topics=[practice],
                    potential_questions=[
                        f"How would results change with proper {practice}?",
                        f"What are the best practices for {practice} in this domain?",
                        f"Why is {practice} not commonly used?"
                    ],
                    priority=0.8 - coverage_ratio  # Higher priority for lower coverage
                )
                gaps.append(gap)
        
        return gaps
    
    async def _detect_dataset_gaps(self, topic_map: TopicMap, claims: List[Claim]) -> List[ResearchGap]:
        """Detect gaps in dataset usage and availability."""
        gaps = []
        
        # Analyze dataset usage
        dataset_usage = Counter()
        for claim in claims:
            for dataset in claim.datasets:
                dataset_usage[dataset] += 1
        
        # Check if expected datasets are underused
        expected_datasets = set(topic_map.datasets)
        used_datasets = set(dataset_usage.keys())
        
        unused_datasets = expected_datasets - used_datasets
        for dataset in unused_datasets:
            gap = ResearchGap(
                description=f"No research found using {dataset} dataset",
                gap_type="missing_dataset",
                related_topics=[dataset],
                potential_questions=[
                    f"How would methods perform on {dataset}?",
                    f"Is {dataset} suitable for current approaches?",
                    f"What challenges does {dataset} present?"
                ],
                priority=0.7
            )
            gaps.append(gap)
        
        # Check for dataset diversity
        if len(used_datasets) < 3 and len(expected_datasets) > 3:
            gap = ResearchGap(
                description="Limited dataset diversity in evaluation",
                gap_type="evaluation_limitation",
                related_topics=list(expected_datasets),
                potential_questions=[
                    "How do methods generalize across different datasets?",
                    "What are the domain-specific challenges?",
                    "Which datasets are most representative?"
                ],
                priority=0.6
            )
            gaps.append(gap)
        
        return gaps
    
    async def _detect_temporal_gaps(self, claims: List[Claim]) -> List[ResearchGap]:
        """Detect temporal gaps in research."""
        gaps = []
        
        # This would require paper publication dates
        # For now, create a placeholder gap about recent developments
        gap = ResearchGap(
            description="Need for recent comparative studies",
            gap_type="temporal_gap",
            related_topics=["recent developments", "comparative analysis"],
            potential_questions=[
                "How do recent methods compare to established ones?",
                "What are the latest trends and developments?",
                "Which recent approaches show the most promise?"
            ],
            priority=0.5
        )
        gaps.append(gap)
        
        return gaps
    
    async def _detect_evaluation_gaps(self, claims: List[Claim]) -> List[ResearchGap]:
        """Detect gaps in evaluation practices."""
        gaps = []
        
        # Check for missing evaluation types
        evaluation_coverage = {}
        for eval_type in self.gap_detection_rules["evaluation_gaps"]:
            coverage_count = 0
            for claim in claims:
                if eval_type.lower() in claim.statement.lower():
                    coverage_count += 1
            evaluation_coverage[eval_type] = coverage_count
        
        # Identify missing evaluation types
        total_claims = len(claims)
        for eval_type, count in evaluation_coverage.items():
            coverage_ratio = count / total_claims if total_claims > 0 else 0
            
            if coverage_ratio < 0.1:  # Less than 10% coverage
                gap = ResearchGap(
                    description=f"Lack of {eval_type} in research",
                    gap_type="evaluation_gap",
                    related_topics=[eval_type],
                    potential_questions=[
                        f"How would methods perform in {eval_type}?",
                        f"What are the challenges of conducting {eval_type}?",
                        f"What metrics are appropriate for {eval_type}?"
                    ],
                    priority=0.7
                )
                gaps.append(gap)
        
        return gaps
    
    def _calculate_priority(self, topic: str, current_count: int, expected_count: int) -> float:
        """Calculate priority score for a research gap."""
        
        # Base priority on how far below expected the current count is
        deficit_ratio = (expected_count - current_count) / expected_count
        base_priority = min(deficit_ratio, 1.0)
        
        # Adjust based on topic importance (simplified)
        importance_keywords = [
            "neural", "deep", "learning", "optimization", "evaluation",
            "performance", "accuracy", "efficiency"
        ]
        
        importance_boost = 0.0
        for keyword in importance_keywords:
            if keyword in topic.lower():
                importance_boost += 0.1
        
        priority = min(base_priority + importance_boost, 1.0)
        return priority
    
    def _rank_gaps(self, gaps: List[ResearchGap]) -> List[ResearchGap]:
        """Rank research gaps by priority."""
        return sorted(gaps, key=lambda g: g.priority, reverse=True)
    
    def get_gap_summary(self, gaps: List[ResearchGap]) -> Dict[str, Any]:
        """Get summary statistics about research gaps."""
        
        if not gaps:
            return {"total": 0}
        
        by_type = Counter(gap.gap_type for gap in gaps)
        priorities = [gap.priority for gap in gaps]
        
        return {
            "total": len(gaps),
            "by_type": dict(by_type),
            "avg_priority": sum(priorities) / len(priorities),
            "high_priority": len([p for p in priorities if p > 0.7]),
            "medium_priority": len([p for p in priorities if 0.4 <= p <= 0.7]),
            "low_priority": len([p for p in priorities if p < 0.4]),
            "top_gaps": [
                {
                    "description": gap.description,
                    "type": gap.gap_type,
                    "priority": gap.priority
                }
                for gap in gaps[:5]
            ]
        }