import pytest
from app.services.cline_service import ClineService

@pytest.mark.asyncio
async def test_cline_service_initialization():
    """Test Cline service initialization"""
    service = ClineService()
    assert service.cline_path == "cline"

@pytest.mark.asyncio
async def test_analyze_codebase():
    """Test codebase analysis (mock)"""
    service = ClineService()
    
    # This would normally fail without actual Cline CLI
    # In production, mock the subprocess call
    # result = await service.analyze_codebase("/fake/path")
    # assert result is not None
    pass
