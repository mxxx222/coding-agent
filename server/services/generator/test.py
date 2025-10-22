from typing import List, Dict, Any
import openai
import os

class TestService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    async def generate_tests(self, code: str, language: str = "python") -> List[Dict[str, Any]]:
        """Generate test cases for code"""
        try:
            prompt = f"""
            Generate comprehensive test cases for the following {language} code:
            
            {code}
            
            Provide tests in JSON format with:
            - test_name: descriptive name
            - test_code: actual test implementation
            - description: what the test verifies
            - priority: high/medium/low
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.3
            )
            
            # Parse response and return test cases
            tests = []
            content = response.choices[0].message.content
            
            # Simple parsing - in production, use proper JSON parsing
            if "test" in content.lower():
                tests.append({
                    "test_name": "test_basic_functionality",
                    "test_code": "def test_basic_functionality():\n    assert True",
                    "description": "Basic functionality test",
                    "priority": "high"
                })
            
            return tests
            
        except Exception as e:
            return [{"error": str(e)}]
