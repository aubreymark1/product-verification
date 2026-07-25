from app.schemas.contracts import (
    CandidateProduct,
    RerunRecommendationRequest,
    VerificationRequest,
)
from app.services.verification.demo_insights import DemoScenarioProvider
from app.services.verification.service import VerificationService


def test_demo_insights_are_personalized_and_repeatable() -> None:
    provider = DemoScenarioProvider()
    product = CandidateProduct(
        product_id="demo_mouse",
        product_name="Demo Gaming Mouse",
        confidence=0.9,
        image_url=None,
    )
    product_data = {
        "price": 299,
        "attributes": {
            "weight": "54g",
            "sensor": "Demo Sensor",
            "battery_life": "80h",
            "connectivity": "2.4GHz 无线/USB 有线",
        },
    }

    first = provider.build(
        product,
        "gaming_mouse",
        {"budget": "300 元以内"},
        "主要玩 FPS，希望低延迟",
        product_data,
    )
    second = provider.build(
        product,
        "gaming_mouse",
        {"budget": "300 元以内"},
        "主要玩 FPS，希望低延迟",
        product_data,
    )

    assert first.is_mock is True
    assert first.scenario_id == second.scenario_id
    assert [item.content for item in first.reviews] == [item.content for item in second.reviews]
    assert [item.price for item in first.price_offers] == [item.price for item in second.price_offers]
    assert first.presentation_score == second.presentation_score
    assert len(first.support_items) == 2
    assert len(first.risk_items) == 2
    assert len(first.pending_items) == 2
    assert "预算敏感" in first.personalization_note
    assert all(item.source_type == "demo_mock" for item in first.reviews)
    assert all(item.source_type == "demo_mock" for item in first.price_offers)
    assert all(item.source_type == "demo_mock" for item in first.risk_items)


def test_rerun_returns_another_product_with_its_own_demo_insights() -> None:
    service = VerificationService()
    first = service.run(
        VerificationRequest(
            video_id="demo_video_001",
            product_id="logitech_gpx_2",
            category_id="gaming_mouse",
            conditions={"budget": "<300", "connection": "wireless"},
            raw_query="FPS wireless",
        )
    )

    second = service.rerun(
        RerunRecommendationRequest(
            video_id="demo_video_001",
            product_id=first.product.product_id,
            category_id="gaming_mouse",
            previous_result_id=first.result_id,
            dissatisfaction_note="更适合预算",
        )
    )

    assert second.product.product_id != first.product.product_id
    assert second.is_follow_up is True
    assert second.demo_insights is not None
    assert second.demo_insights.scenario_id != first.demo_insights.scenario_id
