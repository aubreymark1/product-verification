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


@router.get("/videos/{video_id}", response_model=ApiResponse)
def get_video(video_id: str) -> dict[str, object] | JSONResponse:
    try:
        return ok(Video.model_validate(mock_store.find_by_id("videos.json", "video_id", video_id)))
    except MockDataNotFound as exc:
        return not_found(str(exc))


@router.post("/vision/identify", response_model=ApiResponse)
def identify(selection: SelectionRequest) -> dict[str, object] | JSONResponse:
    try:
        video = mock_store.find_by_id("videos.json", "video_id", selection.video_id)
        detected_object = video["objects"][0]
        object_id = detected_object["object_id"]
        profile = mock_store.find_by_id("category-profiles.json", "category_id", detected_object["category_id"])
        candidates = [
            item for item in mock_store.list("products.json")
            if item["category_id"] == detected_object["category_id"]
        ]
        result = {
            "category_id": detected_object["category_id"],
            "category_name": profile["category_name"],
            "visual_attributes": {"object_id": object_id, "selection_status": "mock_identified"},
            "candidates": candidates,
        }
        return ok(IdentifyResult.model_validate(result))
    except MockDataNotFound as exc:
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
        result = mock_store.find_by_id("verification-results.json", "product_id", request.product_id)
        result["conditions"] = request.conditions
        return ok(VerificationResult.model_validate(result))
    except MockDataNotFound as exc:
        return not_found(str(exc))


@router.get("/evidence/{evidence_id}", response_model=ApiResponse)
def get_evidence(evidence_id: str) -> dict[str, object] | JSONResponse:
    try:
        evidence = Evidence.model_validate(
            mock_store.find_by_id("evidence.json", "evidence_id", evidence_id)
        )
        return ok(evidence)
    except MockDataNotFound as exc:
        return not_found(str(exc))


@router.post("/comparison/add", response_model=ApiResponse)
def add_comparison(request: ComparisonRequest) -> dict[str, object]:
    result = ComparisonResult(
        comparison_id="comparison_demo_001",
        product_ids=[request.product_id],
        status="placeholder",
        message="横评功能将在第二阶段接入。",
    )
    return ok(result)
