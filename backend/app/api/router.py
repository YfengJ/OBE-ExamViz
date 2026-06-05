from fastapi import APIRouter
from sqlalchemy import text

from backend.app.api.analysis_runs import router as analysis_runs_router
from backend.app.api.endpoints import router as analysis_router
from backend.app.api.imports import router as imports_router
from backend.app.core.config import settings
from backend.app.core.database import SessionLocal

router = APIRouter()
router.include_router(analysis_router, prefix="/analysis", tags=["analysis"])
router.include_router(analysis_runs_router, tags=["analysis-runs"])
router.include_router(imports_router, tags=["import"])


@router.get("/health")
def api_health_check() -> dict:
    database_status = "ok"
    try:
        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
        finally:
            db.close()
    except Exception:
        database_status = "error"

    return {
        "status": "healthy" if database_status == "ok" else "degraded",
        "version": settings.VERSION,
        "checks": {
            "database": database_status,
            "auto_seed_demo_data": bool(settings.AUTO_SEED_DEMO_DATA),
            "ai_configured": bool(settings.DEEPSEEK_API_KEY),
        },
        "privacy": {
            "ai_prompt_redaction": True,
            "warning_statistics_only": True,
            "raw_student_identifiers_to_ai": False,
        },
    }
