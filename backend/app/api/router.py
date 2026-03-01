from fastapi import APIRouter

from backend.app.api.endpoints import router as analysis_router

router = APIRouter()
router.include_router(analysis_router, prefix="/analysis", tags=["analysis"])


@router.get("/health")
def api_health_check() -> dict:
    return {"status": "healthy"}
