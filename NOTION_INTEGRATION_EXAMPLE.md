# Notion Integration - Complete Implementation Guide

## Overview

This guide shows how to implement Notion integration for fetching ideas and extracting structured requirements.

---

## 1. Setup Notion Integration

### Prerequisites

```bash
cd server
pip install notion-client
```

### Environment Variables

```bash
# .env
NOTION_API_KEY=secret_your_notion_token
NOTION_DATABASE_ID=your_database_id
```

### Get Notion API Token

1. Go to https://www.notion.so/my-integrations
2. Create new integration
3. Copy the "Internal Integration Token"
4. Share your database/page with the integration

---

## 2. Notion API Service

### `server/services/notion/fetcher.py`

```python
from notion_client import Client
from typing import Dict, List, Any, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class NotionFetcher:
    def __init__(self):
        self.client = Client(auth=os.getenv("NOTION_API_KEY"))
    
    async def get_database(self, database_id: str) -> Dict[str, Any]:
        """Fetch Notion database."""
        try:
            database = self.client.databases.retrieve(database_id=database_id)
            return database
        except Exception as e:
            print(f"Error fetching database: {e}")
            return {}
    
    async def query_database(self, database_id: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Query Notion database with filters."""
        try:
            results = self.client.databases.query(
                database_id=database_id,
                filter=filters
            )
            return results.get("results", [])
        except Exception as e:
            print(f"Error querying database: {e}")
            return []
    
    async def get_page(self, page_id: str) -> Dict[str, Any]:
        """Fetch Notion page content."""
        try:
            page = self.client.pages.retrieve(page_id=page_id)
            blocks = self.client.blocks.children.list(block_id=page_id)
            
            return {
                "page": page,
                "blocks": blocks.get("results", [])
            }
        except Exception as e:
            print(f"Error fetching page: {e}")
            return {}
    
    def extract_structured_data(self, page: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured data from Notion page."""
        page_data = page.get("page", {})
        blocks = page.get("blocks", [])
        
        # Extract properties from page
        properties = page_data.get("properties", {})
        
        # Extract text content from blocks
        text_content = []
        for block in blocks:
            block_type = block.get("type")
            if block_type == "paragraph":
                rich_text = block.get("paragraph", {}).get("rich_text", [])
                text_content.extend([t.get("plain_text") for t in rich_text])
            elif block_type == "heading_1":
                rich_text = block.get("heading_1", {}).get("rich_text", [])
                text_content.extend([t.get("plain_text") for t in rich_text])
        
        return {
            "title": self._extract_property(properties, "title", "Name"),
            "description": self._extract_property(properties, "rich_text", "Description"),
            "status": self._extract_property(properties, "select", "Status"),
            "priority": self._extract_property(properties, "select", "Priority"),
            "tech_stack": self._extract_property(properties, "multi_select", "Tech Stack"),
            "acceptance_criteria": self._extract_property(properties, "rich_text", "Acceptance Criteria"),
            "content": "\n".join(text_content),
            "created_at": page_data.get("created_time"),
            "last_edited": page_data.get("last_edited_time")
        }
    
    def _extract_property(self, properties: Dict, prop_type: str, prop_name: str) -> Any:
        """Extract property value from Notion page."""
        prop = properties.get(prop_name, {})
        if prop_type == "title" and prop.get("title"):
            return prop["title"][0].get("plain_text")
        elif prop_type == "rich_text" and prop.get("rich_text"):
            return prop["rich_text"][0].get("plain_text")
        elif prop_type == "select" and prop.get("select"):
            return prop["select"].get("name")
        elif prop_type == "multi_select" and prop.get("multi_select"):
            return [item.get("name") for item in prop["multi_select"]]
        return None
```

---

## 3. API Endpoints

### `server/api/routes/notion.py`

```python
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List
from pydantic import BaseModel
import os

from services.notion.fetcher import NotionFetcher

router = APIRouter()

# Request models
class FetchPageRequest(BaseModel):
    page_id: str

class QueryDatabaseRequest(BaseModel):
    database_id: str
    filters: Dict[str, Any] = None

# Initialize Notion fetcher
fetcher = NotionFetcher()

@router.get("/databases")
async def list_databases():
    """List available Notion databases."""
    try:
        # In production, store database IDs in config
        databases = [
            {"id": os.getenv("NOTION_DATABASE_ID"), "name": "Ideas Database"}
        ]
        return {"status": "success", "databases": databases}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/fetch-page")
async def fetch_page(request: FetchPageRequest):
    """Fetch Notion page content."""
    try:
        page_data = await fetcher.get_page(request.page_id)
        structured_data = fetcher.extract_structured_data(page_data)
        
        return {
            "status": "success",
            "page_id": request.page_id,
            "data": structured_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query-database")
async def query_database(request: QueryDatabaseRequest):
    """Query Notion database."""
    try:
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/page/{page_id}")
async def get_page(page_id: str):
    """Get Notion page by ID."""
    try:
        page_data = await fetcher.get_page(page_id)
        structured_data = fetcher.extract_structured_data(page_data)
        
        return {
            "status": "success",
            "page": structured_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 4. Integrate with FastAPI Main

### Update `server/api/main.py`

```python
from .routes import code, refactor, test, integrate, indexer, notion

# Add to routers section:
app.include_router(notion.router, prefix="/api/notion", tags=["notion"])
```

---

## 5. Usage Examples

### Fetch a single page

```bash
curl -X POST http://localhost:8000/api/notion/fetch-page \
  -H "Content-Type: application/json" \
  -d '{"page_id": "your-notion-page-id"}'
```

### Query database

```bash
curl -X POST http://localhost:8000/api/notion/query-database \
  -H "Content-Type: application/json" \
  -d '{
    "database_id": "your-database-id",
    "filters": {
      "property": "Status",
      "select": {
        "equals": "In Progress"
      }
    }
  }'
```

### Example Response

```json
{
  "status": "success",
  "data": {
    "title": "Build Todo App",
    "description": "A modern todo application with React",
    "status": "In Progress",
    "priority": "High",
    "tech_stack": ["React", "TypeScript", "Tailwind"],
    "acceptance_criteria": "User can add, edit, delete todos",
    "content": "Detailed requirements...",
    "created_at": "2025-10-22T10:00:00Z",
    "last_edited": "2025-10-22T12:00:00Z"
  }
}
```

---

## 6. Security Considerations

### ✅ Store API Keys Securely

- Use `.env` file (not committed to git)
- Use environment variables in production
- Consider using HashiCorp Vault for production

### ✅ Error Handling

- Always handle Notion API errors gracefully
- Return user-friendly error messages
- Log errors for debugging

### ✅ Rate Limiting

- Notion API has rate limits
- Implement caching for frequently accessed pages
- Use exponential backoff for retries

---

## 7. Next Steps

1. **Add LLM Extraction**: If structured data is incomplete, use LLM to extract requirements
2. **Add Caching**: Cache Notion pages to reduce API calls
3. **Add Webhooks**: Subscribe to Notion changes for real-time updates
4. **UI Integration**: Build UI to select Notion pages/projects

---

## 8. Testing

```bash
# Install dependencies
cd server
pip install notion-client python-dotenv

# Test the fetcher
python -c "
from services.notion.fetcher import NotionFetcher
import asyncio

async def test():
    fetcher = NotionFetcher()
    page = await fetcher.get_page('your-page-id')
    print(page)

asyncio.run(test())
"
```

---

**Ready to use!** 🚀

