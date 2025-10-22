import openai
import os
from typing import Dict, Any, List, Optional
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

class OpenAIClient:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.organization = os.getenv("OPENAI_ORG_ID")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4")
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "4000"))
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        openai.api_key = self.api_key
        if self.organization:
            openai.organization = self.organization

    async def initialize(self):
        """Initialize the OpenAI client."""
        try:
            # Test the connection
            response = await self.test_connection()
            if response.get("success"):
                print("OpenAI client initialized successfully")
            else:
                print(f"OpenAI client initialization failed: {response.get('error')}")
        except Exception as e:
            print(f"OpenAI client initialization error: {e}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def analyze_code(self, prompt: str) -> Dict[str, Any]:
        """Analyze code using OpenAI."""
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert code analyst. Provide detailed analysis of code quality, performance, and suggestions for improvement."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return {
                "success": True,
                "analysis": response.choices[0].message.content,
                "usage": response.usage.dict() if hasattr(response, 'usage') else {}
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def explain_code(self, prompt: str) -> Dict[str, Any]:
        """Explain code using OpenAI."""
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert code explainer. Provide clear, detailed explanations of code functionality, structure, and purpose."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return {
                "success": True,
                "explanation": response.choices[0].message.content,
                "usage": response.usage.dict() if hasattr(response, 'usage') else {}
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_tests(self, prompt: str) -> Dict[str, Any]:
        """Generate tests using OpenAI."""
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert test generator. Create comprehensive, well-structured tests that cover functionality, edge cases, and error conditions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return {
                "success": True,
                "tests": response.choices[0].message.content,
                "usage": response.usage.dict() if hasattr(response, 'usage') else {}
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_code(self, prompt: str) -> Dict[str, Any]:
        """Generate code using OpenAI."""
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert code generator. Generate clean, efficient, and well-documented code that follows best practices."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return {
                "success": True,
                "code": response.choices[0].message.content,
                "usage": response.usage.dict() if hasattr(response, 'usage') else {}
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def optimize_code(self, prompt: str) -> Dict[str, Any]:
        """Optimize code using OpenAI."""
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert code optimizer. Provide optimized versions of code with improved performance, readability, and maintainability."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return {
                "success": True,
                "optimized_code": response.choices[0].message.content,
                "usage": response.usage.dict() if hasattr(response, 'usage') else {}
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def test_connection(self) -> Dict[str, Any]:
        """Test OpenAI API connection."""
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            
            return {
                "success": True,
                "message": "OpenAI API connection successful"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        # In production, you'd track this in a database
        return {
            "total_requests": 0,
            "total_tokens": 0,
            "total_cost": 0.0
        }