from enum import Enum
from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class InformationStatus(str, Enum):
    VERIFIED = "VERIFIED"
    DRAFT = "DRAFT"
    ARCHIVED = "ARCHIVED"
    NEEDS_UPDATE = "NEEDS_UPDATE"


class EligibilityEvaluationStatus(str, Enum):
    MEETS_REQUIREMENT = "MEETS_REQUIREMENT"
    DOES_NOT_MEET_REQUIREMENT = "DOES_NOT_MEET_REQUIREMENT"
    MISSING_INFORMATION = "MISSING_INFORMATION"
    NEEDS_REVIEW = "NEEDS_REVIEW"


class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    message: Optional[str] = None
    data: Optional[T] = None


class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    page: int
    page_size: int
    items: List[T]
