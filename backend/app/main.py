from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from backend.app.api.router import router
from backend.app.core.config import settings
from backend.app.core.database import Base, engine
import backend.app.models  # noqa: F401


def _run_startup_migrations() -> None:
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        try:
            _ensure_sqlite_columns(
                conn,
                "warning_results",
                {"status": "ALTER TABLE warning_results ADD COLUMN status VARCHAR DEFAULT 'pending'"},
            )
            _ensure_sqlite_columns(
                conn,
                "questions",
                {
                    "qgroup_name": "ALTER TABLE questions ADD COLUMN qgroup_name VARCHAR",
                    "sub_qno": "ALTER TABLE questions ADD COLUMN sub_qno VARCHAR",
                    "co_weight": "ALTER TABLE questions ADD COLUMN co_weight FLOAT DEFAULT 0",
                    "expected_threshold": "ALTER TABLE questions ADD COLUMN expected_threshold FLOAT DEFAULT 0.65",
                },
            )
            _ensure_sqlite_columns(
                conn,
                "analysis_runs",
                {
                    "status": "ALTER TABLE analysis_runs ADD COLUMN status VARCHAR DEFAULT 'draft'",
                },
            )
            _ensure_sqlite_columns(
                conn,
                "obe_outcomes",
                {
                    "indicator": "ALTER TABLE obe_outcomes ADD COLUMN indicator VARCHAR",
                    "description": "ALTER TABLE obe_outcomes ADD COLUMN description VARCHAR",
                },
            )
            _ensure_sqlite_columns(
                conn,
                "courses",
                {
                    "owner": "ALTER TABLE courses ADD COLUMN owner VARCHAR",
                },
            )
        except Exception:
            # Non-SQLite databases or already migrated schema should pass through.
            conn.rollback()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    _run_startup_migrations()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="OBE-based final exam analysis and score visualization system",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def _ensure_sqlite_columns(conn, table_name: str, statements: dict[str, str]) -> None:
    rows = conn.execute(text(f"PRAGMA table_info({table_name})")).fetchall()
    columns = {row[1] for row in rows}
    changed = False
    for column_name, statement in statements.items():
        if column_name not in columns:
            conn.execute(text(statement))
            changed = True
    if changed:
        conn.commit()


app.include_router(router, prefix=settings.API_V1_STR)


@app.get("/")
def root() -> dict:
    return {"message": settings.PROJECT_NAME, "version": settings.VERSION}


@app.get("/health")
def health_check() -> dict:
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
