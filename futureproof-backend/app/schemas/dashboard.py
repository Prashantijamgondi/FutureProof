"""
Dashboard Schemas
"""
from typing import List, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class DashboardStats(BaseModel):
    """Dashboard statistics"""
    total_projects: int = 0
    active_projects: int = 0
    completed_projects: int = 0
    failed_projects: int = 0
    total_analyses: int = 0
    total_transformations: int = 0
    avg_code_quality: float = 0.0
    

class ActivityItem(BaseModel):
    """Activity log item"""
    id: int
    type: str  # "project_created", "analysis_completed", "transformation_started", etc.
    project_id: int
    project_name: str
    message: str
    timestamp: datetime
    status: str


class RecentActivity(BaseModel):
    """Recent activity response"""
    activities: List[ActivityItem]
    total: int
