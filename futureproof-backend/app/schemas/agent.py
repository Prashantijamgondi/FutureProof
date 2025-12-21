from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.models.agent_task import AgentType, TaskStatus

class AgentTaskBase(BaseModel):
    agent_type: AgentType
    project_id: int

class AgentTaskResponse(BaseModel):
    id: int
    project_id: int
    agent_type: AgentType
    status: TaskStatus
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AgentOutput(BaseModel):
    agent_type: str
    status: str
    findings: List[Dict[str, Any]]
    score: float
    recommendations: List[str]
    processing_time: float
