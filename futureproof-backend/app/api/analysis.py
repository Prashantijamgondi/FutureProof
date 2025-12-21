"""
Analysis API routes - REAL implementation
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.project import Project
from app.models.analysis import Analysis
from app.services.code_analyzer import CodeAnalyzer  # ✅ REAL analyzer
from datetime import datetime
import traceback

router = APIRouter()


async def run_analysis_task(project_id: int, repo_url: str):
    """Background task to run real code analysis"""
    from app.database import async_session_maker
    from app.services.connection_manager import manager
    
    async with async_session_maker() as db:
        try:
            # Send initial progress
            await manager.send_progress_update(project_id, 0, "Starting analysis...")
            
            # Get analysis record
            result = await db.execute(
                select(Analysis)
                .filter(Analysis.project_id == project_id)
                .order_by(Analysis.created_at.desc())
            )
            analysis_row = result.first()
            if not analysis_row:
                return
            
            analysis = analysis_row[0]
            
            # Update to running
            analysis.status = "running"
            analysis.started_at = datetime.utcnow()
            await db.commit()
            
            await manager.send_progress_update(project_id, 10, "Cloning repository...")
            
            # ✅ RUN REAL ANALYSIS
            analyzer = CodeAnalyzer()
            start_time = datetime.utcnow()
            
            await manager.send_progress_update(project_id, 30, "Analyzing code...")
            
            results = await analyzer.analyze_repository(repo_url)
            
            await manager.send_progress_update(project_id, 80, "Generating recommendations...")
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            # Update analysis with real results
            analysis.status = "completed"
            analysis.overall_score = results['overall_score']
            analysis.security_score = results['security_score']
            analysis.performance_score = results['performance_score']
            analysis.architecture_score = results['architecture_score']
            analysis.dependency_score = results['dependency_score']
            analysis.maintainability_score = results['maintainability_score']
            analysis.code_quality_score = results['code_quality_score']
            
            analysis.total_files_analyzed = results['total_files']
            analysis.total_lines_analyzed = results['total_lines']
            analysis.detected_language = results['detected_language']
            analysis.detected_framework = results['detected_framework']
            analysis.detected_libraries = results['detected_libraries']
            
            analysis.analysis_details = results['analysis_details']
            analysis.recommendations = results['recommendations']
            analysis.issues = results['issues']
            analysis.metrics = results['metrics']
            
            analysis.analysis_duration = duration
            analysis.completed_at = datetime.utcnow()
            analysis.analyzer_version = "1.0.0"
            
            await db.commit()
            
            # Send completion notification
            await manager.send_progress_update(project_id, 100, "Analysis complete!")
            await manager.send_analysis_complete(project_id, {
                "overall_score": results['overall_score'],
                "security_score": results['security_score'],
                "performance_score": results['performance_score'],
                "total_files": results['total_files'],
                "total_lines": results['total_lines']
            })
            
            print(f"✅ Analysis completed for project {project_id}")
            
        except Exception as e:
            # Update analysis with error
            try:
                analysis.status = "failed"
                analysis.error_message = str(e)
                analysis.error_details = {"traceback": traceback.format_exc()}
                analysis.completed_at = datetime.utcnow()
                await db.commit()
                
                # Send error notification
                await manager.send_error(project_id, str(e))
            except:
                pass
            
            print(f"❌ Analysis failed for project {project_id}: {e}")



@router.post("/{project_id}/analyze")
async def analyze_project(
    project_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Start REAL code analysis for a project"""
    
    # Get project
    result = await db.execute(select(Project).filter(Project.id == project_id))
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    
    # Create analysis record
    analysis = Analysis(
        project_id=project_id,
        status="pending"
    )
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)
    
    # Start background analysis task
    background_tasks.add_task(run_analysis_task, project_id, project.repo_url)
    
    return {
        "message": "Real code analysis started",
        "analysis_id": analysis.id,
        "project_id": project_id,
        "status": "pending"
    }



@router.get("/project/{project_id}")
async def get_project_analysis(
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get latest analysis results for a project"""
    
    result = await db.execute(
        select(Analysis)
        .filter(Analysis.project_id == project_id)
        .order_by(Analysis.created_at.desc())
    )
    analysis_row = result.first()
    
    if not analysis_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No analysis found for this project"
        )
    
    return analysis_row[0]


@router.get("/{analysis_id}")
async def get_analysis(
    analysis_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get specific analysis by ID"""
    
    result = await db.execute(select(Analysis).filter(Analysis.id == analysis_id))
    analysis = result.scalar_one_or_none()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis with id {analysis_id} not found"
        )
    
    return analysis
