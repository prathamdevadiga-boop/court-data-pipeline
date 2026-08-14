"""FastAPI entry point."""
from fastapi import FastAPI
from app.api.routes import router
from app.db.database import Base, engine
from app.db import models  # noqa: F401

app = FastAPI(title="Court Data Pipeline", version="0.1.0")
app.include_router(router)


@app.on_event("startup")
def create_tables() -> None:
    """Create local SQLite tables; migrations can replace this later."""
    Base.metadata.create_all(bind=engine)
