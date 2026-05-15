"""
Simple in-memory rate limiting middleware.
Limits requests per user per endpoint per minute.
"""
import time
from collections import defaultdict
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# Rate limit config: (max_requests, window_seconds)
RATE_LIMITS = {
    "/api/v1/sessions": (30, 60),           # 30 session creates per minute
    "/api/v1/auth/register": (5, 60),       # 5 registrations per minute
    "/api/v1/auth/login": (10, 60),         # 10 login attempts per minute
    "/api/v1/sessions/*/analyze": (20, 60), # 20 analyses per minute
    "/api/v1/sessions/*/feynman": (10, 60), # 10 Feynman attempts per minute
    "/api/v1/sessions/*/socratic": (20, 60),# 20 Socratic responses per minute
}

DEFAULT_LIMIT = (60, 60)  # 60 requests per minute for all other endpoints

# In-memory store: {(client_ip, path): [(timestamp, count)]}
_request_counts: dict = defaultdict(list)


def _get_rate_limit(path: str) -> tuple[int, int]:
    """Get rate limit for a given path."""
    for pattern, limit in RATE_LIMITS.items():
        # Simple wildcard matching
        if "*" in pattern:
            parts = pattern.split("*")
            if path.startswith(parts[0]) and path.endswith(parts[1]):
                return limit
        elif path == pattern or path.startswith(pattern):
            return limit
    return DEFAULT_LIMIT


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Per-IP rate limiting middleware."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for health check and docs
        if request.url.path in ("/health", "/docs", "/openapi.json", "/redoc"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path
        key = (client_ip, path)

        max_requests, window_seconds = _get_rate_limit(path)
        now = time.time()
        window_start = now - window_seconds

        # Clean old entries
        _request_counts[key] = [
            ts for ts in _request_counts[key] if ts > window_start
        ]

        # Check limit
        if len(_request_counts[key]) >= max_requests:
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "code": "RATE_LIMITED",
                        "message": f"Too many requests. Limit: {max_requests} per {window_seconds}s.",
                        "user_facing": True,
                        "retry_allowed": True,
                    }
                },
                headers={"Retry-After": str(window_seconds)},
            )

        # Record request
        _request_counts[key].append(now)
        return await call_next(request)
