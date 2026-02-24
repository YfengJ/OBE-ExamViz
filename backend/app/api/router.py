from fastapi import APIRouter
from app.api.endpoints import router as analysis_router

# 创建路由器
router = APIRouter()

# 包含各个模块的路由
router.include_router(analysis_router, prefix="/analysis", tags=["analysis"])

# 健康检查
@router.get("/health")
def health_check():
    return {"status": "healthy"}