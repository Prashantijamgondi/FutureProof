import pytest
from app.agents.security_agent import SecurityAgent

@pytest.mark.asyncio
async def test_security_agent_initialization():
    """Test security agent initialization"""
    agent = SecurityAgent()
    assert agent.name == "Security"

@pytest.mark.asyncio
async def test_security_agent_analysis(sample_code_data):
    """Test security agent analysis"""
    agent = SecurityAgent()
    result = await agent.run(sample_code_data)
    
    assert result["status"] == "completed"
    assert "findings" in result
    assert "score" in result
    assert len(result["findings"]) > 0  # Should find hardcoded password

@pytest.mark.asyncio
async def test_security_agent_detect_sql_injection(sample_code_data):
    """Test SQL injection detection"""
    agent = SecurityAgent()
    result = await agent.analyze(sample_code_data)
    
    findings = result["findings"]
    sql_injection_found = any(f["type"] == "sql_injection" for f in findings)
    
    assert sql_injection_found

@pytest.mark.asyncio
async def test_security_agent_detect_hardcoded_secrets(sample_code_data):
    """Test hardcoded secrets detection"""
    agent = SecurityAgent()
    result = await agent.analyze(sample_code_data)
    
    findings = result["findings"]
    hardcoded_found = any(f["type"] == "hardcoded_secrets" for f in findings)
    
    assert hardcoded_found
