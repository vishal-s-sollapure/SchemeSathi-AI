from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.rule import (
    EligibilityRuleCreate,
    EligibilityRuleResponse,
    EligibilityRuleUpdate,
    RequirementCreate,
    RequirementResponse,
    RequirementUpdate,
)
from app.services.opportunity_service import OpportunityService

router = APIRouter(prefix="/rules", tags=["Eligibility Rules & Requirements"])


# Rules
@router.post("", response_model=EligibilityRuleResponse, status_code=status.HTTP_201_CREATED)
def create_rule(data: EligibilityRuleCreate, db: Session = Depends(get_db)):
    service = OpportunityService(db)
    return service.create_rule(data)


@router.get("/{rule_id}", response_model=EligibilityRuleResponse)
def get_rule(rule_id: str, db: Session = Depends(get_db)):
    service = OpportunityService(db)
    return service.get_rule(rule_id)


@router.put("/{rule_id}", response_model=EligibilityRuleResponse)
def update_rule(rule_id: str, data: EligibilityRuleUpdate, db: Session = Depends(get_db)):
    service = OpportunityService(db)
    return service.update_rule(rule_id, data)


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rule(rule_id: str, db: Session = Depends(get_db)):
    service = OpportunityService(db)
    service.delete_rule(rule_id)


# Requirements
@router.post("/requirements", response_model=RequirementResponse, status_code=status.HTTP_201_CREATED)
def create_requirement(data: RequirementCreate, db: Session = Depends(get_db)):
    service = OpportunityService(db)
    return service.create_requirement(data)


@router.get("/requirements/{req_id}", response_model=RequirementResponse)
def get_requirement(req_id: str, db: Session = Depends(get_db)):
    service = OpportunityService(db)
    return service.get_requirement(req_id)


@router.put("/requirements/{req_id}", response_model=RequirementResponse)
def update_requirement(req_id: str, data: RequirementUpdate, db: Session = Depends(get_db)):
    service = OpportunityService(db)
    return service.update_requirement(req_id, data)


@router.delete("/requirements/{req_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_requirement(req_id: str, db: Session = Depends(get_db)):
    service = OpportunityService(db)
    service.delete_requirement(req_id)
