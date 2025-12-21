# from app.agents.base_agent import BaseAgent
# from typing import Dict, Any, List
# import re

# class DependencyAgent(BaseAgent):
#     """Agent for dependency analysis"""
    
#     def __init__(self):
#         super().__init__("Dependency")
#         self.outdated_packages = {
#             "flask": "2.0.0",
#             "django": "3.0.0",
#             "react": "16.0.0",
#             "express": "4.0.0",
#             "jquery": "3.0.0"
#         }
    
#     async def analyze(self, code_data: Dict[str, Any]) -> Dict[str, Any]:
#         """Analyze project dependencies"""
#         issues = []
#         files = code_data.get("files", [])
        
#         # Find dependency files
#         for file_info in files:
#             file_path = file_info.get("path", "")
#             content = file_info.get("content", "")
            
#             if "package.json" in file_path or "requirements.txt" in file_path:
#                 dep_issues = self._analyze_dependencies(content, file_path)
#                 issues.extend(dep_issues)
        
#         score = self.calculate_score(issues)
        
#         return {
#             "findings": issues,
#             "score": score,
#             "total_issues": len(issues),
#             "outdated_count": len([i for i in issues if i["type"] == "outdated"]),
#             "recommendations": self._generate_recommendations(issues)
#         }
    
#     def _analyze_dependencies(self, content: str, file_path: str) -> List[Dict[str, Any]]:
#         """Check for outdated dependencies"""
#         issues = []
        
#         for package, min_version in self.outdated_packages.items():
#             pattern = rf"{package}[=<>~]*\s*(\d+\.\d+\.\d+)"
#             match = re.search(pattern, content, re.IGNORECASE)
            
#             if match:
#                 version = match.group(1)
#                 if self._is_outdated(version, min_version):
#                     issues.append({
#                         "severity": "medium",
#                         "type": "outdated",
#                         "title": f"Outdated Package: {package}",
#                         "description": f"{package} version {version} is outdated (minimum recommended: {min_version})",
#                         "file_path": file_path,
#                         "suggestion": f"Update {package} to latest stable version"
#                     })
        
#         return issues
    
#     def _is_outdated(self, current: str, minimum: str) -> bool:
#         """Compare version numbers"""
#         try:
#             current_parts = [int(x) for x in current.split('.')]
#             minimum_parts = [int(x) for x in minimum.split('.')]
#             return current_parts < minimum_parts
#         except:
#             return False
    
#     def _generate_recommendations(self, issues: List[Dict[str, Any]]) -> List[str]:
#         """Generate dependency recommendations"""
#         recommendations = []
        
#         if issues:
#             recommendations.append("Update outdated dependencies to latest stable versions")
#             recommendations.append("Implement automated dependency scanning in CI/CD")
#             recommendations.append("Use dependency lock files (package-lock.json, poetry.lock)")
        
#         return recommendations

import logging
from typing import Dict, Any, List

logger = logging.getLogger("agent.Dependency")


class DependencyAgent:
    """Agent for analyzing dependencies and packages"""
    
    async def analyze(self, code_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze dependencies"""
        logger.info("Dependency agent started")
        
        findings = []
        score = 100.0
        
        dependencies = code_data.get('dependencies', {})
        
        # Check if dependencies exist
        if not dependencies:
            findings.append({
                "severity": "low",
                "type": "no_dependencies",
                "title": "No Dependency File Found",
                "description": "Could not find package dependencies",
                "suggestion": "Ensure requirements.txt or package.json exists"
            })
            score -= 5
        
        # Generate recommendations
        recommendations = [
            {
                "category": "dependency",
                "recommendation": "Regularly update dependencies to latest stable versions",
                "priority": "high"
            },
            {
                "category": "dependency",
                "recommendation": "Use dependency scanning tools (Dependabot, Snyk)",
                "priority": "high"
            },
            {
                "category": "dependency",
                "recommendation": "Pin dependency versions for reproducible builds",
                "priority": "medium"
            }
        ]
        
        logger.info(f"Dependency completed in 0.00s")
        
        return {
            "score": max(0, score),
            "findings": findings,
            "recommendations": recommendations
        }
