"""
API endpoints for secret management.
"""

from fastapi import APIRouter, HTTPException, Body, Header, Request
from typing import Optional, Dict, Any
from datetime import datetime
from services.secrets.manager import SecretManager
from services.secrets.rotate import RotationManager
from pydantic import BaseModel
import os
from services.secrets.providers import create_provider
from services.secrets.presets import ProviderPresetsStore
from services.secrets.bundles import export_bundle, import_bundle
from services.audit.events import AuditEvents

router = APIRouter()

# Initialize managers
secret_manager = SecretManager()
rotation_manager = RotationManager(secret_manager)
presets_store = ProviderPresetsStore()
auditor = AuditEvents()

# Request models
class CreateSecretRequest(BaseModel):
    name: str
    value: str
    secret_type: str = "api_key"
    service: str
    rotation_policy: Optional[str] = "30_days"
    expires_in_days: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class ProviderConfigRequest(BaseModel):
    provider: str
    config: Dict[str, Any]


class SyncRequest(BaseModel):
    provider: str
    action: str  # push | pull
    prefix: Optional[str] = None


def _require_admin(request: Request):
    admin_token = os.getenv("ADMIN_TOKEN")
    if not admin_token:
        return
    supplied = request.headers.get("X-Admin-Token")
    if supplied != admin_token:
        raise HTTPException(status_code=403, detail="Admin token required")


def _require_role(request: Request, role: str):
    """Simple RBAC via env tokens. Roles: admin, readonly.
    - admin: ADMIN_TOKEN
    - readonly: READ_TOKEN (falls back to open if not set)
    """
    if role == "admin":
        return _require_admin(request)
    if role == "readonly":
        read_token = os.getenv("READ_TOKEN")
        if not read_token:
            return
        supplied = request.headers.get("X-Read-Token")
        if supplied != read_token:
            raise HTTPException(status_code=403, detail="Read token required")
    return


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
async def retrieve_secret_value(request: Request, secret_id: str, reason: str = Header(None)):
    """Retrieve the actual secret value (requires reason)."""
    _require_admin(request)
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
    
    auditor.emit("secret.retrieve", actor=request.client.host if request.client else "unknown", payload={"secret_id": secret.id, "reason": reason})
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
    request: Request,
    secret_id: str,
    new_value: Optional[str] = None
):
    """Rotate a secret."""
    _require_admin(request)
    try:
        secret = secret_manager.rotate_secret(secret_id, new_value)
        auditor.emit("secret.rotate", actor=request.client.host if request.client else "unknown", payload={"secret_id": secret.id})
        
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
async def rotate_expired_secrets(request: Request):
    """Automatically rotate all expired secrets."""
    _require_admin(request)
    results = rotation_manager.check_and_rotate_all()
    auditor.emit("secret.rotate_all", actor=request.client.host if request.client else "unknown", payload={"summary": results})
    
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
async def get_expired_secrets(request: Request):
    """Get list of expired secrets."""
    _require_admin(request)
    expired = secret_manager.check_expired_secrets()
    
    return {
        "status": "success",
        "count": len(expired),
        "secrets": [s.to_dict() for s in expired]
    }


