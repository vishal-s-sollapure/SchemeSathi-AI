# SchemeSathi AI — Phase 12.4 Priority 3: Production Reliability & Smoke Invariants Audit

**Audit Date:** 2026-11-21T18:16:00+05:30  
**Target Repository:** `C:\Users\VISHAL\OneDrive\Desktop\SchemeSathi-AI`  
**Git Remote:** `https://github.com/vishal-s-sollapure/SchemeSathi-AI.git`  
**Active Branch:** `main` (commit `8d5147e`)  
**Lead Auditor:** Senior Site Reliability Engineer (SRE) & DevSecOps Lead  
**Audit Protocol:** Read-Only, Evidence-Based, Non-Destructive  
**Overall Verdict:** **CONDITIONAL PASS** (Core reliability architecture verified; 1 High-Severity defect identified in Rule Engine attribute resolution under missing `full_name`)

---

## 1. Executive Summary

A comprehensive, evidence-driven production reliability audit was conducted on **SchemeSathi AI** focusing on four critical operational pillars:
1. **Liveness vs. Readiness Probe Isolation**
2. **Disk Space Exhaustion Safety & Vector Store Resilience**
3. **Graceful Shutdown & Container Lifecycle Signals**
4. **Production Smoke Tests & End-to-End Reliability Invariants**

### Summary of Audit Outcomes
- **Liveness/Readiness Isolation (PASS):** `/api/health` functions strictly as a zero-dependency process liveness check (<7ms) completely decoupled from database availability, storage capacity, and external APIs. `/api/ready` rigorously validates storage capacity (<10MB threshold) and database pool connectivity (`SELECT 1`), returning HTTP 503 upon dependency outage.
- **Disk Space Safety & Stateless Architecture (PASS):** SchemeSathi operates in **Option A (In-Memory Stateless Processing)** by default (`STORE_UPLOADED_FILES_ON_DISK = False`). PDF documents are validated, parsed, and hashed in memory via PyMuPDF without writing to ephemeral disk. In-memory Pure-Python Hybrid RAG eliminates any dependency on ChromaDB, local vector indexes, or native C-DLLs.
- **Graceful Shutdown & Signal Handling (PASS):** FastAPI lifespan context manager cleanly drains and disposes the SQLAlchemy database engine pool upon shutdown (measured shutdown duration: **1.25 ms**). HTTP clients are bounded with 8.0s timeouts and context-managed per request.
- **Production Smoke Invariants (CONDITIONAL PASS):** 
  - Frontend production build (`tsc && vite build`) passed in 9.45s with 0 errors.
  - Backend pytest test suite passed 136 of 136 tests.
  - Core discovery, scholarships, RAG consultations (English & Kannada), and dynamic checklists passed smoke testing.
  - **Defect Identified (FINDING-REL-01, High):** In `DeterministicRuleEngine.evaluate_all_scholarships` (line 474) and `evaluate_scheme` (line 676), evaluating a Pydantic `StudentEvaluationInput` or `CitizenEvaluationInput` where `full_name` is `None` causes an unhandled `AttributeError: 'StudentEvaluationInput' object has no attribute 'get'` resulting in an unhandled HTTP 500 error.

---

## 2. Verified Repository Identity & Environment

| Property | Verified Value | Compliance Status |
|:---|:---|:---|
| **Working Directory** | `C:\Users\VISHAL\OneDrive\Desktop\SchemeSathi-AI` | Verified |
| **Git Repository Root** | `C:/Users/VISHAL/OneDrive/Desktop/SchemeSathi-AI` | Verified |
| **Git Remote URL** | `https://github.com/vishal-s-sollapure/SchemeSathi-AI.git` | Verified |
| **Current Branch** | `main` | Verified |
| **HEAD Commit** | `8d5147e` (`Intial commit`) | Verified |
| **Isolation Boundary** | `C:\Users\VISHAL\OneDrive\Desktop\BolKhata AI` completely untouched | Verified |

---

## 3. Initial Git Status

