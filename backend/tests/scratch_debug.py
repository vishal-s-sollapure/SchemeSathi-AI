import sys
sys.path.insert(0, "backend")

print("START SCRIPT", flush=True)

from fastapi import FastAPI
from fastapi.testclient import TestClient

t1 = FastAPI()
print("1. Testing TestClient on empty FastAPI app...", flush=True)
c1 = TestClient(t1)
print("1. Empty app TestClient created!", flush=True)

from fastapi.middleware.cors import CORSMiddleware
t1.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
print("2. Testing TestClient with CORS...", flush=True)
c2 = TestClient(t1)
print("2. CORS TestClient created!", flush=True)

print("3. Importing eligibility router...", flush=True)
from app.api.v1.eligibility import router as el_router
print("3. Eligibility router imported!", flush=True)

t3 = FastAPI()
t3.include_router(el_router)
print("4. Testing TestClient with eligibility router...", flush=True)
c3 = TestClient(t3)
print("4. Eligibility TestClient created!", flush=True)




