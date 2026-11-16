import json
from pathlib import Path
import pytest
from app.database import SessionLocal, init_db
from app.services.opportunity_service import OpportunityService

SEEDS_DIR = Path(__file__).resolve().parent.parent / "app" / "data" / "seeds"


@pytest.fixture(scope="module")
def db_session():
    init_db()
    session = SessionLocal()
    yield session
    session.close()


def test_three_undergraduate_scholarships_verified(db_session):
    service = OpportunityService(db_session)
    expected_scholarship_ids = [
        "SCH-MOE-CSSS-2024",
        "SCH-KAR-SSP-SC-2024",
        "SCH-AICTE-PRAGATI-DEGREE",
    ]

    for sch_id in expected_scholarship_ids:
        sch = service.get_scholarship(sch_id)
        assert sch is not None, f"Scholarship {sch_id} not found in DB!"
        assert sch.information_status == "VERIFIED"
        assert sch.official_source_url.startswith("https://")
        assert sch.academic_cycle is not None
        assert sch.verification_date is not None
        assert len(sch.eligibility_rules) >= 3, f"Scholarship {sch_id} must have at least 3 rules"
        assert len(sch.requirements) >= 3, f"Scholarship {sch_id} must have at least 3 document requirements"


def test_two_welfare_schemes_verified(db_session):
    service = OpportunityService(db_session)
    expected_scheme_ids = [
        "SCHEME-PM-KISAN",
        "SCHEME-KAR-GRUHA-LAKSHMI",
    ]

    for scheme_id in expected_scheme_ids:
        scheme = service.get_scheme(scheme_id)
        assert scheme is not None, f"Scheme {scheme_id} not found in DB!"
        assert scheme.information_status == "VERIFIED"
        assert scheme.official_source_url.startswith("https://")
        assert scheme.policy_cycle is not None
        assert scheme.verification_date is not None
        assert len(scheme.eligibility_rules) >= 2, f"Scheme {scheme_id} must have rules"
        assert len(scheme.requirements) >= 3, f"Scheme {scheme_id} must have document requirements"


def test_eligibility_rules_source_traceability(db_session):
    service = OpportunityService(db_session)
    rules = service.rule_repo.list(limit=50)
    assert len(rules) >= 13

    for rule in rules:
        assert rule.source_id is not None, f"Rule {rule.id} lacks source_id!"
        source = service.get_source(rule.source_id)
        assert source is not None, f"Rule {rule.id} references non-existent source {rule.source_id}"
        assert source.official_url.startswith("https://")
        assert rule.clause_or_section is not None
        assert rule.applicable_cycle is not None
        assert "field" in rule.structured_condition
        assert "operator" in rule.structured_condition
        assert "value" in rule.structured_condition


def test_policy_circulars_structure():
    circulars_file = SEEDS_DIR / "policy_circulars.json"
    assert circulars_file.exists()
    with open(circulars_file, "r", encoding="utf-8") as f:
        circulars = json.load(f)

    assert len(circulars) >= 3
    for circ in circulars:
        assert "id" in circ
        assert "title" in circ
        assert "issuing_department" in circ
        assert "notification_number" in circ
        assert "official_gazette_url" in circ
        assert len(circ["citizen_simplified_points"]) >= 3
        assert len(circ["official_clauses"]) >= 2