```
On branch main
Your branch is up to date with 'origin/main'.
Untracked files:
  docs/ACCIDENTAL_BOLKHATA_CLEANUP_REPORT.md
nothing added to commit but untracked files present
```
Working tree verified clean with zero pending source modifications.

---

## 4. Architecture and Reliability Components Inspected

| Component | Architecture Role | File Inspected |
|:---|:---|:---|
| **Liveness Probe** | Process responsiveness check | `backend/app/main.py` (`/api/health`) |
| **Readiness Probe** | DB & storage readiness check | `backend/app/main.py` (`/api/ready`) |
| **Application Lifespan** | DB schema init & connection pool disposal | `backend/app/main.py` (`lifespan`) |
| **Database Engine** | SQLAlchemy connection pooling (`pool_size=10, max_overflow=20`) | `backend/app/database.py` |
| **Hosting Specification** | Render background container definition | `render.yaml` (`healthCheckPath: /api/health`) |
| **Frontend CDN Config** | SPA routing rewrites & security headers | `vercel.json` |
| **Document Processing** | In-memory PyMuPDF PDF parsing & OCR detection | `backend/app/services/document_intelligence/parser.py` |
| **Vector Engine** | Pure-Python dense & BM25 hybrid in-memory retriever | `backend/app/services/rag/retriever.py` |
| **Eligibility Engine** | Deterministic citizen & student qualification rules | `backend/app/services/rule_engine.py` |

---

## 5. Priority 3.1 — Liveness vs. Readiness Probe Isolation

### 5.1 Probe Architectural Design
1. **Liveness Probe (`GET /api/health`):**
   - Returns immediate HTTP 200: `{"status": "healthy", "application": "SchemeSathi AI"}`.
   - Zero database locks, zero queries, zero storage checks, zero network dependencies.
   - Matched to `render.yaml` `healthCheckPath: /api/health`, preventing spurious container restarts during upstream database maintenance.
2. **Readiness Probe (`GET /api/ready`):**
   - Step 1: Probes storage capacity via `shutil.disk_usage`. Rejects with HTTP 503 if free storage < 10 MB (`disk: "exhausted"`).
   - Step 2: Probes database connectivity via `SELECT 1` with `SessionLocal()`. Rejects with HTTP 503 if unreachable (`database: "unavailable"`).
   - Omits internal connection strings, hostnames, or database credentials from failure responses.

### 5.2 Failure Scenario Verification (Live Execution)
All 6 mandated failure scenarios were safely simulated and recorded using isolated mocks:

| Scenario | Target Endpoint | Expected Status | Actual Status | Execution Latency | Response Payload Summary | Verification Result |
|:---|:---:|:---:|:---:|:---:|:---|:---:|
| **1. Normal Operation (DB + Disk OK)** | `/api/ready` | 200 | **200** | 42.69 ms | `status: ready`, `database: connected`, `disk: healthy` | **PASS** |
| **1b. Liveness during Normal** | `/api/health` | 200 | **200** | 6.00 ms | `status: healthy` | **PASS** |
| **2. Database Unavailable** | `/api/ready` | 503 | **503** | 6.27 ms | `status: not_ready`, `database: unavailable` | **PASS** |
| **2b. Liveness during DB Outage** | `/api/health` | 200 | **200** | 6.95 ms | `status: healthy` (Process survives DB outage) | **PASS** |
| **3. DB Connection Timeout** | `/api/ready` | 503 | **503** | 6.58 ms | `status: not_ready`, `database: unavailable` | **PASS** |
| **4. Storage Warning (25MB free)** | `/api/ready` | 200 | **200** | 5.71 ms | `status: ready`, `disk: warning`, `disk_free_mb: 25.0` | **PASS** |
| **5. Storage Unavailable (5MB free)** | `/api/ready` | 503 | **503** | 5.92 ms | `status: not_ready`, `disk: exhausted`, `free: 5.0MB` | **PASS** |
| **5b. Liveness during Storage Exhaustion** | `/api/health` | 200 | **200** | 5.14 ms | `status: healthy` (Process survives disk warning) | **PASS** |
| **6. Combined DB & Storage Outage** | `/api/ready` | 503 | **503** | 5.41 ms | `status: not_ready`, `disk: exhausted` (503 enforced) | **PASS** |
| **6b. Liveness during Combined Outage** | `/api/health` | 200 | **200** | 5.01 ms | `status: healthy` (Liveness fully isolated) | **PASS** |

