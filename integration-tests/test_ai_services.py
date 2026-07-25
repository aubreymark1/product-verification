import time

from app.schemas.contracts import RerunRecommendationRequest, SelectionRequest, VerificationRequest
from app.services.verification.fallback import FallbackProvider
from app.services.verification.openai_provider import ModelAnalysisOutput, ModelExplanation
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


def test_same_product_changes_status_for_different_user_requirements() -> None:
    service = VerificationService()
    battery_profile = service.run(
        VerificationRequest(
            video_id="demo_video_001",
            product_id="atk_a9_ultimate",
            category_id="gaming_mouse",
            raw_query="希望续航持久",
        )
    )
    quality_profile = service.run(
        VerificationRequest(
            video_id="demo_video_001",
            product_id="atk_a9_ultimate",
            category_id="gaming_mouse",
            raw_query="不能有按键晃动",
        )
    )

    assert battery_profile.requirement_analysis[0].status == "satisfied"
    assert quality_profile.requirement_analysis[0].status == "conflict"
    assert quality_profile.requirement_analysis[0].source_ids == ["ev_risk_001"]
    assert battery_profile.recommendation_score > quality_profile.recommendation_score


def test_missing_evidence_is_unknown_without_unsourced_conclusion() -> None:
    result = VerificationService().run(
        VerificationRequest(
            video_id="demo_video_001",
            product_id="atk_a9_ultimate",
            category_id="gaming_mouse",
            raw_query="主要用于日常办公",
        )
    )

    analysis = result.requirement_analysis[0]
    assert analysis.status == "unknown"
    assert analysis.source_ids == []
    assert result.unknown_items[0].requirement_id == analysis.requirement_id
    assert all(
        analysis.requirement_id not in conclusion.id
        for conclusion in [*result.support, *result.risks, *result.uncertain]
    )


def test_rerun_feedback_becomes_requirements_and_change_explanation() -> None:
    service = VerificationService()
    first = service.run(
        VerificationRequest(
            video_id="demo_video_001",
            product_id="atk_a9_ultimate",
            category_id="gaming_mouse",
            conditions={"hand_size": "小手 (17cm以下)"},
            raw_query="希望续航持久",
        )
    )
    second = service.rerun(
        RerunRecommendationRequest(
            video_id="demo_video_001",
            product_id=first.product.product_id,
            category_id="gaming_mouse",
            previous_result_id=first.result_id,
            dissatisfaction_reasons=["预算不合适"],
            dissatisfaction_note="希望更轻便",
        )
    )

    requirement_values = {item.value for item in second.requirement_analysis}
    assert "预算不合适" in requirement_values
    assert "希望更轻便" in requirement_values
    assert second.product.product_id != first.product.product_id
    assert "已过滤 1 个看过的商品" in second.change_summary
    assert first.product.product_name in second.change_summary
    assert second.product.product_name in second.change_summary


class ValidExplanationProvider:
    def explain(self, requirements: list) -> ModelAnalysisOutput:
        return ModelAnalysisOutput(
            summary="模型仅对服务端已确定的事实与状态进行了受约束解释。",
            explanations=[
                ModelExplanation(
                    requirement_id=item.requirement_id,
                    rationale=f"受约束解释：{item.rationale}",
                    source_ids=item.source_ids,
                )
                for item in requirements
            ],
        )


class InventedSourceProvider:
    def explain(self, requirements: list) -> ModelAnalysisOutput:
        return ModelAnalysisOutput(
            summary="包含伪造来源的输出。",
            explanations=[
                ModelExplanation(
                    requirement_id=item.requirement_id,
                    rationale="不可信解释",
                    source_ids=["invented_source"],
                )
                for item in requirements
            ],
        )


def test_model_explanation_is_validated_and_invalid_sources_degrade() -> None:
    request = VerificationRequest(
        video_id="demo_video_001",
        product_id="atk_a9_ultimate",
        category_id="gaming_mouse",
        raw_query="希望续航持久",
    )
    enhanced = VerificationService(model_provider=ValidExplanationProvider()).run(request)
    degraded = VerificationService(model_provider=InventedSourceProvider()).run(request)

    assert enhanced.analysis_mode == "ai"
    assert enhanced.requirement_analysis[0].rationale.startswith("受约束解释")
    assert degraded.analysis_mode == "degraded"
    assert degraded.summary.startswith("AI 服务不可用")
    assert "invented_source" not in {
        source_id
        for item in degraded.requirement_analysis
        for source_id in item.source_ids
    }
