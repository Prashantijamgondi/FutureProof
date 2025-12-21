"""
Language Detection Service
Detects programming languages, ML/DL frameworks, and project types
Supports: Python, Java, C++, C#, Go, Rust, PHP, Ruby, JS/TS, React, HTML, CSS
"""

import os
import json
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class LanguageDetector:
    """
    Advanced multi-language detection and classification
    """
    
    # Complete language mapping
    LANGUAGE_EXTENSIONS = {
        # ML/DL Languages
        '.py': 'Python',
        '.ipynb': 'Jupyter Notebook',
        
        # Backend Languages
        '.java': 'Java',
        '.cpp': 'C++',
        '.cc': 'C++',
        '.cxx': 'C++',
        '.c': 'C',
        '.cs': 'C#',
        '.go': 'Go',
        '.rs': 'Rust',
        '.php': 'PHP',
        '.rb': 'Ruby',
        
        # Frontend Languages
        '.js': 'JavaScript',
        '.jsx': 'React',
        '.ts': 'TypeScript',
        '.tsx': 'React TypeScript',
        '.html': 'HTML',
        '.htm': 'HTML',
        '.css': 'CSS',
        '.scss': 'SCSS',
        '.sass': 'Sass',
        '.vue': 'Vue',
        
        # Other
        '.swift': 'Swift',
        '.kt': 'Kotlin',
        '.scala': 'Scala',
        '.r': 'R',
        '.m': 'MATLAB',
        '.jl': 'Julia'
    }
    
    # ML/DL Framework indicators
    ML_FRAMEWORKS = {
        'tensorflow': {'files': ['tensorflow', 'keras'], 'type': 'deep_learning'},
        'pytorch': {'files': ['torch', 'pytorch'], 'type': 'deep_learning'},
        'keras': {'files': ['keras'], 'type': 'deep_learning'},
        'scikit-learn': {'files': ['sklearn'], 'type': 'machine_learning'},
        'xgboost': {'files': ['xgboost'], 'type': 'machine_learning'},
        'lightgbm': {'files': ['lightgbm'], 'type': 'machine_learning'},
        'fastai': {'files': ['fastai'], 'type': 'deep_learning'},
        'jax': {'files': ['jax'], 'type': 'deep_learning'},
        'mxnet': {'files': ['mxnet'], 'type': 'deep_learning'},
        'huggingface': {'files': ['transformers', 'datasets'], 'type': 'nlp'}
    }
    
    def detect_project_languages(self, repo_path: str) -> Dict[str, Any]:
        """
        Comprehensive language detection
        Returns primary language, all languages, ML frameworks
        """
        logger.info(f"Detecting languages in {repo_path}")
        
        language_stats = {}
        ml_frameworks = []
        file_count = 0
        
        # Scan directory
        for root, dirs, files in os.walk(repo_path):
            # Skip common ignore directories
            dirs[:] = [d for d in dirs if d not in [
                '.git', 'node_modules', 'venv', '__pycache__', 
                'dist', 'build', 'target', '.vscode', '.idea',
                'vendor', 'bower_components', '.next', 'out'
            ]]
            
            for filename in files:
                file_path = os.path.join(root, filename)
                ext = Path(filename).suffix.lower()
                
                if ext in self.LANGUAGE_EXTENSIONS:
                    lang = self.LANGUAGE_EXTENSIONS[ext]
                    language_stats[lang] = language_stats.get(lang, 0) + 1
                    file_count += 1
                    
                    # Check for ML frameworks in Python files
                    if ext == '.py':
                        frameworks = self._detect_ml_frameworks(file_path)
                        ml_frameworks.extend(frameworks)
        
        # Determine primary language
        primary_language = max(language_stats, key=language_stats.get) if language_stats else "Unknown"
        
        # Detect project type
        project_type = self._detect_project_type(repo_path, primary_language, ml_frameworks)
        
        # Get framework details
        framework_details = self._get_framework_details(repo_path)
        
        result = {
            "primary_language": primary_language,
            "all_languages": language_stats,
            "total_files": file_count,
            "project_type": project_type,
            "ml_frameworks": list(set(ml_frameworks)),
            "is_ml_project": len(ml_frameworks) > 0,
            "framework_details": framework_details
        }
        
        logger.info(f"Detected: {primary_language}, ML frameworks: {len(ml_frameworks)}, Type: {project_type}")
        return result
    
    def _detect_ml_frameworks(self, file_path: str) -> List[str]:
        """Detect ML/DL frameworks in Python file"""
        frameworks = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().lower()
                
                for framework, config in self.ML_FRAMEWORKS.items():
                    for indicator in config['files']:
                        if f"import {indicator}" in content or f"from {indicator}" in content:
                            frameworks.append(framework)
                            break
        except Exception as e:
            logger.debug(f"Could not read {file_path}: {str(e)}")
        
        return frameworks
    
    def _detect_project_type(
        self, 
        repo_path: str, 
        primary_language: str,
        ml_frameworks: List[str]
    ) -> str:
        """Detect overall project type"""
        
        # ML/DL Project - HIGHEST PRIORITY
        if ml_frameworks:
            if any('deep_learning' in self.ML_FRAMEWORKS.get(fw, {}).get('type', '') for fw in ml_frameworks):
                return "deep_learning"
            return "machine_learning"
        
        # Web Frontend
        if primary_language in ['JavaScript', 'TypeScript', 'React', 'React TypeScript', 'HTML']:
            return "web_frontend"
        
        # Web Backend
        if primary_language in ['Python', 'Java', 'Go', 'Ruby', 'PHP', 'C#']:
            if self._has_file(repo_path, ['app.py', 'manage.py', 'main.py', 'server.py']):
                return "web_backend"
        
        # Mobile
        if primary_language in ['Swift', 'Kotlin']:
            return "mobile"
        
        # Systems Programming
        if primary_language in ['C', 'C++', 'Rust']:
            return "systems"
        
        return "general"
    
    def _get_framework_details(self, repo_path: str) -> Dict[str, str]:
        """Detect specific frameworks"""
        frameworks = {}
        
        # Python frameworks
        if self._has_file(repo_path, ['requirements.txt']):
            req_content = self._read_file(repo_path, 'requirements.txt')
            if req_content:
                content_lower = req_content.lower()
                if 'fastapi' in content_lower:
                    frameworks['web'] = 'FastAPI'
                elif 'flask' in content_lower:
                    frameworks['web'] = 'Flask'
                elif 'django' in content_lower:
                    frameworks['web'] = 'Django'
        
        # Check pyproject.toml
        if self._has_file(repo_path, ['pyproject.toml']):
            pyproject = self._read_file(repo_path, 'pyproject.toml')
            if pyproject:
                if 'fastapi' in pyproject.lower():
                    frameworks['web'] = 'FastAPI'
        
        # Node.js frameworks
        pkg_json = self._read_json(repo_path, 'package.json')
        if pkg_json:
            deps = {**pkg_json.get('dependencies', {}), **pkg_json.get('devDependencies', {})}
            if 'next' in deps:
                frameworks['web'] = 'Next.js'
            elif 'react' in deps:
                frameworks['web'] = 'React'
            elif 'vue' in deps:
                frameworks['web'] = 'Vue'
            elif 'express' in deps:
                frameworks['web'] = 'Express'
        
        # Java frameworks
        if self._has_file(repo_path, ['pom.xml']):
            pom = self._read_file(repo_path, 'pom.xml')
            if pom and 'spring-boot' in pom.lower():
                frameworks['web'] = 'Spring Boot'
        
        # Go frameworks
        if self._has_file(repo_path, ['go.mod']):
            gomod = self._read_file(repo_path, 'go.mod')
            if gomod:
                if 'gin-gonic' in gomod.lower():
                    frameworks['web'] = 'Gin'
                elif 'fiber' in gomod.lower():
                    frameworks['web'] = 'Fiber'
        
        # Ruby frameworks
        if self._has_file(repo_path, ['Gemfile']):
            gemfile = self._read_file(repo_path, 'Gemfile')
            if gemfile and 'rails' in gemfile.lower():
                frameworks['web'] = 'Rails'
        
        # PHP frameworks
        if self._has_file(repo_path, ['composer.json']):
            composer = self._read_json(repo_path, 'composer.json')
            if composer:
                deps = {**composer.get('require', {}), **composer.get('require-dev', {})}
                if any('laravel' in dep.lower() for dep in deps.keys()):
                    frameworks['web'] = 'Laravel'
                elif any('symfony' in dep.lower() for dep in deps.keys()):
                    frameworks['web'] = 'Symfony'
        
        return frameworks
    
    def _has_file(self, repo_path: str, filenames: List[str]) -> bool:
        """Check if any of the files exist"""
        return any(os.path.exists(os.path.join(repo_path, f)) for f in filenames)
    
    def _read_file(self, repo_path: str, filename: str) -> Optional[str]:
        """Read file content safely"""
        try:
            with open(os.path.join(repo_path, filename), 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return None
    
    def _read_json(self, repo_path: str, filename: str) -> Optional[Dict]:
        """Read JSON file safely"""
        try:
            with open(os.path.join(repo_path, filename), 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
