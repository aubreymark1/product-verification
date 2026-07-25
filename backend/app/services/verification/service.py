from collections.abc import Iterable, Mapping
from typing import Any

from app.database.mock_store import MockDataNotFound, MockStore, mock_store
from app.schemas.contracts import (
    CandidateProduct,
    Conclusion,
    Evidence,
    PurchaseChannel,
    RerunRecommendationRequest,
    VerificationRequest,
    VerificationResult,
)
from app.services.recommendation.generator import RecommendationArtifact, RecommendationGenerator
from app.services.verification.condition_parser import ConditionParser, ParsedConditions
from app.services.verification.evidence_ranker import EvidenceRanker, RankedEvidence
from app.services.verification.fallback import FallbackProvider
from app.services.verification.source_validator import SourceValidator


class NoAlternativeProductError(RuntimeError):
    """Raised when a rerun has exhausted all candidates in the detected category."""


class VerificationService:
    def __init__(
        self,
        store: MockStore = mock_store,
        condition_parser: ConditionParser | None = None,
        evidence_ranker: EvidenceRanker | None = None,
        recommendation_generator: RecommendationGenerator | None = None,
        source_validator: SourceValidator | None = None,
        fallback_provider: FallbackProvider | None = None,
    ) -> None:
        self.store = store
        self.condition_parser = condition_parser or ConditionParser()
        self.evidence_ranker = evidence_ranker or EvidenceRanker()
        self.recommendation_generator = recommendation_generator or RecommendationGenerator()
        self.source_validator = source_validator or SourceValidator()
        self.fallback_provider = fallback_provider or FallbackProvider()
        self._results: dict[str, VerificationResult] = {}
        self._histories: dict[str, set[str]] = {}

    def run(
        self,
        request: VerificationRequest,
        *,
        round_number: int = 1,
        is_follow_up: bool = False,
        needs_inherited: bool = False,
        dissatisfaction_reasons: Iterable[str] = (),
        result_id: str | None = None,
        previously_seen_product_ids: Iterable[str] = (),
    ) -> VerificationResult:
        product = self._product(request.product_id, request.category_id)
        parsed = self.condition_parser.parse(request.conditions, request.raw_query)
        artifact, evidence_by_id = self._artifact(product, request.category_id, parsed)
        result = self._build_result(
            product=product,
            request=request,
            parsed=parsed,
            artifact=artifact,
            evidence_by_id=evidence_by_id,
            round_number=round_number,
            is_follow_up=is_follow_up,
            needs_inherited=needs_inherited,
            dissatisfaction_reasons=list(dissatisfaction_reasons),
            result_id=result_id or self._initial_result_id(product.product_id),
        )
        self._results[result.result_id] = result
        self._histories[result.result_id] = set(previously_seen_product_ids) | {product.product_id}
        return result

    def rerun(self, request: RerunRecommendationRequest) -> VerificationResult:
        previous = self._get_previous_result(request)
        conditions = dict(previous.conditions) if request.inherit_previous_needs else {}
        conditions.update(request.conditions_patch)
        raw_query = request.raw_query.strip() or previous.raw_query
        if request.dissatisfaction_note.strip():
            raw_query = " ".join(part for part in [raw_query, request.dissatisfaction_note.strip()] if part)

        history = self._histories.get(previous.result_id, {previous.product.product_id})
        candidates = [
            self._product_from_data(item)
            for item in self.store.list("products.json")
            if item.get("category_id") == request.category_id and item.get("product_id") not in history
        ]
        if not candidates:
            raise NoAlternativeProductError("当前品类没有未使用的替代候选商品")

        selected = max(
            candidates,
            key=lambda product: self._artifact(
                product,
                request.category_id,
                self.condition_parser.parse(conditions, raw_query),
            )[0].score,
        )
        return self.run(
            VerificationRequest(
                video_id=request.video_id,
                product_id=selected.product_id,
                category_id=request.category_id,
                conditions=conditions,
                raw_query=raw_query,
                input_mode="text",
            ),
            round_number=previous.round + 1,
            is_follow_up=True,
            needs_inherited=request.inherit_previous_needs,
            dissatisfaction_reasons=request.dissatisfaction_reasons,
            result_id=f"{previous.result_id}_r{previous.round + 1}",
            previously_seen_product_ids=history,
        )

    def purchase_channels(self, product_id: str) -> list[PurchaseChannel]:
        return self._purchase_channels(product_id)

    def _get_previous_result(self, request: RerunRecommendationRequest) -> VerificationResult:
        cached = self._results.get(request.previous_result_id)
        if cached is not None:
            return cached
        source = self.store.find_by_id("verification-results.json", "result_id", request.previous_result_id)
        return self.run(
            VerificationRequest(
                video_id=request.video_id,
                product_id=str(source["product_id"]),
                category_id=request.category_id,
                conditions=source.get("conditions", {}),
                raw_query=str(source.get("raw_query", "")),
            ),
            result_id=request.previous_result_id,
        )

    def _artifact(
        self,
        product: CandidateProduct,
        category_id: str,
        parsed: ParsedConditions,
    ) -> tuple[RecommendationArtifact, dict[str, Evidence]]:
        evidence_by_id = self._evidence(product.product_id, category_id)
        ranked = self.evidence_ranker.rank(evidence_by_id.values(), product.product_id, category_id)
        expected_condition_count = self._expected_condition_count(category_id)
        artifact = self.fallback_provider.execute(
            lambda: self.recommendation_generator.generate(
                product,
                parsed.conditions,
                parsed.raw_query,
                ranked,
                expected_condition_count,
            ),
            lambda _error: self.recommendation_generator.fallback(
                product,
                parsed.conditions,
                parsed.raw_query,
                expected_condition_count,
            ),
        )
        return artifact, evidence_by_id

    def _build_result(
        self,
        *,
        product: CandidateProduct,
        request: VerificationRequest,
        parsed: ParsedConditions,
        artifact: RecommendationArtifact,
        evidence_by_id: Mapping[str, Evidence],
        round_number: int,
        is_follow_up: bool,
        needs_inherited: bool,
        dissatisfaction_reasons: list[str],
        result_id: str,
    ) -> VerificationResult:
        support = self.source_validator.filter_conclusions(artifact.support, evidence_by_id)
        risks = self.source_validator.filter_conclusions(artifact.risks, evidence_by_id)
        uncertain = self.source_validator.filter_conclusions(artifact.uncertain, evidence_by_id)
        summary = artifact.summary
        if is_follow_up:
            summary = f"{summary} 本轮已根据上一轮反馈和补充条件重新筛选未使用的候选商品。"
        return VerificationResult(
            result_id=result_id,
            product=product,
            conditions=parsed.conditions,
            raw_query=parsed.raw_query,
            round=round_number,
            is_follow_up=is_follow_up,
            needs_inherited=needs_inherited,
            recommendation_score=artifact.score,
            recommendation_basis=artifact.basis,
            summary=summary,
            support=support,
            risks=risks,
            uncertain=uncertain,
            dissatisfaction_reasons=dissatisfaction_reasons,
            purchase_channels=self._purchase_channels(product.product_id),
        )

    def _product(self, product_id: str, category_id: str) -> CandidateProduct:
        product = self.store.find_by_id("products.json", "product_id", product_id)
        if product.get("category_id") != category_id:
            raise MockDataNotFound(f"category_id mismatch for product: {product_id}")
        return self._product_from_data(product)

    @staticmethod
    def _product_from_data(data: Mapping[str, Any]) -> CandidateProduct:
        return CandidateProduct.model_validate(data)

    def _evidence(self, product_id: str, category_id: str) -> dict[str, Evidence]:
        try:
            evidence = [Evidence.model_validate(item) for item in self.store.list("evidence.json")]
        except (MockDataNotFound, ValueError):
            return {}
        return {
            item.evidence_id: item
            for item in evidence
            if item.product_id == product_id and item.category_id == category_id
        }

    def _expected_condition_count(self, category_id: str) -> int:
        try:
            profile = self.store.find_by_id("category-profiles.json", "category_id", category_id)
        except MockDataNotFound:
            return 0
        fields = profile.get("condition_fields", [])
        return len(fields) if isinstance(fields, list) else 0

    def _purchase_channels(self, product_id: str) -> list[PurchaseChannel]:
        try:
            return [
                PurchaseChannel.model_validate(item)
                for item in self.store.list("purchase-channels.json")
                if item.get("product_id") == product_id
            ]
        except (MockDataNotFound, ValueError):
            return []

    def _initial_result_id(self, product_id: str) -> str:
        try:
            source = self.store.find_by_id("verification-results.json", "product_id", product_id)
            return str(source.get("result_id", f"result_{product_id}"))
        except MockDataNotFound:
            return f"result_{product_id}"
