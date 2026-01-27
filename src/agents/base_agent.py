"""
Base agent class for the research system.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List
import logging


class BaseAgent(ABC):
    """Abstract base class for all research agents."""
    
    def __init__(self, name: str, memory_store=None):
        self.name = name
        self.memory_store = memory_store
        self.logger = logging.getLogger(f"agent.{name}")
        
    @abstractmethod
    async def process(self, input_data: Any) -> Any:
        """Process input data and return results."""
        pass
    
    def log_operation(self, operation: str, details: Dict[str, Any] = None):
        """Log agent operations for traceability."""
        log_data = {
            "agent": self.name,
            "operation": operation,
            "details": details or {}
        }
        self.logger.info(f"Agent operation: {log_data}")
    
    async def store_result(self, key: str, data: Any):
        """Store results in memory for other agents."""
        if self.memory_store:
            await self.memory_store.store(key, data)
    
    async def retrieve_data(self, key: str) -> Any:
        """Retrieve data from memory."""
        if self.memory_store:
            return await self.memory_store.retrieve(key)
        return None