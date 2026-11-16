import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "SchemeSathi AI" in data["message"]


def test_api_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "application": "SchemeSathi AI",
    }


def test_api_v1_health_endpoint(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["application"] == "SchemeSathi AI"

