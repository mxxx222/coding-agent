# Vercel Deployment Integration - Complete Guide

## Overview

This guide shows how to implement automatic Vercel deployment from automated code generation.

---

## 1. Setup Vercel Integration

### Prerequisites

```bash
cd server
pip install python-dotenv httpx
```

### Environment Variables

```bash
# .env
VERCEL_TOKEN=your_vercel_token
VERCEL_TEAM_ID=your_team_id  # Optional
VERCEL_ORG_ID=your_org_id    # Optional
```

### Get Vercel Token

1. Go to https://vercel.com/account/tokens
2. Create new token
3. Copy the token (store securely!)

---

## 2. Vercel API Service

### `server/services/deployment/vercel.py`

```python
import httpx
import os
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

load_dotenv()

class VercelDeployService:
    def __init__(self):
        self.token = os.getenv("VERCEL_TOKEN")
        self.team_id = os.getenv("VERCEL_TEAM_ID")
        self.base_url = "https://api.vercel.com"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def _get_url(self, endpoint: str) -> str:
        """Build API URL with team parameter."""
        url = f"{self.base_url}{endpoint}"
        if self.team_id:
            url += f"?teamId={self.team_id}"
        return url
    
    async def create_project(self, name: str, framework: str = "nextjs") -> Dict[str, Any]:
        """Create a new Vercel project."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self._get_url("/v9/projects"),
                    headers=self.headers,
                    json={
                        "name": name,
                        "framework": framework
                    }
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Error creating project: {e.response.text}")
            raise
    
    async def create_deployment(
        self,
        project_id: str,
        files: List[Dict[str, str]],
        target: str = "production"
    ) -> Dict[str, Any]:
        """Create a new deployment."""
        try:
            payload = {
                "name": project_id,
                "target": target,
                "files": files
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self._get_url("/v13/deployments"),
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Error creating deployment: {e.response.text}")
            raise
    
    async def get_deployment_status(self, deployment_id: str) -> Dict[str, Any]:
        """Get deployment status."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self._get_url(f"/v13/deployments/{deployment_id}"),
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Error getting deployment status: {e.response.text}")
            raise
    
    async def cancel_deployment(self, deployment_id: str) -> Dict[str, Any]:
        """Cancel a deployment."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    self._get_url(f"/v13/deployments/{deployment_id}/cancel"),
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Error canceling deployment: {e.response.text}")
            raise
    
    async def list_projects(self) -> List[Dict[str, Any]]:
        """List all Vercel projects."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self._get_url("/v9/projects"),
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json().get("projects", [])
        except httpx.HTTPStatusError as e:
            print(f"Error listing projects: {e.response.text}")
            raise
    
    async def get_project(self, project_id: str) -> Dict[str, Any]:
        """Get project details."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self._get_url(f"/v9/projects/{project_id}"),
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Error getting project: {e.response.text}")
            raise
    
    async def connect_github(
        self,
        project_id: str,
        repo: str,
        type: str = "github"
    ) -> Dict[str, Any]:
        """Connect GitHub repository to Vercel project."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    self._get_url(f"/v9/projects/{project_id}"),
                    headers=self.headers,
                    json={
                        "gitRepository": {
                            "repo": repo,
                            "type": type
                        }
                    }
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Error connecting GitHub: {e.response.text}")
            raise
```

---

## 3. API Endpoints

### `server/api/routes/deployment.py`

