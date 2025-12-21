import httpx
from typing import Dict, Any, List
import logging
from app.config import settings
import yaml

logger = logging.getLogger(__name__)

class KestraService:
    """Service for Kestra workflow orchestration"""
    
    def __init__(self):
        self.base_url = settings.KESTRA_API_URL
        self.namespace = "futureproof"
    
    async def trigger_workflow(
        self, 
        workflow_id: str, 
        inputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Trigger a Kestra workflow"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/executions/{self.namespace}/{workflow_id}",
                    json={"inputs": inputs}
                )
                response.raise_for_status()
                
                execution = response.json()
                logger.info(f"Triggered workflow {workflow_id}: {execution['id']}")
                
                return {
                    "execution_id": execution["id"],
                    "status": execution["state"]["current"],
                    "workflow_id": workflow_id
                }
                
        except Exception as e:
            logger.error(f"Failed to trigger workflow: {str(e)}")
            raise
    
    async def get_execution_status(self, execution_id: str) -> Dict[str, Any]:
        """Get workflow execution status"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/executions/{execution_id}"
                )
                response.raise_for_status()
                
                execution = response.json()
                return {
                    "execution_id": execution_id,
                    "status": execution["state"]["current"],
                    "duration": execution.get("duration"),
                    "outputs": execution.get("outputs", {})
                }
                
        except Exception as e:
            logger.error(f"Failed to get execution status: {str(e)}")
            return {"status": "unknown", "error": str(e)}
    
    async def run_multi_agent_workflow(
        self,
        project_id: int,
        repo_path: str,
        code_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run the multi-agent analysis workflow"""
        try:
            inputs = {
                "project_id": project_id,
                "repo_path": repo_path,
                "code_data": code_data
            }
            
            result = await self.trigger_workflow("multi-agent-analysis", inputs)
            
            # Wait for completion (polling)
            execution_id = result["execution_id"]
            status = await self._wait_for_completion(execution_id, timeout=600)
            
            return status
            
        except Exception as e:
            logger.error(f"Multi-agent workflow failed: {str(e)}")
            raise
    
    async def run_decision_workflow(
        self,
        project_id: int,
        agent_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Run decision-making workflow based on agent outputs"""
        try:
            inputs = {
                "project_id": project_id,
                "agent_results": agent_results
            }
            
            result = await self.trigger_workflow("decision-maker", inputs)
            execution_id = result["execution_id"]
            
            status = await self._wait_for_completion(execution_id, timeout=300)
            
            return {
                "decision": status["outputs"].get("decision"),
                "reasoning": status["outputs"].get("reasoning"),
                "confidence": status["outputs"].get("confidence", 0.0)
            }
            
        except Exception as e:
            logger.error(f"Decision workflow failed: {str(e)}")
            raise
    
    async def _wait_for_completion(
        self,
        execution_id: str,
        timeout: int = 600,
        poll_interval: int = 5
    ) -> Dict[str, Any]:
        """Wait for workflow execution to complete"""
        import asyncio
        
        elapsed = 0
        while elapsed < timeout:
            status = await self.get_execution_status(execution_id)
            
            if status["status"] in ["SUCCESS", "FAILED", "KILLED"]:
                return status
            
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval
        
        raise Exception(f"Workflow {execution_id} timed out after {timeout}s")
    
    async def upload_workflow(self, workflow_file: str) -> bool:
        """Upload a workflow definition to Kestra"""
        try:
            with open(workflow_file, 'r') as f:
                workflow_yaml = yaml.safe_load(f)
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/flows",
                    json=workflow_yaml
                )
                response.raise_for_status()
                
                logger.info(f"Uploaded workflow: {workflow_yaml['id']}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to upload workflow: {str(e)}")
            return False
