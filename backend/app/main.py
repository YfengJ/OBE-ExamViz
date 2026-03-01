from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from backend.app.api.router import router
from backend.app.core.config import settings
from backend.app.core.database import Base, engine
import backend.app.models  # noqa: F401

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="OBE-based final exam analysis and score visualization system",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        try:
            rows = conn.execute(text("PRAGMA table_info(warning_results)")).fetchall()
            columns = {row[1] for row in rows}
            if "status" not in columns:
                conn.execute(text("ALTER TABLE warning_results ADD COLUMN status VARCHAR DEFAULT 'pending'"))
                conn.commit()
        except Exception:
            # Non-SQLite databases or already migrated schema should pass through.
            conn.rollback()


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
