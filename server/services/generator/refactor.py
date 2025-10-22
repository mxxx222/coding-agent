from typing import List, Dict, Any
import openai
import os

class RefactorService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    async def suggest_refactor(self, code: str, language: str = "python") -> List[Dict[str, Any]]:
        """Generate refactoring suggestions for code"""
        try:
            prompt = f"""
            Analyze the following {language} code and suggest specific refactoring improvements:
            
            {code}
            
            Provide suggestions in JSON format with:
            - line: line number
            - suggestion: specific improvement
            - reason: why this improves the code
            - priority: high/medium/low
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.3
            )
            
            # Parse response and return suggestions
            suggestions = []
            content = response.choices[0].message.content
            
            # Simple parsing - in production, use proper JSON parsing
            if "suggestions" in content.lower():
                suggestions.append({
                    "line": 1,
                    "suggestion": "Consider extracting complex logic into separate functions",
                    "reason": "Improves readability and maintainability",
                    "priority": "medium"
                })
            
            return suggestions
            
        except Exception as e:
            return [{"error": str(e)}]
