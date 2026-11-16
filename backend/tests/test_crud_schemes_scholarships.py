from datetime import date
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base
from app.schemas.scholarship import ScholarshipCreate, ScholarshipFilter, ScholarshipUpdate
from app.schemas.scheme import GovernmentSchemeCreate, GovernmentSchemeFilter, GovernmentSchemeUpdate
from app.schemas.source import OfficialSourceCreate
from app.schemas.rule import EligibilityRuleCreate, RequirementCreate
from app.services.opportunity_service import OpportunityService

# Isolated in-memory SQLite engine for unit testing
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


def test_official_source_crud(db_session):
    service = OpportunityService(db_session)
    source_data = OfficialSourceCreate(
        id="SRC-GO-AGRI-2021",
        source_title="Karnataka Agriculture Dept Government Order",
        issuing_authority="Department of Agriculture, Govt of Karnataka",
        circular_number="GO-AGRI-44-EDN-2021",
        notification_date=date(2021, 8, 7),
        official_url="https://raitamitra.karnataka.gov.in",
        notes="Verified official notification for student farmer ward financial assistance",
    )
    source = service.create_source(source_data)
    assert source.id == "SRC-GO-AGRI-2021"
    assert source.circular_number == "GO-AGRI-44-EDN-2021"

    # Query source
    fetched = service.get_source("SRC-GO-AGRI-2021")
    assert fetched.issuing_authority == "Department of Agriculture, Govt of Karnataka"


def test_scholarship_with_rules_and_requirements(db_session):
    service = OpportunityService(db_session)

    # 1. Create Source
    source = service.create_source(
        OfficialSourceCreate(
            id="SRC-NSP-POSTMATRIC-SC",
            source_title="Ministry of Social Justice Post-Matric Guidelines",
            issuing_authority="Ministry of Social Justice and Empowerment",
            circular_number="MSJE/SCH/2024/01",
            notification_date=date(2024, 4, 1),
            official_url="https://scholarships.gov.in",
        )
    )

    # 2. Create Scholarship
    sch_data = ScholarshipCreate(
        id="SCH-SSP-POSTMATRIC-SCST",
        official_name="Centrally Sponsored Post-Matric Scholarship for SC/ST Students",
        category="Education & Scholarships",
        description="Comprehensive financial support covering 100% compulsory non-refundable fees and academic allowance.",
        government_department="Department of Social Welfare, Government of Karnataka & Central MoSJE",
        official_source_url="https://ssp.postmatric.karnataka.gov.in",
        application_url="https://ssp.postmatric.karnataka.gov.in/2425_applications",
        academic_cycle="2025-26",
        verification_date=date(2024, 11, 1),
        publication_date=date(2024, 4, 15),
        level="National / Central",
        course_level="Post-Matric / Higher Secondary",
        max_annual_income=250000.0,
        min_percentage=50.0,
        eligible_categories=["SC", "ST"],
        benefit_amount_annual="₹13,500/year + 100% tuition fees",
        application_deadline="31 December 2025",
        official_source_id=source.id,
    )
    scholarship = service.create_scholarship(sch_data)
    assert scholarship.id == "SCH-SSP-POSTMATRIC-SCST"
    assert scholarship.max_annual_income == 250000.0

    # 3. Add Rule
    rule = service.create_rule(
        EligibilityRuleCreate(
            id="RULE-SSP-INCOME-CAP",
            scholarship_id=scholarship.id,
            requirement_description="Total parental/guardian annual income must not exceed ₹2,50,000.",
            rule_type="INCOME_CAP",
            structured_condition={"field": "annual_family_income", "operator": "LTE", "value": 250000.0},
            source_id=source.id,
            clause_or_section="Guidelines Section 3.2 Clause (a)",
            applicable_cycle="2025-26",
            page_number="5",
        )
    )
    assert rule.id == "RULE-SSP-INCOME-CAP"

    # 4. Add Requirement
    req = service.create_requirement(
        RequirementCreate(
            id="REQ-INCOME-CERT-SSP",
            scholarship_id=scholarship.id,
            document_type="INCOME_CERTIFICATE",
            title="Income Certificate issued by Revenue Authority",
            description="Must be issued by Tahsildar with digital RD number and within 5-year validity period.",
            issuing_authority="Revenue Department / Nadakacheri",
            is_mandatory=True,
            verification_criteria={"requires_rd_number": True, "max_validity_years": 5},
        )
    )
    assert req.id == "REQ-INCOME-CERT-SSP"

    # 5. Fetch with Details
    detailed = service.get_scholarship(scholarship.id)
    assert len(detailed.eligibility_rules) == 1
    assert len(detailed.requirements) == 1
    assert detailed.official_source.circular_number == "MSJE/SCH/2024/01"


def test_government_scheme_crud_and_filtering(db_session):
    service = OpportunityService(db_session)

    source = service.create_source(
        OfficialSourceCreate(
            id="SRC-PMKISAN-2024",
            source_title="PM-KISAN Revised Operational Guidelines",
            issuing_authority="Ministry of Agriculture and Farmers Welfare",
            circular_number="1-1/2019-Credit-II",
            notification_date=date(2024, 2, 1),
            official_url="https://pmkisan.gov.in",
        )
    )

    scheme = service.create_scheme(
        GovernmentSchemeCreate(
            id="SCHEME-PM-KISAN",
            official_name="Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
            category="Agriculture & Farming",
            description="Income support to landholding farmer families across India having cultivable land.",
            government_department="Ministry of Agriculture & Farmers Welfare",
            official_source_url="https://pmkisan.gov.in",
            application_url="https://pmkisan.gov.in/RegistrationFormNew.aspx",
            policy_cycle="Continuous (FY 2025-26)",
            verification_date=date(2024, 10, 1),
            level="Central",
            benefit_type="Direct Benefit Transfer (DBT)",
            annual_benefit="₹6,000 / year in 3 installments",
            target_beneficiaries="Small and marginal landholder farmer families",
            application_deadline="Continuous",
            official_source_id=source.id,
        )
    )
    assert scheme.id == "SCHEME-PM-KISAN"

    # Search & Filter
    results = service.list_schemes(GovernmentSchemeFilter(category="Agriculture & Farming"))
    assert len(results) == 1
    assert results[0].official_name == "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)"

    # Filter with non-matching
    no_results = service.list_schemes(GovernmentSchemeFilter(category="Healthcare & Ayushman"))
    assert len(no_results) == 0
