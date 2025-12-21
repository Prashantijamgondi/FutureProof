from fastapi import APIRouter, Request, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_current_db
from app.services.github_service import GitHubService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/github")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_current_db)
):
    """Handle GitHub webhooks (for PR events)"""
    payload = await request.json()
    event_type = request.headers.get("X-GitHub-Event")
    
    logger.info(f"Received GitHub webhook: {event_type}")
    
    if event_type == "pull_request":
        action = payload.get("action")
        if action in ["opened", "synchronize"]:
            pr_number = payload["pull_request"]["number"]
            repo_url = payload["repository"]["html_url"]
            
            # Process PR in background
            github_service = GitHubService()
            background_tasks.add_task(
                github_service.analyze_pr,
                repo_url,
                pr_number,
                db
            )
    
    return {"status": "received"}

@router.post("/kestra")
async def kestra_webhook(request: Request):
    """Handle Kestra workflow webhooks"""
    payload = await request.json()
    logger.info(f"Received Kestra webhook: {payload}")
    
    # Process Kestra events (workflow completion, errors, etc.)
    return {"status": "received"}
