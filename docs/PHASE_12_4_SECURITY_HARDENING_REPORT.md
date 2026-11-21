# SchemeSathi AI — Phase 12.4: Security Remediation & Production Hardening Report

**Project:** SchemeSathi AI  
**Repository:** `https://github.com/vishal-s-sollapure/SchemeSathi-AI.git`  
**Git Branch:** `phase-12.4-security-hardening`  
**Date:** November 21, 2026  
**Auditor & Lead Engineer:** Senior Application Security Engineer, DevSecOps Engineer & Backend Architect  
**Status:** **Remediation Completed & Verified Locally (Awaiting Explicit User Approval Before Push/Merge)**

---

## 1. Executive Summary

In response to the Phase 12.3 production security and reliability audit findings, **Phase 12.4 — Security Remediation & Production Hardening** has been implemented on a dedicated, isolated branch (`phase-12.4-security-hardening`).

Every identified finding across High, Medium, and Low severity tiers has been addressed through defensive architecture, constant-time cryptography, tiered rate limiting, stateless PDF processing, non-blocking asynchronous concurrency, modern browser security headers, and bundle code-splitting.

### Key Metrics Summary
| Metric | Audit Baseline (Phase 12.3) | Hardened Status (Phase 12.4) | Impact |
|---|---|---|---|
| **Automated Backend Tests** | 113 passed | **132 passed** (+19 new security tests) | 100% Pass Rate in 5.77s |
| **Admin Mutation Protection** | 0% (Publicly mutable) | **100% Protected** (Constant-time `X-Admin-Key`) | P0 Vulnerability Neutralized |
| **Rate Limiting** | None (Vulnerable to DoS) | **Tiered Sliding-Window Limiter** (10/min AI/Doc, 60/min General) | DoS & Cost Spike Protection |
| **Gemini API Key Exposure** | URL query parameter | **HTTP Header (`x-goog-api-key`)** | Key logging in proxies eliminated |
| **PDF Disk Storage** | Ephemeral container disk | **Option A: In-Memory Stateless** | Zero broken file references |
| **Health Checks** | Shallow liveness only | **Liveness (`/api/health`) + Readiness (`/api/ready`)** | Prevents cascading reboot loops |
| **Frontend Initial Bundle** | 498 kB (Monolithic) | **342 kB** (Route-level code splitting) | ~31% initial load reduction |
| **Security Headers** | Basic headers | **HSTS, CSP, X-Frame-Options, X-Content-Type** | Edge & browser hardened |

---

## 2. Part A — Critical Security Remediation (P0)

### 2.1 SEC-01: Administrative Mutation Endpoint Protection
- **Vulnerability**: In Phase 12.3, mutating endpoints (`POST`, `PUT`, `DELETE`) for government schemes, scholarships, eligibility rules, and official circulars lacked authentication, exposing core statutory data to unauthorized manipulation.
- **Architectural Solution**:
  1. Implemented centralized authentication dependency `backend/app/core/auth.py` using `require_admin_key`.
  2. Applied `secrets.compare_digest` for **constant-time credential comparison** to completely eliminate timing side-channel attacks.
  3. Strict status code differentiation:
     - Missing `X-Admin-Key` header: Returns **HTTP 401 Unauthorized** with `WWW-Authenticate: ApiKey`.
     - Invalid / incorrect `X-Admin-Key`: Returns **HTTP 403 Forbidden**.
  4. Production Fail-Safe: In production (`ENVIRONMENT == "production"`), requests are blocked with HTTP 403 if `ADMIN_API_KEY` is unconfigured or left at the default development placeholder.
  5. **Protected Endpoints**:
     - `POST /api/v1/schemes`, `PUT /api/v1/schemes/{id}`, `DELETE /api/v1/schemes/{id}`
     - `POST /api/v1/scholarships`, `PUT /api/v1/scholarships/{id}`, `DELETE /api/v1/scholarships/{id}`
     - `POST /api/v1/rules`, `PUT /api/v1/rules/{id}`, `DELETE /api/v1/rules/{id}`
     - `POST /api/v1/rules/requirements`, `PUT /api/v1/rules/requirements/{id}`, `DELETE /api/v1/rules/requirements/{id}`
     - `POST /api/v1/sources`, `PUT /api/v1/sources/{id}`
     - `GET /api/v1/users` (Prevents user enumeration), `DELETE /api/v1/users/{id}`
  6. **Public Citizen Access Preserved**: Citizens retain 100% open, friction-free access to discovery (`GET /schemes`, `GET /scholarships`), eligibility calculation (`POST /eligibility/evaluate`), RAG assistance (`POST /chat/query`), and document verification (`POST /documents/upload`).

