"""
WebSocket API endpoints for real-time updates
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from app.database import get_db
from app.models.project import Project
from app.services.connection_manager import manager

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws/{project_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    WebSocket endpoint for real-time project updates
    
    Sends updates for:
    - Analysis progress
    - Agent execution status
    - Transformation progress
    - Completion/error notifications
    """
    # Verify project exists
    result = await db.execute(select(Project).filter(Project.id == project_id))
    project = result.scalar_one_or_none()
    
    if not project:
        await websocket.close(code=4004, reason="Project not found")
        return
    
    # Accept connection
    await manager.connect(websocket, project_id)
    
    try:
        # Send initial connection confirmation
        await manager.send_personal_message({
            "type": "connected",
            "project_id": project_id,
            "project_name": project.name,
            "message": "Connected to real-time updates"
        }, websocket)
        
        # Keep connection alive and listen for client messages
        while True:
            # Receive message from client (for ping/pong or commands)
            data = await websocket.receive_text()
            
            # Handle ping
            if data == "ping":
                await manager.send_personal_message({
                    "type": "pong",
                    "project_id": project_id
                }, websocket)
            
            # Handle status request
            elif data == "status":
                # Get current project status
                await db.refresh(project)
                await manager.send_personal_message({
                    "type": "status",
                    "project_id": project_id,
                    "status": project.status,
                    "created_at": project.created_at.isoformat() if project.created_at else None
                }, websocket)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, project_id)
        logger.info(f"Client disconnected from project {project_id}")
    
    except Exception as e:
        logger.error(f"WebSocket error for project {project_id}: {e}")
        manager.disconnect(websocket, project_id)


@router.get("/ws/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics"""
    return {
        "total_connections": manager.get_connection_count(),
        "active_projects": len(manager.active_connections),
        "connections_by_project": {
            project_id: manager.get_connection_count(project_id)
            for project_id in manager.active_connections.keys()
        }
    }
