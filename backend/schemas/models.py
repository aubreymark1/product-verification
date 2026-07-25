"""
Pydantic 数据模型 —— 成员C维护
覆盖：视频、商品、品类、用户需求、证据、推荐、购买渠道
"""
from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional


# ──────────────────────────────────────
#  通用响应封装
# ──────────────────────────────────────

class ApiResponse(BaseModel):
    """统一成功响应"""
    success: bool = True
    data: dict | list | None = None
    message: str = ""


class ApiError(BaseModel):
    """统一错误响应"""
    success: bool = False
    error_code: str
    message: str
    detail: str | None = None


# ──────────────────────────────────────
#  视频与候选商品（供成员A参考）
# ──────────────────────────────────────

class VideoInfo(BaseModel):
    video_id: str
    video_url: str = ""
    timestamp: float = 0.0
    title: str = ""


class CandidateProduct(BaseModel):
    product_id: str
    name: str
    confidence: float = 0.0         # 识别置信度 0-1
    bounding_box: dict | None = None


class VisionIdentifyRequest(BaseModel):
    video_id: str
    frame_timestamp: float
    selected_region: dict            # {x, y, w, h}


class VisionIdentifyResponse(BaseModel):
    video_id: str
    candidates: list[CandidateProduct] = []


# ──────────────────────────────────────
#  商品
# ──────────────────────────────────────

class ProductBrief(BaseModel):
    """商品简要信息（列表用）"""
    id: str
    name: str
    category: str
    brand: str = ""
    price_range: list[int]
    tags: list[str] = []


class ProductDetail(BaseModel):
    """商品详细信息"""
    id: str
    name: str
    category: str
    brand: str = ""
    price_range: list[int]
    image_url: str = ""
    video_url: str = ""
    video_timestamp: float = 0.0
    description: str = ""
    features: list[str] = []
    tags: list[str] = []
    candidate_products: list[str] = []


class ProductListResponse(BaseModel):
    products: list[ProductBrief]
    total: int


# ──────────────────────────────────────
#  品类配置
# ──────────────────────────────────────

class CategoryProfile(BaseModel):
    """品类动态需求字段配置"""
    category_id: str
    category_name: str
    default_dimensions: list[str] = []        # 如 ["吸力", "续航", "噪音"]
    dynamic_fields: list[dict] = []           # 动态表单字段定义
    common_priorities: list[str] = []         # 常见关注点


# ──────────────────────────────────────
#  用户需求
# ──────────────────────────────────────

class UserRequirement(BaseModel):
    product_id: str
    text: str = ""
    budget: int | None = None
    priorities: list[str] = []
    usage_scenario: str = ""
    voice_transcript: str = ""


# ──────────────────────────────────────
#  证据
# ──────────────────────────────────────

class EvidenceItem(BaseModel):
    id: str
    product_id: str
    type: str                                # professional_review | user_review
    source_name: str = ""
    source_credibility: float = 0.0
    title: str = ""
    summary: str = ""
    content: str = ""
    evidence_level: str = "support"          # strong_support|support|mixed|oppose
    relevance_score: float = 0.0
    tags: list[str] = []
    created_at: str = ""


class EvidenceListResponse(BaseModel):
    evidences: list[EvidenceItem]
    total: int
    product_id: str


# ──────────────────────────────────────
#  推荐 & 再推荐
# ──────────────────────────────────────

class AlternativeItem(BaseModel):
    product_id: str
    name: str
    brand: str = ""
    price_range: list[int] = []
    quick_score: float = 0.0
    reason: str = ""
    tags: list[str] = []


class PurchaseAdvice(BaseModel):
    lowest_price: dict | None = None
    recommended_channel: dict | None = None
    all_channels: list[dict] = []


class RecommendationResult(BaseModel):
    product_id: str
    product_name: str
    overall_score: float
    verdict: str                             # 强烈推荐|可以考虑|谨慎购买|不推荐|信息不足
    summary: str
    supporting_evidence: list[EvidenceItem] = []
    risk_evidence: list[EvidenceItem] = []
    pending_items: list[str] = []
    alternatives: list[AlternativeItem] = []
    purchase_advice: PurchaseAdvice | None = None


class ReAnalyzeResponse(BaseModel):
    product_id: str
    alternatives: list[AlternativeItem]
    original_requirement: dict | None = None


class DissatisfactionReason(BaseModel):
    product_id: str
    reasons: list[str] = []                  # 如 ["价格太高", "不符合需求"]
    previous_requirements: dict | None = None


# ──────────────────────────────────────
#  购买渠道
# ──────────────────────────────────────

class PurchaseChannel(BaseModel):
    id: str
    product_id: str
    platform: str
    shop_name: str = ""
    price: float = 0.0
    url: str = ""
    in_stock: bool = True
    tags: list[str] = []
    delivery_estimate: str = ""


class ChannelListResponse(BaseModel):
    product_id: str
    channels: list[PurchaseChannel]
    total: int
    lowest_price: float | None = None


class LowestPriceResponse(BaseModel):
    product_id: str
    lowest: PurchaseChannel | None = None


# ──────────────────────────────────────
#  来源详情
# ──────────────────────────────────────

class SourceDetail(BaseModel):
    source_name: str
    source_type: str = ""                    # media|platform|user
    credibility: float = 0.0
    evidence_count: int = 0
    sample_evidence_ids: list[str] = []
