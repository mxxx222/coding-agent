from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import json
import os
from typing import Dict, Any

class PolicyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, policy_file: str = None):
        super().__init__(app)
        self.policy_file = policy_file or "policies/default-policy.json"
        self.policies = self.load_policies()

    def load_policies(self) -> Dict[str, Any]:
        """Load security and safety policies."""
        try:
            if os.path.exists(self.policy_file):
                with open(self.policy_file, 'r') as f:
                    return json.load(f)
            else:
                return self.get_default_policies()
        except Exception as e:
            print(f"Warning: Could not load policies: {e}")
            return self.get_default_policies()

    def get_default_policies(self) -> Dict[str, Any]:
        """Get default security policies."""
        return {
            "security": {
                "max_request_size": 10 * 1024 * 1024,  # 10MB
                "rate_limit": {
                    "requests_per_minute": 60,
                    "burst_limit": 10
                },
                "allowed_origins": ["*"],
                "blocked_patterns": [
                    "rm -rf",
                    "sudo",
                    "chmod 777",
                    "eval(",
                    "exec(",
                    "__import__"
                ]
            },
            "content": {
                "max_code_length": 100000,  # 100KB
                "forbidden_imports": [
                    "os.system",
                    "subprocess",
                    "eval",
                    "exec"
                ],
                "allowed_languages": [
                    "python", "javascript", "typescript", 
                    "java", "go", "rust", "cpp", "c"
                ]
            },
            "cost": {
                "max_tokens_per_request": 4000,
                "max_requests_per_hour": 100,
                "cost_per_token": 0.0001
            }
        }

    async def dispatch(self, request: Request, call_next):
        """Apply security policies to requests."""
        # Check request size
        if hasattr(request, 'headers') and 'content-length' in request.headers:
            content_length = int(request.headers.get('content-length', 0))
            if content_length > self.policies["security"]["max_request_size"]:
                raise HTTPException(
                    status_code=413,
                    detail="Request too large"
                )

        # Check for blocked patterns in request body
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                body_str = body.decode('utf-8', errors='ignore')
                
                for pattern in self.policies["security"]["blocked_patterns"]:
                    if pattern in body_str:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Blocked content pattern detected: {pattern}"
                        )
            except Exception:
                pass  # Continue if body parsing fails

        # Apply rate limiting (simplified)
        client_ip = request.client.host
        # In production, you'd use Redis or similar for rate limiting
        # For now, we'll just pass through

        response = await call_next(request)
        return response

    def check_content_policy(self, content: str, content_type: str) -> bool:
        """Check if content violates policies."""
        # Check content length
        if len(content) > self.policies["content"]["max_code_length"]:
            return False

        # Check for forbidden imports
        for forbidden_import in self.policies["content"]["forbidden_imports"]:
            if forbidden_import in content:
                return False

        return True

    def get_cost_estimate(self, content: str) -> float:
        """Estimate cost based on content length."""
        token_count = len(content.split()) * 1.3  # Rough token estimation
        return token_count * self.policies["cost"]["cost_per_token"]