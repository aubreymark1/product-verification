import time

from app.schemas.contracts import RerunRecommendationRequest, SelectionRequest, VerificationRequest
from app.services.verification.fallback import FallbackProvider
from app.services.verification.service import NoAlternativeProductError, VerificationService
from app.services.vision.service import VisionService


def test_vision_service_uses_selected_region_and_ranks_candidates() -> None:
    result = VisionService().identify(
        SelectionRequest(
            video_id="demo_video_001",
            timestamp=1.0,
            selection={"x": 0.22, "y": 0.25, "width": 0.38, "height": 0.34},
        )
    )
    assert result.category_id == "gaming_mouse"
    assert result.candidates[0].confidence >= result.candidates[-1].confidence


def test_verification_binds_only_same_product_evidence_and_reruns_with_alternative() -> None:
    service = VerificationService()
    first = service.run(
        VerificationRequest(
            video_id="demo_video_001",
            product_id="atk_a9_ultimate",
            category_id="gaming_mouse",
            conditions={"usage_scene": "场景A"},
        )
    )
    assert first.support
    assert all(source_id.startswith("ev_") for item in first.support for source_id in item.source_ids)

    second = service.rerun(
        RerunRecommendationRequest(
            video_id="demo_video_001",
            product_id=first.product.product_id,
            category_id="gaming_mouse",
            previous_result_id=first.result_id,
            dissatisfaction_reasons=["预算不合适"],
            conditions_patch={"notes": "更轻便"},
        )
    )
    assert second.product.product_id != first.product.product_id
    assert second.conditions["usage_scene"] == "场景A"
    assert second.conditions["notes"] == "更轻便"
    assert second.is_follow_up is True

    current = second
    while True:
        try:
            current = service.rerun(
                RerunRecommendationRequest(
                    video_id="demo_video_001",
                    product_id=current.product.product_id,
                    category_id="gaming_mouse",
                    previous_result_id=current.result_id,
                )
            )
        except NoAlternativeProductError:
            break


def test_fallback_provider_handles_timeout() -> None:
    def slow_operation() -> str:
        time.sleep(0.05)
        return "primary"

    assert FallbackProvider().execute(slow_operation, lambda _error: "fallback", timeout_seconds=0.001) == "fallback"
