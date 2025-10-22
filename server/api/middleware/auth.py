from fastapi import Request, HTTPException

async def get_current_user(request: Request) -> dict:
    # Minimal stub: allow all, optionally read user from header
    user = request.headers.get("X-User", "demo-user")
    return {"id": user}

class AuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        await self.app(scope, receive, send)
