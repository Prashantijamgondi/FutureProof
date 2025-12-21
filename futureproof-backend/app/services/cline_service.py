# import subprocess
# import json
# import os
# from typing import Dict, Any, List
# import logging
# from app.config import settings

# logger = logging.getLogger(__name__)

# class ClineService:
#     """Service for Cline CLI integration"""
    
#     def __init__(self):
#         self.cline_path = "cline"  # Installed globally via npm
    
#     async def analyze_codebase(self, repo_path: str) -> Dict[str, Any]:
#         """Use Cline CLI to analyze codebase"""
#         try:
#             logger.info(f"Starting Cline analysis for {repo_path}")
            
#             # Run Cline CLI analysis
#             result = await self._run_cline_command([
#                 "analyze",
#                 "--path", repo_path,
#                 "--output", "json",
#                 "--include-metrics"
#             ])
            
#             return {
#                 "status": "success",
#                 "analysis": result,
#                 "file_count": result.get("file_count", 0),
#                 "language_breakdown": result.get("languages", {}),
#                 "complexity_score": result.get("complexity", 0)
#             }
            
#         except Exception as e:
#             logger.error(f"Cline analysis failed: {str(e)}")
#             return {
#                 "status": "failed",
#                 "error": str(e)
#             }
    
#     async def generate_refactoring_suggestions(self, file_path: str) -> List[Dict[str, Any]]:
#         """Generate refactoring suggestions for a file"""
#         try:
#             result = await self._run_cline_command([
#                 "refactor",
#                 "--file", file_path,
#                 "--suggestions-only",
#                 "--output", "json"
#             ])
            
#             return result.get("suggestions", [])
            
#         except Exception as e:
#             logger.error(f"Refactoring suggestions failed: {str(e)}")
#             return []
    
#     async def generate_tests(self, file_path: str) -> str:
#         """Generate test cases for a file"""
#         try:
#             result = await self._run_cline_command([
#                 "generate-tests",
#                 "--file", file_path,
#                 "--framework", "pytest"
#             ])
            
#             return result.get("test_code", "")
            
#         except Exception as e:
#             logger.error(f"Test generation failed: {str(e)}")
#             return ""
    
#     async def _run_cline_command(self, args: List[str]) -> Dict[str, Any]:
#         """Execute Cline CLI command"""
#         try:
#             # Build command
#             cmd = [self.cline_path] + args
            
#             # Execute
#             process = subprocess.run(
#                 cmd,
#                 capture_output=True,
#                 text=True,
#                 timeout=300  # 5 minutes timeout
#             )
            
#             if process.returncode == 0:
#                 # Parse JSON output
#                 try:
#                     return json.loads(process.stdout)
#                 except json.JSONDecodeError:
#                     return {"output": process.stdout}
#             else:
#                 raise Exception(f"Cline command failed: {process.stderr}")
                
#         except subprocess.TimeoutExpired:
#             raise Exception("Cline command timed out")
#         except Exception as e:
#             raise Exception(f"Cline execution error: {str(e)}")
    
#     async def extract_code_structure(self, repo_path: str) -> Dict[str, Any]:
#         """Extract code structure and AST information"""
#         try:
#             result = await self._run_cline_command([
#                 "structure",
#                 "--path", repo_path,
#                 "--depth", "3",
#                 "--output", "json"
#             ])
            
#             return {
#                 "directory_tree": result.get("tree", {}),
#                 "file_types": result.get("file_types", {}),
#                 "total_files": result.get("total_files", 0),
#                 "total_lines": result.get("total_lines", 0)
#             }
            
#         except Exception as e:
#             logger.error(f"Structure extraction failed: {str(e)}")
#             return {}

