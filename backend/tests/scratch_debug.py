import sys
sys.path.insert(0, "backend")

print("1. Importing app")
from app.main import app

print("2. Creating TestClient")
from fastapi.testclient import TestClient
client = TestClient(app)

print("3. Calling /openapi.json")
res = client.get("/openapi.json")
print("4. Done, status:", res.status_code)
