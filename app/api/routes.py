"""Read-only routes for the first project foundation."""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload
from app.db.database import get_db
from app.db.models import Case, Court, CourtDocument
from app.schemas.court import CaseDetailRead, CaseListRead, CourtRead, DocumentRead

router = APIRouter()
DbSession = Annotated[Session, Depends(get_db)]


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/courts", response_model=list[CourtRead])
def list_courts(db: DbSession) -> list[Court]:
    return list(db.scalars(select(Court).order_by(Court.name)))


@router.get("/cases", response_model=list[CaseListRead])
def list_cases(db: DbSession, court_id: int | None = Query(default=None, gt=0), status: str | None = Query(default=None, min_length=1, max_length=50), skip: int = Query(default=0, ge=0), limit: int = Query(default=50, ge=1, le=100)) -> list[Case]:
    statement = select(Case).order_by(Case.filing_date.desc()).offset(skip).limit(limit)
    if court_id is not None:
        statement = statement.where(Case.court_id == court_id)
    if status is not None:
        statement = statement.where(Case.status == status)
    return list(db.scalars(statement))


@router.get("/cases/{case_id}", response_model=CaseDetailRead)
def get_case(case_id: int, db: DbSession) -> Case:
    statement = select(Case).where(Case.id == case_id).options(joinedload(Case.court), selectinload(Case.parties))
    case = db.scalar(statement)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@router.get("/cases/{case_id}/documents", response_model=list[DocumentRead])
def get_case_documents(case_id: int, db: DbSession) -> list[CourtDocument]:
    if db.get(Case, case_id) is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return list(db.scalars(select(CourtDocument).where(CourtDocument.case_id == case_id).order_by(CourtDocument.document_date)))
