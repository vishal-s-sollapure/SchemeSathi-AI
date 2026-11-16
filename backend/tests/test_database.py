import pytest
from sqlalchemy import inspect
from app.database import Base, engine, init_db


def test_database_initialization():
    """Verify that all 12 core tables are created properly in SQLite."""
    init_db()
    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    expected_tables = [
        "users",
        "student_profiles",
        "citizen_profiles",
        "official_sources",
        "scholarships",
        "government_schemes",
        "eligibility_rules",
        "requirements",
        "uploaded_documents",
        "extracted_evidence",
        "application_checklists",
        "chat_sessions",
        "chat_messages",
    ]

    for table in expected_tables:
        assert table in table_names, f"Table '{table}' was not created in the database!"


def test_table_columns():
    """Verify that crucial audit and trace columns exist on scholarships and eligibility_rules."""
    inspector = inspect(engine)
    
    # Scholarship columns
    scholarship_cols = {col["name"] for col in inspector.get_columns("scholarships")}
    assert "official_name" in scholarship_cols
    assert "category" in scholarship_cols
    assert "description" in scholarship_cols
    assert "government_department" in scholarship_cols
    assert "official_source_url" in scholarship_cols
    assert "verification_date" in scholarship_cols
    assert "information_status" in scholarship_cols
    assert "academic_cycle" in scholarship_cols

    # Scheme columns
    scheme_cols = {col["name"] for col in inspector.get_columns("government_schemes")}
    assert "official_name" in scheme_cols
    assert "category" in scheme_cols
    assert "benefit_type" in scheme_cols
    assert "policy_cycle" in scheme_cols
    assert "information_status" in scheme_cols

    # Eligibility Rule columns
    rule_cols = {col["name"] for col in inspector.get_columns("eligibility_rules")}
    assert "requirement_description" in rule_cols
    assert "rule_type" in rule_cols
    assert "structured_condition" in rule_cols
    assert "source_id" in rule_cols
    assert "clause_or_section" in rule_cols
    assert "applicable_cycle" in rule_cols
