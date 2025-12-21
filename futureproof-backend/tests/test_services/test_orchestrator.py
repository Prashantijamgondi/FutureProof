import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from sqlalchemy.orm import Session
from app.services.orchestrator import OrchestratorService
from app.models.project import Project, ProjectStatus
from app.models.analysis import Analysis
from app.models.agent_task import AgentTask, AgentType, TaskStatus
from datetime import datetime

@pytest.fixture
def mock_db():
    """Mock database session"""
    db = Mock(spec=Session)
    db.query = Mock()
    db.add = Mock()
    db.commit = Mock()
    db.refresh = Mock()
    return db

@pytest.fixture
def mock_project(mock_db):
    """Create a mock project"""
    project = Project(
        id=1,
        name="Test Project",
        repo_url="https://github.com/test/repo",
        status=ProjectStatus.PENDING,
        total_files=0,
        total_lines=0,
        created_at=datetime.utcnow()
    )
    
    # Mock query chain
    mock_db.query.return_value.filter.return_value.first.return_value = project
    
    return project

@pytest.fixture
def orchestrator(mock_db):
    """Create orchestrator instance with mocked dependencies"""
    with patch('app.services.orchestrator.ClineService'), \
         patch('app.services.orchestrator.KestraService'), \
         patch('app.services.orchestrator.GroqService'), \
         patch('app.services.orchestrator.GitHubService'), \
         patch('app.services.orchestrator.CodeRabbitService'), \
         patch('app.services.orchestrator.OumiService'):
        
        orchestrator = OrchestratorService(mock_db)
        return orchestrator

@pytest.mark.asyncio
async def test_orchestrator_initialization(orchestrator):
    """Test orchestrator initializes with all services"""
    assert orchestrator.cline is not None
    assert orchestrator.kestra is not None
    assert orchestrator.groq is not None
    assert orchestrator.github is not None
    assert orchestrator.coderabbit is not None
    assert orchestrator.oumi is not None
    assert len(orchestrator.agents) == 4

@pytest.mark.asyncio
async def test_prepare_repository_success(orchestrator, mock_project):
    """Test successful repository preparation"""
    orchestrator.github.clone_repository = AsyncMock(return_value=True)
    
    with patch('tempfile.mkdtemp', return_value='/tmp/test_repo'):
        repo_path = await orchestrator._prepare_repository(mock_project)
        
        assert repo_path == '/tmp/test_repo/repo'
        assert mock_project.repo_path == '/tmp/test_repo/repo'
        orchestrator.db.commit.assert_called()

@pytest.mark.asyncio
async def test_prepare_repository_failure(orchestrator, mock_project):
    """Test repository preparation failure"""
    orchestrator.github.clone_repository = AsyncMock(return_value=False)
    
    with patch('tempfile.mkdtemp', return_value='/tmp/test_repo'), \
         pytest.raises(Exception, match="Failed to clone repository"):
        await orchestrator._prepare_repository(mock_project)

@pytest.mark.asyncio
async def test_extract_code_data(orchestrator, mock_project):
    """Test code data extraction"""
    mock_structure = {
        "total_files": 10,
        "total_lines": 1000,
        "file_types": {"py": 5, "js": 5}
    }
    
    mock_files = [
        {"path": "test.py", "content": "print('test')", "language": "python"}
    ]
    
    orchestrator.cline.extract_code_structure = AsyncMock(return_value=mock_structure)
    
    with patch('app.services.orchestrator.CodeParser') as MockParser:
        mock_parser_instance = MockParser.return_value
        mock_parser_instance.parse_directory = AsyncMock(return_value=mock_files)
        mock_parser_instance.detect_tech_stack.return_value = {
            "language": "python",
            "framework": "flask"
        }
        
        code_data = await orchestrator._extract_code_data(mock_project, "/tmp/repo")
        
        assert code_data["total_files"] == 10
        assert code_data["total_lines"] == 1000
        assert code_data["language"] == "python"
        assert code_data["framework"] == "flask"
        assert len(code_data["files"]) == 1

