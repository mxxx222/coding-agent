from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import os

router = APIRouter()

# Request models
class CreateProjectRequest(BaseModel):
    name: str
    framework: str = "nextjs"

class CreateDeploymentRequest(BaseModel):
    project_id: str
    files: List[Dict[str, str]]
    target: str = "production"

# Import the deployment service
try:
    from services.deployment.vercel import VercelDeployService
    vercel_service = VercelDeployService()
    VERCEL_ENABLED = True
except ImportError:
    vercel_service = None
    VERCEL_ENABLED = False

@router.get("/health")
async def health_check():
    """Check deployment integration health."""
    return {
        "status": "enabled" if VERCEL_ENABLED else "disabled",
        "vercel_enabled": VERCEL_ENABLED
    }

@router.post("/vercel/create-project")
async def create_project(request: CreateProjectRequest):
    """Create a new Vercel project."""
    try:
        if not VERCEL_ENABLED:
            raise HTTPException(
                status_code=503,
                detail="Vercel integration not configured. Install httpx: pip install httpx"
            )
        
        project = await vercel_service.create_project(
            name=request.name,
            framework=request.framework
        )
        return {
            "status": "success",
            "project": project
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/vercel/deploy")
async def trigger_deployment(request: CreateDeploymentRequest):
    """Trigger a Vercel deployment."""
    try:
        if not VERCEL_ENABLED:
            raise HTTPException(status_code=503, detail="Vercel integration not configured")
        
        deployment = await vercel_service.create_deployment(
            project_id=request.project_id,
            files=request.files,
            target=request.target
        )
        return {
            "status": "success",
            "deployment": deployment
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vercel/deployment/{deployment_id}")
async def get_deployment_status(deployment_id: str):
    """Get deployment status."""
    try:
        if not VERCEL_ENABLED:
            raise HTTPException(status_code=503, detail="Vercel integration not configured")
        
        status = await vercel_service.get_deployment_status(deployment_id)
        return {
            "status": "success",
            "deployment": status
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vercel/projects")
async def list_projects():
    """List all Vercel projects."""
    try:
        if not VERCEL_ENABLED:
            return {
                "status": "disabled",
                "message": "Vercel integration not configured. Install httpx: pip install httpx"
            }
        
        projects = await vercel_service.list_projects()
        return {
            "status": "success",
            "projects": projects
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

