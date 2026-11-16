from app.api.v1.health import health_check
from app.main import get_root_health, root


def test_root_endpoint():
    response = root()
    assert "SchemeSathi AI" in response["message"]


def test_api_health_endpoint():
    response = get_root_health()
    assert response == {
        "status": "healthy",
        "application": "SchemeSathi AI",
    }


def test_api_v1_health_endpoint():
    response = health_check()
    assert response["status"] == "healthy"
    assert response["application"] == "SchemeSathi AI"
