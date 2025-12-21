"""
Project Schemas
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


class ProjectBase(BaseModel):
    """Base project schema"""
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, max_length=1000, description="Project description")
    repo_url: HttpUrl = Field(..., description="Git repository URL")


class ProjectCreate(ProjectBase):
    """Schema for creating a project"""
    pass


class ProjectUpdate(BaseModel):
    """Schema for updating a project"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    repo_url: Optional[HttpUrl] = None
    status: Optional[str] = None


class ProjectResponse(ProjectBase):
    """Schema for project response"""
    id: int
    status: str
    language: Optional[str] = None
    framework: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProjectList(BaseModel):
    """Schema for list of projects"""
    projects: List[ProjectResponse]
    total: int
    page: int = 1
    page_size: int = 10
    
    class Config:
        from_attributes = True


class ProjectDetail(ProjectResponse):
    """Detailed project schema with additional info"""
    analysis_id: Optional[int] = None
    transformation_id: Optional[int] = None
    file_count: Optional[int] = None
    lines_of_code: Optional[int] = None
    
    class Config:
        from_attributes = True
