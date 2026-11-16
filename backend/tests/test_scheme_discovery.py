import pytest
from fastapi.testclient import TestClient

from app.database import SessionLocal, init_db
from app.main import app
from app.models.scheme import GovernmentScheme
from app.schemas.common import EligibilityEvaluationStatus
from app.schemas.eligibility import CitizenEvaluationInput
from app.services.opportunity_service import OpportunityService
from app.services.rule_engine import DeterministicRuleEngine


@pytest.fixture(scope="module")
def db_session():
    init_db()
    session = SessionLocal()
    yield session
    session.close()


client = TestClient(app)


# ============================================================================
# Unit Tests: Deterministic Scheme Evaluation
# ============================================================================

def test_pm_kisan_eligible_farmer(db_session):
    """Test eligible farmer meeting both landholding and tax exclusion in verified records."""
    service = OpportunityService(db_session)
    scheme = service.get_scheme("SCHEME-PM-KISAN")

    profile = CitizenEvaluationInput(
        full_name="Basavaraj Patil",
        domicile_state="Karnataka",
        district="Belagavi",
        occupation="Farmer",
        landholding_hectares=1.8,
        is_income_tax_payer=False,
    )

    result = DeterministicRuleEngine.evaluate_scheme(scheme, profile)
    assert result.overall_status == EligibilityEvaluationStatus.MEETS_REQUIREMENT
    assert result.match_score == 100.0
    assert len(result.requirements_satisfied) == 2
    assert len(result.requirements_not_satisfied) == 0
    assert len(result.missing_information) == 0
    assert "You meet all verified statutory eligibility conditions" in result.suggested_next_actions[0]
    assert result.official_source_title is not None
    assert "pmkisan.gov.in" in result.official_source_url


def test_pm_kisan_tax_payer_exclusion(db_session):
    """Test disqualification under statutory exclusion Clause 5(b)(vi) for income tax payer."""
    service = OpportunityService(db_session)
    scheme = service.get_scheme("SCHEME-PM-KISAN")

    profile = CitizenEvaluationInput(
        full_name="Rajesh Kumar",
        occupation="Farmer",
        landholding_hectares=2.5,
        is_income_tax_payer=True,  # Disqualifier under Clause 5(b)(vi)
    )

    result = DeterministicRuleEngine.evaluate_scheme(scheme, profile)
    assert result.overall_status == EligibilityEvaluationStatus.DOES_NOT_MEET_REQUIREMENT
    assert len(result.requirements_not_satisfied) == 1
    failed_item = result.requirements_not_satisfied[0]
    assert failed_item.rule_id == "RULE-PMKISAN-EXCLUSION-IT"
    assert "Clause 5(b)(vi)" in failed_item.clause_or_section
    assert "Does Not Meet" in failed_item.explanation


def test_pm_kisan_missing_landholding(db_session):
    """Test evaluation when landholding is omitted (never guess values)."""
    service = OpportunityService(db_session)
    scheme = service.get_scheme("SCHEME-PM-KISAN")

    profile = CitizenEvaluationInput(
        full_name="Suresh Patil",
        occupation="Farmer",
        is_income_tax_payer=False,
        landholding_hectares=None,  # Missing
    )

    result = DeterministicRuleEngine.evaluate_scheme(scheme, profile)
    assert result.overall_status == EligibilityEvaluationStatus.MISSING_INFORMATION
    assert len(result.missing_information) == 1
    assert result.missing_information[0].rule_id == "RULE-PMKISAN-LAND"
    assert "Missing input: 'landholding_hectares'" in result.missing_information[0].explanation


def test_pm_kisan_negative_landholding_needs_review(db_session):
    """Test that impossible contradictory data triggers NEEDS_REVIEW."""
    service = OpportunityService(db_session)
    scheme = service.get_scheme("SCHEME-PM-KISAN")

    profile = CitizenEvaluationInput(
        full_name="Contradictory Input",
        landholding_hectares=-2.5,  # Contradictory negative value
        is_income_tax_payer=False,
    )

    result = DeterministicRuleEngine.evaluate_scheme(scheme, profile)
    assert result.overall_status == EligibilityEvaluationStatus.NEEDS_REVIEW
    assert len(result.conditions_under_review) == 1
    assert "Cultivable landholding cannot be negative" in result.conditions_under_review[0].explanation


def test_gruha_lakshmi_eligible_woman_head(db_session):
    """Test Gruha Lakshmi eligibility for female head of household in Karnataka."""
    service = OpportunityService(db_session)
    scheme = service.get_scheme("SCHEME-KAR-GRUHA-LAKSHMI")

    profile = CitizenEvaluationInput(
        full_name="Savita Gowda",
        gender="Female",
        domicile_state="Karnataka",
        district="Mandya",
        occupation="Homemaker",
        is_income_tax_payer=False,
    )

    result = DeterministicRuleEngine.evaluate_scheme(scheme, profile)
    assert result.overall_status == EligibilityEvaluationStatus.MEETS_REQUIREMENT
    assert result.match_score == 100.0
    assert len(result.requirements_satisfied) == 3
    assert len(result.requirements_not_satisfied) == 0


