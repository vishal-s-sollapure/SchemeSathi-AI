# SchemeSathi AI 🇮🇳

> **AI-Powered Government Benefits & Scholarship Readiness Assistant**  
> Built for the **NxtWave IDEA//FORGE Online Hackathon**.

SchemeSathi AI bridges Indian students and citizens with government welfare schemes, scholarships, policies, and entitlements through deterministic eligibility verification, source-grounded citations, and multilingual guidance.

---

## 🌟 Architecture & Core Modules

SchemeSathi AI integrates two complementary user-facing modules on a unified intelligence architecture:

1. **ScholarReady**:
   - Central & State scholarship discovery (e.g. NSP, Karnataka SSP).
   - Student academic & socio-economic profile management.
   - Deterministic 4-status rule evaluation (`MEETS_REQUIREMENT`, `DOES_NOT_MEET_REQUIREMENT`, `MISSING_INFORMATION`, `NEEDS_REVIEW`).
   - Dynamic document checklists & PyMuPDF-based application readiness analysis.

2. **SchemeSathi**:
   - Citizen welfare scheme & subsidy discovery.
   - Multilingual Q&A (English, Kannada, Hindi).
   - Source-grounded government circular citations and policy simplification.
   - Transparent, verifiable application instructions.

---

## 🛠️ Technology Stack

- **Frontend**: React 18, Vite, TypeScript, Tailwind CSS, React Router, Lucide Icons, Axios.
- **Backend**: Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.0.
- **Database**: SQLite (local with WAL mode) with seamless migration path to PostgreSQL.
- **Testing**: Pytest, Vite Build TypeScript validation.

---

## 📁 Repository Structure

```
SchemeSathi-AI/
├── .gitignore
├── README.md
│
├── backend/
│   ├── .env.example
│   ├── .env
│   ├── requirements.txt
│   ├── pytest.ini
│   ├── run.py                       # Uvicorn runner
│   │
│   ├── app/
│   │   ├── main.py                  # FastAPI app & CORS configuration
│   │   ├── config.py                # Pydantic BaseSettings
│   │   ├── database.py              # SQLAlchemy engine & session factory
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── health.py        # /api/v1/health route
│   │   │       └── router.py        # API v1 central router
│   │   ├── models/                  # Database models
│   │   ├── schemas/                 # Pydantic validation schemas
│   │   └── services/                # Business & rule engine services
│   └── tests/
│       └── test_health.py           # API health tests
│
└── frontend/
    ├── package.json
    ├── vite.config.ts
    ├── tailwind.config.js
    ├── postcss.config.js
    ├── tsconfig.json
    ├── .env.example
    ├── .env
    └── src/
        ├── App.tsx                  # Main civic portal shell & health monitor
        ├── main.tsx                 # React entrypoint
        ├── index.css                # Tailwind base styles
        ├── services/
        │   └── api.ts               # Axios client
        └── vite-env.d.ts
```

---

## 🚀 Local Development Setup

### 1. Prerequisites
- **Node.js**: v20.x or higher
- **Python**: v3.11 or v3.12
- **Git**

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create and activate Python virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
python -m pip install -r requirements.txt

# Start FastAPI backend server
python run.py
# Server runs on: http://127.0.0.1:8000
# OpenAPI Docs: http://127.0.0.1:8000/docs
```

### 3. Frontend Setup
```bash
# In a new terminal, navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Start Vite development server
npm run dev
# Frontend runs on: http://localhost:5173
```

---

## 🧪 Verification & Testing

### Backend Health Check Test
```bash
# Run pytest test suite
.venv\Scripts\python.exe -m pytest -c backend/pytest.ini backend/tests
```

### Direct Health Check Probe
```bash
curl http://127.0.0.1:8000/api/health
```
**Expected Response:**
```json
{
  "status": "healthy",
  "application": "SchemeSathi AI"
}
```

### Frontend Build Validation
```bash
cd frontend
npm run build
```
Generates production bundle with zero TypeScript and CSS errors.

---

## 🔒 Security & Quality Principles
- **Strictly Deterministic Rules**: LLMs never invent eligibility conditions.
- **Traceable Government Citations**: All official scheme conditions are grounded with verified source metadata.
- **Document Integrity**: User documents are analyzed for readiness markers, never assumed as forged proof of authenticity.
- **Environment Isolation**: No credentials or secrets committed to repository.
