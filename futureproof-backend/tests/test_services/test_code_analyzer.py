"""
Test for CodeAnalyzer service
"""
import pytest
from app.services.code_analyzer import CodeAnalyzer


@pytest.mark.asyncio
async def test_code_analyzer_initialization():
    """Test that CodeAnalyzer can be initialized"""
    analyzer = CodeAnalyzer()
    assert analyzer is not None
    assert analyzer.temp_dir is None
    assert analyzer.repo_path is None


@pytest.mark.asyncio
async def test_language_detection():
    """Test language detection from file extensions"""
    analyzer = CodeAnalyzer()
    
    # Test Python detection
    files = ['/path/to/file1.py', '/path/to/file2.py', '/path/to/file3.js']
    language = analyzer._detect_primary_language(files)
    assert language == 'Python'
    
    # Test JavaScript detection
    files = ['/path/to/file1.js', '/path/to/file2.js', '/path/to/file3.py']
    language = analyzer._detect_primary_language(files)
    assert language == 'JavaScript'


@pytest.mark.asyncio
async def test_complexity_distribution():
    """Test complexity distribution calculation"""
    analyzer = CodeAnalyzer()
    
    complexity_scores = [2, 5, 8, 12, 15]
    distribution = analyzer._get_complexity_distribution(complexity_scores)
    
    assert distribution['low'] == 1  # 2
    assert distribution['medium'] == 2  # 5, 8
    assert distribution['high'] == 2  # 12, 15


@pytest.mark.asyncio
async def test_security_score_calculation():
    """Test security score calculation"""
    analyzer = CodeAnalyzer()
    
    code_files = ['/path/to/security_config.py', '/path/to/app.py']
    issues = []
    
    score = analyzer._calculate_security_score(code_files, issues)
    assert 0 <= score <= 100
    assert score >= 85  # Should have good base score with security config


@pytest.mark.asyncio
async def test_performance_score_calculation():
    """Test performance score calculation"""
    analyzer = CodeAnalyzer()
    
    # Low complexity should give high score
    low_complexity = [2, 3, 4]
    score = analyzer._calculate_performance_score(low_complexity)
    assert score >= 90
    
    # High complexity should give lower score
    high_complexity = [15, 20, 25]
    score = analyzer._calculate_performance_score(high_complexity)
    assert score <= 65
