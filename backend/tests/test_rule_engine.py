import pytest
from app.database import SessionLocal, init_db
from app.schemas.common import EligibilityEvaluationStatus
from app.schemas.eligibility import StudentEvaluationInput
from app.services.opportunity_service import OpportunityService
from app.services.rule_engine import DeterministicRuleEngine


@pytest.fixture(scope="module")
def db_session():
    init_db()
    session = SessionLocal()
    yield session
    session.close()


# -----------------------------------------------------------------------------
# 1. Normal Matching Cases (All criteria met)
# -----------------------------------------------------------------------------

def test_csss_normal_eligible(db_session):
    """Student with 85% marks, ₹3.5L income, no other scholarship meets all CSSS rules."""
    service = OpportunityService(db_session)
    sch = service.get_scholarship("SCH-MOE-CSSS-2024")

    profile = StudentEvaluationInput(
        full_name="Kavita Rao",
        domicile_state="Karnataka",
        course_level="Undergraduate",
        current_course="B.Sc Physics",
        marks_percentage=85.0,
        annual_family_income=350000.0,
        category="General",
        gender="Female",
        other_scholarship_recipient=False,
    )

    result = DeterministicRuleEngine.evaluate_scholarship(sch, profile)
    assert result.overall_status == EligibilityEvaluationStatus.MEETS_REQUIREMENT
    assert result.match_score == 100.0
    assert len(result.requirements_satisfied) == 3
    assert len(result.requirements_not_satisfied) == 0
    assert len(result.missing_information) == 0
    assert len(result.conditions_under_review) == 0
    assert any("You meet all evaluated conditions" in act for act in result.suggested_next_actions)


def test_ssp_sc_normal_eligible(db_session):
    """SC student of Karnataka with ₹1.8L income meets all SSP SC rules."""
    service = OpportunityService(db_session)
    sch = service.get_scholarship("SCH-KAR-SSP-SC-2024")

    profile = StudentEvaluationInput(
        full_name="Ravi Kumar",
        domicile_state="Karnataka",
        category="SC",
        annual_family_income=180000.0,
        current_course="B.Tech Civil Engineering",
        course_level="Undergraduate",
        marks_percentage=72.0,
        gender="Male",
    )

    result = DeterministicRuleEngine.evaluate_scholarship(sch, profile)
    assert result.overall_status == EligibilityEvaluationStatus.MEETS_REQUIREMENT
    assert result.match_score == 100.0
    assert len(result.requirements_satisfied) == 3
    assert len(result.requirements_not_satisfied) == 0


def test_pragati_normal_eligible(db_session):
    """Female student in B.Tech with ₹4.5L income and 1 daughter meets Pragati rules."""
    service = OpportunityService(db_session)
    sch = service.get_scholarship("SCH-AICTE-PRAGATI-DEGREE")

    profile = StudentEvaluationInput(
        full_name="Sneha Patil",
        gender="Female",
        course_level="Technical / Professional",
        annual_family_income=450000.0,
        eligible_daughters_count=1,
    )

    result = DeterministicRuleEngine.evaluate_scholarship(sch, profile)
    assert result.overall_status == EligibilityEvaluationStatus.MEETS_REQUIREMENT
    assert result.match_score == 100.0
    assert len(result.requirements_satisfied) == 4


# -----------------------------------------------------------------------------
# 2. Boundary Values (Exact Thresholds)
# -----------------------------------------------------------------------------

def test_boundary_values_income_exact_cap(db_session):
    """Tests exact upper income boundary and 1-rupee above cap."""
    service = OpportunityService(db_session)
    csss = service.get_scholarship("SCH-MOE-CSSS-2024")

    # Exact income cap: ₹4,50,000 -> MEETS_REQUIREMENT
    exact_profile = StudentEvaluationInput(
        marks_percentage=85.0,
        annual_family_income=450000.0,
        other_scholarship_recipient=False,
    )
    res_exact = DeterministicRuleEngine.evaluate_scholarship(csss, exact_profile)
    assert res_exact.overall_status == EligibilityEvaluationStatus.MEETS_REQUIREMENT

    # 1 Rupee over cap: ₹4,50,001 -> DOES_NOT_MEET_REQUIREMENT
    over_profile = StudentEvaluationInput(
        marks_percentage=85.0,
        annual_family_income=450001.0,
        other_scholarship_recipient=False,
    )
    res_over = DeterministicRuleEngine.evaluate_scholarship(csss, over_profile)
    assert res_over.overall_status == EligibilityEvaluationStatus.DOES_NOT_MEET_REQUIREMENT
    assert any(item.rule_id == "RULE-CSSS-INCOME" for item in res_over.requirements_not_satisfied)


