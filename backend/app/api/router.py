from fastapi import APIRouter

from backend.app.api.analysis_runs import router as analysis_runs_router
from backend.app.api.endpoints import router as analysis_router
from backend.app.api.imports import router as imports_router

router = APIRouter()
router.include_router(analysis_router, prefix="/analysis", tags=["analysis"])
router.include_router(analysis_runs_router, tags=["analysis-runs"])
router.include_router(imports_router, tags=["import"])


@router.get("/health")
def api_health_check() -> dict:
    return {"status": "healthy"}
