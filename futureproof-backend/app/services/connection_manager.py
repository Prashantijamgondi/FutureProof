"""
WebSocket Connection Manager
Manages WebSocket connections for real-time updates
"""
from typing import Dict, Set
from fastapi import WebSocket
import json
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        # Store active connections by project_id
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, project_id: int):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        
        if project_id not in self.active_connections:
            self.active_connections[project_id] = set()
        
        self.active_connections[project_id].add(websocket)
        logger.info(f"WebSocket connected for project {project_id}. Total connections: {len(self.active_connections[project_id])}")
    
    def disconnect(self, websocket: WebSocket, project_id: int):
        """Remove a WebSocket connection"""
        if project_id in self.active_connections:
            self.active_connections[project_id].discard(websocket)
            
            # Clean up empty project entries
            if not self.active_connections[project_id]:
                del self.active_connections[project_id]
            
            logger.info(f"WebSocket disconnected for project {project_id}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific WebSocket connection"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
    
    async def broadcast_to_project(self, project_id: int, message: dict):
        """Broadcast a message to all connections for a specific project"""
        if project_id not in self.active_connections:
            logger.debug(f"No active connections for project {project_id}")
            return
        
        # Create a copy of the set to avoid modification during iteration
        connections = self.active_connections[project_id].copy()
        
        disconnected = []
        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection, project_id)
    
    async def send_progress_update(self, project_id: int, progress: int, status: str, details: dict = None):
        """Send a progress update to all connections for a project"""
        message = {
            "type": "progress",
            "project_id": project_id,
            "progress": progress,
            "status": status,
            "details": details or {}
        }
        await self.broadcast_to_project(project_id, message)
    
    async def send_analysis_complete(self, project_id: int, results: dict):
        """Send analysis completion message"""
        message = {
            "type": "analysis_complete",
            "project_id": project_id,
            "results": results
        }
        await self.broadcast_to_project(project_id, message)
    
    async def send_error(self, project_id: int, error: str):
        """Send error message"""
        message = {
            "type": "error",
            "project_id": project_id,
            "error": error
        }
        await self.broadcast_to_project(project_id, message)
    
    async def send_agent_update(self, project_id: int, agent_name: str, status: str, score: float = None):
        """Send agent-specific update"""
        message = {
            "type": "agent_update",
            "project_id": project_id,
            "agent": agent_name,
            "status": status,
            "score": score
        }
        await self.broadcast_to_project(project_id, message)
    
    async def send_transformation_update(self, project_id: int, file_path: str, status: str):
        """Send transformation update for a specific file"""
        message = {
            "type": "transformation_update",
            "project_id": project_id,
            "file": file_path,
            "status": status
        }
        await self.broadcast_to_project(project_id, message)
    
    async def send_project_message(self, project_id: int, message: dict):
        """Send a message to all connections for a project (alias for broadcast_to_project)"""
        await self.broadcast_to_project(project_id, message)
    
    def get_connection_count(self, project_id: int = None) -> int:
        """Get the number of active connections"""
        if project_id:
            return len(self.active_connections.get(project_id, set()))
        return sum(len(connections) for connections in self.active_connections.values())


# Global connection manager instance
manager = ConnectionManager()
