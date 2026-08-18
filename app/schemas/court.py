"""Pydantic v2 schemas returned by the API."""

from datetime import date, datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict
from pydantic import BaseModel, ConfigDict, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class CourtRead(ORMModel):
    id: int
    name: str
    jurisdiction: str
    external_id: str
    created_at: datetime


class PartyRead(ORMModel):
    id: int
    name: str
    role: str


class DocumentRead(ORMModel):
    id: int
    title: str
    document_type: str
    document_date: date
    text: str
    source_url: str | None
    content_hash: str
    created_at: datetime


class CaseCreate(BaseModel):
    court_id: int = Field(gt=0)
    case_number: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=500)
    filing_date: date
    status: Literal["open", "pending", "closed"]
    external_id: str = Field(min_length=1, max_length=100)


class CaseListRead(ORMModel):
    id: int
    court_id: int
    case_number: str
    title: str
    filing_date: date
    status: str
    external_id: str
    created_at: datetime
    updated_at: datetime


class CaseDetailRead(CaseListRead):
    court: CourtRead
    parties: list[PartyRead]
