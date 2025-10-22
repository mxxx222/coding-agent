class CostTrackerMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # Stub: could record request cost/time
        await self.app(scope, receive, send)
