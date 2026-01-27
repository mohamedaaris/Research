"""
Memory store for the research system - manages persistent storage and retrieval.
"""
import json
import pickle
import os
from typing import Any, Dict, List, Optional
from datetime import datetime
import asyncio
from pathlib import Path

from ..models.data_models import KnowledgeNode, KnowledgeEdge


class MemoryStore:
    """Persistent memory store for research data."""
    
    def __init__(self, storage_path: str = "data/memory"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # In-memory cache for fast access
        self.cache: Dict[str, Any] = {}
        self.knowledge_graph: Dict[str, KnowledgeNode] = {}
        self.edges: List[KnowledgeEdge] = []
        self._loaded = False
        
        # Don't load data in __init__ - do it lazily when needed
    
    async def _ensure_loaded(self):
        """Ensure persistent data is loaded."""
        if not self._loaded:
            await self._load_persistent_data()
            self._loaded = True
    
    async def store(self, key: str, data: Any) -> None:
        """Store data with a given key."""
        await self._ensure_loaded()
        self.cache[key] = data
        
        # Persist to disk
        await self._persist_data(key, data)
    
    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve data by key."""
        await self._ensure_loaded()
        if key in self.cache:
            return self.cache[key]
        
        # Try to load from disk
        data = await self._load_data(key)
        if data is not None:
            self.cache[key] = data
        
        return data
    
    async def store_knowledge_node(self, node: KnowledgeNode) -> None:
        """Store a knowledge graph node."""
        await self._ensure_loaded()
        self.knowledge_graph[node.id] = node
        await self._persist_knowledge_graph()
    
    async def store_knowledge_edge(self, edge: KnowledgeEdge) -> None:
        """Store a knowledge graph edge."""
        await self._ensure_loaded()
        self.edges.append(edge)
        await self._persist_knowledge_graph()
    
    async def get_knowledge_node(self, node_id: str) -> Optional[KnowledgeNode]:
        """Retrieve a knowledge graph node."""
        await self._ensure_loaded()
        return self.knowledge_graph.get(node_id)
    
    async def get_related_nodes(self, node_id: str, relationship: str = None) -> List[KnowledgeNode]:
        """Get nodes related to a given node."""
        await self._ensure_loaded()
        related_nodes = []
        
        for edge in self.edges:
            if edge.source_id == node_id:
                if relationship is None or edge.relationship == relationship:
                    target_node = self.knowledge_graph.get(edge.target_id)
                    if target_node:
                        related_nodes.append(target_node)
            elif edge.target_id == node_id:
                if relationship is None or edge.relationship == relationship:
                    source_node = self.knowledge_graph.get(edge.source_id)
                    if source_node:
                        related_nodes.append(source_node)
        
        return related_nodes
    
    async def search_nodes(self, node_type: str = None, **filters) -> List[KnowledgeNode]:
        """Search for nodes based on type and filters."""
        await self._ensure_loaded()
        results = []
        
        for node in self.knowledge_graph.values():
            if node_type and node.type != node_type:
                continue
            
            # Apply filters
            match = True
            for key, value in filters.items():
                if key in node.data and node.data[key] != value:
                    match = False
                    break
            
            if match:
                results.append(node)
        
        return results
    
    async def clear_cache(self) -> None:
        """Clear the in-memory cache."""
        self.cache.clear()
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        await self._ensure_loaded()
        return {
            "cache_size": len(self.cache),
            "knowledge_nodes": len(self.knowledge_graph),
            "knowledge_edges": len(self.edges),
            "storage_path": str(self.storage_path)
        }
    
    async def _persist_data(self, key: str, data: Any) -> None:
        """Persist data to disk."""
        try:
            file_path = self.storage_path / f"{key}.pkl"
            
            # Use pickle for complex objects, JSON for simple ones
            if isinstance(data, (str, int, float, bool, list, dict)):
                with open(file_path.with_suffix('.json'), 'w') as f:
                    json.dump(data, f, indent=2, default=str)
            else:
                with open(file_path, 'wb') as f:
                    pickle.dump(data, f)
        
        except Exception as e:
            print(f"Error persisting data for key {key}: {e}")
    
    async def _load_data(self, key: str) -> Optional[Any]:
        """Load data from disk."""
        try:
            # Try JSON first
            json_path = self.storage_path / f"{key}.json"
            if json_path.exists():
                with open(json_path, 'r') as f:
                    return json.load(f)
            
            # Try pickle
            pkl_path = self.storage_path / f"{key}.pkl"
            if pkl_path.exists():
                with open(pkl_path, 'rb') as f:
                    return pickle.load(f)
        
        except Exception as e:
            print(f"Error loading data for key {key}: {e}")
        
        return None
    
    async def _persist_knowledge_graph(self) -> None:
        """Persist the knowledge graph to disk."""
        try:
            # Save nodes
            nodes_data = {
                node_id: {
                    "id": node.id,
                    "type": node.type,
                    "data": node.data,
                    "created_at": node.created_at.isoformat()
                }
                for node_id, node in self.knowledge_graph.items()
            }
            
            with open(self.storage_path / "knowledge_nodes.json", 'w') as f:
                json.dump(nodes_data, f, indent=2, default=str)
            
            # Save edges
            edges_data = [
                {
                    "source_id": edge.source_id,
                    "target_id": edge.target_id,
                    "relationship": edge.relationship,
                    "weight": edge.weight,
                    "metadata": edge.metadata
                }
                for edge in self.edges
            ]
            
            with open(self.storage_path / "knowledge_edges.json", 'w') as f:
                json.dump(edges_data, f, indent=2, default=str)
        
        except Exception as e:
            print(f"Error persisting knowledge graph: {e}")
    
    async def _load_persistent_data(self) -> None:
        """Load persistent data on startup."""
        try:
            # Load knowledge nodes
            nodes_path = self.storage_path / "knowledge_nodes.json"
            if nodes_path.exists():
                with open(nodes_path, 'r') as f:
                    nodes_data = json.load(f)
                
                for node_id, node_data in nodes_data.items():
                    node = KnowledgeNode(
                        id=node_data["id"],
                        type=node_data["type"],
                        data=node_data["data"],
                        created_at=datetime.fromisoformat(node_data["created_at"])
                    )
                    self.knowledge_graph[node_id] = node
            
            # Load knowledge edges
            edges_path = self.storage_path / "knowledge_edges.json"
            if edges_path.exists():
                with open(edges_path, 'r') as f:
                    edges_data = json.load(f)
                
                for edge_data in edges_data:
                    edge = KnowledgeEdge(
                        source_id=edge_data["source_id"],
                        target_id=edge_data["target_id"],
                        relationship=edge_data["relationship"],
                        weight=edge_data["weight"],
                        metadata=edge_data["metadata"]
                    )
                    self.edges.append(edge)
        
        except Exception as e:
            print(f"Error loading persistent data: {e}")