def test_boundary_values_marks_exact_cutoff(db_session):
    """Tests exact marks cutoff at 80.0% vs 79.9%."""
    service = OpportunityService(db_session)
    csss = service.get_scholarship("SCH-MOE-CSSS-2024")

    # Exact cutoff: 80.0% -> MEETS_REQUIREMENT
    exact_marks = StudentEvaluationInput(
        marks_percentage=80.0,
        annual_family_income=300000.0,
        other_scholarship_recipient=False,
    )
    res_exact = DeterministicRuleEngine.evaluate_scholarship(csss, exact_marks)
    assert res_exact.overall_status == EligibilityEvaluationStatus.MEETS_REQUIREMENT

    # Below cutoff: 79.9% -> DOES_NOT_MEET_REQUIREMENT
    below_marks = StudentEvaluationInput(
        marks_percentage=79.9,
        annual_family_income=300000.0,
        other_scholarship_recipient=False,
    )
    res_below = DeterministicRuleEngine.evaluate_scholarship(csss, below_marks)
    assert res_below.overall_status == EligibilityEvaluationStatus.DOES_NOT_MEET_REQUIREMENT
    assert any(item.rule_id == "RULE-CSSS-PERCENTILE" for item in res_below.requirements_not_satisfied)


# -----------------------------------------------------------------------------
# 3. Missing Fields (Separated from Failed Eligibility)
# -----------------------------------------------------------------------------

def test_missing_fields_classified_as_missing_information(db_session):
    """Incomplete student profile must yield MISSING_INFORMATION, never failed eligibility."""
    service = OpportunityService(db_session)
    sch = service.get_scholarship("SCH-KAR-SSP-SC-2024")

    # Provided category and domicile, but missing income
    incomplete_profile = StudentEvaluationInput(
        domicile_state="Karnataka",
        category="SC",
        annual_family_income=None,  # Missing!
    )

    result = DeterministicRuleEngine.evaluate_scholarship(sch, incomplete_profile)
    assert result.overall_status == EligibilityEvaluationStatus.MISSING_INFORMATION
    assert len(result.missing_information) == 1
    assert result.missing_information[0].rule_id == "RULE-SSP-SC-INCOME"
    assert len(result.requirements_satisfied) == 2
    assert len(result.requirements_not_satisfied) == 0
    assert any("Missing" in act for act in result.suggested_next_actions)


# -----------------------------------------------------------------------------
# 4. Contradictory / Out-of-Bounds Values (NEEDS_REVIEW)
# -----------------------------------------------------------------------------

def test_contradictory_percentage_triggers_needs_review(db_session):
    """Marks percentage > 100% or < 0% must trigger NEEDS_REVIEW."""
    service = OpportunityService(db_session)
    csss = service.get_scholarship("SCH-MOE-CSSS-2024")

    invalid_marks_profile = StudentEvaluationInput(
        marks_percentage=108.5,  # Impossible percentage
        annual_family_income=250000.0,
        other_scholarship_recipient=False,
    )

    result = DeterministicRuleEngine.evaluate_scholarship(csss, invalid_marks_profile)
    assert result.overall_status == EligibilityEvaluationStatus.NEEDS_REVIEW
    assert len(result.conditions_under_review) == 1
    assert result.conditions_under_review[0].rule_id == "RULE-CSSS-PERCENTILE"
    assert "Review required" in result.conditions_under_review[0].explanation


