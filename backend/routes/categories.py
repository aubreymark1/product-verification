"""
品类与视觉识别接口 —— 成员C
"""
from fastapi import APIRouter, HTTPException
from repository import get_repository
from schemas.models import (
    ApiResponse, CategoryProfile, VisionIdentifyRequest, VisionIdentifyResponse,
    CandidateProduct,
)

router = APIRouter(tags=["categories-vision"])


# ── 品类配置 ──────────────────────────

@router.get("/api/categories/{category_id}/profile")
async def get_category_profile(category_id: str):
    """获取品类动态需求字段配置"""
    repo = get_repository()
    profile = repo.get_category_profile(category_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"品类不存在: {category_id}")
    return ApiResponse(success=True, data=profile)


# ── 视觉识别（Mock） ──────────────────

@router.post("/api/vision/identify")
async def vision_identify(request: VisionIdentifyRequest):
    """
    根据视频画面圈选结果返回候选商品列表（Mock 实现）
    由成员A准备好候选映射后接入
    """
    repo = get_repository()

    # Mock 实现：返回对应商品作为主要候选
    # 在正式版本中，成员A会提供 video_id → 候选商品 的映射
    products = repo.get_all_products()[:3]
    candidates = [
        CandidateProduct(
            product_id=p["id"],
            name=p["name"],
            confidence=0.95 - i * 0.1,
            bounding_box=request.selected_region if i == 0 else None,
        )
        for i, p in enumerate(products)
    ]

    return VisionIdentifyResponse(
        video_id=request.video_id,
        candidates=candidates,
    )
