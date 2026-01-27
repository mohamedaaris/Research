"""
Topic Expansion Agent - Decomposes research topics into subtopics and research directions.
"""
from typing import List, Dict, Any
import re
from ..models.data_models import TopicMap
from .base_agent import BaseAgent


class TopicExpansionAgent(BaseAgent):
    """Agent responsible for expanding research topics into structured maps."""
    
    def __init__(self, memory_store=None):
        super().__init__("TopicExpansionAgent", memory_store)
        self.domain_keywords = self._load_domain_keywords()
    
    def _load_domain_keywords(self) -> Dict[str, List[str]]:
        """Load domain-specific keywords for topic expansion."""
        return {
            "machine_learning": [
                "neural networks", "deep learning", "supervised learning", 
                "unsupervised learning", "reinforcement learning", "transfer learning"
            ],
            "drug_discovery": [
                "molecular design", "pharmacokinetics", "drug screening", 
                "target identification", "lead optimization", "clinical trials"
            ],
            "graph_neural_networks": [
                "graph convolution", "message passing", "graph attention", 
                "graph pooling", "node classification", "link prediction"
            ],
            "computer_vision": [
                "image classification", "object detection", "segmentation", 
                "feature extraction", "convolutional networks"
            ],
            "natural_language_processing": [
                "text classification", "named entity recognition", "sentiment analysis", 
                "language modeling", "machine translation"
            ]
        }
    
    async def process(self, topic: str) -> TopicMap:
        """
        Expand a research topic into a structured topic map.
        
        Args:
            topic: Main research topic string
            
        Returns:
            TopicMap: Structured representation of the topic
        """
        self.log_operation("topic_expansion_start", {"topic": topic})
        
        # Extract main components
        main_topic = topic.strip()
        subtopics = self._extract_subtopics(topic)
        methods = self._extract_methods(topic)
        datasets = self._extract_datasets(topic)
        related_areas = self._extract_related_areas(topic)
        keywords = self._extract_keywords(topic)
        
        topic_map = TopicMap(
            main_topic=main_topic,
            subtopics=subtopics,
            methods=methods,
            datasets=datasets,
            related_areas=related_areas,
            keywords=keywords
        )
        
        # Store in memory for other agents
        await self.store_result("topic_map", topic_map)
        
        self.log_operation("topic_expansion_complete", {
            "subtopics_count": len(subtopics),
            "methods_count": len(methods),
            "keywords_count": len(keywords)
        })
        
        return topic_map
    
    def _extract_subtopics(self, topic: str) -> List[str]:
        """Extract potential subtopics from the main topic."""
        subtopics = []
        topic_lower = topic.lower()
        
        # Domain-specific subtopic extraction
        if "graph neural network" in topic_lower or "gnn" in topic_lower:
            subtopics.extend([
                "Graph Convolutional Networks",
                "Graph Attention Networks", 
                "Message Passing Neural Networks",
                "Graph Transformer Networks",
                "Spectral Graph Networks"
            ])
        
        if "drug discovery" in topic_lower:
            subtopics.extend([
                "Molecular Property Prediction",
                "Drug-Target Interaction",
                "Molecular Generation",
                "ADMET Prediction",
                "Virtual Screening"
            ])
        
        if "computer vision" in topic_lower:
            subtopics.extend([
                "Image Classification",
                "Object Detection",
                "Semantic Segmentation",
                "Instance Segmentation",
                "Image Generation"
            ])
        
        # Generic subtopic patterns
        if "classification" in topic_lower:
            subtopics.append("Multi-class Classification")
            subtopics.append("Binary Classification")
        
        if "prediction" in topic_lower:
            subtopics.append("Regression Analysis")
            subtopics.append("Time Series Prediction")
        
        return list(set(subtopics))
    
    def _extract_methods(self, topic: str) -> List[str]:
        """Extract relevant methods and techniques."""
        methods = []
        topic_lower = topic.lower()
        
        # Method extraction based on keywords
        method_patterns = {
            "neural": ["Neural Networks", "Deep Learning"],
            "graph": ["Graph Theory", "Network Analysis"],
            "machine learning": ["Supervised Learning", "Unsupervised Learning"],
            "optimization": ["Gradient Descent", "Evolutionary Algorithms"],
            "statistical": ["Statistical Analysis", "Bayesian Methods"]
        }
        
        for pattern, method_list in method_patterns.items():
            if pattern in topic_lower:
                methods.extend(method_list)
        
        return list(set(methods))
    
    def _extract_datasets(self, topic: str) -> List[str]:
        """Extract commonly used datasets for the topic."""
        datasets = []
        topic_lower = topic.lower()
        
        # Domain-specific datasets
        dataset_mapping = {
            "drug discovery": ["ChEMBL", "PubChem", "DrugBank", "ZINC", "QM9"],
            "computer vision": ["ImageNet", "COCO", "CIFAR-10", "MNIST", "Pascal VOC"],
            "natural language": ["GLUE", "SQuAD", "CoNLL", "WikiText", "Common Crawl"],
            "graph": ["Cora", "CiteSeer", "PubMed", "Reddit", "OGB"]
        }
        
        for domain, dataset_list in dataset_mapping.items():
            if any(keyword in topic_lower for keyword in domain.split()):
                datasets.extend(dataset_list)
        
        return list(set(datasets))
    
    def _extract_related_areas(self, topic: str) -> List[str]:
        """Extract related research areas."""
        related_areas = []
        topic_lower = topic.lower()
        
        # Cross-domain relationships
        if "drug discovery" in topic_lower:
            related_areas.extend([
                "Computational Chemistry",
                "Bioinformatics", 
                "Pharmacology",
                "Molecular Biology"
            ])
        
        if "graph neural" in topic_lower:
            related_areas.extend([
                "Network Science",
                "Social Network Analysis",
                "Knowledge Graphs",
                "Recommender Systems"
            ])
        
        if "machine learning" in topic_lower:
            related_areas.extend([
                "Artificial Intelligence",
                "Data Mining",
                "Pattern Recognition",
                "Statistical Learning"
            ])
        
        return list(set(related_areas))
    
    def _extract_keywords(self, topic: str) -> List[str]:
        """Extract relevant keywords for literature search."""
        keywords = []
        topic_lower = topic.lower()
        
        # Extract words from topic
        words = re.findall(r'\b\w+\b', topic_lower)
        keywords.extend(words)
        
        # Add domain-specific keywords
        for domain, keyword_list in self.domain_keywords.items():
            if any(word in topic_lower for word in domain.split('_')):
                keywords.extend(keyword_list)
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'use', 'using'}
        keywords = [kw for kw in keywords if kw not in stop_words and len(kw) > 2]
        
        return list(set(keywords))