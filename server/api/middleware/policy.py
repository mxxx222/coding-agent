class PolicyMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # Stub: no-op policy enforcement
        await self.app(scope, receive, send)
