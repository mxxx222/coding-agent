from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio

from services.integrations.supabase import SupabaseIntegration
from services.integrations.stripe import StripeIntegration
from services.integrations.nextjs import NextJSIntegration
from services.integrations.fastapi import FastAPIIntegration
from services.integrations.prefect import PrefectIntegration
from api.middleware.auth import get_current_user

router = APIRouter()

class IntegrationRequest(BaseModel):
    service: str
    config: Dict[str, Any]
    project_path: Optional[str] = None

class IntegrationResponse(BaseModel):
    success: bool
    service: str
    files_created: List[str]
    dependencies: List[str]
    config_updated: bool
    next_steps: List[str]

class IntegrationStatus(BaseModel):
    service: str
    enabled: bool
    configured: bool
    last_used: Optional[str] = None

@router.get("/", response_model=List[IntegrationStatus])
async def get_integrations(current_user: dict = Depends(get_current_user)):
    """Get status of all available integrations."""
    try:
        integrations = []
        
        # Check each integration service
        services = [
            ("supabase", SupabaseIntegration),
            ("stripe", StripeIntegration),
            ("nextjs", NextJSIntegration),
            ("fastapi", FastAPIIntegration),
            ("prefect", PrefectIntegration)
        ]
        
        for service_name, service_class in services:
            integration = service_class()
            status = await integration.get_status()
            
            integrations.append(IntegrationStatus(
                service=service_name,
                enabled=status.get("enabled", False),
                configured=status.get("configured", False),
                last_used=status.get("last_used")
            ))
        
        return integrations
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get integrations: {str(e)}")

@router.post("/setup", response_model=IntegrationResponse)
async def setup_integration(
    request: IntegrationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Setup a new integration."""
    try:
        # Get the appropriate integration service
        integration_service = get_integration_service(request.service)
        
        if not integration_service:
            raise HTTPException(status_code=400, detail=f"Unknown service: {request.service}")
        
        # Setup the integration
        result = await integration_service.setup(
            config=request.config,
            project_path=request.project_path
        )
        
        return IntegrationResponse(
            success=result.get("success", False),
            service=request.service,
            files_created=result.get("files_created", []),
            dependencies=result.get("dependencies", []),
            config_updated=result.get("config_updated", False),
            next_steps=result.get("next_steps", [])
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Integration setup failed: {str(e)}")

@router.post("/{service}/test", response_model=dict)
async def test_integration(
    service: str,
    current_user: dict = Depends(get_current_user)
):
    """Test an integration connection."""
    try:
        integration_service = get_integration_service(service)
        
        if not integration_service:
            raise HTTPException(status_code=400, detail=f"Unknown service: {service}")
        
        # Test the integration
        test_result = await integration_service.test_connection()
        
        return {
            "success": test_result.get("success", False),
            "message": test_result.get("message", ""),
            "details": test_result.get("details", {})
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Integration test failed: {str(e)}")

@router.delete("/{service}", response_model=dict)
async def remove_integration(
    service: str,
    current_user: dict = Depends(get_current_user)
):
    """Remove an integration."""
    try:
        integration_service = get_integration_service(service)
        
        if not integration_service:
            raise HTTPException(status_code=400, detail=f"Unknown service: {service}")
        
        # Remove the integration
        result = await integration_service.remove()
        
        return {
            "success": result.get("success", False),
            "message": f"{service} integration removed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove integration: {str(e)}")

@router.get("/{service}/config", response_model=dict)
async def get_integration_config(
    service: str,
    current_user: dict = Depends(get_current_user)
):
    """Get integration configuration."""
    try:
        integration_service = get_integration_service(service)
        
        if not integration_service:
            raise HTTPException(status_code=400, detail=f"Unknown service: {service}")
        
        config = await integration_service.get_config()
        
        return {
            "service": service,
            "config": config
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get config: {str(e)}")

@router.put("/{service}/config", response_model=dict)
async def update_integration_config(
    service: str,
    config: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Update integration configuration."""
    try:
        integration_service = get_integration_service(service)
        
        if not integration_service:
            raise HTTPException(status_code=400, detail=f"Unknown service: {service}")
        
        result = await integration_service.update_config(config)
        
        return {
            "success": result.get("success", False),
            "message": f"{service} configuration updated"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update config: {str(e)}")

def get_integration_service(service: str):
    """Get the appropriate integration service class."""
    services = {
        "supabase": SupabaseIntegration,
        "stripe": StripeIntegration,
        "nextjs": NextJSIntegration,
        "fastapi": FastAPIIntegration,
        "prefect": PrefectIntegration
    }
    
    service_class = services.get(service)
    if service_class:
        return service_class()
    
    return None