# from app.agents.base_agent import BaseAgent
# from typing import Dict, Any, List
# import re

# class SecurityAgent(BaseAgent):
#     """Agent for security vulnerability analysis"""
    
#     def __init__(self):
#         super().__init__("Security")
#         self.vulnerability_patterns = {
#             "sql_injection": [
#                 r"execute\s*\(\s*['\"].*%s.*['\"]",
#                 r"cursor\.execute\s*\(\s*f['\"]",
#                 r"query\s*=.*\+.*input"
#             ],
#             "xss": [
#                 r"innerHTML\s*=",
#                 r"document\.write\s*\(",
#                 r"eval\s*\("
#             ],
#             "hardcoded_secrets": [
#                 r"password\s*=\s*['\"][^'\"]{8,}['\"]",
#                 r"api_key\s*=\s*['\"][^'\"]+['\"]",
#                 r"secret\s*=\s*['\"][^'\"]+['\"]"
#             ],
#             "insecure_crypto": [
#                 r"md5\(",
#                 r"sha1\(",
#                 r"DES\."
#             ]
#         }
    
#     async def analyze(self, code_data: Dict[str, Any]) -> Dict[str, Any]:
#         """Analyze code for security vulnerabilities"""
#         issues = []
#         files = code_data.get("files", [])
        
#         for file_info in files:
#             file_path = file_info.get("path", "")
#             content = file_info.get("content", "")
            
#             # Check for vulnerabilities
#             for vuln_type, patterns in self.vulnerability_patterns.items():
#                 for pattern in patterns:
#                     matches = re.finditer(pattern, content, re.IGNORECASE)
#                     for match in matches:
#                         line_num = content[:match.start()].count('\n') + 1
#                         issues.append({
#                             "severity": self._get_severity(vuln_type),
#                             "type": vuln_type,
#                             "title": f"Potential {vuln_type.replace('_', ' ').title()}",
#                             "description": f"Found potential security issue at line {line_num}",
#                             "file_path": file_path,
#                             "line_number": line_num,
#                             "code_snippet": match.group(0),
#                             "suggestion": self._get_suggestion(vuln_type)
#                         })
        
#         score = self.calculate_score(issues)
        
#         return {
#             "findings": issues,
#             "score": score,
#             "total_issues": len(issues),
#             "critical_issues": len([i for i in issues if i["severity"] == "critical"]),
#             "recommendations": self._generate_recommendations(issues)
#         }
    
#     def _get_severity(self, vuln_type: str) -> str:
#         """Get severity level for vulnerability type"""
#         severity_map = {
#             "sql_injection": "critical",
#             "xss": "high",
#             "hardcoded_secrets": "critical",
#             "insecure_crypto": "high"
#         }
#         return severity_map.get(vuln_type, "medium")
    
#     def _get_suggestion(self, vuln_type: str) -> str:
#         """Get fix suggestion for vulnerability"""
#         suggestions = {
#             "sql_injection": "Use parameterized queries or ORM to prevent SQL injection",
#             "xss": "Sanitize user input and use textContent instead of innerHTML",
#             "hardcoded_secrets": "Move secrets to environment variables or secret management system",
#             "insecure_crypto": "Use modern cryptographic algorithms like SHA-256 or bcrypt"
#         }
#         return suggestions.get(vuln_type, "Review and fix this security issue")
    
#     def _generate_recommendations(self, issues: List[Dict[str, Any]]) -> List[str]:
#         """Generate overall security recommendations"""
#         recommendations = []
        
#         if any(i["type"] == "sql_injection" for i in issues):
#             recommendations.append("Implement input validation and parameterized queries")
        
#         if any(i["type"] == "hardcoded_secrets" for i in issues):
#             recommendations.append("Use environment variables or AWS Secrets Manager for sensitive data")
        
#         if any(i["severity"] == "critical" for i in issues):
#             recommendations.append("Address critical security vulnerabilities immediately before deployment")
        
#         return recommendations
import logging
from typing import Dict, Any, List

logger = logging.getLogger("agent.Security")


class SecurityAgent:
    """Agent for analyzing security vulnerabilities"""
    
    async def analyze(self, code_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze security issues in code"""
        logger.info("Security agent started")
        
        findings = []
        score = 100.0
        
        # Check for common security files
        has_security_config = any(
            'security' in f.get('path', '').lower() or 
            'auth' in f.get('path', '').lower()
            for f in code_data.get('files', [])
        )
        
        # Check for sensitive file exposure
        sensitive_files = ['.env', 'secrets.json', 'credentials.json']
        exposed_files = [
            f.get('path') for f in code_data.get('files', [])
            if any(sf in f.get('path', '') for sf in sensitive_files)
        ]
        
        if exposed_files:
            findings.append({
                "severity": "critical",
                "type": "exposed_secrets",
                "title": "Potential Secret Files in Repository",
                "description": f"Found sensitive files: {', '.join(exposed_files)}",
                "suggestion": "Add these files to .gitignore and use environment variables"
            })
            score -= 30
        
        # Generate recommendations
        recommendations = [
            {
                "category": "security",
                "recommendation": "Implement rate limiting on API endpoints",
                "priority": "high"
            },
            {
                "category": "security",
                "recommendation": "Add input validation and sanitization",
                "priority": "high"
            },
            {
                "category": "security",
                "recommendation": "Enable HTTPS and secure headers (HSTS, CSP)",
                "priority": "high"
            }
        ]
        
        logger.info(f"Security completed in 0.00s")
        
        return {
            "score": max(0, score),
            "findings": findings,
            "recommendations": recommendations
        }
