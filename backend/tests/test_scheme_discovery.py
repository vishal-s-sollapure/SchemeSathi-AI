import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.rule import EligibilityRule, Requirement
from app.models.scheme import GovernmentScheme
from app.models.source import OfficialSource
from app.schemas.common import EligibilityEvaluationStatus
from app.schemas.eligibility import CitizenEvaluationInput
from app.services.rule_engine import DeterministicRuleEngine


# In-memory SQLite with StaticPool for test isolation
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    # Seed Official Sources
    src_pmkisan = OfficialSource(
        id="SRC-MOA-PMKISAN-T",
        source_title="Revised Operational Guidelines for PM-KISAN",
        issuing_authority="Ministry of Agriculture & Farmers Welfare, GoI",
        circular_number="1-1/2019-Credit-II",
        notification_date=date(2020, 3, 1),
        official_url="https://pmkisan.gov.in/",
    )
    src_gl = OfficialSource(
        id="SRC-KRN-DWCD-GL-T",
        source_title="Government Order on Gruha Lakshmi Scheme",
        issuing_authority="Department of Women and Child Development, Karnataka",
        circular_number="GO-WCD-41-WES-2023",
        notification_date=date(2023, 6, 5),
        official_url="https://sevasindhugs.karnataka.gov.in/",
    )
    session.add_all([src_pmkisan, src_gl])
    session.commit()

    # Seed PM-KISAN Scheme
    pm_kisan = GovernmentScheme(
        id="SCHEME-PM-KISAN",
        official_name="Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
        category="Agriculture & Farming",
        description="Assistance of ₹6,000 per annum to cultivable landholding farmer families.",
        government_department="Department of Agriculture and Farmers Welfare",
        official_source_url="https://pmkisan.gov.in/",
        application_url="https://pmkisan.gov.in/RegistrationFormNew.aspx",
        policy_cycle="Continuous (FY 2024-25 / 2025-26)",
        verification_date=date(2024, 11, 1),
        level="Central",
        benefit_type="Direct Benefit Transfer (DBT)",
        annual_benefit="₹6,000 / year",
        target_beneficiaries="Cultivable landholder farmer families",
        official_source_id="SRC-MOA-PMKISAN-T",
    )

    # Seed Karnataka Gruha Lakshmi Scheme
    gruha_lakshmi = GovernmentScheme(
        id="SCHEME-KAR-GRUHA-LAKSHMI",
        official_name="Karnataka Gruha Lakshmi Scheme",
        category="Social Security & Pensions",
        description="Monthly financial assistance of ₹2,000 to female head of household (Yajamani).",
        government_department="Department of Women and Child Development, Karnataka",
        official_source_url="https://sevasindhugs.karnataka.gov.in/",
        application_url="https://sevasindhu.karnataka.gov.in/Gruhalakshmi/",
        policy_cycle="Continuous (FY 2024-25 / 2025-26)",
        verification_date=date(2024, 11, 1),
        level="State (Karnataka)",
        benefit_type="Direct Benefit Transfer (DBT)",
        annual_benefit="₹24,000 / year",
        target_beneficiaries="Female head of household (Yajamani) in Karnataka",
        official_source_id="SRC-KRN-DWCD-GL-T",
    )
    session.add_all([pm_kisan, gruha_lakshmi])
    session.commit()

    # Seed PM-KISAN Rules
    r_pmk_land = EligibilityRule(
        id="RULE-PMKISAN-LAND-T",
        scheme_id="SCHEME-PM-KISAN",
        requirement_description="Must own cultivable agricultural land.",
        rule_type="LAND_CRITERION",
        structured_condition={"field": "landholding_hectares", "operator": "GT", "value": 0.0},
        source_id="SRC-MOA-PMKISAN-T",
        page_number="2",
        clause_or_section="Clause 3.1",
        applicable_cycle="Continuous",
        is_mandatory=True,
    )
    r_pmk_tax = EligibilityRule(
        id="RULE-PMKISAN-IT-T",
        scheme_id="SCHEME-PM-KISAN",
        requirement_description="Must not have paid income tax in last assessment year.",
        rule_type="EXCLUSION_CHECK",
        structured_condition={"field": "is_income_tax_payer", "operator": "EQ", "value": False},
        source_id="SRC-MOA-PMKISAN-T",
        page_number="4",
        clause_or_section="Clause 5(b)(vi)",
        applicable_cycle="Continuous",
        is_mandatory=True,
        failure_guidance="Income tax payers are excluded under Clause 5.",
    )

    # Seed Gruha Lakshmi Rules
    r_gl_gender = EligibilityRule(
        id="RULE-GL-GENDER-T",
        scheme_id="SCHEME-KAR-GRUHA-LAKSHMI",
        requirement_description="Applicant must be the female head of family.",
        rule_type="GENDER_CRITERION",
        structured_condition={"field": "gender", "operator": "EQ", "value": "Female"},
        source_id="SRC-KRN-DWCD-GL-T",
        page_number="2",
        clause_or_section="Clause 2",
        applicable_cycle="Continuous",
        is_mandatory=True,
    )
    r_gl_domicile = EligibilityRule(
        id="RULE-GL-DOMICILE-T",
        scheme_id="SCHEME-KAR-GRUHA-LAKSHMI",
        requirement_description="Resident of Karnataka with ration card.",
        rule_type="DOMICILE_CRITERION",
        structured_condition={"field": "domicile_state", "operator": "EQ", "value": "Karnataka"},
        source_id="SRC-KRN-DWCD-GL-T",
        page_number="2",
        clause_or_section="Clause 3",
        applicable_cycle="Continuous",
        is_mandatory=True,
    )
    r_gl_tax = EligibilityRule(
        id="RULE-GL-IT-T",
        scheme_id="SCHEME-KAR-GRUHA-LAKSHMI",
        requirement_description="Applicant or spouse must not be income tax payer.",
        rule_type="EXCLUSION_CHECK",
        structured_condition={"field": "is_income_tax_payer", "operator": "EQ", "value": False},
        source_id="SRC-KRN-DWCD-GL-T",
        page_number="3",
        clause_or_section="Clause 4",
        applicable_cycle="Continuous",
        is_mandatory=True,
    )

    # Seed Requirements
    doc_pmk = Requirement(
        id="REQ-PMK-LAND-T",
        scheme_id="SCHEME-PM-KISAN",
        title="Land Record (ROR / Patta)",
        document_type="LAND_REVENUE_RECORD",
        is_mandatory=True,
    )
    doc_gl = Requirement(
        id="REQ-GL-RC-T",
        scheme_id="SCHEME-KAR-GRUHA-LAKSHMI",
        title="Karnataka Ration Card",
        document_type="RATION_CARD",
        is_mandatory=True,
    )

    session.add_all([r_pmk_land, r_pmk_tax, r_gl_gender, r_gl_domicile, r_gl_tax, doc_pmk, doc_gl])
    session.commit()

    yield session

    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# ============================================================================
