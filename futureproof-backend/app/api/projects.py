# from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
# from sqlalchemy.orm import Session
# from typing import List
# import logging

# from app.database import get_db
# from app.models.project import Project, ProjectStatus
# from app.schemas.project import ProjectCreate, ProjectResponse, ProjectList
# from app.services.orchestrator import OrchestratorService

# router = APIRouter()
# logger = logging.getLogger(__name__)


# @router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
# async def create_project(
#     project_data: ProjectCreate,
#     background_tasks: BackgroundTasks,
#     db: Session = Depends(get_db)  # This is correct
# ):
#     """Create a new project and start analysis"""
#     try:
#         # Create project
#         project = Project(
#             name=project_data.name,
#             repo_url=project_data.repo_url,
#             status=ProjectStatus.PENDING,
#             total_files=0,
#             total_lines=0
#         )
        
#         db.add(project)
#         db.commit()
#         db.refresh(project)
        
#         # Start analysis in background
#         orchestrator = OrchestratorService(db)
#         background_tasks.add_task(orchestrator.start_analysis, project.id)
        
#         logger.info(f"Created project {project.id}: {project.name}")
#         return project
        
#     except Exception as e:
#         db.rollback()
#         logger.error(f"Error creating project: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to create project: {str(e)}"
#         )


# @router.get("/", response_model=ProjectList)
# async def get_projects(
#     skip: int = 0,
#     limit: int = 100,
#     db: Session = Depends(get_db)
# ):
#     """Get all projects"""
#     try:
#         projects = db.query(Project).offset(skip).limit(limit).all()
#         total = db.query(Project).count()
        
#         return ProjectList(total=total, projects=projects)
        
#     except Exception as e:
#         logger.error(f"Error fetching projects: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to fetch projects: {str(e)}"
#         )


# @router.get("/{project_id}", response_model=ProjectResponse)
# async def get_project(
#     project_id: int,
#     db: Session = Depends(get_db)
# ):
#     """Get a specific project by ID"""
#     try:
#         project = db.query(Project).filter(Project.id == project_id).first()
        
#         if not project:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail=f"Project {project_id} not found"
#             )
        
#         return project
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error fetching project {project_id}: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to fetch project: {str(e)}"
#         )


# @router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_project(
#     project_id: int,
#     db: Session = Depends(get_db)
# ):
#     """Delete a project"""
#     try:
#         project = db.query(Project).filter(Project.id == project_id).first()
        
#         if not project:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail=f"Project {project_id} not found"
#             )
        
#         db.delete(project)
#         db.commit()
        
#         logger.info(f"Deleted project {project_id}")
#         return None
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         db.rollback()
#         logger.error(f"Error deleting project {project_id}: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to delete project: {str(e)}"
#         )
"""
Projects API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.project import Project
from app.schemas.project import (
    ProjectCreate,
    ProjectResponse,
    ProjectList,
    ProjectDetail,
)
from app.services.github_service import GitHubService

router = APIRouter()


@router.post("/", response_model=ProjectResponse, status_code=201)
async def create_project(
    project: ProjectCreate,
    db: AsyncSession = Depends(get_db)
) -> ProjectResponse:
    """Create a new project"""
    github_service = GitHubService()
    
    # Validate repo URL
    is_valid = await github_service.validate_repo_url(str(project.repo_url))
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail="Invalid GitHub repository URL or repository not accessible"
        )
    
    # Create project
    db_project = Project(
        name=project.name,
        description=project.description,
        repo_url=str(project.repo_url),
        status="pending"
    )
    
    db.add(db_project)
    await db.commit()
    await db.refresh(db_project)
    
    return ProjectResponse.model_validate(db_project)


@router.get("/", response_model=ProjectList)
async def list_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
) -> ProjectList:
    """Get list of all projects"""
    from sqlalchemy import select, func
    
    # Get total count
    count_query = select(func.count(Project.id))
    total = await db.scalar(count_query)
    
    # Get paginated projects
    offset = (page - 1) * page_size
    query = select(Project).offset(offset).limit(page_size).order_by(Project.created_at.desc())
    result = await db.execute(query)
    projects = result.scalars().all()
    
    return ProjectList(
        projects=[ProjectResponse.model_validate(p) for p in projects],
        total=total or 0,
        page=page,
        page_size=page_size
    )


@router.get("/{project_id}", response_model=ProjectDetail)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db)
) -> ProjectDetail:
    """Get project by ID"""
    from sqlalchemy import select
    
    query = select(Project).where(Project.id == project_id)
    result = await db.execute(query)
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return ProjectDetail.model_validate(project)


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a project"""
    from sqlalchemy import select
    
    query = select(Project).where(Project.id == project_id)
    result = await db.execute(query)
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    await db.delete(project)
    await db.commit()
    
    return {"message": f"Project {project_id} deleted successfully"}
