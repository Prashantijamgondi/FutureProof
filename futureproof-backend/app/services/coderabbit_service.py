import httpx
from typing import Dict, Any, List, Optional
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class CodeRabbitService:
    """Service for CodeRabbit integration"""
    
    def __init__(self):
        self.api_key = settings.CODERABBIT_API_KEY
        self.base_url = "https://api.coderabbit.ai/v1"
    
    async def review_code(
        self,
        code: str,
        file_path: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Submit code for CodeRabbit review"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "code": code,
                "file_path": file_path,
                "context": context or ""
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/review",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                
                return response.json()
                
        except Exception as e:
            logger.error(f"CodeRabbit review failed: {str(e)}")
            return {"error": str(e)}
    
    async def create_pr_comment(
        self,
        repo: str,
        pr_number: int,
        comments: List[Dict[str, Any]]
    ) -> bool:
        """Create PR comments via CodeRabbit"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "repository": repo,
                "pull_request": pr_number,
                "comments": comments
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/pr/comment",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                
                logger.info(f"Created {len(comments)} PR comments")
                return True
                
        except Exception as e:
            logger.error(f"Failed to create PR comments: {str(e)}")
            return False
    
    async def analyze_pr_diff(
        self,
        diff_content: str
    ) -> Dict[str, Any]:
        """Analyze PR diff for quality issues"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {"diff": diff_content}
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/analyze/diff",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                
                return response.json()
                
        except Exception as e:
            logger.error(f"Diff analysis failed: {str(e)}")
            return {"error": str(e)}
