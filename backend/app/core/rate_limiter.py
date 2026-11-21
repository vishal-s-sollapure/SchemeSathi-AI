from collections import defaultdict, deque
import logging
import threading
import time
from typing import Dict, Tuple
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

logger = logging.getLogger("schemesathi.ratelimit")


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

            # Allow request and record timestamp
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
    - AI chat (/api/v1/chat/query): 10 requests/minute
    - Document uploads (/api/v1/documents/upload): 10 requests/minute
    - PDF policy simplification (/api/v1/policy/simplify-pdf): 10 requests/minute
    - Policy explainer queries (/api/v1/policy/explain): 20 requests/minute
    - General discovery & read APIs (/api/v1/...): 60 requests/minute
    - System health & readiness probes (/api/health, /api/ready, /api/v1/health): Exempt
    """

    EXEMPT_PATHS = {
        "/",
        "/api/health",
        "/api/ready",
        "/api/v1/health",
        "/docs",
        "/redoc",
        "/openapi.json",
    }

    STRICT_EXPENSIVE_PATHS = {
        "/api/v1/chat/query",
        "/api/v1/documents/upload",
        "/api/v1/policy/simplify-pdf",
    }

    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path

        # Bypass exempt system paths and CORS preflights
        if path in self.EXEMPT_PATHS or request.method == "OPTIONS":
            return await call_next(request)

        # Extract client IP accounting for reverse proxies (Render, Cloudflare, AWS ALB)
        client_ip = None
        # 1. Cloudflare True Client IP
        cf_ip = request.headers.get("cf-connecting-ip")
        if cf_ip:
            client_ip = cf_ip.strip()

        # 2. X-Forwarded-For: Client IP is the leftmost entry
        if not client_ip:
            xff = request.headers.get("x-forwarded-for")
            if xff:
                client_ip = xff.split(",")[0].strip()

        # 3. Direct socket client host fallback
        if not client_ip:
            client_ip = request.client.host if request.client else "127.0.0.1"

        # Determine route bucket and limit
        if any(path.startswith(strict_path) for strict_path in self.STRICT_EXPENSIVE_PATHS):
            bucket = "expensive_ai_doc"
            limit = 10
            window = 60
        elif path.startswith("/api/v1/policy/explain"):
            bucket = "policy_explainer"
            limit = 20
            window = 60
        else:
            bucket = "general_discovery_api"
            limit = 60
            window = 60

        allowed, remaining, retry_after = limiter.is_allowed(client_ip, bucket, limit, window)

        if not allowed:
            logger.warning(
                f"Rate limit exceeded for IP {client_ip} on {path} (bucket={bucket}, limit={limit}/min)"
            )
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
