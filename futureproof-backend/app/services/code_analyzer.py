"""
Code Analyzer Service - Real Implementation
Analyzes code repositories for quality, security, and modernization opportunities
"""
import os
import tempfile
import shutil
from typing import Dict, List, Any, Optional
from pathlib import Path
import asyncio
from git import Repo
import radon.complexity as radon_cc
import radon.metrics as radon_metrics
from radon.raw import analyze
from pygments.lexers import get_lexer_for_filename, guess_lexer
from pygments.util import ClassNotFound
import ast
import json


class CodeAnalyzer:
    """Analyzes code repositories for quality metrics and modernization opportunities"""
    
    def __init__(self):
        self.temp_dir = None
        self.repo_path = None
        
    async def analyze_repository(self, repo_url: str) -> Dict[str, Any]:
        """
        Main entry point for repository analysis
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Clone repository
            self.temp_dir = tempfile.mkdtemp()
            self.repo_path = os.path.join(self.temp_dir, "repo")
            
            print(f"📦 Cloning repository: {repo_url}")
            await asyncio.to_thread(Repo.clone_from, repo_url, self.repo_path, depth=1)
            
            # Analyze code
            results = await self._analyze_codebase()
            
            return results
            
        except Exception as e:
            raise Exception(f"Analysis failed: {str(e)}")
        finally:
            # Cleanup
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
    
    async def _analyze_codebase(self) -> Dict[str, Any]:
        """Analyze the cloned codebase"""
        
        # Collect all code files
        code_files = self._get_code_files()
        
        # Detect language and framework
        detected_language = self._detect_primary_language(code_files)
        detected_framework = self._detect_framework(code_files, detected_language)
        detected_libraries = self._detect_libraries(code_files, detected_language)
        
        # Analyze code quality
        total_lines = 0
        complexity_scores = []
        maintainability_scores = []
        issues = []
        
        for file_path in code_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                # Count lines
                lines = len(content.splitlines())
                total_lines += lines
                
                # Python-specific analysis
                if file_path.endswith('.py'):
                    # Complexity analysis
                    try:
                        cc_results = radon_cc.cc_visit(content)
                        for item in cc_results:
                            complexity_scores.append(item.complexity)
                            if item.complexity > 10:
                                issues.append({
                                    "type": "high_complexity",
                                    "file": os.path.relpath(file_path, self.repo_path),
                                    "function": item.name,
                                    "complexity": item.complexity,
                                    "severity": "high" if item.complexity > 15 else "medium"
                                })
                    except:
                        pass
                    
                    # Maintainability index
                    try:
                        mi_result = radon_metrics.mi_visit(content, multi=True)
                        if mi_result:
                            maintainability_scores.append(mi_result)
                    except:
                        pass
                    
                    # Check for deprecated patterns
                    deprecated_issues = self._check_deprecated_patterns(content, file_path)
                    issues.extend(deprecated_issues)
                    
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")
                continue
        
        # Calculate scores
        security_score = self._calculate_security_score(code_files, issues)
        performance_score = self._calculate_performance_score(complexity_scores)
        architecture_score = self._calculate_architecture_score(code_files)
        code_quality_score = self._calculate_code_quality_score(maintainability_scores, complexity_scores)
        maintainability_score = self._calculate_maintainability_score(maintainability_scores)
        dependency_score = self._calculate_dependency_score(code_files)
        
        overall_score = int((
            security_score * 0.25 +
            performance_score * 0.20 +
            architecture_score * 0.20 +
            code_quality_score * 0.20 +
            maintainability_score * 0.15
        ))
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            security_score, performance_score, architecture_score,
            code_quality_score, issues
        )
        
        return {
            "overall_score": overall_score,
            "security_score": security_score,
            "performance_score": performance_score,
            "architecture_score": architecture_score,
            "dependency_score": dependency_score,
            "maintainability_score": maintainability_score,
            "code_quality_score": code_quality_score,
            "total_files": len(code_files),
            "total_lines": total_lines,
            "detected_language": detected_language,
            "detected_framework": detected_framework,
            "detected_libraries": detected_libraries,
            "analysis_details": {
                "avg_complexity": sum(complexity_scores) / len(complexity_scores) if complexity_scores else 0,
                "high_complexity_functions": len([c for c in complexity_scores if c > 10]),
                "files_analyzed": len(code_files)
            },
            "recommendations": recommendations,
            "issues": issues[:50],  # Limit to 50 issues
            "metrics": {
                "complexity_distribution": self._get_complexity_distribution(complexity_scores),
                "file_size_distribution": self._get_file_size_distribution(code_files)
            }
        }
    
    def _get_code_files(self) -> List[str]:
        """Get all code files from the repository"""
        code_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rs',
            '.cpp', '.c', '.h', '.hpp', '.cs', '.rb', '.php', '.swift',
            '.kt', '.scala', '.r', '.m', '.mm'
        }
        
        code_files = []
        exclude_dirs = {'.git', 'node_modules', 'venv', 'env', '__pycache__', 'dist', 'build', '.next'}
        
        for root, dirs, files in os.walk(self.repo_path):
            # Remove excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if any(file.endswith(ext) for ext in code_extensions):
                    code_files.append(os.path.join(root, file))
        
        return code_files
    
    def _detect_primary_language(self, code_files: List[str]) -> str:
        """Detect the primary programming language"""
        language_counts = {}
        
        for file_path in code_files:
            ext = os.path.splitext(file_path)[1]
            language_map = {
                '.py': 'Python',
                '.js': 'JavaScript',
                '.ts': 'TypeScript',
                '.jsx': 'JavaScript',
                '.tsx': 'TypeScript',
                '.java': 'Java',
                '.go': 'Go',
                '.rs': 'Rust',
                '.cpp': 'C++',
                '.c': 'C',
                '.cs': 'C#',
                '.rb': 'Ruby',
                '.php': 'PHP',
                '.swift': 'Swift',
                '.kt': 'Kotlin'
            }
            
            language = language_map.get(ext, 'Unknown')
            language_counts[language] = language_counts.get(language, 0) + 1
        
        if language_counts:
            return max(language_counts, key=language_counts.get)
        return "Unknown"
    
    def _detect_framework(self, code_files: List[str], language: str) -> Optional[str]:
        """Detect the framework being used"""
        framework_indicators = {
            'Python': {
                'Django': ['django', 'settings.py', 'manage.py'],
                'Flask': ['flask', 'app.py'],
                'FastAPI': ['fastapi', 'main.py'],
            },
            'JavaScript': {
                'React': ['react', 'jsx'],
                'Vue': ['vue'],
                'Angular': ['angular'],
                'Next.js': ['next.config'],
            },
            'TypeScript': {
                'Next.js': ['next.config'],
                'NestJS': ['nest'],
            }
        }
        
        if language in framework_indicators:
            for framework, indicators in framework_indicators[language].items():
                for file_path in code_files:
                    file_content = Path(file_path).read_text(errors='ignore').lower()
                    if any(indicator in file_content for indicator in indicators):
                        return framework
        
        return None
    
    def _detect_libraries(self, code_files: List[str], language: str) -> List[str]:
        """Detect libraries being used"""
        libraries = set()
        
        # Check requirements.txt for Python
        if language == "Python":
            req_file = os.path.join(self.repo_path, "requirements.txt")
            if os.path.exists(req_file):
                with open(req_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            lib = line.split('==')[0].split('>=')[0].split('<=')[0]
                            libraries.add(lib)
        
        # Check package.json for JavaScript/TypeScript
        elif language in ["JavaScript", "TypeScript"]:
            pkg_file = os.path.join(self.repo_path, "package.json")
            if os.path.exists(pkg_file):
                try:
                    with open(pkg_file, 'r') as f:
                        pkg_data = json.load(f)
                        if 'dependencies' in pkg_data:
                            libraries.update(pkg_data['dependencies'].keys())
                except:
                    pass
        
        return list(libraries)[:20]  # Limit to 20 libraries
    
    def _check_deprecated_patterns(self, content: str, file_path: str) -> List[Dict]:
        """Check for deprecated patterns in code"""
        issues = []
        
        # Python 2 print statements
        if 'print ' in content and not 'print(' in content:
            issues.append({
                "type": "deprecated_syntax",
                "file": os.path.relpath(file_path, self.repo_path),
                "description": "Python 2 print statement detected",
                "severity": "medium"
            })
        
        # Old-style string formatting
        if '"%s"' in content or "'%s'" in content:
            issues.append({
                "type": "outdated_pattern",
                "file": os.path.relpath(file_path, self.repo_path),
                "description": "Old-style string formatting (use f-strings)",
                "severity": "low"
            })
        
        return issues
    
    def _calculate_security_score(self, code_files: List[str], issues: List[Dict]) -> int:
        """Calculate security score"""
        base_score = 85
        
        # Deduct for security issues
        security_issues = [i for i in issues if i.get('type') == 'security']
        base_score -= len(security_issues) * 5
        
        # Check for common security files
        has_security_config = any('security' in f.lower() for f in code_files)
        if has_security_config:
            base_score += 5
        
        return max(0, min(100, base_score))
    
    def _calculate_performance_score(self, complexity_scores: List[int]) -> int:
        """Calculate performance score based on complexity"""
        if not complexity_scores:
            return 75
        
        avg_complexity = sum(complexity_scores) / len(complexity_scores)
        
        if avg_complexity < 5:
            return 95
        elif avg_complexity < 10:
            return 80
        elif avg_complexity < 15:
            return 65
        else:
            return 50
    
    def _calculate_architecture_score(self, code_files: List[str]) -> int:
        """Calculate architecture score"""
        base_score = 75
        
        # Check for good structure
        has_tests = any('test' in f.lower() for f in code_files)
        has_docs = any('readme' in f.lower() or 'doc' in f.lower() for f in code_files)
        has_config = any('config' in f.lower() for f in code_files)
        
        if has_tests:
            base_score += 10
        if has_docs:
            base_score += 5
        if has_config:
            base_score += 5
        
        return min(100, base_score)
    
    def _calculate_code_quality_score(self, maintainability_scores: List[float], complexity_scores: List[int]) -> int:
        """Calculate code quality score"""
        if not maintainability_scores:
            return 70
        
        avg_mi = sum(maintainability_scores) / len(maintainability_scores)
        
        # Maintainability Index ranges from 0-100
        # Higher is better
        if avg_mi > 80:
            return 90
        elif avg_mi > 60:
            return 75
        elif avg_mi > 40:
            return 60
        else:
            return 45
    
    def _calculate_maintainability_score(self, maintainability_scores: List[float]) -> int:
        """Calculate maintainability score"""
        if not maintainability_scores:
            return 70
        
        avg_score = sum(maintainability_scores) / len(maintainability_scores)
        return int(min(100, max(0, avg_score)))
    
    def _calculate_dependency_score(self, code_files: List[str]) -> int:
        """Calculate dependency score"""
        # Simple heuristic based on file count
        file_count = len(code_files)
        
        if file_count < 20:
            return 90
        elif file_count < 50:
            return 80
        elif file_count < 100:
            return 70
        else:
            return 60
    
    def _generate_recommendations(self, security_score: int, performance_score: int,
                                 architecture_score: int, code_quality_score: int,
                                 issues: List[Dict]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        if security_score < 70:
            recommendations.append("Update dependencies to patch security vulnerabilities")
            recommendations.append("Implement security best practices (input validation, authentication)")
        
        if performance_score < 70:
            recommendations.append("Reduce code complexity by refactoring complex functions")
            recommendations.append("Implement caching strategies for better performance")
        
        if architecture_score < 70:
            recommendations.append("Add comprehensive test coverage")
            recommendations.append("Improve project documentation")
        
        if code_quality_score < 70:
            recommendations.append("Add type hints and documentation to improve code quality")
            recommendations.append("Refactor code to improve maintainability index")
        
        # Add specific recommendations based on issues
        if any(i.get('type') == 'deprecated_syntax' for i in issues):
            recommendations.append("Migrate from deprecated syntax to modern alternatives")
        
        if any(i.get('type') == 'high_complexity' for i in issues):
            recommendations.append("Break down complex functions into smaller, more manageable pieces")
        
        return recommendations[:10]  # Limit to 10 recommendations
    
    def _get_complexity_distribution(self, complexity_scores: List[int]) -> Dict[str, int]:
        """Get distribution of complexity scores"""
        if not complexity_scores:
            return {"low": 0, "medium": 0, "high": 0}
        
        return {
            "low": len([c for c in complexity_scores if c < 5]),
            "medium": len([c for c in complexity_scores if 5 <= c <= 10]),
            "high": len([c for c in complexity_scores if c > 10])
        }
    
    def _get_file_size_distribution(self, code_files: List[str]) -> Dict[str, int]:
        """Get distribution of file sizes"""
        sizes = []
        for file_path in code_files:
            try:
                size = os.path.getsize(file_path)
                sizes.append(size)
            except:
                pass
        
        if not sizes:
            return {"small": 0, "medium": 0, "large": 0}
        
        return {
            "small": len([s for s in sizes if s < 10000]),  # < 10KB
            "medium": len([s for s in sizes if 10000 <= s <= 50000]),  # 10-50KB
            "large": len([s for s in sizes if s > 50000])  # > 50KB
        }