```python
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any
from services.deployment.vercel import VercelDeployService

router = APIRouter()

# Request models
class CreateProjectRequest(BaseModel):
    name: str
    framework: str = "nextjs"

class CreateDeploymentRequest(BaseModel):
    project_id: str
    files: List[Dict[str, str]]
    target: str = "production"

class GetDeploymentStatusRequest(BaseModel):
    deployment_id: str

# Initialize service
vercel_service = VercelDeployService()

@router.post("/vercel/create-project")
async def create_project(request: CreateProjectRequest):
    """Create a new Vercel project."""
    try:
        project = await vercel_service.create_project(
            name=request.name,
            framework=request.framework
        )
        return {
            "status": "success",
            "project": project
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/vercel/deploy")
async def trigger_deployment(request: CreateDeploymentRequest):
    """Trigger a Vercel deployment."""
    try:
        deployment = await vercel_service.create_deployment(
            project_id=request.project_id,
            files=request.files,
            target=request.target
        )
        return {
            "status": "success",
            "deployment": deployment
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vercel/deployment/{deployment_id}")
async def get_deployment_status(deployment_id: str):
    """Get deployment status."""
    try:
        status = await vercel_service.get_deployment_status(deployment_id)
        return {
            "status": "success",
            "deployment": status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/vercel/cancel/{deployment_id}")
async def cancel_deployment(deployment_id: str):
    """Cancel a deployment."""
    try:
        result = await vercel_service.cancel_deployment(deployment_id)
        return {
            "status": "success",
            "deployment": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vercel/projects")
async def list_projects():
    """List all Vercel projects."""
    try:
        projects = await vercel_service.list_projects()
        return {
            "status": "success",
            "projects": projects
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vercel/project/{project_id}")
async def get_project(project_id: str):
    """Get project details."""
    try:
        project = await vercel_service.get_project(project_id)
        return {
            "status": "success",
            "project": project
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 4. Integrate with FastAPI Main

### Update `server/api/main.py`

```python
from .routes import code, refactor, test, integrate, indexer, notion, deployment

# Add to routers section:
app.include_router(deployment.router, prefix="/api/deploy", tags=["deployment"])
```

---

## 5. Usage Examples

### Create Project

```bash
curl -X POST http://localhost:8000/api/deploy/vercel/create-project \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-automated-app",
    "framework": "nextjs"
  }'
```

### Trigger Deployment

```bash
curl -X POST http://localhost:8000/api/deploy/vercel/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "prj_abc123",
    "files": [
      {"path": "package.json", "content": "..."},
      {"path": "pages/index.js", "content": "..."}
    ],
    "target": "production"
  }'
```

### Get Deployment Status

```bash
curl http://localhost:8000/api/deploy/vercel/deployment/dpl_abc123
```

### Example Response

```json
{
  "status": "success",
  "deployment": {
    "url": "https://my-app.vercel.app",
    "state": "READY",
    "created_at": 1698064800000,
    "ready_at": 1698064900000
  }
}
```

---

## 6. Complete Workflow Example

```python
# Complete automation flow
async def automate_deployment():
    # 1. Create Vercel project
    project = await vercel_service.create_project(
        name="my-automated-app",
        framework="nextjs"
    )
    
    # 2. Generate code files (from your code generation)
    files = [
        {"path": "package.json", "content": "..."},
        {"path": "pages/index.js", "content": "..."},
        {"path": "vercel.json", "content": "..."}
    ]
    
    # 3. Deploy
    deployment = await vercel_service.create_deployment(
        project_id=project["id"],
        files=files,
        target="production"
    )
    
    # 4. Monitor status
    while True:
        status = await vercel_service.get_deployment_status(
            deployment_id=deployment["id"]
        )
        
        if status["readyState"] == "READY":
            print(f"Deployed at: {status['url']}")
            break
        elif status["readyState"] == "ERROR":
            print("Deployment failed!")
            break
        
        await asyncio.sleep(5)
```

---

## 7. Security Considerations

### ✅ Store Tokens Securely

- Never commit tokens to git
- Use environment variables
- Consider using HashiCorp Vault

### ✅ Validate Input

- Sanitize file paths
- Validate file sizes
- Check for malicious content

### ✅ Rate Limiting

- Vercel has rate limits
- Implement retry logic
- Use exponential backoff

### ✅ Error Handling

- Handle all API errors gracefully
- Provide user-friendly messages
- Log errors for debugging

---

## 8. Advanced Features

### Connect GitHub Repo

```python
await vercel_service.connect_github(
    project_id="prj_abc123",
    repo="username/repo-name"
)
```

### Cancel Deployment

```python
await vercel_service.cancel_deployment(deployment_id="dpl_abc123")
```

### List Projects

```python
projects = await vercel_service.list_projects()
```

---

## 9. Testing

```bash
# Test the service
python -c "
from services.deployment.vercel import VercelDeployService
import asyncio

async def test():
    service = VercelDeployService()
    projects = await service.list_projects()
    print(projects)

asyncio.run(test())
"
```

---

**Ready for automatic deployments!** 🚀

