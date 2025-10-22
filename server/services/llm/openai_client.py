import os
import httpx

class OpenAIClient:
    async def initialize(self):
        self.api_key = os.getenv('OPENAI_API_KEY', 'test')

    async def analyze_code(self, prompt: str):
        # Stubbed response
        return {"summary": "analysis stub", "prompt_tokens": len(prompt)}

    async def explain_code(self, prompt: str):
        return {"explanation": "explanation stub", "prompt_tokens": len(prompt)}
