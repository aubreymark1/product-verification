"""
健康检查路由 —— 成员C
统一响应格式
"""
from fastapi import APIRouter
from schemas.models import ApiResponse

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    return ApiResponse(
        success=True,
        data={"service": "video-verify-api", "version": "0.1.0"},
        message="服务运行正常"
    )


@router.get("/api/health")
async def health_check_api():
    """兼容 /api/health 路径"""
    return await health_check()
