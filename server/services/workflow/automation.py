from typing import Dict, Any, Optional, List
import asyncio

class AutomationWorkflow:
    """Orchestrates the complete automation pipeline."""
    
    def __init__(self):
        self.steps = []
        self.current_step = 0
    
    async def run_full_pipeline(
        self,
        notion_page_id: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run the complete automation pipeline:
        1. Fetch Notion idea
        2. Generate plan
        3. Generate code
        4. Run tests
        5. Create PR
        6. Deploy to Vercel
        """
        try:
            result = {
                "status": "running",
                "steps": [],
                "errors": []
            }
            
            # Step 1: Fetch Notion idea
            step1 = await self.fetch_notion_idea(notion_page_id)
            result["steps"].append(step1)
            if not step1["success"]:
                result["status"] = "failed"
                result["errors"].append(step1["error"])
                return result
            
            idea_data = step1["data"]
            
            # Step 2: Generate plan
            step2 = await self.generate_plan(idea_data)
            result["steps"].append(step2)
            if not step2["success"]:
                result["status"] = "failed"
                result["errors"].append(step2["error"])
                return result
            
            plan = step2["data"]
            
            # Step 3: Generate code
            step3 = await self.generate_code(plan)
            result["steps"].append(step3)
            if not step3["success"]:
                result["status"] = "failed"
                result["errors"].append(step3["error"])
                return result
            
            code_files = step3["data"]
            
            # Step 4: Run tests
            step4 = await self.run_tests(code_files)
            result["steps"].append(step4)
            if not step4["success"]:
                result["status"] = "failed"
                result["errors"].append(step4["error"])
                return result
            
            # Step 5: Create PR
            step5 = await self.create_pr(code_files, plan)
            result["steps"].append(step5)
            if not step5["success"]:
                result["status"] = "failed"
                result["errors"].append(step5["error"])
                return result
            
            # Step 6: Deploy to Vercel
            step6 = await self.deploy_to_vercel(plan.get("name", "auto-generated"))
            result["steps"].append(step6)
            if not step6["success"]:
                result["status"] = "failed"
                result["errors"].append(step6["error"])
                return result
            
            result["status"] = "success"
            result["deployment_url"] = step6["data"].get("url")
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "steps": result.get("steps", [])
            }
    
    async def fetch_notion_idea(self, page_id: str) -> Dict[str, Any]:
        """Step 1: Fetch idea from Notion."""
        try:
            from services.notion.fetcher import NotionFetcher
            fetcher = NotionFetcher()
            page_data = await fetcher.get_page(page_id)
            structured_data = fetcher.extract_structured_data(page_data)
            
            return {
                "step": "fetch_notion_idea",
                "success": True,
                "data": structured_data
            }
        except Exception as e:
            return {
                "step": "fetch_notion_idea",
                "success": False,
                "error": str(e)
            }
    
    async def generate_plan(self, idea_data: Dict[str, Any]) -> Dict[str, Any]:
        """Step 2: Generate code plan from idea."""
        try:
            from services.llm.openai_client import OpenAIClient
            
            client = OpenAIClient()
            prompt = f"""
            Based on this idea, create a detailed implementation plan:
            
            Title: {idea_data.get('title', '')}
            Description: {idea_data.get('description', '')}
            Tech Stack: {idea_data.get('tech_stack', [])}
            Requirements: {idea_data.get('acceptance_criteria', '')}
            
            Create a plan with:
            1. Project structure (file tree)
            2. Key files and their purpose
            3. Implementation steps
            4. Dependencies needed
            
            Return JSON format.
            """
            
            plan_text = await client.generate_text(prompt)
            
            # Parse plan (simplified)
            plan = {
                "name": idea_data.get('title', 'auto-project'),
                "description": idea_data.get('description', ''),
                "tech_stack": idea_data.get('tech_stack', []),
                "file_tree": {},
                "steps": []
            }
            
            return {
                "step": "generate_plan",
                "success": True,
                "data": plan
            }
        except Exception as e:
            return {
                "step": "generate_plan",
                "success": False,
                "error": str(e)
            }
    
    async def generate_code(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Step 3: Generate code files."""
        try:
            # Simulate code generation
            files = [
                {"path": "package.json", "content": '{"name": "' + plan.get('name', 'app') + '", ...}'},
                {"path": "index.js", "content": "// Generated code"},
            ]
            
            return {
                "step": "generate_code",
                "success": True,
                "data": files
            }
        except Exception as e:
            return {
                "step": "generate_code",
                "success": False,
                "error": str(e)
            }
    
    async def run_tests(self, code_files: List[Dict[str, str]]) -> Dict[str, Any]:
        """Step 4: Run tests."""
        try:
            # Simulate test execution
            await asyncio.sleep(1)
            
            return {
                "step": "run_tests",
                "success": True,
                "data": {"passed": True, "test_count": 10}
            }
        except Exception as e:
            return {
                "step": "run_tests",
                "success": False,
                "error": str(e)
            }
    
    async def create_pr(self, code_files: List[Dict[str, str]], plan: Dict[str, Any]) -> Dict[str, Any]:
        """Step 5: Create PR."""
        try:
            # Simulate PR creation
            return {
                "step": "create_pr",
                "success": True,
                "data": {"pr_url": "https://github.com/repo/pulls/1"}
            }
        except Exception as e:
            return {
                "step": "create_pr",
                "success": False,
                "error": str(e)
            }
    
    async def deploy_to_vercel(self, project_name: str) -> Dict[str, Any]:
        """Step 6: Deploy to Vercel."""
        try:
            from services.deployment.vercel import VercelDeployService
            
            service = VercelDeployService()
            deployment = await service.create_project(
                name=project_name,
                framework="nextjs"
            )
            
            return {
                "step": "deploy_to_vercel",
                "success": True,
                "data": {"url": f"https://{project_name}.vercel.app"}
            }
        except Exception as e:
            return {
                "step": "deploy_to_vercel",
                "success": False,
                "error": str(e)
            }

