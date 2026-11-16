from datetime import date
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.schemas.common import EligibilityEvaluationStatus
from app.schemas.rule import EligibilityRuleCreate
from app.schemas.scholarship import ScholarshipCreate
from app.schemas.source import OfficialSourceCreate
from app.services.opportunity_service import OpportunityService

# In-memory SQLite with StaticPool so all requests share the in-memory schema
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    service = OpportunityService(session)

    # Seed test source, scholarship, and rule
    source = service.create_source(
        OfficialSourceCreate(
            id="SRC-TEST-MOE-CSSS",
            source_title="Ministry of Education CSSS Guidelines",
            issuing_authority="Department of Higher Education",
            circular_number="F.No. 1-1/2022-NS-I",
            notification_date=date(2023, 4, 1),
            official_url="https://scholarships.gov.in/",
        )
    )

    scholarship = service.create_scholarship(
        ScholarshipCreate(
            id="SCH-TEST-CSSS",
            official_name="Central Sector Scheme of Scholarship (CSSS)",
            category="Education & Scholarships",
            description="College scholarship assistance.",
            government_department="Ministry of Education",
            official_source_url="https://scholarships.gov.in/",
            academic_cycle="2024-25",
            verification_date=date(2024, 11, 1),
            level="National / Central",
            course_level="Undergraduate",
            max_annual_income=450000.0,
            benefit_amount_annual="₹12,000/year",
            official_source_id=source.id,
        )
    )

    service.create_rule(
        EligibilityRuleCreate(
            id="RULE-TEST-CSSS-INCOME",
            scholarship_id=scholarship.id,
            requirement_description="Parental annual income must not exceed ₹4,50,000.",
            rule_type="INCOME_CAP",
            structured_condition={"field": "annual_family_income", "operator": "LTE", "value": 450000.0},
            source_id=source.id,
            clause_or_section="Clause 4.1.2",
            applicable_cycle="2024-25",
        )
    )
    service.create_rule(
        EligibilityRuleCreate(
            id="RULE-TEST-CSSS-MARKS",
            scholarship_id=scholarship.id,
            requirement_description="Scored >= 80% in qualifying board exam.",
            rule_type="PERCENTILE_CUTOFF",
            structured_condition={"field": "marks_percentage", "operator": "GTE", "value": 80.0},
            source_id=source.id,
            clause_or_section="Clause 4.1.1",
            applicable_cycle="2024-25",
        )
    )
    session.close()

    yield
    Base.metadata.drop_all(bind=test_engine)


def test_openapi_schema_generated():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "paths" in schema
    assert "/api/v1/users" in schema["paths"]
    assert "/api/v1/scholarships" in schema["paths"]
    assert "/api/v1/schemes" in schema["paths"]
    assert "/api/v1/eligibility/evaluate-scholarship/{scholarship_id}" in schema["paths"]
    assert "/api/v1/eligibility/evaluate-scholarships" in schema["paths"]


def test_api_user_and_profile_flow():
    # 1. Create User
    user_payload = {
        "full_name": "Deepak Kumar",
        "email": "deepak.kumar@test.gov.in",
        "phone_number": "+919876543000",
        "role": "STUDENT",
    }
    res = client.post("/api/v1/users", json=user_payload)
    assert res.status_code == 201
    user_data = res.json()
    user_id = user_data["id"]

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
    assert res_prof.status_code == 201
    prof_data = res_prof.json()
    assert prof_data["annual_family_income"] == 150000.0


def test_api_scheme_and_source_flow():
    source_payload = {
        "id": "SRC-NHA-PMJAY-2024",
        "source_title": "Ayushman Bharat PM-JAY Operational Guidelines",
        "issuing_authority": "National Health Authority",
        "circular_number": "NHA/AB-PMJAY/2024/02",
        "notification_date": "2024-03-01",
        "official_url": "https://pmjay.gov.in",
    }
    res_src = client.post("/api/v1/sources", json=source_payload)
    assert res_src.status_code == 201

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
    assert res_scheme.status_code == 201

    res_list = client.get("/api/v1/schemes", params={"category": "Healthcare & Ayushman"})
    assert res_list.status_code == 200
    schemes = res_list.json()
    assert len(schemes) == 1
    assert schemes[0]["id"] == "SCHEME-PM-JAY-2024"


def test_api_eligibility_evaluate_single():
    """Tests POST /api/v1/eligibility/evaluate-scholarship/{scholarship_id}."""
    payload = {
        "full_name": "Priya Sharma",
        "marks_percentage": 86.0,
        "annual_family_income": 320000.0,
        "other_scholarship_recipient": False,
    }
    res = client.post("/api/v1/eligibility/evaluate-scholarship/SCH-TEST-CSSS", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["scholarship_id"] == "SCH-TEST-CSSS"
    assert data["overall_status"] == EligibilityEvaluationStatus.MEETS_REQUIREMENT
    assert data["match_score"] == 100.0
    assert len(data["requirements_satisfied"]) == 2


def test_api_eligibility_evaluate_all():
    """Tests POST /api/v1/eligibility/evaluate-scholarships."""
    payload = {
        "full_name": "Rahul Verma",
        "marks_percentage": 75.0,  # Below 80% cutoff for CSSS
        "annual_family_income": 300000.0,
    }
    res = client.post("/api/v1/eligibility/evaluate-scholarships", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["total_scholarships_evaluated"] >= 1
    # Check that Rahul didn't meet marks cutoff
    csss_res = next(s for s in data["scholarships"] if s["scholarship_id"] == "SCH-TEST-CSSS")
    assert csss_res["overall_status"] == EligibilityEvaluationStatus.DOES_NOT_MEET_REQUIREMENT
    assert len(csss_res["requirements_not_satisfied"]) == 1
    assert csss_res["requirements_not_satisfied"][0]["rule_id"] == "RULE-TEST-CSSS-MARKS"
