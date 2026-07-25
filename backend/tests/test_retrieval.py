"""成员 C：商品事实、证据检索和结果恢复测试。"""
from __future__ import annotations

import pytest

from app.database.mock_store import MockDataNotFound, MockStore
from app.schemas.contracts import VerificationResult
from app.services.retrieval import RetrievalService, search_evidence


class InMemoryStore(MockStore):
    def __init__(self, data: dict[str, list[dict[str, object]]]) -> None:
        self.data = data

    def list(self, filename: str) -> list[dict[str, object]]:
        try:
            return self.data[filename]
        except KeyError as exc:
            raise MockDataNotFound(filename) from exc

    def find_by_id(
        self,
        filename: str,
        key: str,
        value: str,
    ) -> dict[str, object]:
        for item in self.list(filename):
            if item.get(key) == value:
                return item
        raise MockDataNotFound(f"{key} not found: {value}")


service = RetrievalService()


class TestProductFacts:
    def test_facts_are_derived_from_traceable_evidence(self) -> None:
        result = service.search_facts("atk_a9_ultimate", "gaming_mouse")

        assert result.total == 4
        assert result.insufficient is False
        assert all(fact.source_ids for fact in result.facts)
        assert all(fact.source_ids == [fact.fact_id.removeprefix("fact_")] for fact in result.facts)

    def test_facts_filter_by_requirement_key(self) -> None:
        support = service.search_facts(
            "atk_a9_ultimate",
            "gaming_mouse",
            keys=["support"],
        )
        risks = service.search_facts(
            "atk_a9_ultimate",
            "gaming_mouse",
            keys=["risk"],
        )

        assert {fact.fact_id for fact in support.facts} == {"fact_ev_video_002"}
        assert {fact.fact_id for fact in risks.facts} == {"fact_ev_risk_001"}

    def test_facts_filter_by_source_type(self) -> None:
        result = service.search_facts(
            "atk_a9_ultimate",
            "gaming_mouse",
            source_types=["official"],
        )

        assert result.total == 0
        assert result.insufficient is True

    def test_facts_reject_category_mismatch(self) -> None:
        result = service.search_facts("atk_a9_ultimate", "wrong_category")

        assert result.total == 0
        assert result.insufficient is True

    def test_facts_for_unknown_product_are_insufficient(self) -> None:
        result = service.search_facts("unknown_product", "gaming_mouse")

        assert result.total == 0
        assert result.insufficient is True


class TestEvidenceSearch:
    def test_search_preserves_required_metadata(self) -> None:
        result = service.search_evidence("atk_a9_ultimate", category_id="gaming_mouse")
        evidences = result.supporting + result.risks + result.pending

        assert result.total == 4
        assert result.insufficient is False
        assert len(evidences) == result.total
        assert all(evidence.evidence_id for evidence in evidences)
        assert all(evidence.source_title for evidence in evidences)
        assert all(0 <= evidence.confidence <= 1 for evidence in evidences)
        assert result.source_ids == [evidence.evidence_id for evidence in evidences]

    def test_search_returns_different_sets_for_different_dimensions(self) -> None:
        support = service.search_evidence(
            "atk_a9_ultimate",
            category_id="gaming_mouse",
            dimensions=["support"],
        )
        risks = service.search_evidence(
            "atk_a9_ultimate",
            category_id="gaming_mouse",
            dimensions=["risk"],
        )

        assert support.source_ids == ["ev_video_002"]
        assert risks.source_ids == ["ev_risk_001"]
        assert support.source_ids != risks.source_ids

    def test_search_filters_by_source_type(self) -> None:
        demo = service.search_evidence(
            "atk_a9_ultimate",
            category_id="gaming_mouse",
            source_types=["demo_mock"],
        )
        official = service.search_evidence(
            "atk_a9_ultimate",
            category_id="gaming_mouse",
            source_types=["official"],
        )

        assert demo.total == 4
        assert official.insufficient is True
        assert official.source_ids == []

    def test_related_evidence_is_marked_similar_to_target(self) -> None:
        store = InMemoryStore(
            {
                "products.json": [
                    {"product_id": "target", "category_id": "category"},
                    {"product_id": "related", "category_id": "category"},
                ],
                "evidence.json": [
                    {
                        "evidence_id": "ev_related",
                        "product_id": "related",
                        "category_id": "category",
                        "dimension": "support",
                        "source_type": "official",
                        "relation_level": "exact_product",
                        "summary": "相关商品证据",
                        "content": "完整内容",
                        "source_title": "官方资料",
                        "source_platform": "official",
                        "source_url": "https://example.com",
                        "published_at": "2026-07-25",
                        "confidence": 0.9,
                    }
                ],
            }
        )

        result = RetrievalService(store).search_evidence(
            "target",
            category_id="category",
        )

        assert result.source_ids == ["ev_related"]
        assert result.supporting[0].product_id == "related"
        assert result.supporting[0].relation_level == "similar_product"

    def test_unknown_or_wrong_category_does_not_leak_related_evidence(self) -> None:
        unknown = service.search_evidence("unknown_product", category_id="gaming_mouse")
        mismatch = service.search_evidence("atk_a9_ultimate", category_id="wrong_category")

        assert unknown.insufficient is True
        assert mismatch.insufficient is True
        assert unknown.source_ids == []
        assert mismatch.source_ids == []

    def test_missing_evidence_file_degrades_to_insufficient(self) -> None:
        store = InMemoryStore(
            {
                "products.json": [
                    {"product_id": "target", "category_id": "category"},
                ]
            }
        )

        result = RetrievalService(store).search_evidence("target", "category")

        assert result.insufficient is True
        assert result.total == 0

    def test_invalid_limit_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="greater than zero"):
            service.search_evidence("atk_a9_ultimate", "gaming_mouse", limit=0)

    def test_legacy_function_keeps_dictionary_contract(self) -> None:
        result = search_evidence(
            "atk_a9_ultimate",
            category_id="gaming_mouse",
            dimensions=["risk"],
        )

        assert result["source_ids"] == ["ev_risk_001"]
        assert result["risks"][0]["evidence_id"] == "ev_risk_001"


class TestResultRecovery:
    def test_stored_result_is_normalized_to_verification_result(self) -> None:
        result = service.get_result("res_001")

        assert isinstance(result, VerificationResult)
        assert result.result_id == "res_001"
        assert result.recommendation_score == 0.95
        assert result.round == 1
        assert result.recommendation_basis == []
        assert result.purchase_channels == []

    def test_cached_result_keeps_same_model(self) -> None:
        stored = service.get_result("res_001")
        assert stored is not None
        cached = stored.model_copy(update={"summary": "缓存结果"})

        result = service.get_result("cached", cached_results={"cached": cached})

        assert result is cached
        assert result.summary == "缓存结果"

    def test_unknown_result_returns_none(self) -> None:
        assert service.get_result("unknown_result") is None