# Unit Tests: Deterministic Scheme Evaluation
# ============================================================================

def test_pm_kisan_eligible_farmer(db_session):
    """Test eligible farmer meeting both landholding and tax exclusion."""
    scheme = db_session.query(GovernmentScheme).filter_by(id="SCHEME-PM-KISAN").first()
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


def test_pm_kisan_tax_payer_exclusion(db_session):
    """Test disqualification under statutory exclusion Clause 5(b)(vi) for income tax payer."""
    scheme = db_session.query(GovernmentScheme).filter_by(id="SCHEME-PM-KISAN").first()
    profile = CitizenEvaluationInput(
        full_name="Rajesh Kumar",
        occupation="Farmer",
        landholding_hectares=2.5,
        is_income_tax_payer=True,  # Disqualifier
    )

    result = DeterministicRuleEngine.evaluate_scheme(scheme, profile)
    assert result.overall_status == EligibilityEvaluationStatus.DOES_NOT_MEET_REQUIREMENT
    assert len(result.requirements_not_satisfied) == 1
    failed_item = result.requirements_not_satisfied[0]
    assert failed_item.rule_id == "RULE-PMKISAN-IT-T"
    assert "Clause 5(b)(vi)" in failed_item.clause_or_section
    assert "Does Not Meet" in failed_item.explanation


