"""
API endpoints for prompt template management.
"""

from fastapi import APIRouter, HTTPException, Body
from typing import List, Dict, Any, Optional
from services.prompts.template import TemplateStore, PromptTemplate
from services.prompts.ab_testing import ABTestManager, ABTest

router = APIRouter()

# Initialize stores
template_store = TemplateStore()
ab_test_manager = ABTestManager()

# Request models
class CreateTemplateRequest:
    name: str
    description: str
    category: str
    template: str
    input_schema: Dict[str, Any]
    examples: Optional[List[Dict[str, Any]]] = None

class CreateTestRequest:
    name: str
    description: str
    template_ids: List[str]
    traffic_allocation: Optional[List[float]] = None


@router.get("/templates")
async def list_templates(
    category: Optional[str] = None,
    tags: Optional[str] = None,
    min_quality: float = 0.0,
    limit: int = 50
):
    """List available templates."""
    tags_list = tags.split(",") if tags else None
    
    templates = template_store.search_templates(
        category=category,
        tags=tags_list,
        min_quality=min_quality
    )
    
    return {
        "status": "success",
        "count": len(templates),
        "templates": [t.to_dict() for t in templates[:limit]]
    }


@router.get("/templates/top")
async def get_top_templates(limit: int = 10):
    """Get top templates by quality score."""
    templates = template_store.get_top_templates(limit=limit)
    
    return {
        "status": "success",
        "templates": [t.to_dict() for t in templates]
    }


@router.get("/templates/{template_id}")
async def get_template(template_id: str):
    """Get a specific template."""
    template = template_store.get_template(template_id)
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return {
        "status": "success",
        "template": template.to_dict()
    }


@router.post("/templates")
async def create_template(request: CreateTemplateRequest):
    """Create a new template."""
    template = template_store.create_template(
        name=request.name,
        description=request.description,
        category=request.category,
        template=request.template,
        input_schema=request.input_schema,
        examples=request.examples
    )
    
    return {
        "status": "success",
        "template": template.to_dict()
    }


@router.post("/templates/{template_id}/render")
async def render_template(
    template_id: str,
    variables: Dict[str, Any] = Body(...)
):
    """Render a template with variables."""
    template = template_store.get_template(template_id)
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    try:
        rendered = template.render(**variables)
        
        # Update metrics
        template_store.update_metrics(template_id, True)
        
        return {
            "status": "success",
            "rendered": rendered
        }
    except Exception as e:
        template_store.update_metrics(template_id, False)
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tests")
async def list_tests():
    """List all A/B tests."""
    return {
        "status": "success",
        "tests": [test.to_dict() for test in ab_test_manager.tests.values()]
    }


@router.post("/tests")
async def create_test(request: CreateTestRequest):
    """Create a new A/B test."""
    test = ab_test_manager.create_test(
        name=request.name,
        description=request.description,
        template_ids=request.template_ids,
        traffic_allocation=request.traffic_allocation
    )
    
    return {
        "status": "success",
        "test": test.to_dict()
    }


@router.post("/tests/{test_id}/start")
async def start_test(test_id: str):
    """Start an A/B test."""
    ab_test_manager.start_test(test_id)
    
    return {
        "status": "success",
        "message": "Test started"
    }


@router.get("/tests/{test_id}/select")
async def select_variant(test_id: str):
    """Select a variant for testing."""
    variant_id = ab_test_manager.select_template_for_test(test_id)
    
    if not variant_id:
        raise HTTPException(status_code=404, detail="Test not found or not running")
    
    return {
        "status": "success",
        "variant_id": variant_id
    }


@router.post("/tests/{test_id}/result")
async def record_result(
    test_id: str,
    variant_id: str,
    success: bool
):
    """Record a test result."""
    ab_test_manager.record_test_result(test_id, variant_id, success)
    
    return {
        "status": "success",
        "message": "Result recorded"
    }

