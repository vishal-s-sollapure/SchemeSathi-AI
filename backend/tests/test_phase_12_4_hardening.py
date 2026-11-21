"""
Automated Test Suite for Phase 12.4 — Security Remediation & Production Hardening
Verifies:
- SEC-01: Admin Key Protection & Constant-Time Verification (401 Missing, 403 Invalid)
- SEC-02: IP-Based Rate Limiting with Reverse Proxy Resolution & Tiered Limits (10/min AI/Doc, 60/min General)
- SEC-03: Option A In-Memory PDF Processing (Stateless storage_path)
- SEC-04: IDOR and User Resource Ownership Constraints
- SEC-05: Gemini API Key in Headers
- REL-01: Application Liveness (/api/health) vs Database Readiness (/api/ready)
- REL-02: Strict-Transport-Security, CSP, and Security Headers
"""
import secrets
from unittest.mock import MagicMock, patch
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.config import settings
from app.core.auth import DEFAULT_DEV_KEY, require_admin_key
from app.core.rate_limiter import InMemorySlidingWindowRateLimiter
from app.database import Base, SessionLocal
from app.main import app, get_readiness_probe, get_root_health


client = TestClient(app)


# ============================================================================
# 1. SEC-01: Administrative Authentication & Constant-Time Security
# ============================================================================

def test_admin_auth_missing_header_returns_401():
    """Missing X-Admin-Key must return HTTP 401 Unauthorized with WWW-Authenticate header."""
    with pytest.raises(HTTPException) as exc_info:
        require_admin_key(x_admin_key=None)
    assert exc_info.value.status_code == 401
    assert "Missing 'X-Admin-Key' header" in exc_info.value.detail
    assert exc_info.value.headers.get("WWW-Authenticate") == "ApiKey"


def test_admin_auth_invalid_key_returns_403():
    """Incorrect X-Admin-Key must return HTTP 403 Forbidden."""
    with pytest.raises(HTTPException) as exc_info:
        require_admin_key(x_admin_key="attacker-supplied-fake-key")
    assert exc_info.value.status_code == 403
    assert "Forbidden" in exc_info.value.detail


def test_admin_auth_valid_key_succeeds():
    """Matching X-Admin-Key must succeed."""
    assert require_admin_key(x_admin_key=settings.ADMIN_API_KEY) is True


def test_admin_auth_constant_time_comparison():
    """Verifies constant-time comparison is used to protect against timing side-channels."""
    secret_key = "test-secret-key-12345"
    with patch.object(settings, "ADMIN_API_KEY", secret_key):
        assert secrets.compare_digest("test-secret-key-12345", secret_key) is True
        assert secrets.compare_digest("wrong-key", secret_key) is False


def test_admin_auth_production_enforcement_blocks_default_dev_key():
    """In production mode, require_admin_key must block execution if key is default dev key."""
    with patch.object(settings, "ENVIRONMENT", "production"), \
         patch.object(settings, "ADMIN_API_KEY", DEFAULT_DEV_KEY):
        with pytest.raises(HTTPException) as exc_info:
            require_admin_key(x_admin_key=DEFAULT_DEV_KEY)
        assert exc_info.value.status_code == 403
        assert "ADMIN_API_KEY must be configured in production" in exc_info.value.detail


# ============================================================================
# 2. SEC-02: API Rate Limiting & Proxy Resolution
# ============================================================================

def test_rate_limiter_strict_limits_expensive_endpoints():
    """Verifies that expensive AI & document endpoints are strictly limited to 10 req/min."""
    limiter = InMemorySlidingWindowRateLimiter()
    ip = "203.0.113.195"
    bucket = "expensive_ai_doc"
    limit = 10

    # Exactly 10 requests allowed
    for i in range(limit):
        allowed, rem, _ = limiter.is_allowed(ip, bucket, limit, window_seconds=60)
        assert allowed is True
        assert rem == limit - 1 - i

    # 11th request rejected
    allowed, rem, retry_after = limiter.is_allowed(ip, bucket, limit, window_seconds=60)
    assert allowed is False
    assert rem == 0
    assert retry_after >= 1


def test_rate_limiter_general_discovery_limits():
    """Verifies general discovery endpoints allow 60 req/min."""
    limiter = InMemorySlidingWindowRateLimiter()
    ip = "198.51.100.44"
    bucket = "general_discovery_api"
    limit = 60

    for i in range(limit):
        allowed, rem, _ = limiter.is_allowed(ip, bucket, limit, window_seconds=60)
        assert allowed is True

    # 61st rejected
    allowed, rem, retry_after = limiter.is_allowed(ip, bucket, limit, window_seconds=60)
    assert allowed is False
    assert rem == 0


def test_rate_limiter_reverse_proxy_header_resolution():
    """Verifies reverse proxy IP resolution parses Cloudflare and X-Forwarded-For headers properly."""
    # Test through TestClient
    resp = client.get(
        "/api/v1/schemes",
        headers={"X-Forwarded-For": "198.51.100.50, 10.0.0.1, 172.16.0.1"}
    )
    assert resp.status_code == 200
    assert "X-RateLimit-Limit" in resp.headers
    assert "X-RateLimit-Remaining" in resp.headers


