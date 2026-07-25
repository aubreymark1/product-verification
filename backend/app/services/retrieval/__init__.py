"""商品事实、证据检索和结果恢复服务。"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from app.database.mock_store import MockDataNotFound, MockStore, mock_store
from app.schemas.contracts import (
    Evidence,
    EvidenceSearchResult,
    ProductFact,
    ProductFactsResponse,
    SourceType,
    VerificationResult,
)
from app.services.retrieval.product_image import (
    CachedProductImageProvider,
    NullProductImageProvider,
    ProductImageProvider,
    ProductImageRequest,
    ProductImageResult,
    SearchImageProvider,
    TavilyImageProvider,
    configured_product_image_provider,
)


_RELATION_WEIGHTS = {
    "exact_product": 1.0,
    "likely_same_product": 0.8,
    "similar_product": 0.5,
}
_SUPPORT_DIMENSIONS = {"support", "identity", "fit"}


class RetrievalService:
    """从现有数据源读取并验证可追溯的商品上下文。"""

    def __init__(self, store: MockStore | None = None) -> None:
        self.store = store or mock_store

    def search_facts(
        self,
        product_id: str,
        category_id: str,
        keys: list[str] | None = None,
        source_types: list[SourceType] | None = None,
    ) -> ProductFactsResponse:
        """把目标商品的证据整理为带稳定来源的结构化事实。"""
        resolved_category = self._resolve_category(product_id, category_id)
        if resolved_category is None:
            return self._empty_facts(product_id, category_id)

        evidences = [
            evidence
            for evidence in self._load_evidence()
            if evidence.product_id == product_id
            and evidence.category_id == resolved_category
            and (not keys or evidence.dimension in keys)
            and (not source_types or evidence.source_type in source_types)
        ]
        facts = [
            ProductFact(
                fact_id=f"fact_{evidence.evidence_id}",
                product_id=evidence.product_id,
                category_id=evidence.category_id,
                key=evidence.dimension,
                label=evidence.dimension,
                value=evidence.summary,
                confidence=evidence.confidence,
                source_type=evidence.source_type,
                source_ids=[evidence.evidence_id],
            )
            for evidence in evidences
        ]
        return ProductFactsResponse(
            product_id=product_id,
            category_id=resolved_category,
            facts=facts,
            total=len(facts),
            insufficient=not facts,
        )

    def search_evidence(
        self,
        product_id: str,
        category_id: str | None = None,
        dimensions: list[str] | None = None,
        source_types: list[SourceType] | None = None,
        limit: int = 20,
    ) -> EvidenceSearchResult:
        """按商品、品类、需求维度和来源类型检索证据。"""
        if limit < 1:
            raise ValueError("limit must be greater than zero")

        resolved_category = self._resolve_category(product_id, category_id)
        if resolved_category is None:
            return self._empty_evidence(product_id, category_id)

        filtered = [
            evidence
            for evidence in self._load_evidence()
            if evidence.category_id == resolved_category
            and (not dimensions or evidence.dimension in dimensions)
            and (not source_types or evidence.source_type in source_types)
        ]
        exact = [evidence for evidence in filtered if evidence.product_id == product_id]

        related: list[Evidence] = []
        if len(exact) < 3:
            related_product_ids = self._product_ids_for_category(resolved_category) - {product_id}
            related = [
                evidence.model_copy(update={"relation_level": "similar_product"})
                for evidence in filtered
                if evidence.product_id in related_product_ids
            ]

        unique: list[Evidence] = []
        seen_ids: set[str] = set()
        for evidence in exact + related:
            if evidence.evidence_id not in seen_ids:
                seen_ids.add(evidence.evidence_id)
                unique.append(evidence)

        unique.sort(
            key=lambda evidence: (
                _RELATION_WEIGHTS[evidence.relation_level] * evidence.confidence,
                evidence.evidence_id,
            ),
            reverse=True,
        )
        selected = unique[:limit]
        supporting = [
            evidence for evidence in selected if evidence.dimension in _SUPPORT_DIMENSIONS
        ]
        risks = [evidence for evidence in selected if evidence.dimension == "risk"]
        pending = [
            evidence
            for evidence in selected
            if evidence.dimension not in _SUPPORT_DIMENSIONS
            and evidence.dimension != "risk"
        ]
        return EvidenceSearchResult(
            product_id=product_id,
            category_id=resolved_category,
            supporting=supporting,
            risks=risks,
            pending=pending,
            source_ids=[evidence.evidence_id for evidence in selected],
            total=len(selected),
            insufficient=not selected,
        )

    def get_result(
        self,
        result_id: str,
        cached_results: Mapping[str, VerificationResult | dict[str, Any]] | None = None,
    ) -> VerificationResult | None:
        """从运行时缓存或现有持久化数据恢复统一的验证结果模型。"""
        if cached_results and result_id in cached_results:
            cached = cached_results[result_id]
            if isinstance(cached, VerificationResult):
                return cached
            return VerificationResult.model_validate(cached)

        try:
            stored = dict(
                self.store.find_by_id("verification-results.json", "result_id", result_id)
            )
        except MockDataNotFound:
            return None

        if "recommendation_score" not in stored:
            stored["recommendation_score"] = stored.pop("confidence", 0)
        return VerificationResult.model_validate(stored)

    def _resolve_category(
        self,
        product_id: str,
        category_id: str | None,
    ) -> str | None:
        try:
            product = self.store.find_by_id("products.json", "product_id", product_id)
        except MockDataNotFound:
            return None

        actual_category = product.get("category_id")
        if not isinstance(actual_category, str) or not actual_category:
            return None
        if category_id is not None and category_id != actual_category:
            return None
        return actual_category

    def _product_ids_for_category(self, category_id: str) -> set[str]:
        try:
            products = self.store.list("products.json")
        except MockDataNotFound:
            return set()
        return {
            str(product["product_id"])
            for product in products
            if product.get("category_id") == category_id and product.get("product_id")
        }

    def _load_evidence(self) -> list[Evidence]:
        try:
            rows = self.store.list("evidence.json")
        except MockDataNotFound:
            return []
        normalized: list[Evidence] = []
        for row in rows:
            payload = dict(row)
            payload.setdefault("source_type", "demo_mock")
            payload.setdefault("relation_level", "exact_product")
            payload.setdefault("summary", payload.get("claim") or payload.get("content") or payload.get("dimension") or "")
            payload.setdefault("content", payload.get("summary", ""))
            payload.setdefault("source_title", payload.get("evidence_id", "unknown"))
            payload.setdefault("source_platform", "unknown")
            normalized.append(Evidence.model_validate(payload))
        return normalized

    @staticmethod
    def _empty_facts(product_id: str, category_id: str) -> ProductFactsResponse:
        return ProductFactsResponse(
            product_id=product_id,
            category_id=category_id,
            facts=[],
            total=0,
            insufficient=True,
        )

    @staticmethod
    def _empty_evidence(
        product_id: str,
        category_id: str | None,
    ) -> EvidenceSearchResult:
        return EvidenceSearchResult(
            product_id=product_id,
            category_id=category_id,
            supporting=[],
            risks=[],
            pending=[],
            source_ids=[],
            total=0,
            insufficient=True,
        )


_retrieval_service = RetrievalService()


def search_evidence(
    product_id: str,
    category_id: str | None = None,
    dimensions: list[str] | None = None,
    source_types: list[SourceType] | None = None,
    limit: int = 20,
    store: MockStore | None = None,
) -> dict[str, Any]:
    """保留既有字典接口，供验证服务兼容调用。"""
    service = RetrievalService(store) if store else _retrieval_service
    return service.search_evidence(
        product_id=product_id,
        category_id=category_id,
        dimensions=dimensions,
        source_types=source_types,
        limit=limit,
    ).model_dump()