@router.delete("/secrets/{secret_id}")
async def delete_secret(request: Request, secret_id: str):
    """Delete a secret."""
    _require_admin(request)
    success = secret_manager.delete_secret(secret_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Secret not found")
    
    auditor.emit("secret.delete", actor=request.client.host if request.client else "unknown", payload={"secret_id": secret_id, "success": success})
    return {
        "status": "success",
        "message": "Secret deleted successfully"
    }


@router.post("/secrets/{secret_id}/test")
async def test_secret(request: Request, secret_id: str):
    """Test if a secret works with its service."""
    _require_admin(request)
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


@router.post("/secrets/providers/test")
async def test_provider(request: Request, req: ProviderConfigRequest):
    _require_admin(request)
    provider = create_provider(req.provider, req.config)
    healthy = provider.healthy()
    auditor.emit("provider.test", actor=request.client.host if request.client else "unknown", payload={"provider": req.provider, "healthy": healthy})
    return {"status": "success", "healthy": healthy, "provider": req.provider}


@router.post("/secrets/sync")
async def sync_secrets(request: Request, req: SyncRequest):
    _require_admin(request)
    provider = create_provider(req.provider)
    if req.action not in ("push", "pull"):
        raise HTTPException(status_code=400, detail="Invalid action; use 'push' or 'pull'")

    prefix = (req.prefix or "").rstrip("/")

    if req.action == "push":
        pushed = 0
        for s in list(secret_manager.secrets_storage.values()):
            key = f"{prefix}/{s.service}/{s.name}" if prefix else f"{s.service}/{s.name}"
            dec = secret_manager.get_secret(s.id, decrypt=True)
            if not dec:
                continue
            if provider.put(key, dec.value):
                pushed += 1
        auditor.emit("provider.sync.push", actor=request.client.host if request.client else "unknown", payload={"provider": req.provider, "pushed": pushed})
        return {"status": "success", "provider": req.provider, "action": req.action, "pushed": pushed}

    # pull
    pulled = 0
    keys = provider.list(prefix=prefix)
    for key in keys:
        # expected pattern: <prefix>/service/name or service/name
        path = key[len(prefix)+1:] if prefix and key.startswith(prefix + "/") else key
        parts = path.split("/", 1)
        if len(parts) != 2:
            continue
        service, name = parts
        value = provider.get(key)
        if not value:
            continue
        # create or update
        existing = secret_manager.get_secret_by_name(name, service)
        if existing:
            secret_manager.rotate_secret(existing.id, value)
        else:
            secret_manager.create_secret(name=name, value=value, secret_type="api_key", service=service)
        pulled += 1

    auditor.emit("provider.sync.pull", actor=request.client.host if request.client else "unknown", payload={"provider": req.provider, "pulled": pulled})
    return {"status": "success", "provider": req.provider, "action": req.action, "pulled": pulled}


class ExportRequest(BaseModel):
    secret_ids: Optional[List[str]] = None
    include_services: Optional[List[str]] = None
    passphrase: str


@router.post("/secrets/export")
async def export_secrets(request: Request, body: ExportRequest):
    _require_role(request, "admin")
    # Collect items to export (decrypt values)
    items = []
    for s in list(secret_manager.secrets_storage.values()):
        if body.secret_ids and s.id not in body.secret_ids:
            continue
        if body.include_services and s.service not in body.include_services:
            continue
        dec = secret_manager.get_secret(s.id, decrypt=True)
        if not dec:
            continue
        items.append({
            "id": dec.id,
            "name": dec.name,
            "service": dec.service,
            "secret_type": dec.secret_type,
            "value": dec.value,
            "metadata": dec.metadata or {}
        })
    bundle = export_bundle(items, body.passphrase)
    auditor.emit("secrets.export", actor=request.client.host if request.client else "unknown", payload={"count": len(items)})
    return {"status": "success", "bundle": bundle}


class ImportRequest(BaseModel):
    bundle: Dict[str, Any]
    passphrase: str
    overwrite: bool = True


@router.post("/secrets/import")
async def import_secrets(request: Request, body: ImportRequest):
    _require_role(request, "admin")
    payload = import_bundle(body.bundle, body.passphrase)
    imported = 0
    for item in payload.get("items", []):
        existing = secret_manager.get_secret_by_name(item.get("name"), item.get("service"))
        if existing and not body.overwrite:
            continue
        if existing:
            secret_manager.rotate_secret(existing.id, item.get("value"))
        else:
            secret_manager.create_secret(
                name=item.get("name"),
                value=item.get("value"),
                secret_type=item.get("secret_type", "api_key"),
                service=item.get("service"),
                metadata=item.get("metadata") or {}
            )
        imported += 1
    auditor.emit("secrets.import", actor=request.client.host if request.client else "unknown", payload={"count": imported})
    return {"status": "success", "imported": imported}


class PresetUpsert(BaseModel):
    name: str
    provider: str
    config: Dict[str, Any]


@router.get("/secrets/providers/presets")
async def list_presets():
    return {"status": "success", "presets": presets_store.list()}


@router.post("/secrets/providers/presets")
async def upsert_preset(request: Request, body: PresetUpsert):
    _require_role(request, "admin")
    item = presets_store.upsert(body.name, body.provider, body.config)
    return {"status": "success", "preset": item}


@router.delete("/secrets/providers/presets/{name}")
async def delete_preset(request: Request, name: str):
    _require_role(request, "admin")
    ok = presets_store.delete(name)
    if not ok:
        raise HTTPException(status_code=404, detail="Preset not found")
    return {"status": "success"}

