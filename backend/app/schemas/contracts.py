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
    input_mode: Literal["text", "voice", "mixed"] = "text"


class Conclusion(BaseModel):
    id: str
    claim: str
    source_ids: list[str] = Field(min_length=1)
    confidence: float = Field(ge=0, le=1)


class RecommendationDimension(BaseModel):
    key: str
    label: str
    score: float = Field(ge=0, le=1)
    rationale: str
    source_ids: list[str] = Field(default_factory=list)


class PurchaseChannel(BaseModel):
    channel_id: str
    product_id: str
    channel_name: str
    channel_type: PurchaseChannelType
    url: str | None = None
    availability: Literal["available", "pending", "placeholder"] = "placeholder"
    note: str = ""


class VerificationResult(BaseModel):
    result_id: str
    product: CandidateProduct
    conditions: dict[str, Any]
    raw_query: str = ""
    round: int = Field(default=1, ge=1)
    is_follow_up: bool = False
    needs_inherited: bool = False
    recommendation_score: float = Field(default=0, ge=0, le=1)
    recommendation_basis: list[RecommendationDimension] = Field(default_factory=list)
    summary: str
    support: list[Conclusion]
    risks: list[Conclusion]
    uncertain: list[Conclusion]
    dissatisfaction_reasons: list[str] = Field(default_factory=list)
    purchase_channels: list[PurchaseChannel] = Field(default_factory=list)


class RerunRecommendationRequest(BaseModel):
    video_id: str
    product_id: str
    category_id: str
    previous_result_id: str
    dissatisfaction_reasons: list[str] = Field(default_factory=list)
    dissatisfaction_note: str = ""
    inherit_previous_needs: bool = True
    conditions_patch: dict[str, Any] = Field(default_factory=dict)
    raw_query: str = ""


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
