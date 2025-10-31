from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import json
import os
import time
import re
from collections import defaultdict
from typing import Dict, Any, List, Callable, Optional

class PolicyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, policy_file: str = None, route_configs: Dict[str, Dict] = None):
        super().__init__(app)
        self.policy_file = policy_file or "policies/default-policy.json"
        self.policies = self.load_policies()
        self.route_configs = route_configs or {}
        self.rate_limit_store = defaultdict(list)  # In-memory rate limiting
        self.custom_rules: List[Callable[[Request], None]] = []

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
                ],
                "access_control": {
                    "require_auth": False,
                    "allowed_roles": [],
                    "ip_whitelist": [],
                    "ip_blacklist": []
                }
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
                ],
                "validation_rules": {
                    "require_syntax_check": True,
                    "max_function_complexity": 10,
                    "forbidden_keywords": ["debugger", "console.log"]
                }
            },
            "cost": {
                "max_tokens_per_request": 4000,
                "max_requests_per_hour": 100,
                "cost_per_token": 0.0001
            },
            "business_rules": {
                "max_concurrent_requests": 5,
                "time_window_restrictions": {
                    "maintenance_hours": [],
                    "peak_hours_multiplier": 1.0
                },
                "custom_validations": []
            }
        }

    async def dispatch(self, request: Request, call_next):
        """Apply comprehensive security policies to requests."""
        route_path = f"{request.method}:{request.url.path}"
        route_config = self.route_configs.get(route_path, {})

        # Get effective policies (route-specific or global)
        effective_policies = self._merge_policies(route_config)

        # Access control checks
        await self._check_access_control(request, effective_policies)

        # Rate limiting
        await self._check_rate_limit(request, effective_policies)

        # Request size validation
        await self._check_request_size(request, effective_policies)

        # Content validation for POST/PUT/PATCH
        if request.method in ["POST", "PUT", "PATCH"]:
            await self._check_content_validation(request, effective_policies)

        # Business rules validation
        await self._check_business_rules(request, effective_policies)

        # Apply custom rules
        for rule in self.custom_rules:
            rule(request)

        response = await call_next(request)
        return response

    def _merge_policies(self, route_config: Dict) -> Dict[str, Any]:
        """Merge global policies with route-specific overrides."""
        merged = self.policies.copy()
        for category, rules in route_config.items():
            if category in merged:
                merged[category].update(rules)
            else:
                merged[category] = rules
        return merged

    async def _check_access_control(self, request: Request, policies: Dict):
        """Check access control policies."""
        access_config = policies.get("security", {}).get("access_control", {})

        # IP-based access control
        client_ip = request.client.host if request.client else None
        if client_ip:
            if client_ip in access_config.get("ip_blacklist", []):
                raise HTTPException(status_code=403, detail="IP address blocked")
            if access_config.get("ip_whitelist") and client_ip not in access_config["ip_whitelist"]:
                raise HTTPException(status_code=403, detail="IP address not allowed")

        # Role-based access control (placeholder - integrate with auth system)
        if access_config.get("require_auth"):
            # This would integrate with your authentication system
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                raise HTTPException(status_code=401, detail="Authentication required")

    async def _check_rate_limit(self, request: Request, policies: Dict):
        """Apply rate limiting."""
        rate_config = policies.get("security", {}).get("rate_limit", {})
        client_ip = request.client.host if request.client else "unknown"

        current_time = time.time()
        window_start = current_time - 60  # 1 minute window

        # Clean old requests
        self.rate_limit_store[client_ip] = [
            req_time for req_time in self.rate_limit_store[client_ip]
            if req_time > window_start
        ]

        # Check rate limit
        if len(self.rate_limit_store[client_ip]) >= rate_config.get("requests_per_minute", 60):
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        # Add current request
        self.rate_limit_store[client_ip].append(current_time)

    async def _check_request_size(self, request: Request, policies: Dict):
        """Check request size limits."""
        max_size = policies.get("security", {}).get("max_request_size", 10 * 1024 * 1024)
        if hasattr(request, 'headers') and 'content-length' in request.headers:
            content_length = int(request.headers.get('content-length', 0))
            if content_length > max_size:
                raise HTTPException(status_code=413, detail="Request too large")

    async def _check_content_validation(self, request: Request, policies: Dict):
        """Validate request content."""
        try:
            body = await request.body()
            body_str = body.decode('utf-8', errors='ignore')

            # Check blocked patterns
            blocked_patterns = policies.get("security", {}).get("blocked_patterns", [])
            for pattern in blocked_patterns:
                if pattern in body_str:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Blocked content pattern detected: {pattern}"
                    )

            # Content validation rules
            content_config = policies.get("content", {})
            if len(body_str) > content_config.get("max_code_length", 100000):
                raise HTTPException(status_code=413, detail="Content too large")

            # Check forbidden imports
            for forbidden_import in content_config.get("forbidden_imports", []):
                if forbidden_import in body_str:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Forbidden import detected: {forbidden_import}"
                    )

            # Syntax and complexity checks (basic)
            if content_config.get("validation_rules", {}).get("require_syntax_check"):
                await self._validate_syntax(body_str, request.headers.get("content-type", ""))

        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="Invalid request encoding")

    async def _check_business_rules(self, request: Request, policies: Dict):
        """Apply business rules."""
        business_config = policies.get("business_rules", {})

        # Time window restrictions
        current_hour = time.gmtime().tm_hour
        maintenance_hours = business_config.get("time_window_restrictions", {}).get("maintenance_hours", [])
        if current_hour in maintenance_hours:
            raise HTTPException(status_code=503, detail="Service under maintenance")

        # Custom validations
        for validation in business_config.get("custom_validations", []):
            if not self._run_custom_validation(validation, request):
                raise HTTPException(status_code=400, detail=f"Business rule violation: {validation}")

    async def _validate_syntax(self, content: str, content_type: str):
        """Basic syntax validation."""
        # This is a placeholder - in production, you'd integrate with language-specific linters
        if "python" in content_type.lower():
            try:
                compile(content, '<string>', 'exec')
            except SyntaxError as e:
                raise HTTPException(status_code=400, detail=f"Syntax error: {str(e)}")

    def _run_custom_validation(self, validation_rule: str, request: Request) -> bool:
        """Run custom validation rule."""
        # Placeholder for custom business logic
        # In production, this could integrate with a rules engine
        return True

    def add_custom_rule(self, rule: Callable[[Request], None]):
        """Add a custom validation rule."""
        self.custom_rules.append(rule)

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