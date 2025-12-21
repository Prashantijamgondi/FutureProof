# from app.agents.base_agent import BaseAgent
# from typing import Dict, Any, List

# class ArchitectureAgent(BaseAgent):
#     """Agent for architecture analysis"""
    
#     def __init__(self):
#         super().__init__("Architecture")
    
#     async def analyze(self, code_data: Dict[str, Any]) -> Dict[str, Any]:
#         """Analyze code architecture"""
#         issues = []
#         files = code_data.get("files", [])
        
#         # Analyze file structure
#         structure_issues = self._analyze_structure(files)
#         issues.extend(structure_issues)
        
#         # Analyze patterns
#         pattern_issues = self._analyze_patterns(files)
#         issues.extend(pattern_issues)
        
#         score = self.calculate_score(issues)
        
#         return {
#             "findings": issues,
#             "score": score,
#             "total_issues": len(issues),
#             "recommendations": self._generate_recommendations(files, issues)
#         }
    
#     def _analyze_structure(self, files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#         """Analyze project structure"""
#         issues = []
#         file_paths = [f.get("path", "") for f in files]
        
#         # Check for missing standard directories
#         has_tests = any("test" in path.lower() for path in file_paths)
#         if not has_tests:
#             issues.append({
#                 "severity": "high",
#                 "type": "missing_tests",
#                 "title": "No Test Directory Found",
#                 "description": "Project lacks a dedicated test directory",
#                 "suggestion": "Create a tests/ directory and add unit tests"
#             })
        
#         # Check for config management
#         has_config = any("config" in path.lower() or ".env" in path for path in file_paths)
#         if not has_config:
#             issues.append({
#                 "severity": "medium",
#                 "type": "missing_config",
#                 "title": "No Configuration Management",
#                 "description": "No centralized configuration found",
#                 "suggestion": "Create a config file or use environment variables"
#             })
        
#         return issues
    
#     def _analyze_patterns(self, files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#         """Analyze code patterns"""
#         issues = []
        
#         # Check for large files
#         for file_info in files:
#             content = file_info.get("content", "")
#             lines = len(content.split('\n'))
            
#             if lines > 500:
#                 issues.append({
#                     "severity": "medium",
#                     "type": "large_file",
#                     "title": "Large File Detected",
#                     "description": f"File has {lines} lines (>500)",
#                     "file_path": file_info.get("path", ""),
#                     "suggestion": "Consider splitting into smaller modules"
#                 })
        
#         return issues
    
#     def _generate_recommendations(self, files: List[Dict[str, Any]], issues: List[Dict[str, Any]]) -> List[str]:
#         """Generate architecture recommendations"""
#         recommendations = []
        
#         recommendations.append("Consider adopting a microservices architecture for better scalability")
#         recommendations.append("Implement API versioning for backward compatibility")
#         recommendations.append("Add health check endpoints for monitoring")
        
#         if any(i["type"] == "missing_tests" for i in issues):
#             recommendations.append("Implement comprehensive test coverage (aim for >80%)")
        
#         return recommendations

import logging
from typing import Dict, Any, List

logger = logging.getLogger("agent.Architecture")


class ArchitectureAgent:
    """Agent for analyzing code architecture and design patterns"""
    
    async def analyze(self, code_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code architecture"""
        logger.info("Architecture agent started")
        
        findings = []
        score = 100.0
        
        # Check for tests directory
        has_tests = any('test' in f.get('path', '').lower() for f in code_data.get('files', []))
        if not has_tests:
            findings.append({
                "severity": "high",
                "type": "missing_tests",
                "title": "No Test Directory Found",
                "description": "Project lacks a dedicated test directory",
                "suggestion": "Create a tests/ directory and add unit tests"
            })
            score -= 15
        
        # Check for configuration management
        config_files = ['config.py', 'config.json', '.env.example', 'settings.py']
        has_config = any(
            any(cf in f.get('path', '') for cf in config_files) 
            for f in code_data.get('files', [])
        )
        
        if not has_config:
            findings.append({
                "severity": "medium",
                "type": "missing_config",
                "title": "No Configuration Management",
                "description": "No centralized configuration found",
                "suggestion": "Create a config file or use environment variables"
            })
            score -= 10
        
        # Generate recommendations - PROPER DICT FORMAT
        recommendations = [
            {
                "category": "architecture",
                "recommendation": "Consider adopting a microservices architecture for better scalability",
                "priority": "medium"
            },
            {
                "category": "architecture",
                "recommendation": "Implement API versioning for backward compatibility",
                "priority": "medium"
            },
            {
                "category": "architecture",
                "recommendation": "Add health check endpoints for monitoring",
                "priority": "medium"
            },
            {
                "category": "architecture",
                "recommendation": "Implement comprehensive test coverage (aim for >80%)",
                "priority": "medium"
            }
        ]
        
        logger.info(f"Architecture completed in 0.00s")
        
        return {
            "score": max(0, score),
            "findings": findings,
            "recommendations": recommendations
        }
