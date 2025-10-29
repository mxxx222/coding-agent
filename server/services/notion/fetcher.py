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

