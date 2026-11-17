from collections import defaultdict, deque
import threading
import time
from typing import Dict, Tuple
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class InMemorySlidingWindowRateLimiter:
    """Thread-safe sliding-window in-memory rate limiter per IP address."""

    def __init__(self):
        self._lock = threading.Lock()
        # Key: (ip, route_bucket) -> deque of request timestamps
        self._history: Dict[Tuple[str, str], deque] = defaultdict(deque)

    def is_allowed(self, ip: str, bucket: str, limit: int, window_seconds: int = 60) -> Tuple[bool, int, int]:
        """
        Evaluates whether an incoming request from `ip` under `bucket` is within `limit`.
        Returns (is_allowed, remaining, retry_after_seconds).
        """
        now = time.time()
        window_start = now - window_seconds
        key = (ip, bucket)

        with self._lock:
            queue = self._history[key]
            # Prune timestamps older than window
            while queue and queue[0] < window_start:
                queue.popleft()

            if len(queue) >= limit:
                # Rate limit exceeded; calculate retry_after from earliest request in window
                earliest = queue[0]
                retry_after = max(1, int(earliest + window_seconds - now))
                return False, 0, retry_after

            # Allow request and append timestamp
            queue.append(now)
            remaining = limit - len(queue)
            return True, remaining, 0

    def reset(self):
        with self._lock:
            self._history.clear()


limiter = InMemorySlidingWindowRateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware applying tiered rate limits based on endpoint sensitivity:
    - High-load AI & Document processing (Chat, PDF Upload, PDF Simplification): 15 req/min
    - Standard discovery & evaluation endpoints: 120 req/min
    - Health checks & system info: Exempt
    """

    EXEMPT_PATHS = {
        "/",
        "/api/health",
        "/api/v1/health",
        "/docs",
        "/redoc",
        "/openapi.json",
    }

    AI_DOC_PATHS = {
        "/api/v1/chat/query",
        "/api/v1/documents/upload",
        "/api/v1/policy/simplify-pdf",
        "/api/v1/policy/explain",
    }

    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path

        # Bypass exempt system paths
        if path in self.EXEMPT_PATHS or request.method == "OPTIONS":
            return await call_next(request)

        # Extract client IP (handle proxies & reverse load balancers like Render/Cloudflare)
        client_ip = request.headers.get("x-forwarded-for")
        if client_ip:
            client_ip = client_ip.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "127.0.0.1"

        # Determine route bucket and limit
        if any(path.startswith(ai_path) for ai_path in self.AI_DOC_PATHS):
            bucket = "ai_doc_intensive"
            limit = 15
            window = 60
        else:
            bucket = "standard_api"
            limit = 120
            window = 60

        allowed, remaining, retry_after = limiter.is_allowed(client_ip, bucket, limit, window)

        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "RateLimitExceeded",
                    "message": "Too many requests. Please slow down and try again shortly.",
                    "path": path,
                    "retry_after_seconds": retry_after,
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
