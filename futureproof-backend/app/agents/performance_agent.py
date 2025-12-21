# from app.agents.base_agent import BaseAgent
# from typing import Dict, Any, List
# import re

# class PerformanceAgent(BaseAgent):
#     """Agent for performance analysis"""
    
#     def __init__(self):
#         super().__init__("Performance")
#         self.performance_patterns = {
#             "n_plus_one": [
#                 r"for\s+\w+\s+in\s+.*:\s*\n\s*.*\.query\(",
#                 r"forEach\s*\(.*=>\s*.*\.find\("
#             ],
#             "inefficient_loop": [
#                 r"for\s+\w+\s+in\s+range\(len\(",
#                 r"while\s+True:.*break"
#             ],
#             "memory_leak": [
#                 r"global\s+\w+\s*=\s*\[\]",
#                 r"cache\s*=\s*\{\}"
#             ],
#             "blocking_io": [
#                 r"requests\.get\(",
#                 r"open\s*\(.*\)\.read\(\)"
#             ]
#         }
    
#     async def analyze(self, code_data: Dict[str, Any]) -> Dict[str, Any]:
#         """Analyze code for performance issues"""
#         issues = []
#         files = code_data.get("files", [])
        
#         for file_info in files:
#             file_path = file_info.get("path", "")
#             content = file_info.get("content", "")
            
#             # Check for performance issues
#             for issue_type, patterns in self.performance_patterns.items():
#                 for pattern in patterns:
#                     matches = re.finditer(pattern, content, re.IGNORECASE)
#                     for match in matches:
#                         line_num = content[:match.start()].count('\n') + 1
#                         issues.append({
#                             "severity": "medium",
#                             "type": issue_type,
#                             "title": f"Performance Issue: {issue_type.replace('_', ' ').title()}",
#                             "description": f"Potential performance bottleneck at line {line_num}",
#                             "file_path": file_path,
#                             "line_number": line_num,
#                             "code_snippet": match.group(0)[:100],
#                             "suggestion": self._get_suggestion(issue_type)
#                         })
        
#         score = self.calculate_score(issues)
        
#         return {
#             "findings": issues,
#             "score": score,
#             "total_issues": len(issues),
#             "recommendations": self._generate_recommendations(issues)
#         }
    
#     def _get_suggestion(self, issue_type: str) -> str:
#         """Get optimization suggestion"""
#         suggestions = {
#             "n_plus_one": "Use eager loading or batch queries to avoid N+1 queries",
#             "inefficient_loop": "Consider using list comprehensions or built-in functions",
#             "memory_leak": "Implement proper cleanup or use context managers",
#             "blocking_io": "Use async/await or thread pools for I/O operations"
#         }
#         return suggestions.get(issue_type, "Optimize this code section")
    
#     def _generate_recommendations(self, issues: List[Dict[str, Any]]) -> List[str]:
#         """Generate performance recommendations"""
#         recommendations = []
        
#         if any(i["type"] == "n_plus_one" for i in issues):
#             recommendations.append("Implement database query optimization with eager loading")
        
#         if any(i["type"] == "blocking_io" for i in issues):
#             recommendations.append("Convert synchronous I/O to asynchronous operations")
        
#         if len(issues) > 10:
#             recommendations.append("Consider profiling the application to identify major bottlenecks")
        
#         return recommendations

import logging
from typing import Dict, Any, List

logger = logging.getLogger("agent.Performance")


class PerformanceAgent:
    """Agent for analyzing performance issues"""
    
    async def analyze(self, code_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance"""
        logger.info("Performance agent started")
        
        findings = []
        score = 100.0
        
        # Check for large files (potential performance issue)
        large_files = [
            f for f in code_data.get('files', [])
            if f.get('lines', 0) > 500
        ]
        
        if large_files:
            findings.append({
                "severity": "medium",
                "type": "large_files",
                "title": "Large Files Detected",
                "description": f"Found {len(large_files)} files with >500 lines",
                "suggestion": "Consider refactoring large files into smaller modules"
            })
            score -= 10
        
        # Generate recommendations
        recommendations = [
            {
                "category": "performance",
                "recommendation": "Implement caching strategy (Redis/Memcached)",
                "priority": "high"
            },
            {
                "category": "performance",
                "recommendation": "Add database query optimization and indexing",
                "priority": "high"
            },
            {
                "category": "performance",
                "recommendation": "Use async/await for I/O operations",
                "priority": "medium"
            }
        ]
        
        logger.info(f"Performance completed in 0.00s")
        
        return {
            "score": max(0, score),
            "findings": findings,
            "recommendations": recommendations
        }