### 2.2 SEC-02: IP-Based API Rate Limiting
- **Vulnerability**: Expensive LLM queries, multi-page PDF extractions, and document parsing endpoints could be abused to induce denial of service (DoS) or trigger high Gemini API billing spikes.
- **Architectural Solution**:
  1. Built thread-safe sliding-window rate limiter `backend/app/core/rate_limiter.py` in pure Python (zero external dependencies).
  2. Enforced exact threshold limits requested:
     - **AI Consultation Chat** (`/api/v1/chat/query`): **10 requests / minute**
     - **Document Uploads** (`/api/v1/documents/upload`): **10 requests / minute**
     - **Government PDF Simplification** (`/api/v1/policy/simplify-pdf`): **10 requests / minute**
     - **Policy Explanation** (`/api/v1/policy/explain`): **20 requests / minute**
     - **General Discovery & Read APIs** (`/api/v1/...`): **60 requests / minute**
     - **System Liveness & Readiness Probes**: Exempt from rate limiting.
  3. **Reverse-Proxy IP Extraction**:
     - Checks `CF-Connecting-IP` (Cloudflare).
     - Parses leftmost IP from `X-Forwarded-For` (Render reverse proxy).
     - Falls back safely to socket `client.host`.
  4. Returns **HTTP 429 Too Many Requests** with standard `Retry-After`, `X-RateLimit-Limit`, and `X-RateLimit-Remaining: 0` headers.
  5. **Multi-Instance Scalability Strategy**:
     - *Single-Instance / Free Tier*: Zero-latency in-memory sliding window.
     - *Multi-Instance Horizontal Scale*: The middleware architecture is abstracted so it can seamlessly plug into a shared Redis store via `limits` / Redis when the application scales beyond a single backend container.

---

## 3. Part B — Document & AI Security (P1)

### 3.1 SEC-03: Option A — Stateless In-Memory PDF Processing
- **Problem**: Uploaded PDFs stored on Render's ephemeral container filesystem disappear during container restarts, causing 404 errors for any downstream downloads.
- **Solution (Option A)**:
  1. Added `STORE_UPLOADED_FILES_ON_DISK: bool = False` configuration in `backend/app/config.py`.
  2. In `backend/app/services/document_service.py`, PyMuPDF parses `file_bytes` directly from memory stream. Text extraction, page tracking, OCR detection, and structured candidate fields are persisted to persistent PostgreSQL.
  3. `storage_path` is recorded as `memory://{sha256[:16]}_{filename}`.
  4. Physical disk saving is completely avoided on ephemeral containers, preventing stale filesystem pointers and storage accumulation.

### 3.2 SEC-04: IDOR & User Resource Ownership Architecture Analysis
- **Current Architecture Reality**:
  - The `User` model currently holds basic contact and role fields (`full_name`, `phone_number`, `role`), but the application is designed for open citizen discovery with **no user authentication session (no JWT, passwords, or session cookies)**.
  - Per the prompt's instruction: *"If the application does not currently have a reliable user identity or authentication system, do not invent ownership using an arbitrary client-supplied user ID."*
- **Actionable Hardening Implemented in Phase 12.4**:
  1. Administrative user enumeration (`GET /api/v1/users`) and user deletion (`DELETE /api/v1/users/{id}`) are strictly locked behind `require_admin_key`.
  2. Document deletion (`DELETE /api/v1/documents/{doc_id}`) rolls back linked checklist items safely and does not leak cross-tenant profile metadata.
  3. Checklist queries return only specifically linked profiles without exposing directory listings of all checklists.
- **Production Authentication Roadmap**:
  - *Recommended Minimum Secure Architecture*: Integrate a stateless JWT authentication layer or mobile OTP authentication (standard for Indian civic platforms like DigiLocker / MeriPehchan SSO).
  - *Database Migration*: Add `password_hash: Optional[str]`, `auth_provider: str`, and `phone_verified: bool` to the `users` table.

### 3.3 SEC-05: Gemini API Key Request Header Hardening
- **Fix**: In `backend/app/services/rag/generator.py`, removed `?key=` query parameter from the Gemini API URL.
- **Implementation**:
  ```python
  url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.LLM_MODEL}:generateContent"
  headers = {
      "Content-Type": "application/json",
      "x-goog-api-key": settings.GEMINI_API_KEY or "",
  }
  ```
