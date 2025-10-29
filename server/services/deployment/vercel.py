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
            url += f"?teamId={self.team_id}" if "?" not in endpoint else f"&teamId={self.team_id}"
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

