# import httpx
# from typing import Dict, Any, Optional, List 
# import logging
# from app.config import settings
# import base64

# logger = logging.getLogger(__name__)

# class GitHubService:
#     """Service for GitHub operations"""
    
#     def __init__(self):
#         self.token = settings.GITHUB_TOKEN
#         self.base_url = "https://api.github.com"
    
#     async def clone_repository(self, repo_url: str, target_path: str) -> bool:
#         """Clone a GitHub repository"""
#         try:
#             import git
            
#             logger.info(f"Cloning {repo_url} to {target_path}")
#             git.Repo.clone_from(repo_url, target_path)
            
#             return True
            
#         except Exception as e:
#             logger.error(f"Failed to clone repository: {str(e)}")
#             return False
    
#     async def get_repository_files(
#         self,
#         owner: str,
#         repo: str,
#         path: str = ""
#     ) -> List[Dict[str, Any]]:
#         """Get repository file tree"""
#         try:
#             headers = {
#                 "Authorization": f"Bearer {self.token}",
#                 "Accept": "application/vnd.github.v3+json"
#             }
            
#             async with httpx.AsyncClient(timeout=30.0) as client:
#                 response = await client.get(
#                     f"{self.base_url}/repos/{owner}/{repo}/contents/{path}",
#                     headers=headers
#                 )
#                 response.raise_for_status()
                
#                 return response.json()
                
#         except Exception as e:
#             logger.error(f"Failed to get repository files: {str(e)}")
#             return []
    
#     async def get_file_content(
#         self,
#         owner: str,
#         repo: str,
#         file_path: str
#     ) -> Optional[str]:
#         """Get content of a specific file"""
#         try:
#             headers = {
#                 "Authorization": f"Bearer {self.token}",
#                 "Accept": "application/vnd.github.v3+json"
#             }
            
#             async with httpx.AsyncClient(timeout=30.0) as client:
#                 response = await client.get(
#                     f"{self.base_url}/repos/{owner}/{repo}/contents/{file_path}",
#                     headers=headers
#                 )
#                 response.raise_for_status()
                
#                 data = response.json()
#                 content = base64.b64decode(data["content"]).decode('utf-8')
                
#                 return content
                
#         except Exception as e:
#             logger.error(f"Failed to get file content: {str(e)}")
#             return None
    
#     async def create_pull_request(
#         self,
#         owner: str,
#         repo: str,
#         title: str,
#         body: str,
#         head: str,
#         base: str = "main"
#     ) -> Dict[str, Any]:
#         """Create a pull request"""
#         try:
#             headers = {
#                 "Authorization": f"Bearer {self.token}",
#                 "Accept": "application/vnd.github.v3+json"
#             }
            
#             payload = {
#                 "title": title,
#                 "body": body,
#                 "head": head,
#                 "base": base
#             }
            
#             async with httpx.AsyncClient(timeout=30.0) as client:
#                 response = await client.post(
#                     f"{self.base_url}/repos/{owner}/{repo}/pulls",
#                     headers=headers,
#                     json=payload
#                 )
#                 response.raise_for_status()
                
#                 return response.json()
                
#         except Exception as e:
#             logger.error(f"Failed to create PR: {str(e)}")
#             return {"error": str(e)}
    
#     async def analyze_pr(
#         self,
#         repo_url: str,
#         pr_number: int,
#         db: Any
#     ):
#         """Analyze a pull request (webhook handler)"""
#         try:
#             # Extract owner/repo from URL
#             parts = repo_url.replace("https://github.com/", "").split("/")
#             owner, repo = parts[0], parts[1]
            
#             # Get PR details
#             headers = {
#                 "Authorization": f"Bearer {self.token}",
#                 "Accept": "application/vnd.github.v3+json"
#             }
            
#             async with httpx.AsyncClient(timeout=30.0) as client:
#                 response = await client.get(
#                     f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}",
#                     headers=headers
#                 )
#                 response.raise_for_status()
                
#                 pr_data = response.json()
                
#                 logger.info(f"Analyzing PR #{pr_number}: {pr_data['title']}")
                
#                 # Trigger analysis workflow here
#                 # (Implementation would call orchestrator service)
                
#         except Exception as e:
#             logger.error(f"PR analysis failed: {str(e)}")
"""
GitHub Service
Handles GitHub repository operations
"""
import os
import logging
import httpx
import tempfile
from typing import Optional
from git import Repo

logger = logging.getLogger(__name__)


class GitHubService:
    """Service for GitHub operations"""
    
    def __init__(self):
        self.github_token = os.getenv("GITHUB_TOKEN")
        
    async def validate_repo_url(self, repo_url: str) -> bool:
        """
        Validate if GitHub repository URL is accessible
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            bool: True if valid and accessible, False otherwise
        """
        try:
            # Extract owner and repo from URL
            # e.g., https://github.com/owner/repo
            parts = repo_url.rstrip('/').split('/')
            if len(parts) < 2:
                return False
            
            repo_name = parts[-1].replace('.git', '')
            owner = parts[-2]
            
            # Basic validation
            if not owner or not repo_name:
                return False
            
            # If we have a GitHub token, check if repo exists
            if self.github_token:
                headers = {
                    "Authorization": f"token {self.github_token}",
                    "Accept": "application/vnd.github.v3+json"
                }
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"https://api.github.com/repos/{owner}/{repo_name}",
                        headers=headers,
                        timeout=10.0
                    )
                    return response.status_code == 200
            
            # Without token, just validate URL format
            return repo_url.startswith("https://github.com/") and len(owner) > 0 and len(repo_name) > 0
            
        except Exception as e:
            logger.error(f"Failed to validate repo URL: {str(e)}")
            return False
    
    async def clone_repository(self, repo_url: str, target_dir: str) -> str:
        """
        Clone a GitHub repository
        
        Args:
            repo_url: GitHub repository URL
            target_dir: Target directory for cloning
            
        Returns:
            str: Path to cloned repository
        """
        try:
            logger.info(f"Cloning repository: {repo_url}")
            
            # Create temp directory if needed
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            
            # Clone repository
            if self.github_token:
                # Use token for private repos
                auth_url = repo_url.replace(
                    "https://github.com/",
                    f"https://{self.github_token}@github.com/"
                )
                repo = Repo.clone_from(auth_url, target_dir)
            else:
                repo = Repo.clone_from(repo_url, target_dir)
            
            logger.info(f"Repository cloned successfully to: {target_dir}")
            return target_dir
            
        except Exception as e:
            logger.error(f"Failed to clone repository: {str(e)}")
            raise
    
    async def get_repo_info(self, repo_url: str) -> dict:
        """
        Get repository information from GitHub API
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            dict: Repository information
        """
        try:
            parts = repo_url.rstrip('/').split('/')
            repo_name = parts[-1].replace('.git', '')
            owner = parts[-2]
            
            headers = {}
            if self.github_token:
                headers["Authorization"] = f"token {self.github_token}"
            
            headers["Accept"] = "application/vnd.github.v3+json"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.github.com/repos/{owner}/{repo_name}",
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "name": data.get("name"),
                        "description": data.get("description"),
                        "language": data.get("language"),
                        "stars": data.get("stargazers_count"),
                        "forks": data.get("forks_count"),
                        "is_private": data.get("private"),
                        "default_branch": data.get("default_branch"),
                    }
                
                return {}
                
        except Exception as e:
            logger.error(f"Failed to get repo info: {str(e)}")
            return {}