---

## 6. Priority 3.2 — Disk Space Exhaustion Safety & Vector Store Resilience

### 6.1 Storage Strategy Audit
- **Default Stateless Mode:** `settings.STORE_UPLOADED_FILES_ON_DISK = False`.
- In this default state, uploaded document bytes are processed in memory using PyMuPDF `fitz.open(stream=file_bytes, filetype="pdf")`. The storage URI is registered as `memory://{sha256[:16]}_{original_filename}`.
- Zero ephemeral disk writes occur during normal uploads, rendering the application largely immune to local container disk exhaustion.
- **Persistent Disk Fallback:** If `STORE_UPLOADED_FILES_ON_DISK = True`, `DocumentParser.save_file_securely` sanitizes paths to prevent path traversal (`..`, `/`, `\`) and writes to `UPLOAD_DIR`.

### 6.2 Vector Store Audit
- **ChromaDB / External Vector DB Check:** Confirmed that **no ChromaDB, FAISS, Pinecone, or external native vector databases are present or required**.
- **Implementation:** `HybridDocumentRetriever` (`backend/app/services/rag/retriever.py`) uses a pure-Python lexical and dense semantic document retriever with hash-projected unit embedding vectors and BM25 scoring over in-memory verified policy circulars.
- **Safety Benefit:** Zero native C-extension / DLL loading issues, zero risk of disk corruption from embedded vector databases on ephemeral container filesystems.

### 6.3 Storage Exhaustion & Upload Limit Simulation
Simulated via isolated mock testing:
1. **In-Memory Upload (Default):** Returned `201 Created` with `memory://eb41ce42f015d6f3_test.pdf` in 18ms.
2. **Disk Full (`ENOSPC`) Simulation:** When `STORE_UPLOADED_FILES_ON_DISK = True`, disk write failure safely returns HTTP 500 (`"Document parsing failed: [Errno 28] No space left on device"`). No corrupt or partial database record was committed.
3. **Permission Denied (`EACCES`):** Returned HTTP 500 without crashing the FastAPI process.
4. **Oversized Upload (>15MB):** Correctly rejected before processing with HTTP 400 (`"File size (16.00 MB) exceeds maximum allowed limit of 15 MB"`).
5. **Non-PDF Extension:** Rejected with HTTP 400 (`"Unsupported file format '.exe'. Only verified PDF documents are supported."`).
6. **Corrupt PDF Header:** Rejected with HTTP 400 (`"Corrupted or invalid PDF header"`).

---

## 7. Priority 3.3 — Graceful Shutdown & Signal Handling

### 7.1 Container Lifecycle Contract
Render deploys web services inside Docker containers and signals lifecycle changes via:
- `SIGTERM`: Container termination notification (e.g. redeployment or restart).
- Render allows 30 seconds for graceful termination before issuing `SIGKILL`.

### 7.2 Uvicorn & FastAPI Lifespan Teardown
- Render `startCommand`: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
- Uvicorn intercepts `SIGTERM` and `SIGINT`:
  1. Stops accepting incoming TCP connections on `$PORT`.
  2. Awaits completion of in-flight requests.
  3. Exits FastAPI `lifespan` context manager.
  4. Executes post-yield cleanup:
     ```python
     logger.info("SchemeSathi AI shutdown initiated: disposing database connection pool...")
     from app.database import engine
     await anyio.to_thread.run_sync(engine.dispose)
     logger.info("SchemeSathi AI shutdown complete: database connections successfully drained.")
     ```

### 7.3 Live Lifespan Timing & Drain Measurement
Executed locally via `test_lifecycle`:
- **Startup Latency:** 123.71 ms (includes DB schema check and seed data synchronization).
- **Active Lifecycle:** Verified healthy database session creation during runtime.
- **Shutdown Latency:** **1.25 ms** (engine connection pool cleanly drained and disposed).
- **Total Overhead:** 124.95 ms.
- **HTTP Client Leaks:** Audited external HTTP calls in `backend/app/services/rag/generator.py`. External Gemini requests use scoped context managers (`with httpx.Client(timeout=httpx.Timeout(8.0, connect=3.0)) as client:`) ensuring zero persistent leaked sockets upon process exit.
- **Background Tasks:** No unmanaged background thread loops or detached asyncio tasks detected.

---

## 8. Priority 3.4 — Production Smoke Tests & Reliability Invariants

### 8.1 Frontend Reliability Smoke Test
- **Command:** `npm --prefix frontend run build` (`tsc && vite build`)
- **Modules Transformed:** 1,663
- **TypeScript Errors:** 0
- **Bundle Duration:** 9.45 s
- **Assets Generated:** Gzipped bundles with content hashes (`index-VXnk9PM9.js`, `index-DpFH9sNw.css`, route chunks).
- **SPA Routing Invariant:** `vercel.json` rewrite rule `{"source": "/(.*)", "destination": "/index.html"}` verified.
- **Security Headers Invariant:** Strict-Transport-Security, nosniff, DENY, and production Content-Security-Policy verified in `vercel.json`.

### 8.2 Backend Core Workflows Smoke Test

| Test # | Workflow / Endpoint | HTTP Status | Response Data Verification | Invariant Status |
|:---:|:---|:---:|:---|:---:|
| 1 | **Root Welcome** (`GET /`) | **200** | Returns API info, version `0.1.0`, docs link | **PASS** |
| 2 | **Liveness Probe** (`GET /api/health`) | **200** | Returns `status: "healthy"` in 6.0ms | **PASS** |
| 3 | **Readiness Probe** (`GET /api/ready`) | **200** | Returns `status: "ready"`, `database: "connected"` | **PASS** |
| 4 | **Scheme Catalog** (`GET /api/v1/schemes`) | **200** | 2 official welfare schemes returned | **PASS** |
| 5 | **Scholarship Catalog** (`GET /api/v1/scholarships`) | **200** | 3 official verified scholarships returned | **PASS** |
| 6 | **ScholarReady Evaluation** (`POST /api/v1/eligibility/evaluate-scholarships`) | **200** | 3 scholarships evaluated for student profile | **CONDITIONAL PASS** (Fails if `full_name` omitted) |
| 7 | **Citizen Discovery** (`POST /api/v1/eligibility/discover-schemes`) | **200** | 2 schemes evaluated for citizen profile | **CONDITIONAL PASS** (Fails if `full_name` omitted) |
| 8 | **RAG Consultation (EN)** (`POST /api/v1/chat/query`) | **200** | Grounded answer returned with official citations | **PASS** |
| 9 | **RAG Consultation (KN)** (`POST /api/v1/chat/query`) | **200** | Kannada multilingual query resolved with citations | **PASS** |
| 10 | **Sensitive Fields** (`GET /api/v1/eligibility/sensitive-fields`) | **200** | Civic rationale returned for sensitive profile data | **PASS** |
| 11 | **Dynamic Checklists** (`POST /api/v1/checklists/generate`) | **201** | Checklist generated with statutory requirements | **PASS** |
| 12 | **Security Headers** (All HTTP responses) | **200** | `nosniff`, `X-Frame-Options: DENY`, `CSP` present | **PASS** |

---

## 9. Backend Pytest Results

```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Users\VISHAL\OneDrive\Desktop\SchemeSathi-AI\backend
configfile: pytest.ini
collected 136 items

backend\tests\test_api_v1.py .........................                  [ 18%]
backend\tests\test_crud_documents_checklists.py ...                      [ 20%]
backend\tests\test_crud_profiles.py ..                                  [ 22%]
backend\tests\test_crud_schemes_scholarships.py ...                     [ 24%]
backend\tests\test_database.py ..                                       [ 25%]
backend\tests\test_document_intelligence.py ...............             [ 36%]
backend\tests\test_health.py ...                                        [ 38%]
backend\tests\test_multilingual_voice.py .......                        [ 43%]
backend\tests\test_phase_12_4_hardening.py ....................         [ 58%]
backend\tests\test_policy_explainer.py ...........                       [ 66%]
backend\tests\test_rag_and_citations.py .........                       [ 73%]
backend\tests\test_scheme_discovery.py .....                            [ 77%]
backend\tests\test_security_audit.py .................                  [ 89%]
backend\tests\test_system_integration.py ..........                     [ 97%]
backend\tests\test_verified_knowledge_base.py ....                    [100%]

======================= 136 passed, 2 warnings in 4.67s =======================
```
- **Total Tests:** 136
- **Passed:** 136 (100%)
- **Failed:** 0

---

## 10. Audit Findings & Defect Catalog

### Finding FINDING-REL-01: Pydantic Model `.get()` AttributeError on Omitted `full_name`
- **Severity:** **HIGH**
- **Classification:** **FAIL**
- **Affected File:** `backend/app/services/rule_engine.py` (Lines 474 and 676)
- **Functions:** `DeterministicRuleEngine.evaluate_all_scholarships` and `DeterministicRuleEngine.evaluate_scheme`
- **Defective Code:**
  ```python
  # Line 474:
  student_name = getattr(profile_input, "full_name", None) or profile_input.get("full_name")
  # Line 676:
  citizen_name = getattr(profile_input, "full_name", None) or profile_input.get("full_name")
  ```
- **Evidence:** When `profile_input` is an instance of `StudentEvaluationInput` or `CitizenEvaluationInput` (Pydantic `BaseModel`) and `full_name` is `None` or omitted from the request payload, `getattr(..., "full_name", None)` evaluates to `None`. The RHS of the `or` condition attempts to invoke `.get("full_name")` on the Pydantic instance, raising:
  `AttributeError: 'StudentEvaluationInput' object has no attribute 'get'`
  and generating an unhandled HTTP 500 error.
- **Impact:** Any citizen or student using the ScholarReady or Scheme Discovery forms who does not provide their full name experiences a 500 Internal Server Error.
- **Recommended Remediation:**
  Safely resolve the field depending on whether `profile_input` is a dictionary or an object:
  ```python
  student_name = profile_input.get("full_name") if isinstance(profile_input, dict) else getattr(profile_input, "full_name", None)
  ```
- **Production Intervention Required:** Yes (backend code patch required before production release).

---

### Finding FINDING-REL-02: Readiness Probe Short-Circuit Masks Database State During Storage Outage
- **Severity:** **LOW / INFORMATIONAL**
- **Classification:** **PARTIAL**
- **Affected File:** `backend/app/main.py` (`get_readiness_probe`, Lines 164–176)
- **Evidence:** During Scenario 6 (dual database outage and storage exhaustion <10MB), the readiness probe short-circuits at step 1 and returns:
  `{"status": "not_ready", "database": "connected", "disk": "exhausted", ...}`
  The `"database": "connected"` claim is returned without executing the database probe.
- **Impact:** Low. HTTP status is correctly 503 Service Unavailable, preventing traffic from reaching the container; however, diagnostic payload displays misleading database status during disk emergencies.
- **Recommended Remediation:** Execute the database probe or report `"database": "unverified"` when storage exhaustion triggers early return.
- **Production Intervention Required:** No (Non-blocking).

---

### Finding FINDING-REL-03: Raw `OSError` Detail Pass-through in Upload Handler
- **Severity:** **LOW**
- **Classification:** **PARTIAL**
- **Affected File:** `backend/app/api/v1/documents.py` (Line 49)
- **Evidence:** 
  ```python
  except Exception as e:
      raise HTTPException(status_code=500, detail=f"Document parsing failed: {str(e)}")
  ```
  If physical disk storage is enabled (`STORE_UPLOADED_FILES_ON_DISK = True`) and an `OSError` occurs during file write, `str(e)` may leak raw host errno strings (e.g. `[Errno 28] No space left on device` or host paths in `PermissionError`).
- **Impact:** Low in default configuration (`STORE_UPLOADED_FILES_ON_DISK = False`), as files are processed in memory.
- **Recommended Remediation:** Log `str(e)` internally and return a sanitized user-facing error message.
- **Production Intervention Required:** No (Non-blocking).

---

## 11. Unverified and Deferred Items

1. **Hardware-Level SIGTERM on Render Free Tier:**
   - *Status:* DEFERRED to live staging deployment.
   - *Reason:* Physical SIGTERM emission requires stopping an active Render cloud container instance, which is unsafe during local read-only audit. Verified locally via uvicorn lifespan harness.
2. **PostgreSQL High-Concurrency Connection Starvation (100+ concurrent clients):**
   - *Status:* DEFERRED to load testing phase.
   - *Reason:* Current test environment uses local SQLite; production PostgreSQL connection pool parameters (`pool_size=10, max_overflow=20`) are configured but require an external load generator against a cloud staging database.

---

## 12. Production Risk Assessment

| Risk Category | Severity | Probability | Mitigation Present in SchemeSathi | Residual Risk |
|:---|:---:|:---:|:---|:---:|
| **Unhandled 500 on Evaluation without Name** | HIGH | HIGH | Form validation requires name in UI, but API accepts optional name | **Active Risk (Fix required: FINDING-REL-01)** |
| **Spurious Container Restarts on DB Reboot** | HIGH | LOW | `/api/health` liveness probe does not probe DB | **Negligible (Protected)** |
| **Container Disk Exhaustion during Uploads** | HIGH | LOW | Option A In-Memory processing is default (`STORE_UPLOADED_FILES_ON_DISK=False`) | **Negligible (Protected)** |
| **Database Pool Leak on Deployments** | MEDIUM | LOW | `engine.dispose()` executed in lifespan shutdown | **Negligible (Protected)** |
| **Slow External API Hanging Worker Threads** | HIGH | LOW | Gemini API calls have strict 8s timeout with fallback to local engine | **Negligible (Protected)** |

---

## 13. Recommended Remediation Order

1. **Phase 12.4.3 (Immediate Pre-Release Patch):**
   - Patch `backend/app/services/rule_engine.py` (Lines 474 and 676) to resolve `student_name` and `citizen_name` safely across both dictionary and Pydantic model inputs without calling `.get()` on `BaseModel` instances.
   - Add unit test in `backend/tests/test_scheme_discovery.py` and `test_system_integration.py` passing payloads where `full_name` is omitted.
2. **Phase 12.5 (Minor Diagnostics Cleanup):**
   - Refactor `get_readiness_probe()` in `main.py` so that storage and database probes run independently before assembling the final diagnostic dictionary.
   - Sanitize `detail` in `documents.py` upload exception handler.

---

## 14. Final Git Status & Compliance Confirmation

```
On branch main
Your branch is up to date with 'origin/main'.
Untracked files:
  docs/ACCIDENTAL_BOLKHATA_CLEANUP_REPORT.md
  docs/PHASE_12_4_PRIORITY_3_RELIABILITY_AUDIT.md
nothing added to commit but untracked files present
```

### Safety & Integrity Confirmations
- [x] Zero application source code files modified.
- [x] Zero production configuration files modified.
- [x] Zero Render or Vercel settings modified.
- [x] Zero environment variables changed.
- [x] Zero database records deleted or corrupted.
- [x] Zero git commits, pushes, merges, rebases, or resets executed.
- [x] `C:\Users\VISHAL\OneDrive\Desktop\BolKhata AI` completely untouched and isolated.
