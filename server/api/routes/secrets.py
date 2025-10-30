"""
API endpoints for secret management.
"""

from fastapi import APIRouter, HTTPException, Body, Header
from typing import Optional, Dict, Any
from services.secrets.manager import SecretManager
from services.secrets.rotate import RotationManager
from pydantic import BaseModel

router = APIRouter()

# Initialize managers
secret_manager = SecretManager()
rotation_manager = RotationManager(secret_manager)

# Request models
class CreateSecretRequest(BaseModel):
    name: str
    value: str
    secret_type: str = "api_key"
    service: str
    rotation_policy: Optional[str] = "30_days"
    expires_in_days: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


@router.get("/secrets")
async def list_secrets(
    service: Optional[str] = None,
    show_expired: bool = False
):
    """List all secrets (metadata only)."""
    secrets = secret_manager.list_secrets(service=service)
    
    # Filter expired if requested
    if not show_expired:
        secrets = [s for s in secrets if not s.get("expires_at") or s["expires_at"] > datetime.now().isoformat()]
    
    return {
        "status": "success",
        "count": len(secrets),
        "secrets": secrets
    }


@router.get("/secrets/{secret_id}")
async def get_secret_metadata(secret_id: str):
    """Get secret metadata (not the actual value)."""
    secret = secret_manager.secrets_storage.get(secret_id)
    
    if not secret:
        raise HTTPException(status_code=404, detail="Secret not found")
    
    # Return metadata only
    secret_dict = secret.to_dict()
    secret_dict["value"] = "***HIDDEN***"
    
    return {
        "status": "success",
        "secret": secret_dict
    }


@router.post("/secrets")
async def create_secret(request: CreateSecretRequest):
    """Create a new secret."""
    secret = secret_manager.create_secret(
        name=request.name,
        value=request.value,
        secret_type=request.secret_type,
        service=request.service,
        rotation_policy=request.rotation_policy,
        expires_in_days=request.expires_in_days,
        metadata=request.metadata
    )
    
    # Return metadata only
    secret_dict = secret.to_dict()
    secret_dict["value"] = "***HIDDEN***"
    
    return {
        "status": "success",
        "message": "Secret created successfully",
        "secret": secret_dict
    }


@router.post("/secrets/{secret_id}/retrieve")
async def retrieve_secret_value(secret_id: str, reason: str = Header(None)):
    """Retrieve the actual secret value (requires reason)."""
    if not reason:
        raise HTTPException(status_code=400, detail="Reason required for secret retrieval")
    
    secret = secret_manager.get_secret(secret_id, decrypt=True)
    
    if not secret:
        raise HTTPException(status_code=404, detail="Secret not found")
    
    # Check if expired
    if secret.expires_at and secret.expires_at < datetime.now():
        return {
            "status": "expired",
            "message": "Secret has expired and needs rotation",
            "secret": {
                "id": secret.id,
                "name": secret.name,
                "service": secret.service,
                "value": secret.value
            }
        }
    
    return {
        "status": "success",
        "secret": {
            "id": secret.id,
            "name": secret.name,
            "service": secret.service,
            "value": secret.value
        }
    }


@router.post("/secrets/{secret_id}/rotate")
async def rotate_secret(
    secret_id: str,
    new_value: Optional[str] = None
):
    """Rotate a secret."""
    try:
        secret = secret_manager.rotate_secret(secret_id, new_value)
        
        return {
            "status": "success",
            "message": "Secret rotated successfully",
            "secret": {
                "id": secret.id,
                "name": secret.name,
                "service": secret.service,
                "new_value": secret.value,
                "rotated_at": secret.last_rotated.isoformat()
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/secrets/rotate-all")
async def rotate_expired_secrets():
    """Automatically rotate all expired secrets."""
    results = rotation_manager.check_and_rotate_all()
    
    return {
        "status": "success",
        "summary": results
    }


@router.get("/secrets/rotation-schedule")
async def get_rotation_schedule():
    """Get upcoming rotation schedule."""
    schedule = rotation_manager.get_rotation_schedule()
    
    return {
        "status": "success",
        "schedule": schedule
    }


@router.get("/secrets/expired")
async def get_expired_secrets():
    """Get list of expired secrets."""
    expired = secret_manager.check_expired_secrets()
    
    return {
        "status": "success",
        "count": len(expired),
        "secrets": [s.to_dict() for s in expired]
    }


@router.delete("/secrets/{secret_id}")
async def delete_secret(secret_id: str):
    """Delete a secret."""
    success = secret_manager.delete_secret(secret_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Secret not found")
    
    return {
        "status": "success",
        "message": "Secret deleted successfully"
    }


@router.post("/secrets/{secret_id}/test")
async def test_secret(secret_id: str):
    """Test if a secret works with its service."""
    secret = secret_manager.get_secret(secret_id, decrypt=True)
    
    if not secret:
        raise HTTPException(status_code=404, detail="Secret not found")
    
    from services.secrets.rotate import ServiceIntegration
    
    is_valid = ServiceIntegration.test_connection(secret.service, secret.value)
    
    return {
        "status": "success",
        "is_valid": is_valid,
        "service": secret.service
    }

