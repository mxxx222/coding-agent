from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import os

router = APIRouter()

# Request models
class FetchPageRequest(BaseModel):
    page_id: str

class QueryDatabaseRequest(BaseModel):
    database_id: str
    filters: Optional[Dict[str, Any]] = None

# Import the fetcher service
try:
    from services.notion.fetcher import NotionFetcher
    fetcher = NotionFetcher()
    NOTION_ENABLED = True
except ImportError:
    fetcher = None
    NOTION_ENABLED = False

@router.get("/health")
async def health_check():
    """Check Notion integration health."""
    return {
        "status": "enabled" if NOTION_ENABLED else "disabled",
        "notion_enabled": NOTION_ENABLED
    }

@router.get("/databases")
async def list_databases():
    """List available Notion databases."""
    try:
        if not NOTION_ENABLED:
            return {
                "status": "disabled",
                "message": "Notion integration not configured. Install notion-client: pip install notion-client"
            }
        
        # In production, store database IDs in config
        databases = [
            {"id": os.getenv("NOTION_DATABASE_ID", ""), "name": "Ideas Database"}
        ]
        return {"status": "success", "databases": databases}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/fetch-page")
async def fetch_page(request: FetchPageRequest):
    """Fetch Notion page content."""
    try:
        if not NOTION_ENABLED:
            raise HTTPException(status_code=503, detail="Notion integration not configured")
        
        page_data = await fetcher.get_page(request.page_id)
        structured_data = fetcher.extract_structured_data(page_data)
        
        return {
            "status": "success",
            "page_id": request.page_id,
            "data": structured_data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query-database")
async def query_database(request: QueryDatabaseRequest):
    """Query Notion database."""
    try:
        if not NOTION_ENABLED:
            raise HTTPException(status_code=503, detail="Notion integration not configured")
        
        results = await fetcher.query_database(
            database_id=request.database_id,
            filters=request.filters
        )
        
        pages = []
        for result in results:
            structured = fetcher.extract_structured_data({"page": result, "blocks": []})
            pages.append({
                "id": result.get("id"),
                "data": structured
            })
        
        return {
            "status": "success",
            "database_id": request.database_id,
            "pages": pages
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/page/{page_id}")
async def get_page(page_id: str):
    """Get Notion page by ID."""
    try:
        if not NOTION_ENABLED:
            raise HTTPException(status_code=503, detail="Notion integration not configured")
        
        page_data = await fetcher.get_page(page_id)
        structured_data = fetcher.extract_structured_data(page_data)
        
        return {
            "status": "success",
            "page": structured_data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

