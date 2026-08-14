"""Seed idempotent, deliberately synthetic court data for local development."""
from datetime import date
from pathlib import Path
import sys
from sqlalchemy import select

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.db.database import Base, SessionLocal, engine
from app.db.models import Case, Court, CourtDocument, Party


def get_or_create_court(db, name: str, jurisdiction: str, external_id: str) -> Court:
    court = db.scalar(select(Court).where(Court.external_id == external_id))
    if court is None:
        court = Court(name=name, jurisdiction=jurisdiction, external_id=external_id)
        db.add(court)
        db.flush()
    return court


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        coastal = get_or_create_court(db, "Coastal County Civil Court", "Synthetic Coastal County", "SYN-COURT-001")
        harbor = get_or_create_court(db, "Harbor District Commercial Court", "Synthetic Harbor District", "SYN-COURT-002")
        samples = [
            (coastal, "SYN-CIV-2026-001", "Aster Labs v. Beacon Systems", date(2026, 1, 12), "open", "SYN-CASE-001", "Complaint"),
            (coastal, "SYN-CIV-2026-002", "Cedar Estates v. Delta Works", date(2026, 2, 4), "pending", "SYN-CASE-002", "Motion"),
            (harbor, "SYN-COM-2026-003", "Ember Logistics v. Fjord Supply", date(2026, 3, 18), "closed", "SYN-CASE-003", "Order"),
        ]
        for court, number, title, filed, status, external_id, document_type in samples:
            case = db.scalar(select(Case).where(Case.external_id == external_id))
            if case is None:
                case = Case(court_id=court.id, case_number=number, title=title, filing_date=filed, status=status, external_id=external_id)
                db.add(case)
                db.flush()
            if not db.scalar(select(Party).where(Party.case_id == case.id)):
                plaintiff, defendant = title.split(" v. ")
                db.add_all([Party(case_id=case.id, name=plaintiff, role="plaintiff"), Party(case_id=case.id, name=defendant, role="defendant")])
            content_hash = f"synthetic-document-{external_id}"
            if not db.scalar(select(CourtDocument).where(CourtDocument.content_hash == content_hash)):
                db.add(CourtDocument(case_id=case.id, title=f"{document_type}: {number}", document_type=document_type, document_date=filed, text=f"Synthetic {document_type.lower()} for portfolio demonstration only.", source_url=None, content_hash=content_hash))
        db.commit()
    print("Synthetic court data seeded successfully.")


if __name__ == "__main__":
    seed()