def test_pm_kisan_missing_landholding(db_session):
    """Test evaluation when landholding is omitted (never guess values)."""
    scheme = db_session.query(GovernmentScheme).filter_by(id="SCHEME-PM-KISAN").first()
    profile = CitizenEvaluationInput(
        full_name="Suresh Patil",
        occupation="Farmer",
        is_income_tax_payer=False,
        landholding_hectares=None,  # Missing
    )

    result = DeterministicRuleEngine.evaluate_scheme(scheme, profile)
    assert result.overall_status == EligibilityEvaluationStatus.MISSING_INFORMATION
    assert len(result.missing_information) == 1
    assert result.missing_information[0].rule_id == "RULE-PMKISAN-LAND-T"
    assert "Missing input: 'landholding_hectares'" in result.missing_information[0].explanation


def test_pm_kisan_negative_landholding_needs_review(db_session):
    """Test that impossible contradictory data triggers NEEDS_REVIEW."""
    scheme = db_session.query(GovernmentScheme).filter_by(id="SCHEME-PM-KISAN").first()
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
    """Test Gruha Lakshmi eligibility for female head in Karnataka."""
    scheme = db_session.query(GovernmentScheme).filter_by(id="SCHEME-KAR-GRUHA-LAKSHMI").first()
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


def test_gruha_lakshmi_disqualified_by_gender(db_session):
    """Test male applicant is disqualified for Gruha Lakshmi."""
    scheme = db_session.query(GovernmentScheme).filter_by(id="SCHEME-KAR-GRUHA-LAKSHMI").first()
    profile = CitizenEvaluationInput(
        full_name="Kiran Kumar",
        gender="Male",  # Gruha Lakshmi requires Female
        domicile_state="Karnataka",
        is_income_tax_payer=False,
    )

    result = DeterministicRuleEngine.evaluate_scheme(scheme, profile)
    assert result.overall_status == EligibilityEvaluationStatus.DOES_NOT_MEET_REQUIREMENT
    assert any(r.rule_id == "RULE-GL-GENDER-T" for r in result.requirements_not_satisfied)


def test_gruha_lakshmi_disqualified_by_domicile(db_session):
    """Test non-Karnataka applicant is disqualified."""
    scheme = db_session.query(GovernmentScheme).filter_by(id="SCHEME-KAR-GRUHA-LAKSHMI").first()
    profile = CitizenEvaluationInput(
        full_name="Sunita Sharma",
        gender="Female",
        domicile_state="Maharashtra",  # Non-Karnataka
        is_income_tax_payer=False,
    )

    result = DeterministicRuleEngine.evaluate_scheme(scheme, profile)
    assert result.overall_status == EligibilityEvaluationStatus.DOES_NOT_MEET_REQUIREMENT
    assert any(r.rule_id == "RULE-GL-DOMICILE-T" for r in result.requirements_not_satisfied)


# ============================================================================
# Multi-Scheme Discovery Ranking & Priority Tests
# ============================================================================

def test_scheme_discovery_ranking(db_session):
    """Test ranking where matching scheme is sorted ahead of non-matching scheme."""
    schemes = db_session.query(GovernmentScheme).all()

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

def test_api_sensitive_fields_explanation(client):
    """Test API endpoint returning explanation for sensitive data fields."""
    response = client.get("/api/v1/eligibility/sensitive-fields")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3
    fields = [item["field_name"] for item in data]
    assert "is_income_tax_payer" in fields
    assert "landholding_hectares" in fields
    assert "bpl_card_holder" in fields


def test_api_evaluate_single_scheme(client):
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
    assert data["official_source_title"] == "Government Order on Gruha Lakshmi Scheme"


def test_api_discover_schemes_with_filter(client):
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