import os
import subprocess
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ClineService:
    """
    Service for integrating with Cline CLI for code structure extraction
    """
    
    def __init__(self):
        self.cline_path = self._find_cline_cli()
    
    def _find_cline_cli(self) -> Optional[str]:
        """Find Cline CLI executable"""
        try:
            # Try to find cline in PATH
            result = subprocess.run(
                ["which", "cline"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception as e:
            logger.warning(f"Could not find Cline CLI: {str(e)}")
        
        return None
    
    async def extract_structure(self, repo_path: str) -> Dict[str, Any]:
        """
        Extract code structure using Cline CLI
        
        Args:
            repo_path: Path to the repository
            
        Returns:
            Dictionary with code structure data
        """
        try:
            if not self.cline_path:
                logger.warning("Cline CLI not found, using fallback parser")
                return await self._fallback_extract(repo_path)
            
            # Run Cline CLI to extract structure
            logger.info(f"Running Cline CLI on {repo_path}")
            
            result = subprocess.run(
                [self.cline_path, "analyze", repo_path, "--format", "json"],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=repo_path
            )
            
            if result.returncode != 0:
                logger.error(f"Cline CLI failed: {result.stderr}")
                return await self._fallback_extract(repo_path)
            
            # Parse Cline output
            try:
                data = json.loads(result.stdout)
                logger.info("Cline CLI extraction successful")
                return self._normalize_cline_output(data)
            except json.JSONDecodeError:
                logger.error("Failed to parse Cline output")
                return await self._fallback_extract(repo_path)
                
        except subprocess.TimeoutExpired:
            logger.error("Cline CLI timed out")
            return await self._fallback_extract(repo_path)
        except Exception as e:
            logger.error(f"Structure extraction failed: {str(e)}")
            return await self._fallback_extract(repo_path)
    
    async def _fallback_extract(self, repo_path: str) -> Dict[str, Any]:
        """
        Fallback extraction using basic file analysis
        """
        logger.info("Using fallback code extraction")
        
        from app.utils.code_parser import CodeParser
        parser = CodeParser()
        return parser.parse_directory(repo_path)
    
    def _normalize_cline_output(self, cline_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize Cline CLI output to standard format
        """
        return {
            "total_files": cline_data.get("file_count", 0),
            "total_lines": cline_data.get("line_count", 0),
            "language": cline_data.get("primary_language", "Unknown"),
            "framework": cline_data.get("framework", "Unknown"),
            "files": cline_data.get("files", []),
            "dependencies": cline_data.get("dependencies", {}),
            "structure": cline_data.get("structure", {}),
            "metadata": cline_data.get("metadata", {})
        }
    
    async def generate_context(self, repo_path: str, max_tokens: int = 8000) -> str:
        """
        Generate context for AI analysis
        
        Args:
            repo_path: Path to repository
            max_tokens: Maximum tokens for context
            
        Returns:
            Context string for AI models
        """
        try:
            if not self.cline_path:
                return await self._fallback_generate_context(repo_path, max_tokens)
            
            result = subprocess.run(
                [self.cline_path, "context", repo_path, f"--max-tokens={max_tokens}"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=repo_path
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                return await self._fallback_generate_context(repo_path, max_tokens)
                
        except Exception as e:
            logger.error(f"Context generation failed: {str(e)}")
            return await self._fallback_generate_context(repo_path, max_tokens)
    
    async def _fallback_generate_context(self, repo_path: str, max_tokens: int) -> str:
        """
        Fallback context generation
        """
        context_parts = []
        
        # Add README if exists
        readme_path = os.path.join(repo_path, "README.md")
        if os.path.exists(readme_path):
            try:
                with open(readme_path, 'r', encoding='utf-8') as f:
                    context_parts.append(f"README:\n{f.read()[:2000]}")
            except:
                pass
        
        # Add package.json or requirements.txt
        for dep_file in ["package.json", "requirements.txt", "pom.xml", "build.gradle"]:
            dep_path = os.path.join(repo_path, dep_file)
            if os.path.exists(dep_path):
                try:
                    with open(dep_path, 'r', encoding='utf-8') as f:
                        context_parts.append(f"\n{dep_file}:\n{f.read()[:1000]}")
                except:
                    pass
        
        # Add main source files
        for root, dirs, files in os.walk(repo_path):
            # Skip common ignore directories
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', 'venv', '__pycache__']]
            
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.java', '.go')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()[:500]
                            rel_path = os.path.relpath(file_path, repo_path)
                            context_parts.append(f"\n{rel_path}:\n{content}")
                            
                            # Limit total context
                            if len('\n'.join(context_parts)) > max_tokens * 4:  # rough char estimate
                                break
                    except:
                        continue
                
                if len('\n'.join(context_parts)) > max_tokens * 4:
                    break
            
            if len('\n'.join(context_parts)) > max_tokens * 4:
                break
        
        return '\n'.join(context_parts)
