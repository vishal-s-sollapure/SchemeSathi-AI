"""
Priority 1 Security Verification Deep Dive Script
Executes live probes for:
1. Admin Authentication enforcement (missing, invalid, valid, production dev-key block, public preservation)
2. Rate-limit saturation simulation (10 req/min expensive bucket saturation, 429 response, header inspection)
3. Proxy-header resolution & spoofing inspection (CF-Connecting-IP precedence, multi-hop X-Forwarded-For)
"""

import sys
import os

# Ensure backend root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from starlette.testclient import TestClient
from app.main import app
from app.config import settings
from app.core.rate_limiter import limiter

def run_verification():
    client = TestClient(app, base_url="http://testserver")
    
    print("=" * 60)
    print("1. ADMIN AUTHENTICATION VERIFICATION")
    print("=" * 60)

    # 1a. Missing Header on POST /api/v1/schemes/
    r = client.post("/api/v1/schemes/", json={"title": "Test Scheme"})
    detail = r.json().get("detail")
    print(f"[1a] Missing Header -> Status: {r.status_code}")
    print(f"     Detail: {detail}")
    print(f"     WWW-Authenticate: {r.headers.get('www-authenticate')}")
    assert r.status_code == 401, f"Expected 401, got {r.status_code}"
    assert "Missing 'X-Admin-Key' header" in detail

    # 1b. Invalid Header on POST /api/v1/schemes/
    r = client.post("/api/v1/schemes/", headers={"X-Admin-Key": "malicious-attacker-key"}, json={"title": "Test Scheme"})
    detail = r.json().get("detail")
    print(f"[1b] Invalid Header -> Status: {r.status_code}")
    print(f"     Detail: {detail}")
    assert r.status_code == 403, f"Expected 403, got {r.status_code}"
    assert "Invalid 'X-Admin-Key' credentials" in detail

    # 1c. Valid Header on POST /api/v1/schemes/
    r = client.post("/api/v1/schemes/", headers={"X-Admin-Key": settings.ADMIN_API_KEY}, json={"title": "Test"})
    print(f"[1c] Valid Header -> Status: {r.status_code} (Auth passed; schema validation responded)")
    assert r.status_code not in (401, 403), f"Auth check should pass, got {r.status_code}"

    # 1d. Production enforcement with default dev key
    original_env = settings.ENVIRONMENT
    settings.ENVIRONMENT = "production"
    try:
        r = client.post("/api/v1/schemes/", headers={"X-Admin-Key": settings.ADMIN_API_KEY}, json={})
        detail = r.json().get("detail")
        print(f"[1d] Production Mode with Default Dev Key -> Status: {r.status_code}")
        print(f"     Detail: {detail}")
        assert r.status_code == 403, f"Expected 403 in prod with dev key, got {r.status_code}"
        assert "ADMIN_API_KEY must be configured in production" in detail
    finally:
        settings.ENVIRONMENT = original_env

    # 1e. Public endpoints require ZERO authentication
    r_schemes = client.get("/api/v1/schemes/")
    r_health = client.get("/api/health")
    r_ready = client.get("/api/ready")
    print(f"[1e] Public Discovery GET /api/v1/schemes/ -> Status: {r_schemes.status_code}")
    print(f"     Public Liveness  GET /api/health        -> Status: {r_health.status_code}")
    print(f"     Public Readiness GET /api/ready         -> Status: {r_ready.status_code}")
    assert r_schemes.status_code == 200
    assert r_health.status_code == 200
    assert r_ready.status_code == 200

    print("\n" + "=" * 60)
    print("2. RATE-LIMIT SATURATION SIMULATION")
    print("=" * 60)
    limiter.reset()
    test_ip = "192.0.2.100"

    # Expensive path: /api/v1/chat/query (Limit = 10 req/min)
    responses = []
    for i in range(12):
        res = client.post(
            "/api/v1/chat/query",
            headers={"CF-Connecting-IP": test_ip},
            json={"query": f"Test query {i}"}
        )
        rem = res.headers.get("X-RateLimit-Remaining")
        limit_h = res.headers.get("X-RateLimit-Limit")
        retry = res.headers.get("Retry-After")
        responses.append((i + 1, res.status_code, rem, limit_h, retry))

    print("Sending 12 consecutive requests to /api/v1/chat/query (bucket limit: 10/min):")
    for req_num, st, rem, limit_h, retry in responses[:10]:
        print(f"  Req #{req_num:2d} -> Status: {st}, Limit: {limit_h}, Remaining: {rem}")
        assert st != 429, f"Req #{req_num} was unexpectedly rate limited"

    for req_num, st, rem, limit_h, retry in responses[10:]:
        print(f"  Req #{req_num:2d} -> Status: {st} (SATURATED 429), Remaining: {rem}, Retry-After: {retry}s")
        assert st == 429, f"Req #{req_num} expected 429, got {st}"
        assert retry is not None and int(retry) > 0

    # Verify exempt path is not affected by saturated IP
    exempt_statuses = [client.get("/api/health", headers={"CF-Connecting-IP": test_ip}).status_code for _ in range(15)]
    print(f"Exempt /api/health (15 requests from saturated IP) -> All 200 OK: {all(s == 200 for s in exempt_statuses)}")
    assert all(s == 200 for s in exempt_statuses)

    print("\n" + "=" * 60)
    print("3. PROXY-HEADER SPOOFING & IP RESOLUTION")
    print("=" * 60)
    limiter.reset()

    # 3a. CF-Connecting-IP vs X-Forwarded-For precedence
    ip_cf = "198.51.100.50"
    ip_xff_spoofed = "203.0.113.99"
    client.get(
        "/api/v1/schemes/",
        headers={
            "CF-Connecting-IP": ip_cf,
            "X-Forwarded-For": f"{ip_xff_spoofed}, 10.0.0.1",
        }
    )
    cf_key = (ip_cf, "general_discovery_api")
    xff_key = (ip_xff_spoofed, "general_discovery_api")
    print(f"[3a] Cloudflare Precedence Test:")
    print(f"     CF-Connecting-IP bucket ({ip_cf}) request count: {len(limiter._history[cf_key])}")
    print(f"     Spoofed XFF bucket ({ip_xff_spoofed}) request count: {len(limiter._history[xff_key])}")
    assert len(limiter._history[cf_key]) == 1, "CF-Connecting-IP must take precedence"
    assert len(limiter._history[xff_key]) == 0, "Spoofed XFF must be ignored when CF header present"

    # 3b. Multi-hop X-Forwarded-For resolution when CF header absent
    limiter.reset()
    client.get(
        "/api/v1/schemes/",
        headers={"X-Forwarded-For": "203.0.113.77, 10.0.0.2, 172.16.0.1"}
    )
    resolved_key = ("203.0.113.77", "general_discovery_api")
    print(f"[3b] Multi-hop X-Forwarded-For Resolution:")
    print(f"     Header value: '203.0.113.77, 10.0.0.2, 172.16.0.1'")
    print(f"     Resolved client IP: 203.0.113.77 -> Bucket count: {len(limiter._history[resolved_key])}")
    assert len(limiter._history[resolved_key]) == 1

    print("\n" + "=" * 60)
    print("SUMMARY: ALL PRIORITY 1 SECURITY VERIFICATIONS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_verification()
