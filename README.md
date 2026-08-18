# Court Data Pipeline

A small FastAPI foundation for a court-data portfolio project. All seed data is deliberately fictional and synthetic; this project makes no external API or court website requests.

## Setup

Requires Python 3.12.

```powershell
cd court-data-pipeline
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Initialize and seed the local database

```powershell
python -m alembic upgrade head
python scripts/seed_data.py
```

The seed script is idempotent: running it again does not create duplicate courts, cases, parties, or documents.

## Run the API

```powershell
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for interactive API documentation.

## Test and lint

```powershell
python -m pytest
ruff check .
```

## Available endpoints

- `GET /health`
- `GET /courts`
- `GET /cases?court_id=&status=&skip=&limit=`
- `GET /cases/{case_id}`
- `GET /cases/{case_id}/documents`
- `POST /cases`

## Current limitations

This is intentionally the first foundation only: SQLite, synthetic data, and read-only endpoints. Migrations, ingestion jobs, external integrations, authentication, search, and a frontend are out of scope for this session.
