from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Any
import time
import json
import os
from datetime import datetime, timedelta

class CostTrackerMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.cost_file = "data/cost_tracking.json"
        self.max_cost_per_user = float(os.getenv("MAX_COST_PER_USER", "100.00"))
        self.max_cost_per_day = float(os.getenv("MAX_COST_PER_DAY", "1000.00"))
        self.cost_tracking_enabled = os.getenv("COST_TRACKING_ENABLED", "true").lower() == "true"

    async def dispatch(self, request: Request, call_next):
        """Track costs for API requests."""
        if not self.cost_tracking_enabled:
            response = await call_next(request)
            return response

        start_time = time.time()
        
        # Get user info (simplified - in production, extract from JWT)
        user_id = self.extract_user_id(request)
        
        # Check cost limits before processing
        if not self.check_cost_limits(user_id):
            raise HTTPException(
                status_code=429,
                detail="Cost limit exceeded"
            )

        # Process request
        response = await call_next(request)
        
        # Calculate and track cost
        processing_time = time.time() - start_time
        cost = self.calculate_cost(request, processing_time)
        
        await self.record_cost(user_id, cost, request.url.path)
        
        # Add cost headers to response
        response.headers["X-Cost"] = str(cost)
        response.headers["X-Processing-Time"] = str(processing_time)
        
        return response

    def extract_user_id(self, request: Request) -> str:
        """Extract user ID from request."""
        # In production, extract from JWT token
        # For now, use IP address as a fallback
        return request.client.host

    def calculate_cost(self, request: Request, processing_time: float) -> float:
        """Calculate cost for the request."""
        base_cost = 0.001  # Base cost per request
        
        # Add cost based on processing time
        time_cost = processing_time * 0.01
        
        # Add cost based on request size
        content_length = int(request.headers.get('content-length', 0))
        size_cost = content_length * 0.000001  # 1 microcent per byte
        
        # Add cost based on endpoint complexity
        endpoint_cost = self.get_endpoint_cost(request.url.path)
        
        return base_cost + time_cost + size_cost + endpoint_cost

    def get_endpoint_cost(self, path: str) -> float:
        """Get cost multiplier based on endpoint."""
        cost_multipliers = {
            "/api/analyze/code": 0.01,
            "/api/analyze/refactor": 0.02,
            "/api/generate/test": 0.015,
            "/api/optimize/code": 0.02,
            "/api/explain/code": 0.01
        }
        
        return cost_multipliers.get(path, 0.005)

    def check_cost_limits(self, user_id: str) -> bool:
        """Check if user has exceeded cost limits."""
        try:
            cost_data = self.load_cost_data()
            
            # Check daily limit
            today = datetime.now().date()
            daily_cost = cost_data.get("daily", {}).get(str(today), 0)
            if daily_cost > self.max_cost_per_day:
                return False
            
            # Check user limit
            user_cost = cost_data.get("users", {}).get(user_id, {}).get("total", 0)
            if user_cost > self.max_cost_per_user:
                return False
            
            return True
            
        except Exception:
            return True  # Allow if cost tracking fails

    async def record_cost(self, user_id: str, cost: float, endpoint: str):
        """Record cost for user and endpoint."""
        try:
            cost_data = self.load_cost_data()
            
            # Update daily cost
            today = str(datetime.now().date())
            if "daily" not in cost_data:
                cost_data["daily"] = {}
            cost_data["daily"][today] = cost_data["daily"].get(today, 0) + cost
            
            # Update user cost
            if "users" not in cost_data:
                cost_data["users"] = {}
            if user_id not in cost_data["users"]:
                cost_data["users"][user_id] = {"total": 0, "endpoints": {}}
            
            cost_data["users"][user_id]["total"] += cost
            cost_data["users"][user_id]["endpoints"][endpoint] = cost_data["users"][user_id]["endpoints"].get(endpoint, 0) + cost
            
            # Update last activity
            cost_data["users"][user_id]["last_activity"] = datetime.now().isoformat()
            
            self.save_cost_data(cost_data)
            
        except Exception as e:
            print(f"Failed to record cost: {e}")

    def load_cost_data(self) -> Dict[str, Any]:
        """Load cost tracking data."""
        try:
            if os.path.exists(self.cost_file):
                with open(self.cost_file, 'r') as f:
                    return json.load(f)
            else:
                return {"daily": {}, "users": {}}
        except Exception:
            return {"daily": {}, "users": {}}

    def save_cost_data(self, cost_data: Dict[str, Any]):
        """Save cost tracking data."""
        try:
            os.makedirs(os.path.dirname(self.cost_file), exist_ok=True)
            with open(self.cost_file, 'w') as f:
                json.dump(cost_data, f, indent=2)
        except Exception as e:
            print(f"Failed to save cost data: {e}")

    def get_user_cost_summary(self, user_id: str) -> Dict[str, Any]:
        """Get cost summary for a user."""
        cost_data = self.load_cost_data()
        user_data = cost_data.get("users", {}).get(user_id, {})
        
        return {
            "total_cost": user_data.get("total", 0),
            "last_activity": user_data.get("last_activity"),
            "endpoints": user_data.get("endpoints", {}),
            "daily_limit": self.max_cost_per_user,
            "remaining": max(0, self.max_cost_per_user - user_data.get("total", 0))
        }