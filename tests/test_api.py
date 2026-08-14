"""API tests use an isolated in-memory SQLite database."""
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.db.database import Base, get_db
from app.db.models import Case, Court, CourtDocument, Party
from app.main import app

test_engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(bind=test_engine, autocommit=False, autoflush=False)


def override_get_db():
    with TestingSessionLocal() as db:
        yield db


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def setup_function() -> None:
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    with TestingSessionLocal() as db:
        court = Court(name="Test Court", jurisdiction="Test Jurisdiction", external_id="TEST-COURT-1")
        db.add(court); db.flush()
        case = Case(court_id=court.id, case_number="TEST-2026-1", title="Alpha v. Beta", filing_date=date(2026, 1, 1), status="open", external_id="TEST-CASE-1")
        db.add(case); db.flush()
        db.add_all([Party(case_id=case.id, name="Alpha", role="plaintiff"), Party(case_id=case.id, name="Beta", role="defendant")])
        db.add(CourtDocument(case_id=case.id, title="Test Complaint", document_type="Complaint", document_date=date(2026, 1, 1), text="Synthetic test document", source_url=None, content_hash="test-document-hash"))
        db.commit()


def test_health() -> None:
    assert client.get("/health").json() == {"status": "ok"}


def test_list_courts() -> None:
    response = client.get("/courts")
    assert response.status_code == 200
    assert response.json()[0]["name"] == "Test Court"


def test_list_cases_and_filters() -> None:
    response = client.get("/cases?status=open&limit=1")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_case_detail_includes_court_and_parties() -> None:
    response = client.get("/cases/1")
    assert response.status_code == 200
    assert response.json()["court"]["name"] == "Test Court"
    assert len(response.json()["parties"]) == 2


def test_missing_case_returns_404() -> None:
    assert client.get("/cases/999").status_code == 404


def test_case_documents() -> None:
    response = client.get("/cases/1/documents")
    assert response.status_code == 200
    assert response.json()[0]["document_type"] == "Complaint"
