import subprocess
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class GitOperations:
    """Git utility operations"""
    
    @staticmethod
    def get_repo_info(repo_path: str) -> Dict[str, Any]:
        """Get repository information"""
        try:
            # Get current branch
            branch = subprocess.check_output(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                cwd=repo_path,
                text=True
            ).strip()
            
            # Get latest commit
            commit = subprocess.check_output(
                ['git', 'rev-parse', 'HEAD'],
                cwd=repo_path,
                text=True
            ).strip()
            
            # Get remote URL
            remote = subprocess.check_output(
                ['git', 'config', '--get', 'remote.origin.url'],
                cwd=repo_path,
                text=True
            ).strip()
            
            return {
                "branch": branch,
                "commit": commit,
                "remote": remote
            }
            
        except Exception as e:
            logger.error(f"Failed to get repo info: {str(e)}")
            return {}
    
    @staticmethod
    def create_branch(repo_path: str, branch_name: str) -> bool:
        """Create a new branch"""
        try:
            subprocess.run(
                ['git', 'checkout', '-b', branch_name],
                cwd=repo_path,
                check=True
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to create branch: {str(e)}")
            return False
