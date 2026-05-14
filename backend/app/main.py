from fastapi import FastAPI
from sqlalchemy import inspect, text
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, candidates, ai, analytics, documents, applications
from app.core.config import settings
from app.core.db import Base, engine
from app.models import entities  # noqa: F401

Base.metadata.create_all(bind=engine)

def ensure_sqlite_schema() -> None:
    """Development-only SQLite migration helper.

    SQLAlchemy create_all() creates missing tables but does not alter existing
    tables. During local iteration, an old resume_ai.db may be missing newly
    added columns. This helper keeps the local prototype from breaking with
    errors such as: table candidates has no column named created_at.
    Production should use Alembic migrations instead.
    """
    if not str(engine.url).startswith("sqlite"):
        return
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    required_columns = {
        "users": {
            "username": "VARCHAR(60) DEFAULT 'candidate'",
            "preferred_provider": "VARCHAR(50) DEFAULT 'ollama'",
            "preferred_model": "VARCHAR(100) DEFAULT 'llama3.1:8b'",
            "created_at": "DATETIME",
        },
        "candidates": {
            "user_id": "INTEGER DEFAULT 1",
            "target_role": "VARCHAR(255) DEFAULT 'Software Engineer'",
            "location": "VARCHAR(255) DEFAULT ''",
            "skills": "TEXT DEFAULT ''",
            "created_at": "DATETIME",
        },
        "job_descriptions": {
            "user_id": "INTEGER DEFAULT 1",
            "company": "VARCHAR(255) DEFAULT ''",
            "seniority": "VARCHAR(100) DEFAULT ''",
            "created_at": "DATETIME",
        },
        "generation_results": {
            "created_at": "DATETIME",
        },
        "application_logs": {
            "result_id": "INTEGER",
            "portal_url": "VARCHAR(1000) DEFAULT ''",
            "summary": "TEXT DEFAULT ''",
            "applied_at": "DATETIME",
        },
    }
    with engine.begin() as conn:
        for table, columns in required_columns.items():
            if table not in existing_tables:
                continue
            current = {c["name"] for c in inspector.get_columns(table)}
            for column, definition in columns.items():
                if column not in current:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {definition}"))

ensure_sqlite_schema()

app = FastAPI(title=settings.app_name, version="1.3.0")

# During local development the frontend may be opened from localhost, 127.0.0.1,
# or a LAN IP like 192.168.x.x. allow_origin_regex avoids 400 preflight errors.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()],
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(candidates.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(applications.router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "AI Resume Intelligence API", "docs": "/docs", "health": "/health"}

@app.get("/health")
def health():
    return {"status": "ok", "app": settings.app_name}
