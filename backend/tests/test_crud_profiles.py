import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base
from app.schemas.profile import CitizenProfileCreate, CitizenProfileUpdate, StudentProfileCreate, StudentProfileUpdate
from app.schemas.user import UserCreate
from app.services.profile_service import ProfileService
from app.services.user_service import UserService

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


def test_user_and_student_profile_lifecycle(db_session):
    user_service = UserService(db_session)
    profile_service = ProfileService(db_session)

    # 1. Create User
    user = user_service.create_user(
        UserCreate(
            full_name="Ananya Sharma",
            email="ananya.sharma@example.edu.in",
            phone_number="+919876543210",
            role="STUDENT",
        )
    )
    assert user.id is not None
    assert user.email == "ananya.sharma@example.edu.in"

    # 2. Create Student Profile attached to User
    student = profile_service.create_student_profile(
        StudentProfileCreate(
            user_id=user.id,
            full_name="Ananya Sharma",
            domicile_state="Karnataka",
            category="OBC",
            annual_family_income=180000.0,
            current_course="B.Tech Computer Science & Engineering",
            year_of_study="3rd Year",
            marks_percentage=84.5,
            gender="Female",
            disability_status=False,
            hosteller_status="Hosteller",
            extra_attributes={"rural_student": True, "kannada_medium": True},
        )
    )
    assert student.id is not None
    assert student.annual_family_income == 180000.0
    assert student.user_id == user.id

    # 3. Update Student Profile
    updated = profile_service.update_student_profile(
        student.id,
        StudentProfileUpdate(marks_percentage=86.2),
    )
    assert updated.marks_percentage == 86.2

    # 4. Filter Student Profiles
    matches = profile_service.list_student_profiles(
        domicile_state="Karnataka",
        category="OBC",
        max_income=200000.0,
    )
    assert len(matches) == 1
    assert matches[0].full_name == "Ananya Sharma"


def test_citizen_profile_lifecycle(db_session):
    user_service = UserService(db_session)
    profile_service = ProfileService(db_session)

    # 1. Create Citizen User
    user = user_service.create_user(
        UserCreate(
            full_name="Ramesh Patil",
            phone_number="+919812345678",
            role="CITIZEN",
        )
    )

    # 2. Create Citizen Profile
    citizen = profile_service.create_citizen_profile(
        CitizenProfileCreate(
            user_id=user.id,
            full_name="Ramesh Patil",
            age=48,
            gender="Male",
            domicile_state="Karnataka",
            district="Dharwad",
            area_type="Rural",
            occupation="Farmer",
            annual_family_income=120000.0,
            social_category="General",
            landholding_hectares=1.5,
            is_income_tax_payer=False,
            bpl_card_holder=True,
            extra_attributes={"crop_type": "Kharif Maize"},
        )
    )
    assert citizen.id is not None
    assert citizen.landholding_hectares == 1.5
    assert citizen.bpl_card_holder is True

    # 3. Filter Citizen Profiles
    matches = profile_service.list_citizen_profiles(
        domicile_state="Karnataka",
        occupation="Farmer",
        max_income=150000.0,
    )
    assert len(matches) == 1
    assert matches[0].full_name == "Ramesh Patil"
