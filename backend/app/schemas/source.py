from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl


class OfficialSourceBase(BaseModel):
    source_title: str = Field(..., max_length=255)
    issuing_authority: str = Field(..., max_length=255)
    circular_number: str = Field(..., max_length=100)
    notification_date: Optional[date] = None
    official_url: str = Field(..., max_length=500)
    document_checksum: Optional[str] = Field(None, max_length=64)
    file_path: Optional[str] = None
    notes: Optional[str] = None


class OfficialSourceCreate(OfficialSourceBase):
    id: Optional[str] = None


class OfficialSourceUpdate(BaseModel):
    source_title: Optional[str] = None
    issuing_authority: Optional[str] = None
    circular_number: Optional[str] = None
    notification_date: Optional[date] = None
    official_url: Optional[str] = None
    document_checksum: Optional[str] = None
    file_path: Optional[str] = None
    notes: Optional[str] = None


class OfficialSourceResponse(OfficialSourceBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
