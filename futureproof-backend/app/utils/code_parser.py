# import os
# from typing import List, Dict, Any
# import logging

# logger = logging.getLogger(__name__)

# class CodeParser:
#     """Utility for parsing and analyzing code files"""
    
#     def __init__(self):
#         self.supported_extensions = {
#             '.py': 'python',
#             '.js': 'javascript',
#             '.jsx': 'javascript',
#             '.ts': 'typescript',
#             '.tsx': 'typescript',
#             '.java': 'java',
#             '.go': 'go',
#             '.rb': 'ruby',
#             '.php': 'php',
#             '.cs': 'csharp',
#             '.cpp': 'cpp',
#             '.c': 'c',
#             '.rs': 'rust'
#         }
        
#         self.ignore_patterns = [
#             '__pycache__', 'node_modules', '.git', '.venv', 'venv',
#             'dist', 'build', '.pytest_cache', 'coverage', '.next'
#         ]
    
#     async def parse_directory(self, directory: str, max_files: int = 100) -> List[Dict[str, Any]]:
#         """Parse all code files in directory"""
#         files = []
#         count = 0
        
#         try:
#             for root, dirs, filenames in os.walk(directory):
#                 # Skip ignored directories
#                 dirs[:] = [d for d in dirs if d not in self.ignore_patterns]
                
#                 for filename in filenames:
#                     if count >= max_files:
#                         break
                    
#                     file_path = os.path.join(root, filename)
#                     ext = os.path.splitext(filename)[1]
                    
#                     if ext in self.supported_extensions:
#                         file_data = await self._parse_file(file_path, directory)
#                         if file_data:
#                             files.append(file_data)
#                             count += 1
                
#                 if count >= max_files:
#                     break
            
#             logger.info(f"Parsed {len(files)} files from {directory}")
#             return files
            
#         except Exception as e:
#             logger.error(f"Directory parsing failed: {str(e)}")
#             return []
    
#     async def _parse_file(self, file_path: str, base_path: str) -> Dict[str, Any]:
#         """Parse a single file"""
#         try:
#             with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
#                 content = f.read()
            
#             relative_path = os.path.relpath(file_path, base_path)
#             ext = os.path.splitext(file_path)[1]
#             language = self.supported_extensions.get(ext, 'unknown')
            
#             return {
#                 "path": relative_path,
#                 "full_path": file_path,
#                 "content": content,
#                 "language": language,
#                 "lines": len(content.split('\n')),
#                 "size": len(content)
#             }
            
#         except Exception as e:
#             logger.error(f"Failed to parse {file_path}: {str(e)}")
#             return None
    
#     def detect_tech_stack(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
#         """Detect primary language and framework"""
#         language_counts = {}
#         frameworks = []
        
#         for file_data in files:
#             lang = file_data.get("language", "unknown")
#             language_counts[lang] = language_counts.get(lang, 0) + 1
            
#             # Detect frameworks from file content
#             content = file_data.get("content", "")
#             detected = self._detect_framework(content, lang)
#             if detected:
#                 frameworks.append(detected)
        
#         # Get primary language
#         primary_language = max(language_counts, key=language_counts.get) if language_counts else "unknown"
        
#         # Get primary framework
#         primary_framework = max(set(frameworks), key=frameworks.count) if frameworks else "unknown"
        
#         return {
#             "language": primary_language,
#             "framework": primary_framework,
#             "language_distribution": language_counts
#         }
    
#     def _detect_framework(self, content: str, language: str) -> str:
#         """Detect framework from file content"""
#         framework_patterns = {
#             "python": {
#                 "flask": ["from flask import", "Flask(__name__)"],
#                 "django": ["from django", "django."],
#                 "fastapi": ["from fastapi import", "FastAPI()"]
#             },
#             "javascript": {
#                 "react": ["import React", "from 'react'"],
#                 "vue": ["import Vue", "from 'vue'"],
#                 "express": ["require('express')", "from 'express'"],
#                 "nextjs": ["from 'next", "next/"]
#             }
#         }
        
#         patterns = framework_patterns.get(language, {})
        
#         for framework, pattern_list in patterns.items():
#             if any(pattern in content for pattern in pattern_list):
#                 return framework
        