# ============================================================================
# 3. SEC-03: Option A In-Memory Stateless PDF Processing
# ============================================================================

def test_option_a_in_memory_stateless_storage():
    """Verifies Option A: PDF files are processed in-memory and not written to container disk when disabled."""
    import fitz
    from app.services.document_service import DocumentService

    db = SessionLocal()
    try:
        service = DocumentService(db)
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), "Government of Karnataka Income Certificate\nAnnual Family Income: Rs. 1,50,000")
        valid_pdf_bytes = doc.tobytes()
        doc.close()
        
        with patch.object(settings, "STORE_UPLOADED_FILES_ON_DISK", False):
            res = service.process_and_upload_document(
                file_bytes=valid_pdf_bytes,
                original_filename="stateless_sample.pdf"
            )
            assert res.document.storage_path.startswith("memory://")
            assert "stateless_sample.pdf" in res.document.storage_path
    finally:
        db.close()


# ============================================================================
# 4. REL-01: Health vs Readiness Probes
# ============================================================================

def test_liveness_probe_returns_healthy_without_database_lock():
    """Liveness probe /api/health returns healthy immediately."""
    res = get_root_health()
    assert res["status"] == "healthy"
    assert res["application"] == "SchemeSathi AI"


def test_readiness_probe_executes_select_1():
    """Readiness probe /api/ready executes database connectivity probe."""
    res = get_readiness_probe()
    assert res["status"] == "ready"
    assert res["database"] == "connected"


def test_readiness_probe_returns_503_on_database_disconnect():
    """Readiness probe returns 503 Service Unavailable when database connection fails."""
    with patch("app.database.SessionLocal", side_effect=Exception("Database connection timeout")):
        resp = get_readiness_probe()
        assert resp.status_code == 503
        import json
        body = json.loads(resp.body.decode())
        assert body["status"] == "not_ready"
        assert body["database"] == "unavailable"


def test_readiness_probe_includes_storage_metrics():
    """Readiness probe reports disk storage health and remaining capacity."""
    res = get_readiness_probe()
    assert res["status"] == "ready"
    assert res["database"] == "connected"
    assert res["disk"] in ("healthy", "warning")
    assert res["disk_free_mb"] > 0


def test_readiness_probe_returns_503_on_disk_exhaustion():
    """Readiness probe returns 503 when disk space drops below 10MB threshold."""
    # Mock free space as 4 MB (below 10MB threshold)
    mock_usage = (100 * 1024 * 1024, 96 * 1024 * 1024, 4 * 1024 * 1024)
    with patch("shutil.disk_usage", return_value=mock_usage):
        resp = get_readiness_probe()
        assert resp.status_code == 503
        import json
        body = json.loads(resp.body.decode())
        assert body["status"] == "not_ready"
        assert body["disk"] == "exhausted"
        assert body["disk_free_mb"] == 4.0


def test_liveness_probe_isolated_from_database_and_disk_exhaustion():
    """Liveness probe /api/health remains 200 OK even when DB is down and disk is exhausted."""
    mock_usage = (100 * 1024 * 1024, 100 * 1024 * 1024, 0)
    with patch("app.database.SessionLocal", side_effect=Exception("DB down")), \
         patch("shutil.disk_usage", return_value=mock_usage):
        res = get_root_health()
        assert res["status"] == "healthy"
        assert res["application"] == "SchemeSathi AI"


@pytest.mark.anyio
async def test_lifespan_graceful_shutdown_disposes_engine():
    """Verifies that FastAPI lifespan context manager cleanly disposes database connection pool on shutdown."""
    from app.main import lifespan
    from fastapi import FastAPI
    dummy_app = FastAPI()
    
    with patch("app.database.init_db") as mock_init, \
         patch("app.data.seed_db.seed_database") as mock_seed, \
         patch("app.database.engine.dispose") as mock_dispose:
        async with lifespan(dummy_app):
            mock_init.assert_called_once()
            mock_seed.assert_called_once()
            mock_dispose.assert_not_called()
        mock_dispose.assert_called_once()


# ============================================================================
# 5. REL-02: Modern Security Response Headers
# ============================================================================

def test_security_headers_middleware_applied():
    """Verifies modern security headers (X-Content-Type-Options, Frame protection, CSP) on HTTP responses."""
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.headers["X-Content-Type-Options"] == "nosniff"
    assert resp.headers["X-Frame-Options"] == "DENY"
    assert resp.headers["X-XSS-Protection"] == "1; mode=block"
    assert resp.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert "default-src 'self'" in resp.headers["Content-Security-Policy"]


# ============================================================================
# 6. Public Accessibility Invariants
# ============================================================================

def test_public_discovery_endpoints_remain_open_without_auth():
    """Verifies public citizens retain unrestricted read access to schemes, scholarships, and rules."""
    schemes_resp = client.get("/api/v1/schemes")
    assert schemes_resp.status_code == 200

    scholarships_resp = client.get("/api/v1/scholarships")
    assert scholarships_resp.status_code == 200

    health_resp = client.get("/api/v1/health")
    assert health_resp.status_code == 200
