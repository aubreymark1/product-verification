from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.database.mock_store import MockDataNotFound, mock_store
from app.schemas.contracts import (
    ApiError,
    ApiResponse,
    CategoryProfile,
    ComparisonRequest,
    ComparisonResult,
    Evidence,
    IdentifyResult,
    SelectionRequest,
    VerificationRequest,
    VerificationResult,
    Video,
)
from app.services.verification import build_fallback_verification

router = APIRouter()


def ok(data: object) -> dict[str, object]:
    return ApiResponse(success=True, data=data, error=None).model_dump()


def not_found(message: str) -> JSONResponse:
    payload = ApiResponse(
        success=False,
        data=None,
        error=ApiError(code="NOT_FOUND", message=message),
    ).model_dump()
    return JSONResponse(status_code=404, content=payload)


@router.get("/health", response_model=ApiResponse)
def health() -> dict[str, object]:
    return ok({"status": "ok", "environment": "development"})


# ── 视频 ──────────────────────────────

@router.get("/videos/{video_id}", response_model=ApiResponse)
def get_video(video_id: str) -> dict[str, object] | JSONResponse:
    try:
        return ok(Video.model_validate(mock_store.find_by_id("videos.json", "video_id", video_id)))
    except MockDataNotFound as exc:
        return not_found(str(exc))


# ── 视觉识别 ──────────────────────────

@router.post("/vision/identify", response_model=ApiResponse)
def identify(selection: SelectionRequest) -> dict[str, object] | JSONResponse:
    try:
        video = mock_store.find_by_id("videos.json", "video_id", selection.video_id)
        detected_object = video["objects"][0]
        profile = mock_store.find_by_id("category-profiles.json", "category_id", detected_object["category_id"])
        candidates = [
            item for item in mock_store.list("products.json")
            if item["category_id"] == detected_object["category_id"]
        ]
        result = {
            "category_id": detected_object["category_id"],
            "category_name": profile["category_name"],
            "visual_attributes": {"object_id": detected_object.get("object_id", ""), "selection_status": "mock_identified"},
            "candidates": candidates,
        }
        return ok(IdentifyResult.model_validate(result))
    except MockDataNotFound as exc:
        return not_found(str(exc))


# ── 品类配置 ──────────────────────────

@router.get("/categories/{category_id}/profile", response_model=ApiResponse)
def get_profile(category_id: str) -> dict[str, object] | JSONResponse:
    try:
        profile = CategoryProfile.model_validate(
            mock_store.find_by_id("category-profiles.json", "category_id", category_id)
        )
        return ok(profile)
    except MockDataNotFound as exc:
        return not_found(str(exc))


# ── 验证 ⭐ 核心 ───────────────────────

@router.post("/verification/run", response_model=ApiResponse)
def run_verification(request: VerificationRequest) -> dict[str, object] | JSONResponse:
    # 优先从预置缓存读取
    try:
        result = mock_store.find_by_id("verification-results.json", "product_id", request.product_id)
        result["conditions"] = request.conditions
        # 确保所有结论都有 source_ids
        for key in ("support", "risks", "uncertain"):
            result[key] = [
                c for c in result.get(key, [])
                if c.get("source_ids") and any(s for s in c["source_ids"] if s)
            ]
        return ok(VerificationResult.model_validate(result))
    except MockDataNotFound:
        pass

    # 降级：基于证据检索构造验证结果
    try:
        product = mock_store.find_by_id("products.json", "product_id", request.product_id)
    except MockDataNotFound:
        return not_found(f"product_id not found: {request.product_id}")

    fallback = build_fallback_verification(
        product_id=request.product_id,
        category_id=request.category_id,
        conditions=request.conditions,
        product_name=product.get("product_name", ""),
        confidence=product.get("confidence", 0.85),
        image_url=product.get("image_url"),
    )
    return ok(fallback)


# ── 证据详情 ──────────────────────────

@router.get("/evidence/{evidence_id}", response_model=ApiResponse)
def get_evidence(evidence_id: str) -> dict[str, object] | JSONResponse:
    try:
        evidence = Evidence.model_validate(
            mock_store.find_by_id("evidence.json", "evidence_id", evidence_id)
        )
        return ok(evidence)
    except MockDataNotFound as exc:
        return not_found(str(exc))


# ── 横评 ──────────────────────────────

@router.post("/comparison/add", response_model=ApiResponse)
def add_comparison(request: ComparisonRequest) -> dict[str, object]:
    result = ComparisonResult(
        comparison_id="comparison_demo_001",
        product_ids=[request.product_id],
        status="placeholder",
        message="横评功能将在第二阶段接入。",
    )
    return ok(result)