#         return None
import os
import json
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class CodeParser:
    """
    Fallback code parser for extracting basic code structure
    """
    
    # File extensions to analyze
    CODE_EXTENSIONS = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.ts': 'TypeScript',
        '.jsx': 'React',
        '.tsx': 'React TypeScript',
        '.java': 'Java',
        '.go': 'Go',
        '.rb': 'Ruby',
        '.php': 'PHP',
        '.cs': 'C#',
        '.cpp': 'C++',
        '.c': 'C',
        '.rs': 'Rust',
        '.swift': 'Swift',
        '.kt': 'Kotlin',
        '.scala': 'Scala',
        '.html': 'HTML',
        '.css': 'CSS',
        '.vue': 'Vue',
        '.sol': 'Solidity'
    }
    
    # Directories to ignore
    IGNORE_DIRS = {
        '.git', 'node_modules', 'venv', '__pycache__', 'dist', 'build',
        'target', '.idea', '.vscode', 'coverage', '.pytest_cache',
        'vendor', 'bower_components', '.next', 'out'
    }
    
    def parse_directory(self, directory_path: str) -> Dict[str, Any]:
        """
        Parse a directory and extract code structure
        
        Args:
            directory_path: Path to the directory to analyze
            
        Returns:
            Dictionary with code structure information
        """
        logger.info(f"Parsing directory: {directory_path}")
        
        files_data = []
        total_lines = 0
        language_count = {}
        
        for root, dirs, files in os.walk(directory_path):
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if d not in self.IGNORE_DIRS]
            
            for file in files:
                file_path = os.path.join(root, file)
                ext = os.path.splitext(file)[1].lower()
                
                if ext in self.CODE_EXTENSIONS:
                    try:
                        file_info = self._analyze_file(file_path, directory_path)
                        files_data.append(file_info)
                        total_lines += file_info['lines']
                        
                        language = self.CODE_EXTENSIONS[ext]
                        language_count[language] = language_count.get(language, 0) + 1
                        
                    except Exception as e:
                        logger.warning(f"Failed to analyze {file_path}: {str(e)}")
                        continue
        
        # Determine primary language
        primary_language = max(language_count, key=language_count.get) if language_count else "Unknown"
        
        # Detect framework
        framework = self._detect_framework(directory_path, files_data)
        
        result = {
            "total_files": len(files_data),
            "total_lines": total_lines,
            "language": primary_language,
            "framework": framework,
            "language_distribution": language_count,
            "files": files_data,
            "dependencies": self._extract_dependencies(directory_path)
        }
        
        logger.info(f"Parsed {len(files_data)} files from {directory_path}")
        return result
    
    def _analyze_file(self, file_path: str, base_path: str) -> Dict[str, Any]:
        """Analyze a single file"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')
        
        rel_path = os.path.relpath(file_path, base_path)
        ext = os.path.splitext(file_path)[1].lower()
        
        return {
            "path": rel_path,
            "language": self.CODE_EXTENSIONS.get(ext, "Unknown"),
            "lines": len(lines),
            "size": os.path.getsize(file_path),
            "extension": ext
        }
    
    def _detect_framework(self, directory_path: str, files_data: List[Dict]) -> str:
        """Detect the framework used in the project"""
        
        # Check for common framework files
        framework_indicators = {
            'package.json': ['React', 'Vue', 'Angular', 'Next.js', 'Express'],
            'requirements.txt': ['Django', 'Flask', 'FastAPI'],
            'pom.xml': ['Spring Boot', 'Maven'],
            'build.gradle': ['Spring Boot', 'Gradle'],
            'Gemfile': ['Rails', 'Sinatra'],
            'composer.json': ['Laravel', 'Symfony'],
            'go.mod': ['Go']
        }
        
        for indicator_file, frameworks in framework_indicators.items():
            file_path = os.path.join(directory_path, indicator_file)
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                        
                        for framework in frameworks:
                            if framework.lower() in content:
                                return framework
                except:
                    pass
        
        return "Unknown"
    
    def _extract_dependencies(self, directory_path: str) -> Dict[str, List[str]]:
        """Extract dependencies from common dependency files"""
        dependencies = {}
        
        # Python
        req_file = os.path.join(directory_path, 'requirements.txt')
        if os.path.exists(req_file):
            try:
                with open(req_file, 'r') as f:
                    dependencies['python'] = [
                        line.split('==')[0].strip() 
                        for line in f.readlines() 
                        if line.strip() and not line.startswith('#')
                    ]
            except:
                pass
        
        # Node.js
        pkg_file = os.path.join(directory_path, 'package.json')
        if os.path.exists(pkg_file):
            try:
                with open(pkg_file, 'r') as f:
                    pkg_data = json.load(f)
                    deps = list(pkg_data.get('dependencies', {}).keys())
                    dev_deps = list(pkg_data.get('devDependencies', {}).keys())
                    dependencies['node'] = deps + dev_deps
            except:
                pass
        
        return dependencies