@pytest.mark.asyncio
async def test_run_multi_agent_analysis(orchestrator, mock_project):
    """Test multi-agent analysis execution"""
    mock_code_data = {
        "files": [],
        "total_files": 10,
        "language": "python"
    }
    
    # Mock agent results
    for agent_type, agent in orchestrator.agents.items():
        agent.run = AsyncMock(return_value={
            "status": "completed",
            "agent_type": agent_type,
            "findings": [],
            "score": 85.0,
            "recommendations": []
        })
    
    # Mock database operations
    orchestrator.db.query.return_value.filter.return_value.all.return_value = []
    
    results = await orchestrator._run_multi_agent_analysis(mock_project, mock_code_data)
    
    assert len(results) == 4
    assert all(r["status"] == "completed" for r in results)

@pytest.mark.asyncio
async def test_run_single_agent_success(orchestrator, mock_project):
    """Test single agent execution success"""
    mock_agent = AsyncMock()
    mock_agent.run = AsyncMock(return_value={
        "status": "completed",
        "findings": [{"issue": "test"}],
        "score": 90.0
    })
    
    mock_task = AgentTask(
        id=1,
        project_id=mock_project.id,
        agent_type=AgentType.SECURITY,
        status=TaskStatus.PENDING
    )
    
    result = await orchestrator._run_single_agent(
        AgentType.SECURITY,
        mock_agent,
        {"files": []},
        [mock_task]
    )
    
    assert result["status"] == "completed"
    assert result["score"] == 90.0
    assert mock_task.status == TaskStatus.COMPLETED
    orchestrator.db.commit.assert_called()

@pytest.mark.asyncio
async def test_run_single_agent_failure(orchestrator, mock_project):
    """Test single agent execution failure"""
    mock_agent = AsyncMock()
    mock_agent.run = AsyncMock(side_effect=Exception("Agent failed"))
    
    mock_task = AgentTask(
        id=1,
        project_id=mock_project.id,
        agent_type=AgentType.SECURITY,
        status=TaskStatus.PENDING
    )
    
    with pytest.raises(Exception):
        await orchestrator._run_single_agent(
            AgentType.SECURITY,
            mock_agent,
            {"files": []},
            [mock_task]
        )
    
    assert mock_task.status == TaskStatus.FAILED
    assert mock_task.error_message == "Agent failed"

@pytest.mark.asyncio
async def test_make_decision(orchestrator, mock_project):
    """Test AI decision making"""
    mock_agent_results = [
        {"agent_type": "security", "score": 70.0},
        {"agent_type": "performance", "score": 80.0},
        {"agent_type": "architecture", "score": 75.0},
        {"agent_type": "dependency", "score": 85.0}
    ]
    
    orchestrator.groq.make_decision = AsyncMock(return_value={
        "decision": "NEEDS_WORK",
        "reasoning": "Some issues found",
        "confidence": 0.85
    })
    
    decision = await orchestrator._make_decision(mock_project, mock_agent_results)
    
    assert decision["decision"] == "NEEDS_WORK"
    assert decision["confidence"] == 0.85

@pytest.mark.asyncio
async def test_generate_modernization_plan(orchestrator, mock_project):
    """Test modernization plan generation"""
    mock_project.language = "python"
    mock_project.framework = "flask"
    mock_project.total_files = 100
    mock_project.total_lines = 5000
    
    mock_agent_results = [
        {"score": 70.0, "findings": []},
        {"score": 80.0, "findings": []},
        {"score": 75.0, "findings": []},
        {"score": 85.0, "findings": []}
    ]
    
    orchestrator.groq.generate_modernization_plan = AsyncMock(return_value={
        "priority_actions": ["Fix security issues"],
        "short_term_goals": ["Update dependencies"],
        "long_term_vision": ["Migrate to microservices"]
    })
    
    plan = await orchestrator._generate_modernization_plan(mock_project, mock_agent_results)
    
    assert "priority_actions" in plan
    assert len(plan["priority_actions"]) > 0

@pytest.mark.asyncio
async def test_save_analysis_results(orchestrator, mock_project):
    """Test saving analysis results to database"""
    mock_agent_results = [
        {
            "agent_type": AgentType.SECURITY,
            "score": 70.0,
            "findings": [{"severity": "high", "title": "SQL Injection"}]
        },
        {
            "agent_type": AgentType.PERFORMANCE,
            "score": 80.0,
            "findings": []
        },
        {
            "agent_type": AgentType.ARCHITECTURE,
            "score": 75.0,
            "findings": []
        },
        {
            "agent_type": AgentType.DEPENDENCY,
            "score": 85.0,
            "findings": []
        }
    ]
    
    mock_decision = {
        "decision": "NEEDS_WORK",
        "reasoning": "Security issues found"
    }
    
    mock_plan = {
        "priority_actions": ["Fix SQL injection"]
    }
    
    analysis = await orchestrator._save_analysis_results(
        mock_project,
        mock_agent_results,
        mock_decision,
        mock_plan
    )
    
    orchestrator.db.add.assert_called_once()
    orchestrator.db.commit.assert_called()
    orchestrator.db.refresh.assert_called()

