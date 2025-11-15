import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger("gateway")


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time
        logger.info(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.2f}s"
        )

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 100, window: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window
        self.requests = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        now = time.time()

        self.requests[client_ip] = [
            req_time
            for req_time in self.requests.get(client_ip, [])
            if now - req_time < self.window
        ]

        if len(self.requests[client_ip]) >= self.max_requests:
            from fastapi import HTTPException

            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        self.requests[client_ip].append(now)

        return await call_next(request)
