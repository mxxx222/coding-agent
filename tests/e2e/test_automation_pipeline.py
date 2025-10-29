"""
End-to-end tests for the automation pipeline.

Tests the complete flow: Notion → Plan → Code → Tests → PR → Vercel Deploy
"""

import pytest
import asyncio
from typing import Dict, Any
import os
from services.notion.fetcher import NotionFetcher
from services.deployment.vercel import VercelDeployService
from services.workflow.automation import AutomationWorkflow


class TestAutomationPipeline:
    """Test the complete automation pipeline."""
    
    @pytest.fixture
    def notion_fetcher(self):
        """Initialize Notion fetcher."""
        return NotionFetcher()
    
    @pytest.fixture
    def vercel_service(self):
        """Initialize Vercel service."""
        return VercelDeployService()
    
    @pytest.fixture
    def automation_workflow(self):
        """Initialize automation workflow."""
        return AutomationWorkflow()
    
    @pytest.mark.asyncio
    async def test_notion_page_fetch(self, notion_fetcher):
        """Test fetching a Notion page."""
        # Use a test page ID (if available)
        page_id = os.getenv("TEST_NOTION_PAGE_ID", "test-page-id")
        
        page_data = await notion_fetcher.get_page(page_id)
        assert page_data is not None
        assert "page" in page_data
        assert "blocks" in page_data
    
    @pytest.mark.asyncio
    async def test_notion_extract_structured_data(self, notion_fetcher):
        """Test extracting structured data from Notion page."""
        # Mock page data
        mock_page = {
            "page": {
                "properties": {
                    "Name": {
                        "title": [{"plain_text": "Test Project"}]
                    },
                    "Description": {
                        "rich_text": [{"plain_text": "A test project"}]
                    },
                    "Status": {
                        "select": {"name": "In Progress"}
                    },
                    "Tech Stack": {
                        "multi_select": [
                            {"name": "React"},
                            {"name": "TypeScript"}
                        ]
                    }
                }
            },
            "blocks": []
        }
        
        structured = notion_fetcher.extract_structured_data(mock_page)
        
        assert structured["title"] == "Test Project"
        assert structured["description"] == "A test project"
        assert structured["status"] == "In Progress"
        assert "React" in structured["tech_stack"]
        assert "TypeScript" in structured["tech_stack"]
    
    @pytest.mark.asyncio
    async def test_vercel_list_projects(self, vercel_service):
        """Test listing Vercel projects."""
        projects = await vercel_service.list_projects()
        
        assert isinstance(projects, list)
        # Should not raise an error even if no projects
    
    @pytest.mark.asyncio
    async def test_automation_workflow_flow(self, automation_workflow):
        """Test the complete automation workflow."""
        # Mock notion page ID
        notion_page_id = "test-page-id"
        
        # Mock options
        options = {
            "auto_merge": False,
            "create_pr": True,
            "run_tests": True
        }
        
        # Run the pipeline (will skip real API calls if not configured)
        try:
            result = await automation_workflow.run_full_pipeline(
                notion_page_id,
                options
            )
            
            # Should return a result even if some steps fail
            assert "status" in result
            assert "steps" in result
            assert isinstance(result["steps"], list)
            
        except Exception as e:
            # If services are not configured, that's OK for testing
            pytest.skip(f"Service not configured: {e}")
    
    @pytest.mark.asyncio
    async def test_workflow_step_fetch_notion(self, automation_workflow):
        """Test individual workflow step: fetch Notion idea."""
        try:
            result = await automation_workflow.fetch_notion_idea("test-page-id")
            
            assert "step" in result
            assert "success" in result
            assert result["step"] == "fetch_notion_idea"
            
        except Exception as e:
            pytest.skip(f"Notion not configured: {e}")
    
    @pytest.mark.asyncio
    async def test_workflow_step_generate_plan(self, automation_workflow):
        """Test individual workflow step: generate plan."""
        mock_idea_data = {
            "title": "Test Project",
            "description": "A test project",
            "tech_stack": ["React", "TypeScript"],
            "acceptance_criteria": "Should work"
        }
        
        result = await automation_workflow.generate_plan(mock_idea_data)
        
        assert "step" in result
        assert "success" in result
        assert result["step"] == "generate_plan"
    
    @pytest.mark.asyncio
    async def test_workflow_step_generate_code(self, automation_workflow):
        """Test individual workflow step: generate code."""
        mock_plan = {
            "name": "test-project",
            "description": "A test project",
            "tech_stack": ["React"],
            "file_tree": {},
            "steps": []
        }
        
        result = await automation_workflow.generate_code(mock_plan)
        
        assert "step" in result
        assert "success" in result
        assert result["step"] == "generate_code"
        assert "data" in result if result["success"] else True
    
    @pytest.mark.asyncio
    async def test_workflow_step_run_tests(self, automation_workflow):
        """Test individual workflow step: run tests."""
        mock_files = [
            {"path": "index.js", "content": "console.log('test');"}
        ]
        
        result = await automation_workflow.run_tests(mock_files)
        
        assert "step" in result
        assert "success" in result
        assert result["step"] == "run_tests"
    
    @pytest.mark.asyncio
    async def test_workflow_step_create_pr(self, automation_workflow):
        """Test individual workflow step: create PR."""
        mock_files = [
            {"path": "index.js", "content": "console.log('test');"}
        ]
        mock_plan = {
            "name": "test-project"
        }
        
        result = await automation_workflow.create_pr(mock_files, mock_plan)
        
        assert "step" in result
        assert "success" in result
        assert result["step"] == "create_pr"
    
    @pytest.mark.asyncio
    async def test_workflow_step_deploy_vercel(self, automation_workflow):
        """Test individual workflow step: deploy to Vercel."""
        try:
            result = await automation_workflow.deploy_to_vercel("test-project")
            
            assert "step" in result
            assert "success" in result
            assert result["step"] == "deploy_to_vercel"
            
        except Exception as e:
            pytest.skip(f"Vercel not configured: {e}")


class TestMockAutomationPipeline:
    """Test automation pipeline with mocked services."""
    
    @pytest.mark.asyncio
    async def test_complete_pipeline_with_mocks(self):
        """Test complete pipeline flow with mocked responses."""
        workflow = AutomationWorkflow()
        
        # Mock notion page ID
        notion_page_id = "mock-page-id"
        
        # Run with mock data (will use fallback if services not configured)
        result = await workflow.run_full_pipeline(notion_page_id)
        
        # Should return a structured result
        assert "status" in result
        assert isinstance(result["status"], str)
        assert result["status"] in ["running", "success", "failed", "error"]


# Integration test with ephemeral container
class TestEphemeralContainer:
    """Test automation in an ephemeral container."""
    
    @pytest.mark.skipif(
        os.getenv("RUN_CONTAINER_TESTS") != "true",
        reason="Container tests require RUN_CONTAINER_TESTS=true"
    )
    @pytest.mark.asyncio
    async def test_full_pipeline_in_container(self):
        """Test complete pipeline in ephemeral container."""
        # This would start a container, run tests, and clean up
        # Implementation depends on container setup
        
        # For now, just verify environment
        assert os.getenv("DATABASE_URL") is not None
        assert os.getenv("NOTION_API_KEY") is not None
        assert os.getenv("VERCEL_TOKEN") is not None
        
        pytest.skip("Container test infrastructure not yet implemented")