@pytest.mark.asyncio
async def test_extract_critical_issues(orchestrator):
    """Test extraction of critical issues"""
    mock_agent_results = [
        {
            "findings": [
                {"severity": "critical", "title": "SQL Injection"},
                {"severity": "high", "title": "XSS"}
            ]
        },
        {
            "findings": [
                {"severity": "critical", "title": "Hardcoded Password"},
                {"severity": "medium", "title": "Slow Query"}
            ]
        }
    ]
    
    critical = orchestrator._extract_critical_issues(mock_agent_results)
    
    assert len(critical) == 2
    assert all(issue["severity"] == "critical" for issue in critical)

@pytest.mark.asyncio
async def test_aggregate_recommendations(orchestrator):
    """Test aggregation of recommendations"""
    mock_agent_results = [
        {
            "agent_type": AgentType.SECURITY,
            "recommendations": ["Use parameterized queries", "Add input validation"],
            "findings": [{"severity": "critical"}]
        },
        {
            "agent_type": AgentType.PERFORMANCE,
            "recommendations": ["Add caching", "Optimize queries"],
            "findings": []
        }
    ]
    
    recommendations = orchestrator._aggregate_recommendations(mock_agent_results)
    
    assert len(recommendations) == 4
    assert recommendations[0]["category"] == "security"
    assert recommendations[0]["priority"] == "high"
    assert recommendations[2]["category"] == "performance"

@pytest.mark.asyncio
async def test_prepare_training_data(orchestrator):
    """Test Oumi training data preparation"""
    mock_code_data = {"files": []}
    
    mock_analysis = Analysis(
        id=1,
        project_id=1,
        security_issues=[
            {
                "code_snippet": "query = 'SELECT * FROM users WHERE id=' + user_input",
                "suggestion": "Use parameterized queries"
            }
        ],
        performance_issues=[],
        architecture_issues=[],
        dependency_issues=[],
        overall_score=75.0
    )
    
    training_data = orchestrator._prepare_training_data(mock_code_data, mock_analysis)
    
    assert len(training_data) > 0
    assert "input" in training_data[0]
    assert "output" in training_data[0]

@pytest.mark.asyncio
async def test_start_analysis_full_flow(orchestrator, mock_project):
    """Test full analysis workflow (integration test)"""
    # Mock all async methods
    orchestrator._prepare_repository = AsyncMock(return_value="/tmp/repo")
    orchestrator._extract_code_data = AsyncMock(return_value={
        "files": [],
        "total_files": 10,
        "language": "python"
    })
    orchestrator._run_multi_agent_analysis = AsyncMock(return_value=[
        {"agent_type": "security", "score": 80.0}
    ])
    orchestrator._make_decision = AsyncMock(return_value={
        "decision": "APPROVE"
    })
    orchestrator._generate_modernization_plan = AsyncMock(return_value={})
    orchestrator._save_analysis_results = AsyncMock(return_value=Mock())
    orchestrator._fine_tune_oumi_model = AsyncMock()
    orchestrator._create_improvement_pr = AsyncMock()
    
    # Run analysis
    await orchestrator.start_analysis(mock_project.id)
    
    # Verify project status was updated
    assert mock_project.status == ProjectStatus.COMPLETED
    assert mock_project.completed_at is not None
    orchestrator.db.commit.assert_called()

@pytest.mark.asyncio
async def test_start_analysis_failure_handling(orchestrator, mock_project):
    """Test analysis failure handling"""
    orchestrator._prepare_repository = AsyncMock(side_effect=Exception("Clone failed"))
    
    await orchestrator.start_analysis(mock_project.id)
    
    assert mock_project.status == ProjectStatus.FAILED
    assert mock_project.error_message == "Clone failed"
    orchestrator.db.commit.assert_called()
