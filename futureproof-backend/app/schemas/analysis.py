# from pydantic import BaseModel, Field
# from typing import List, Dict, Optional, Any
# from datetime import datetime

# class AnalysisBase(BaseModel):
#     project_id: int

# class AnalysisCreate(AnalysisBase):
#     pass

# class IssueDetail(BaseModel):
#     severity: str = Field(..., description="critical, high, medium, low")
#     title: str
#     description: str
#     file_path: Optional[str] = None
#     line_number: Optional[int] = None
#     suggestion: Optional[str] = None

# class Recommendation(BaseModel):
#     category: str
#     priority: str
#     title: str
#     description: str
#     estimated_effort: str

# class AnalysisResponse(BaseModel):
#     id: int
#     project_id: int
    
#     # Scores
#     security_score: float
#     performance_score: float
#     architecture_score: float
#     dependency_score: float
#     overall_score: float
    
#     # Issues
#     security_issues: List[Dict[str, Any]]
#     performance_issues: List[Dict[str, Any]]
#     architecture_issues: List[Dict[str, Any]]
#     dependency_issues: List[Dict[str, Any]]
    
#     # Recommendations
#     recommendations: List[Dict[str, Any]]
#     modernization_roadmap: List[Dict[str, Any]]
    
#     # Decision
#     decision: Optional[str] = None
#     decision_reasoning: Optional[str] = None
    
#     # Timestamps
#     created_at: datetime
#     completed_at: Optional[datetime] = None
#     processing_time_seconds: Optional[float] = None

#     class Config:
#         from_attributes = True
"""
Analysis Schemas
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class AnalysisStatus(str, Enum):
    """Analysis status enum"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentStatus(str, Enum):
    """Agent task status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class CodeIssue(BaseModel):
    """Code quality issue"""
    severity: str = Field(..., description="Severity: critical, high, medium, low")
    category: str = Field(..., description="Issue category")
    message: str = Field(..., description="Issue description")
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    suggestion: Optional[str] = None


class SecurityIssue(BaseModel):
    """Security vulnerability"""
    severity: str
    title: str
    description: str
    cwe_id: Optional[str] = None
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    recommendation: Optional[str] = None


class DependencyInfo(BaseModel):
    """Dependency information"""
    name: str
    current_version: str
    latest_version: Optional[str] = None
    is_outdated: bool = False
    security_issues: List[str] = []


class AnalysisMetrics(BaseModel):
    """Code metrics"""
    total_files: int = 0
    total_lines: int = 0
    code_lines: int = 0
    comment_lines: int = 0
    blank_lines: int = 0
    complexity_score: Optional[float] = None
    maintainability_index: Optional[float] = None
    code_quality_score: Optional[float] = None


class AnalysisResponse(BaseModel):
    """Analysis result response"""
    id: int
    project_id: int
    status: str
    language: str
    framework: Optional[str] = None
    
    # Metrics
    metrics: Optional[AnalysisMetrics] = None
    total_files: int = 0
    total_lines: int = 0
    code_quality_score: Optional[float] = None
    maintainability_index: Optional[float] = None
    
    # Issues
    code_issues: List[CodeIssue] = []
    security_issues: List[SecurityIssue] = []
    
    # Dependencies
    dependencies: Dict[str, Any] = {}
    outdated_dependencies: List[str] = []
    
    # Recommendations
    recommendations: List[str] = []
    
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AnalysisStatusResponse(BaseModel):
    """Analysis status response"""
    analysis_id: int
    project_id: int
    status: AnalysisStatus
    progress: int = Field(0, ge=0, le=100, description="Progress percentage")
    current_step: Optional[str] = None
    message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AgentTaskResponse(BaseModel):
    """Agent task response"""
    task_id: str
    agent_name: str
    status: AgentStatus
    progress: int = Field(0, ge=0, le=100)
    message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AnalysisCreate(BaseModel):
    """Schema for creating an analysis"""
    project_id: int
    full_scan: bool = True
    include_dependencies: bool = True
    include_security: bool = True


class AnalysisDetail(AnalysisResponse):
    """Detailed analysis with agent tasks"""
    agent_tasks: List[AgentTaskResponse] = []
    execution_time: Optional[float] = None
    
    class Config:
        from_attributes = True
