"""
Transformation Schemas
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class TransformStatus(str, Enum):
    """Transformation status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class TransformationResponse(BaseModel):
    """Transformation result"""
    id: int
    project_id: int
    status: TransformStatus
    target_language: Optional[str] = None
    target_framework: Optional[str] = None
    transformed_files: Dict[str, Any] = {}
    improvements: Dict[str, Any] = {}
    migration_guide: List[Dict[str, Any]] = []
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TransformCreate(BaseModel):
    """Schema for creating transformation"""
    project_id: int
    target_year: int = Field(2028, ge=2024, le=2030)
    target_language: Optional[str] = None
    target_framework: Optional[str] = None


class TransformPreview(BaseModel):
    """Preview of transformation"""
    project_id: int
    detected_language: str
    detected_framework: Optional[str] = None
    recommended_target: str
    estimated_changes: int
    sample_transformations: List[Dict[str, Any]] = []
