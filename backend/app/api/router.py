from fastapi import APIRouter, Request
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
    RerunRecommendationRequest,
    SelectionRequest,
    VerificationRequest,
    Video,
)
from app.services.retrieval import RetrievalService
from app.services.verification.service import NoAlternativeProductError, VerificationService
from app.services.vision.service import VisionService

router = APIRouter()
vision_service = VisionService()
verification_service = VerificationService()
retrieval_service = RetrievalService()


def ok(data: object) -> dict[str, object]:
    return ApiResponse(success=True, data=data, error=None).model_dump()


def not_found(message: str) -> JSONResponse:
    payload = ApiResponse(
        success=False,
        data=None,
        error=ApiError(code="NOT_FOUND", message=message),
    ).model_dump()
    return JSONResponse(status_code=404, content=payload)


def bad_request(code: str, message: str) -> JSONResponse:
    payload = ApiResponse(
        success=False,
        data=None,
        error=ApiError(code=code, message=message),
    ).model_dump()
    return JSONResponse(status_code=400, content=payload)


def conflict(message: str) -> JSONResponse:
    payload = ApiResponse(
        success=False,
        data=None,
        error=ApiError(code="NO_ALTERNATIVE_PRODUCT", message=message),
    ).model_dump()
    return JSONResponse(status_code=409, content=payload)


def internal_error(message: str = "服务器内部错误") -> JSONResponse:
    payload = ApiResponse(
        success=False,
        data=None,
        error=ApiError(code="INTERNAL_ERROR", message=message),
    ).model_dump()
    return JSONResponse(status_code=500, content=payload)


@router.get("/health", response_model=ApiResponse)
def health() -> dict[str, object]:
    return ok({"status": "ok", "environment": "development"})


@router.get("/videos/{video_id}", response_model=ApiResponse)
def get_video(video_id: str) -> dict[str, object] | JSONResponse:
    try:
        return ok(Video.model_validate(mock_store.find_by_id("videos.json", "video_id", video_id)))
    except MockDataNotFound as exc:
        return not_found(str(exc))


@router.post("/vision/identify", response_model=ApiResponse)
def identify(selection: SelectionRequest) -> dict[str, object] | JSONResponse:
    try:
        return ok(vision_service.identify(selection))
    except (MockDataNotFound, FileNotFoundError) as exc:
        return not_found(str(exc))


@router.get("/categories/{category_id}/profile", response_model=ApiResponse)
def get_profile(category_id: str) -> dict[str, object] | JSONResponse:
    try:
        profile = CategoryProfile.model_validate(
            mock_store.find_by_id("category-profiles.json", "category_id", category_id)
        )
        return ok(profile)
    except MockDataNotFound as exc:
        return not_found(str(exc))


@router.post("/verification/run", response_model=ApiResponse)
def run_verification(request: VerificationRequest) -> dict[str, object] | JSONResponse:
    try:
        return ok(verification_service.run(request))
    except MockDataNotFound as exc:
        return not_found(str(exc))


@router.post("/recommendations/rerun", response_model=ApiResponse)
def rerun_recommendation(request: RerunRecommendationRequest) -> dict[str, object] | JSONResponse:
    try:
        return ok(verification_service.rerun(request))
    except MockDataNotFound as exc:
        return not_found(str(exc))
    except NoAlternativeProductError as exc:
        return conflict(str(exc))


@router.get("/purchase-channels/{product_id}", response_model=ApiResponse)
def get_purchase_channels(product_id: str) -> dict[str, object]:
    return ok(verification_service.purchase_channels(product_id))


@router.get("/evidence/{evidence_id}", response_model=ApiResponse)
def get_evidence(evidence_id: str) -> dict[str, object] | JSONResponse:
    try:
        evidence = Evidence.model_validate(
            mock_store.find_by_id("evidence.json", "evidence_id", evidence_id)
        )
        return ok(evidence)
    except MockDataNotFound as exc:
        return not_found(str(exc))


@router.get("/results/{result_id}", response_model=ApiResponse)
def get_result(result_id: str) -> dict[str, object] | JSONResponse:
    """按 result_id 恢复验证结果，支持刷新或重新打开结果链接。"""
    try:
        cached = getattr(verification_service, "_results", {})
        result = retrieval_service.get_result(result_id, cached_results=cached)
        if result is None:
            return not_found(f"result_id not found: {result_id}")
        return ok(result)
    except Exception:
        return internal_error("获取验证结果时发生内部错误")


@router.post("/comparison/add", response_model=ApiResponse)
def add_comparison(request: ComparisonRequest) -> dict[str, object]:
    result = ComparisonResult(
        comparison_id="comparison_demo_001",
        product_ids=[request.product_id],
        status="placeholder",
        message="横评功能将在第二阶段接入。",
    )
    return ok(result)
