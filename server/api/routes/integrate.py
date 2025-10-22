from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

from services.integrations.supabase import setup_supabase
from services.integrations.stripe import setup_stripe
from services.integrations.nextjs import setup_nextjs
from services.integrations.fastapi import setup_fastapi
from services.integrations.prefect import setup_prefect

router = APIRouter()

class IntegrationRequest(BaseModel):
    services: List[str]

@router.post("/integrate")
async def integrate_services(req: IntegrationRequest):
    results = {}
    try:
        for svc in req.services:
            match svc.lower():
                case 'supabase':
                    results['supabase'] = await setup_supabase()
                case 'stripe':
                    results['stripe'] = await setup_stripe()
                case 'nextjs':
                    results['nextjs'] = await setup_nextjs()
                case 'fastapi':
                    results['fastapi'] = await setup_fastapi()
                case 'prefect':
                    results['prefect'] = await setup_prefect()
                case _:
                    results[svc] = {'status': 'skipped', 'reason': 'unknown'}
        return {"status": "ok", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
