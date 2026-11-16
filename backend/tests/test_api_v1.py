from datetime import date
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    init_db()


def test_openapi_schema_generated():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "paths" in schema
    assert "/api/v1/users" in schema["paths"]
    assert "/api/v1/scholarships" in schema["paths"]
    assert "/api/v1/schemes" in schema["paths"]
    assert "/api/v1/profiles/student" in schema["paths"]
    assert "/api/v1/profiles/citizen" in schema["paths"]
    assert "/api/v1/rules" in schema["paths"]
    assert "/api/v1/documents" in schema["paths"]
    assert "/api/v1/checklists" in schema["paths"]
    assert "/api/v1/chat/sessions" in schema["paths"]


def test_api_user_and_profile_flow():
    # 1. Create User
    user_payload = {
        "full_name": "Deepak Kumar",
        "email": "deepak.kumar@test.gov.in",
        "phone_number": "+919876543000",
        "role": "STUDENT",
    }
    res = client.post("/api/v1/users", json=user_payload)
    assert res.status_code in (201, 200, 409)  # Handle if previously created
    if res.status_code == 409:
        user_list = client.get("/api/v1/users").json()
        user_id = next(u["id"] for u in user_list if u["email"] == "deepak.kumar@test.gov.in")
    else:
        user_id = res.json()["id"]

    # 2. Create Student Profile
    profile_payload = {
        "user_id": user_id,
        "full_name": "Deepak Kumar",
        "domicile_state": "Karnataka",
        "category": "SC",
        "annual_family_income": 150000.0,
        "current_course": "Diploma in Mechanical Engineering",
        "year_of_study": "2nd Year",
        "marks_percentage": 78.5,
        "gender": "Male",
        "disability_status": False,
        "hosteller_status": "Day Scholar",
        "extra_attributes": {},
    }
    res_prof = client.post("/api/v1/profiles/student", json=profile_payload)
    assert res_prof.status_code in (201, 200)
    prof_data = res_prof.json()
    assert prof_data["annual_family_income"] == 150000.0


def test_api_scheme_and_source_flow():
    # 1. Create Source
    source_payload = {
        "id": "SRC-NHA-PMJAY-2024",
        "source_title": "Ayushman Bharat PM-JAY Operational Guidelines",
        "issuing_authority": "National Health Authority",
        "circular_number": "NHA/AB-PMJAY/2024/02",
        "notification_date": "2024-03-01",
        "official_url": "https://pmjay.gov.in",
        "notes": "Verified national health cover circular",
    }
    res_src = client.post("/api/v1/sources", json=source_payload)
    assert res_src.status_code in (201, 200)

    # 2. Create Scheme
    scheme_payload = {
        "id": "SCHEME-PM-JAY-2024",
        "official_name": "Ayushman Bharat Pradhan Mantri Jan Arogya Yojana",
        "category": "Healthcare & Ayushman",
        "description": "Health assurance scheme providing ₹5,00,000 cashless hospitalization cover per family.",
        "government_department": "National Health Authority",
        "official_source_url": "https://pmjay.gov.in",
        "application_url": "https://setu.pmjay.gov.in",
        "policy_cycle": "Continuous",
        "verification_date": "2024-10-15",
        "level": "Central",
        "benefit_type": "Health Insurance Cover",
        "annual_benefit": "₹5,00,000 / family / year",
        "target_beneficiaries": "Vulnerable families identified under SECC 2011",
        "official_source_id": "SRC-NHA-PMJAY-2024",
    }
    res_scheme = client.post("/api/v1/schemes", json=scheme_payload)
    assert res_scheme.status_code in (201, 200)

    # 3. List Schemes with category filter using params dict for proper URL encoding
    res_list = client.get("/api/v1/schemes", params={"category": "Healthcare & Ayushman"})
    assert res_list.status_code == 200
    schemes = res_list.json()
    assert len(schemes) >= 1
    assert any(s["id"] == "SCHEME-PM-JAY-2024" for s in schemes)
