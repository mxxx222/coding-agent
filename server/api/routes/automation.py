from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uuid

router = APIRouter()

# Request models
class StartAutomationRequest(BaseModel):
    notion_page_id: str
    options: Optional[Dict[str, Any]] = None

# Job storage (in production, use Redis/Database)
jobs = {}

@router.post("/start")
async def start_automation(request: StartAutomationRequest, background_tasks: BackgroundTasks):
    """Start automation pipeline."""
    try:
        job_id = str(uuid.uuid4())
        
        # Initialize job
        jobs[job_id] = {
            "id": job_id,
            "status": "running",
            "progress": 0,
            "steps": [],
            "error": None
        }
        
        # Run in background
        background_tasks.add_task(run_automation, job_id, request.notion_page_id, request.options)
        
        return {
            "status": "started",
            "job_id": job_id,
            "message": "Automation pipeline started"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/job/{job_id}")
async def get_job_status(job_id: str):
    """Get job status."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return jobs[job_id]

@router.get("/jobs")
async def list_jobs():
    """List all jobs."""
    return {
        "jobs": list(jobs.values())
    }

async def run_automation(job_id: str, notion_page_id: str, options: Optional[Dict[str, Any]]):
    """Run automation pipeline."""
    try:
        from services.workflow.automation import AutomationWorkflow
        
        workflow = AutomationWorkflow()
        result = await workflow.run_full_pipeline(notion_page_id, options)
        
        # Update job
        jobs[job_id].update({
            "status": result.get("status"),
            "progress": 100,
            "steps": result.get("steps", []),
            "result": result,
            "error": result.get("error")
        })
        
    except Exception as e:
        jobs[job_id].update({
            "status": "failed",
            "error": str(e)
        })