- **Logging Guard**: Error logging captures only `type(exc).__name__` and never dumps request headers, guaranteeing the API key is never exposed in Render console logs, proxy traces, or error reports.

---

## 4. Part C — Database Persistence & Lifecycle (SEC-06)

A dedicated, comprehensive guide has been authored at `docs/DATABASE_PERSISTENCE_BACKUP_STRATEGY.md`.

### Summary of Policies
1. **Render Free PostgreSQL Limitation**: 1 GB storage, 30-day auto-deletion policy. Automated daily snapshots are not supported on Free tier.
2. **Standardized Backup SOP**:
   ```bash
   pg_dump "$DATABASE_URL" -Fc -f "schemesathi_prod_backup_$(date +%Y%m%d_%H%M%S).dump"
   ```
3. **Disaster Recovery SOP**:
   ```bash
   pg_restore --dbname="$TARGET_DB_URL" --clean --if-exists "schemesathi_prod_backup_YYYYMMDD_HHMMSS.dump"
   ```
4. **Managed Database Plan Comparison**:
   - *Render Paid ($7/mo)*: Seamless upgrade, zero configuration change, 7-day automated backups.
   - *Neon Serverless (Free)*: Best free alternative with scale-to-zero and no 30-day deletion.
   - *Supabase (Free)*: Viable, but pauses after 7 days of inactivity.

---

## 5. Part D — Performance & Concurrency (PERF-01, PERF-02)

### 5.1 PERF-01: Asynchronous Concurrency & Non-Blocking PDF Parsing
1. **HTTP Client Upgrade**: Replaced synchronous `requests.post()` in the Gemini generator with `httpx.Client(timeout=httpx.Timeout(8.0, connect=3.0))` featuring connection pooling and explicit connect/read timeouts.
2. **Event Loop Protection**:
   - In `backend/app/api/v1/documents.py`, offloaded PyMuPDF document extraction to the worker thread pool via `await anyio.to_thread.run_sync()`.
   - In `backend/app/api/v1/policy.py`, offloaded government circular simplification to `await anyio.to_thread.run_sync()`.
   - This ensures CPU-bound PDF operations do not block incoming citizen HTTP requests on Uvicorn's event loop.

### 5.2 PERF-02: Frontend Route-Level Code Splitting
In `frontend/src/App.tsx`, converted all major route pages to dynamic `React.lazy()` imports wrapped in `<Suspense fallback={<PageLoadingFallback />}>`:
- `DashboardPage` (11.08 kB)
- `ScholarReadyPage` (23.72 kB)
- `SchemeDiscoveryPage` (31.42 kB)
- `PolicyExplainerPage` (27.00 kB)
- `AIAssistantPage` (25.65 kB)
- `DocumentIntelligencePage` (19.75 kB)
- `AboutPage` (10.80 kB)

**Build Outcome**: Initial entry JavaScript bundle dropped from 498 kB down to **342 kB** (106 kB gzipped) — a **31% reduction** in initial download size, significantly improving mobile loading speeds on Indian 3G/4G networks.

---

## 6. Part E — Reliability & Security Headers (REL-01, REL-02)

### 6.1 REL-01: Health vs. Readiness Decoupling
- **Liveness Probe** (`GET /api/health`): Returns HTTP 200 immediately if the FastAPI process is responsive. Does not block on database connectivity, preventing Render from entering cascading restart loops during transient database restarts.
- **Readiness Probe** (`GET /api/ready`): Executes a lightweight `SELECT 1` query with connection verification:
  - When database is connected: Returns **HTTP 200** with `{"status": "ready", "database": "connected"}`.
  - When database fails or times out: Returns **HTTP 503 Service Unavailable** with `{"status": "not_ready", "database": "unavailable"}`.

