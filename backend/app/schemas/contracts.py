from typing import Any, Literal

from pydantic import BaseModel, Field


RelationLevel = Literal["exact_product", "likely_same_product", "similar_product"]
SourceType = Literal["official", "professional_test", "user_feedback", "demo_mock"]
FieldType = Literal["single_select", "multi_select", "number", "text", "boolean"]
PurchaseChannelType = Literal["official", "marketplace", "retail", "other"]


class ApiError(BaseModel):
    code: str
    message: str


class ApiResponse(BaseModel):
    success: bool
    data: Any | None = None
    error: ApiError | None = None


class BBox(BaseModel):
    x: float = Field(ge=0, le=1)
    y: float = Field(ge=0, le=1)
    width: float = Field(ge=0, le=1)
    height: float = Field(ge=0, le=1)


class VideoObject(BaseModel):
    object_id: str
    category_id: str
    label: str
    bbox: BBox


class Video(BaseModel):
    video_id: str
    title: str
    video_url: str | None = None
    duration: float = Field(ge=0)
    objects: list[VideoObject]


class SelectionRequest(BaseModel):
    video_id: str
    timestamp: float = Field(ge=0)
    selection: BBox


class CandidateProduct(BaseModel):
    product_id: str
    product_name: str
    confidence: float = Field(ge=0, le=1)
    image_url: str | None = None


class IdentifyResult(BaseModel):
    category_id: str
    category_name: str
    visual_attributes: dict[str, str]
    candidates: list[CandidateProduct]


class ConditionField(BaseModel):
    key: str
    label: str
    type: FieldType
    required: bool = False
    options: list[str] = Field(default_factory=list)
    min: float | None = None
    max: float | None = None


class VerificationDimension(BaseModel):
    key: str
    label: str


class CategoryProfile(BaseModel):
    category_id: str
    category_name: str
    condition_fields: list[ConditionField]
    verification_dimensions: list[VerificationDimension]


class VerificationRequest(BaseModel):
    video_id: str
    product_id: str
    category_id: str
    conditions: dict[str, Any] = Field(default_factory=dict)
    raw_query: str = ""


class Conclusion(BaseModel):
    id: str
    claim: str
    source_ids: list[str]
    confidence: float = Field(ge=0, le=1)


class VerificationResult(BaseModel):
    result_id: str
    product: CandidateProduct
    conditions: dict[str, Any]
    summary: str
    support: list[Conclusion]
    risks: list[Conclusion]
    uncertain: list[Conclusion]
    confidence: float = Field(ge=0, le=1)


class Evidence(BaseModel):
    evidence_id: str
    product_id: str
    category_id: str
    dimension: str
    source_type: SourceType
    relation_level: RelationLevel
    summary: str
    content: str
    source_title: str
    source_platform: str
    source_url: str | None = None
    published_at: str | None = None
    confidence: float = Field(ge=0, le=1)


class ComparisonRequest(BaseModel):
    product_id: str
    category_id: str
    result_id: str | None = None


class ComparisonResult(BaseModel):
    comparison_id: str
    product_ids: list[str]
    status: Literal["placeholder"]
    message: str


# ── 购买渠道 ───────────────────────────

class PurchaseChannel(BaseModel):
    channel_id: str
    product_id: str
    channel_name: str
    channel_type: PurchaseChannelType
    url: str | None = None
    availability: Literal["available", "pending", "placeholder"] = "placeholder"
    note: str = ""


# ── 商品事实模型（成员C：品类无关，避免写死具体字段）──

class ProductFact(BaseModel):
    """单一商品事实，通过 key/value 保持品类无关。"""
    fact_id: str
    product_id: str
    category_id: str
    key: str
    label: str
    value: str
    confidence: float = Field(default=0, ge=0, le=1)
    source_type: SourceType = "demo_mock"
    source_ids: list[str] = Field(default_factory=list)


class ProductFactsResponse(BaseModel):
    """商品事实集合的响应包装。"""
    product_id: str
    category_id: str
    facts: list[ProductFact] = Field(default_factory=list)
    total: int = 0
    insufficient: bool = False


# ── 结果持久化模型（成员C：支持重新打开结果链接）──

class StoredResult(BaseModel):
    """可持久化的验证结果，用于 GET /api/results/{result_id}。"""
    result_id: str
    product_id: str
    category_id: str
    conditions: dict[str, Any] = Field(default_factory=dict)
    raw_query: str = ""
    round: int = Field(default=1, ge=1)
    is_follow_up: bool = False
    needs_inherited: bool = False
    recommendation_score: float = Field(default=0, ge=0, le=1)
    summary: str = ""
    support: list[Conclusion] = Field(default_factory=list)
    risks: list[Conclusion] = Field(default_factory=list)
    uncertain: list[Conclusion] = Field(default_factory=list)
    created_at: str | None = None