def test_negative_income_triggers_needs_review(db_session):
    """Negative family income must trigger NEEDS_REVIEW."""
    service = OpportunityService(db_session)
    ssp = service.get_scholarship("SCH-KAR-SSP-SC-2024")

    negative_income_profile = StudentEvaluationInput(
        domicile_state="Karnataka",
        category="SC",
        annual_family_income=-50000.0,  # Impossible negative income
    )

    result = DeterministicRuleEngine.evaluate_scholarship(ssp, negative_income_profile)
    assert result.overall_status == EligibilityEvaluationStatus.NEEDS_REVIEW
    assert any(item.rule_id == "RULE-SSP-SC-INCOME" for item in result.conditions_under_review)


# -----------------------------------------------------------------------------
# 5. Restrictions and Disqualifiers
# -----------------------------------------------------------------------------

def test_disqualification_exclusivity_rule(db_session):
    """Availing another government scholarship triggers DOES_NOT_MEET_REQUIREMENT for CSSS."""
    service = OpportunityService(db_session)
    csss = service.get_scholarship("SCH-MOE-CSSS-2024")

    duplicate_scholarship_profile = StudentEvaluationInput(
        marks_percentage=90.0,
        annual_family_income=200000.0,
        other_scholarship_recipient=True,  # Disqualified under exclusivity
    )

    result = DeterministicRuleEngine.evaluate_scholarship(csss, duplicate_scholarship_profile)
    assert result.overall_status == EligibilityEvaluationStatus.DOES_NOT_MEET_REQUIREMENT
    assert any(item.rule_id == "RULE-CSSS-EXCLUSIVITY" for item in result.requirements_not_satisfied)


def test_disqualification_category_and_gender_restrictions(db_session):
    """Male student applying for Pragati Girls scholarship must be disqualified."""
    service = OpportunityService(db_session)
    pragati = service.get_scholarship("SCH-AICTE-PRAGATI-DEGREE")

    male_profile = StudentEvaluationInput(
        gender="Male",
        course_level="Technical / Professional",
        annual_family_income=300000.0,
        eligible_daughters_count=1,
    )

    result = DeterministicRuleEngine.evaluate_scholarship(pragati, male_profile)
    assert result.overall_status == EligibilityEvaluationStatus.DOES_NOT_MEET_REQUIREMENT
    assert any(item.rule_id == "RULE-PRAGATI-GENDER" for item in result.requirements_not_satisfied)


# -----------------------------------------------------------------------------
# 6. Traceability and Full Assessment Metadata
# -----------------------------------------------------------------------------

def test_assessment_contains_traceable_citations(db_session):
    """Every assessed item must contain official circular, clause, and page number."""
    service = OpportunityService(db_session)
    sch = service.get_scholarship("SCH-MOE-CSSS-2024")

    profile = StudentEvaluationInput(
        marks_percentage=88.0,
        annual_family_income=300000.0,
        other_scholarship_recipient=False,
    )

    result = DeterministicRuleEngine.evaluate_scholarship(sch, profile)
    for item in result.requirements_satisfied:
        assert item.official_source_title is not None
        assert item.circular_number is not None
        assert item.clause_or_section is not None
        assert item.official_source_url.startswith("https://")
        assert item.explanation is not None


# -----------------------------------------------------------------------------
# 7. Batch Evaluation & Prioritized Recommendations
# -----------------------------------------------------------------------------

def test_evaluate_all_scholarships_prioritizes_eligible(db_session):
    """Evaluating all scholarships sorts eligible opportunities to the top."""
    service = OpportunityService(db_session)
    all_schs = service.scholarship_repo.list()

    # Profile: SC Female student of Karnataka with 85% marks and ₹2.0L income
    profile = StudentEvaluationInput(
        full_name="Pooja Meghraj",
        gender="Female",
        category="SC",
        domicile_state="Karnataka",
        course_level="Technical / Professional",
        marks_percentage=85.0,
        annual_family_income=200000.0,
        other_scholarship_recipient=False,
        eligible_daughters_count=1,
    )

    summary = DeterministicRuleEngine.evaluate_all_scholarships(all_schs, profile)
    assert summary.total_scholarships_evaluated == 3
    assert summary.eligible_count >= 2
    # First item in list must be MEETS_REQUIREMENT
    assert summary.scholarships[0].overall_status == EligibilityEvaluationStatus.MEETS_REQUIREMENT