### 6.2 REL-02: Modern Browser Security Headers
Applied in `backend/app/main.py` and `frontend/vercel.json`:
- `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`
- `Content-Security-Policy: default-src 'self'; frame-ancestors 'none';`
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: camera=(), microphone=(), geolocation=()`

---

## 7. Verification & Automated Test Results

### Backend Test Suite
```bash
backend\.venv\Scripts\python -m pytest backend\tests\ -q
........................................................................ [ 54%]
............................................................             [100%]
132 passed, 2 warnings in 5.77s
```
- **Total Tests Passed**: **132 of 132** (100% pass rate).
- **New Test Suite**: `backend/tests/test_phase_12_4_hardening.py` covers:
  - `test_admin_auth_missing_header_returns_401`
  - `test_admin_auth_invalid_key_returns_403`
  - `test_admin_auth_valid_key_succeeds`
  - `test_admin_auth_constant_time_comparison`
  - `test_admin_auth_production_enforcement_blocks_default_dev_key`
  - `test_rate_limiter_strict_limits_expensive_endpoints` (10 req/min)
  - `test_rate_limiter_general_discovery_limits` (60 req/min)
  - `test_rate_limiter_reverse_proxy_header_resolution`
  - `test_option_a_in_memory_stateless_storage`
  - `test_liveness_probe_returns_healthy_without_database_lock`
  - `test_readiness_probe_executes_select_1`
  - `test_readiness_probe_returns_503_on_database_disconnect`
  - `test_security_headers_middleware_applied`
  - `test_public_discovery_endpoints_remain_open_without_auth`

### Frontend Production Build
```bash
cd frontend && npm run build
✓ 1663 modules transformed.
dist/index.html                     1.08 kB │ gzip:   0.64 kB
dist/assets/index-DpFH9sNw.css     55.00 kB │ gzip:   8.93 kB
dist/assets/index-VXnk9PM9.js     342.07 kB │ gzip: 106.11 kB
dist/assets/SchemeDiscoveryPage    31.42 kB │ gzip:   7.64 kB
dist/assets/PolicyExplainerPage    27.00 kB │ gzip:   6.11 kB
dist/assets/AIAssistantPage        25.65 kB │ gzip:   8.88 kB
dist/assets/ScholarReadyPage       23.72 kB │ gzip:   6.07 kB
dist/assets/DocumentIntelligence   19.75 kB │ gzip:   6.06 kB
dist/assets/DashboardPage          11.08 kB │ gzip:   2.91 kB
dist/assets/AboutPage              10.80 kB │ gzip:   3.25 kB
✓ built in 9.85s (0 errors)
```

---

## 8. Summary of Git Changes on `phase-12.4-security-hardening`

| File | Change Summary |
|---|---|
| `backend/app/core/auth.py` | Added constant-time admin authorization with 401/403 status codes. |
| `backend/app/core/rate_limiter.py` | Sliding-window rate limiter with reverse proxy IP parsing & tiered limits. |
| `backend/app/config.py` | Added `ADMIN_API_KEY` and `STORE_UPLOADED_FILES_ON_DISK=False` (Option A). |
| `backend/app/main.py` | Mounted rate limiting, security headers, HSTS, CSP, and `/api/ready` probe. |
| `backend/app/api/v1/health.py` | Deep database health verification endpoint. |
| `backend/app/api/v1/schemes.py` | Protected `POST`, `PUT`, `DELETE` behind `require_admin_key`. |
| `backend/app/api/v1/scholarships.py` | Protected `POST`, `PUT`, `DELETE` behind `require_admin_key`. |
| `backend/app/api/v1/rules.py` | Protected `POST`, `PUT`, `DELETE` for rules & requirements behind admin key. |
| `backend/app/api/v1/sources.py` | Protected `POST`, `PUT` behind `require_admin_key`. |
| `backend/app/api/v1/users.py` | Protected `GET /users` and `DELETE /users/{id}` behind `require_admin_key`. |
| `backend/app/api/v1/documents.py` | Offloaded PDF parsing to worker thread pool (`anyio.to_thread.run_sync`). |
| `backend/app/api/v1/policy.py` | Offloaded circular simplification to thread pool. |
| `backend/app/services/document_service.py` | Implemented stateless in-memory processing (`memory://` storage path). |
| `backend/app/services/rag/generator.py` | Moved Gemini API key to `x-goog-api-key` header; added `httpx` client with timeouts. |
| `backend/tests/test_phase_12_4_hardening.py` | 14 automated security regression tests. |
| `backend/tests/test_security_audit.py` | Enhanced with constant-time and header tests. |
| `frontend/src/App.tsx` | Route code-splitting with `React.lazy()` and `<Suspense>`. |
| `frontend/vercel.json` | Modern browser security headers on Vercel edge. |
| `docs/DATABASE_PERSISTENCE_BACKUP_STRATEGY.md` | Standard operating procedures for backup, restore, and plan comparisons. |

---

## 9. Next Steps (Awaiting User Approval)

Per your instructions, **no code has been pushed to GitHub, merged into `main`, or deployed to production.**

All work is staged on the local branch `phase-12.4-security-hardening`.

When you are ready, please provide your explicit approval to:
1. Commit any remaining documentation or artifacts on `phase-12.4-security-hardening`.
2. Merge `phase-12.4-security-hardening` into `main` (or push the branch to GitHub for pull request review).
3. Trigger deployment to Vercel and Render.
