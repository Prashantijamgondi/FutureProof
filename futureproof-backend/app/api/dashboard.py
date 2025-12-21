"""
Dashboard API endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.project import Project
from app.schemas.dashboard import DashboardStats, RecentActivity, ActivityItem

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """Get dashboard statistics"""
    
    # Count total projects
    total_query = select(func.count(Project.id))
    total_projects = await db.scalar(total_query) or 0
    
    # Count by status
    active_query = select(func.count(Project.id)).where(Project.status == "in_progress")
    active_projects = await db.scalar(active_query) or 0
    
    completed_query = select(func.count(Project.id)).where(Project.status == "completed")
    completed_projects = await db.scalar(completed_query) or 0
    
    failed_query = select(func.count(Project.id)).where(Project.status == "failed")
    failed_projects = await db.scalar(failed_query) or 0
    
    return DashboardStats(
        total_projects=total_projects,
        active_projects=active_projects,
        completed_projects=completed_projects,
        failed_projects=failed_projects,
        total_analyses=0,  # TODO: Count from analysis table
        total_transformations=0,  # TODO: Count from transformation table
        avg_code_quality=0.0
    )


@router.get("/activity", response_model=RecentActivity)
async def get_recent_activity(db: AsyncSession = Depends(get_db)):
    """Get recent activity"""
    
    # Get recent projects
    query = select(Project).order_by(Project.created_at.desc()).limit(10)
    result = await db.execute(query)
    projects = result.scalars().all()
    
    activities = [
        ActivityItem(
            id=p.id,
            type="project_created",
            project_id=p.id,
            project_name=p.name,
            message=f"Project '{p.name}' created",
            timestamp=p.created_at,
            status=p.status
        )
        for p in projects
    ]
    
    return RecentActivity(
        activities=activities,
        total=len(activities)
    )