def test_gruha_lakshmi_disqualified_by_gender(db_session):
    """Test male applicant is disqualified for Gruha Lakshmi."""
    service = OpportunityService(db_session)
    scheme = service.get_scheme("SCHEME-KAR-GRUHA-LAKSHMI")

    profile = CitizenEvaluationInput(
        full_name="Kiran Kumar",
        gender="Male",  # Gruha Lakshmi requires Female
        domicile_state="Karnataka",
        is_income_tax_payer=False,
    )

    result = DeterministicRuleEngine.evaluate_scheme(scheme, profile)
    assert result.overall_status == EligibilityEvaluationStatus.DOES_NOT_MEET_REQUIREMENT
    assert any(r.rule_id == "RULE-GL-GENDER-HEAD" for r in result.requirements_not_satisfied)


def test_gruha_lakshmi_disqualified_by_domicile(db_session):
    """Test non-Karnataka applicant is disqualified."""
    service = OpportunityService(db_session)
    scheme = service.get_scheme("SCHEME-KAR-GRUHA-LAKSHMI")

    profile = CitizenEvaluationInput(
        full_name="Sunita Sharma",
        gender="Female",
        domicile_state="Maharashtra",  # Non-Karnataka
        is_income_tax_payer=False,
    )

    result = DeterministicRuleEngine.evaluate_scheme(scheme, profile)
    assert result.overall_status == EligibilityEvaluationStatus.DOES_NOT_MEET_REQUIREMENT
    assert any(r.rule_id == "RULE-GL-DOMICILE" for r in result.requirements_not_satisfied)


# ============================================================================
# Multi-Scheme Discovery Ranking & Priority Tests
# ============================================================================

def test_scheme_discovery_ranking(db_session):
    """Test ranking where matching scheme is sorted ahead of non-matching scheme."""
    service = OpportunityService(db_session)
    schemes = [
        service.get_scheme("SCHEME-PM-KISAN"),
        service.get_scheme("SCHEME-KAR-GRUHA-LAKSHMI"),
    ]

    # Profile: Male Farmer from Uttar Pradesh
    # Expected: PM-KISAN -> MEETS_REQUIREMENT (ranked 1st)
    #           Gruha Lakshmi -> DOES_NOT_MEET_REQUIREMENT (ranked 2nd)
    profile = CitizenEvaluationInput(
        full_name="Ramesh Singh",
        gender="Male",
        domicile_state="Uttar Pradesh",
        occupation="Farmer",
        landholding_hectares=1.2,
        is_income_tax_payer=False,
    )

    summary = DeterministicRuleEngine.evaluate_all_schemes(schemes, profile)
    assert summary.total_schemes_evaluated == 2
    assert summary.eligible_count == 1
    assert summary.ineligible_count == 1

    # First ranked scheme must be the eligible one (PM-KISAN)
    assert summary.schemes[0].scheme_id == "SCHEME-PM-KISAN"
    assert summary.schemes[0].overall_status == EligibilityEvaluationStatus.MEETS_REQUIREMENT
    assert summary.schemes[1].scheme_id == "SCHEME-KAR-GRUHA-LAKSHMI"
    assert summary.schemes[1].overall_status == EligibilityEvaluationStatus.DOES_NOT_MEET_REQUIREMENT


# ============================================================================
# API Endpoint Integration Tests
# ============================================================================

def test_api_sensitive_fields_explanation():
    """Test API endpoint returning explanation for sensitive data fields."""
    response = client.get("/api/v1/eligibility/sensitive-fields")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3
    fields = [item["field_name"] for item in data]
    assert "is_income_tax_payer" in fields
    assert "landholding_hectares" in fields
    assert "bpl_card_holder" in fields


def test_api_evaluate_single_scheme():
    """Test API endpoint POST /api/v1/eligibility/evaluate-scheme/{id}."""
    payload = {
        "full_name": "Parvati Devi",
        "gender": "Female",
        "domicile_state": "Karnataka",
        "district": "Dharwad",
        "is_income_tax_payer": False,
    }
    response = client.post("/api/v1/eligibility/evaluate-scheme/SCHEME-KAR-GRUHA-LAKSHMI", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["scheme_id"] == "SCHEME-KAR-GRUHA-LAKSHMI"
    assert data["overall_status"] == "MEETS_REQUIREMENT"
    assert data["match_score"] == 100.0
    assert len(data["requirements_satisfied"]) == 3
    assert len(data["required_documents"]) >= 1
    assert "Gruha Lakshmi" in data["official_source_title"]


def test_api_discover_schemes_with_filter():
    """Test API endpoint POST /api/v1/eligibility/discover-schemes with category filter."""
    payload = {
        "full_name": "Anand Rao",
        "occupation": "Farmer",
        "landholding_hectares": 2.0,
        "is_income_tax_payer": False,
    }
    response = client.post(
        "/api/v1/eligibility/discover-schemes",
        params={"category": "Agriculture & Farming"},
        json=payload,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_schemes_evaluated"] == 1
    assert data["eligible_count"] == 1
    assert data["schemes"][0]["scheme_id"] == "SCHEME-PM-KISAN"
