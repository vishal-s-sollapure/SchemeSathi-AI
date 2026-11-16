from typing import List, Optional
from sqlalchemy.orm import Session

from app.core.exceptions import EntityNotFoundException
from app.models.rule import EligibilityRule, Requirement
from app.models.scholarship import Scholarship
from app.models.scheme import GovernmentScheme
from app.models.source import OfficialSource
from app.repositories.rule_repo import EligibilityRuleRepository, RequirementRepository
from app.repositories.scholarship_repo import ScholarshipRepository
from app.repositories.scheme_repo import GovernmentSchemeRepository
from app.repositories.source_repo import OfficialSourceRepository
from app.schemas.rule import (
    EligibilityRuleCreate,
    EligibilityRuleUpdate,
    RequirementCreate,
    RequirementUpdate,
)
from app.schemas.scholarship import (
    ScholarshipCreate,
    ScholarshipFilter,
    ScholarshipUpdate,
)
from app.schemas.scheme import (
    GovernmentSchemeCreate,
    GovernmentSchemeFilter,
    GovernmentSchemeUpdate,
)
from app.schemas.source import OfficialSourceCreate, OfficialSourceUpdate


class OpportunityService:
    """Manages verified scholarships, government welfare schemes, sources, rules, and requirements."""

    def __init__(self, db: Session):
        self.scholarship_repo = ScholarshipRepository(db)
        self.scheme_repo = GovernmentSchemeRepository(db)
        self.source_repo = OfficialSourceRepository(db)
        self.rule_repo = EligibilityRuleRepository(db)
        self.requirement_repo = RequirementRepository(db)

    # Official Sources
    def get_source(self, source_id: str) -> OfficialSource:
        source = self.source_repo.get_by_id(source_id)
        if not source:
            raise EntityNotFoundException("OfficialSource", source_id)
        return source

    def list_sources(self, skip: int = 0, limit: int = 100) -> List[OfficialSource]:
        return self.source_repo.list(skip=skip, limit=limit)

    def create_source(self, data: OfficialSourceCreate) -> OfficialSource:
        source = OfficialSource(**data.model_dump())
        return self.source_repo.create(source)

    def update_source(self, source_id: str, data: OfficialSourceUpdate) -> OfficialSource:
        source = self.get_source(source_id)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(source, key, value)
        return self.source_repo.update(source)

    # Scholarships
    def get_scholarship(self, scholarship_id: str) -> Scholarship:
        scholarship = self.scholarship_repo.get_with_details(scholarship_id)
        if not scholarship:
            raise EntityNotFoundException("Scholarship", scholarship_id)
        return scholarship

    def list_scholarships(self, filters: ScholarshipFilter, skip: int = 0, limit: int = 100) -> List[Scholarship]:
        return self.scholarship_repo.search_and_filter(
            search=filters.search,
            level=filters.level,
            course_level=filters.course_level,
            category=filters.category,
            max_income=filters.max_income,
            information_status=filters.information_status.value if filters.information_status else None,
            skip=skip,
            limit=limit,
        )

    def create_scholarship(self, data: ScholarshipCreate) -> Scholarship:
        if data.official_source_id:
            self.get_source(data.official_source_id)
        scholarship = Scholarship(**data.model_dump())
        return self.scholarship_repo.create(scholarship)

    def update_scholarship(self, scholarship_id: str, data: ScholarshipUpdate) -> Scholarship:
        scholarship = self.get_scholarship(scholarship_id)
        if data.official_source_id:
            self.get_source(data.official_source_id)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(scholarship, key, value)
        return self.scholarship_repo.update(scholarship)

    def delete_scholarship(self, scholarship_id: str) -> None:
        scholarship = self.get_scholarship(scholarship_id)
        self.scholarship_repo.delete(scholarship)

    # Government Schemes
    def get_scheme(self, scheme_id: str) -> GovernmentScheme:
        scheme = self.scheme_repo.get_with_details(scheme_id)
        if not scheme:
            raise EntityNotFoundException("GovernmentScheme", scheme_id)
        return scheme

    def list_schemes(self, filters: GovernmentSchemeFilter, skip: int = 0, limit: int = 100) -> List[GovernmentScheme]:
        return self.scheme_repo.search_and_filter(
            search=filters.search,
            category=filters.category,
            level=filters.level,
            benefit_type=filters.benefit_type,
            information_status=filters.information_status.value if filters.information_status else None,
            skip=skip,
            limit=limit,
        )

    def create_scheme(self, data: GovernmentSchemeCreate) -> GovernmentScheme:
        if data.official_source_id:
            self.get_source(data.official_source_id)
        scheme = GovernmentScheme(**data.model_dump())
        return self.scheme_repo.create(scheme)

    def update_scheme(self, scheme_id: str, data: GovernmentSchemeUpdate) -> GovernmentScheme:
        scheme = self.get_scheme(scheme_id)
        if data.official_source_id:
            self.get_source(data.official_source_id)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(scheme, key, value)
        return self.scheme_repo.update(scheme)

    def delete_scheme(self, scheme_id: str) -> None:
        scheme = self.get_scheme(scheme_id)
        self.scheme_repo.delete(scheme)

    # Eligibility Rules
    def get_rule(self, rule_id: str) -> EligibilityRule:
        rule = self.rule_repo.get_by_id(rule_id)
        if not rule:
            raise EntityNotFoundException("EligibilityRule", rule_id)
        return rule

    def create_rule(self, data: EligibilityRuleCreate) -> EligibilityRule:
        self.get_source(data.source_id)
        if data.scholarship_id:
            self.get_scholarship(data.scholarship_id)
        if data.scheme_id:
            self.get_scheme(data.scheme_id)
        rule = EligibilityRule(**data.model_dump())
        return self.rule_repo.create(rule)

    def update_rule(self, rule_id: str, data: EligibilityRuleUpdate) -> EligibilityRule:
        rule = self.get_rule(rule_id)
        if data.source_id:
            self.get_source(data.source_id)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(rule, key, value)
        return self.rule_repo.update(rule)

    def delete_rule(self, rule_id: str) -> None:
        rule = self.get_rule(rule_id)
        self.rule_repo.delete(rule)

    # Requirements
    def get_requirement(self, req_id: str) -> Requirement:
        req = self.requirement_repo.get_by_id(req_id)
        if not req:
            raise EntityNotFoundException("Requirement", req_id)
        return req

    def create_requirement(self, data: RequirementCreate) -> Requirement:
        if data.scholarship_id:
            self.get_scholarship(data.scholarship_id)
        if data.scheme_id:
            self.get_scheme(data.scheme_id)
        req = Requirement(**data.model_dump())
        return self.requirement_repo.create(req)

    def update_requirement(self, req_id: str, data: RequirementUpdate) -> Requirement:
        req = self.get_requirement(req_id)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(req, key, value)
        return self.requirement_repo.update(req)

    def delete_requirement(self, req_id: str) -> None:
        req = self.get_requirement(req_id)
        self.requirement_repo.delete(req)
