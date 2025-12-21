from abc import ABC, abstractmethod
from typing import Dict, Any, List
import time
import logging

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all AI agents"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"agent.{name}")
    
    @abstractmethod
    async def analyze(self, code_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code and return findings"""
        pass
    
    def calculate_score(self, issues: List[Dict[str, Any]]) -> float:
        """Calculate score based on issues (0-100)"""
        if not issues:
            return 100.0
        
        severity_weights = {
            "critical": 25,
            "high": 10,
            "medium": 5,
            "low": 2
        }
        
        penalty = sum(severity_weights.get(issue.get("severity", "low"), 0) for issue in issues)
        score = max(0, 100 - penalty)
        return round(score, 2)
    
    async def run(self, code_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run agent analysis with timing"""
        start_time = time.time()
        self.logger.info(f"{self.name} agent started")
        
        try:
            result = await self.analyze(code_data)
            processing_time = time.time() - start_time
            
            result["processing_time"] = processing_time
            result["agent_name"] = self.name
            result["status"] = "completed"
            
            self.logger.info(f"{self.name} completed in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"{self.name} failed: {str(e)}")
            return {
                "agent_name": self.name,
                "status": "failed",
                "error": str(e),
                "processing_time": time.time() - start_time
            }
