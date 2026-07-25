from collections.abc import Iterable, Mapping
from typing import Any

from app.core.config import settings
from app.database.mock_store import MockDataNotFound, MockStore, mock_store
from app.schemas.contracts import (
    AnalysisMode,
    CandidateProduct,
    DemoInsights,
    Evidence,
    PurchaseChannel,
    RerunRecommendationRequest,
    VerificationRequest,
    VerificationResult,
)
from app.services.recommendation.generator import RecommendationGenerator
from app.services.verification.analysis import AnalysisArtifact, EvidenceConstrainedAnalyzer
from app.services.verification.condition_parser import ConditionParser, ParsedConditions
from app.services.verification.demo_insights import DemoScenarioProvider
from app.services.verification.evidence_ranker import EvidenceRanker
from app.services.verification.fallback import FallbackProvider
from app.services.verification.model_validator import ModelOutputValidator
from app.services.verification.openai_provider import OpenAIVerificationProvider
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
        analyzer: EvidenceConstrainedAnalyzer | None = None,
        model_provider: OpenAIVerificationProvider | None = None,
        model_validator: ModelOutputValidator | None = None,
        demo_scenario_provider: DemoScenarioProvider | None = None,
    ) -> None:
        self.store = store
        self.condition_parser = condition_parser or ConditionParser()
        self.evidence_ranker = evidence_ranker or EvidenceRanker()
        self.recommendation_generator = recommendation_generator or RecommendationGenerator()
        self.source_validator = source_validator or SourceValidator()
        self.fallback_provider = fallback_provider or FallbackProvider()
        self.analyzer = analyzer or EvidenceConstrainedAnalyzer(store)
        self.model_validator = model_validator or ModelOutputValidator()
        self.demo_scenario_provider = demo_scenario_provider or DemoScenarioProvider()
        self._model_requested = settings.openai_verification_enabled or model_provider is not None
        self._model_setup_failed = False
        if model_provider is not None:
            self.model_provider = model_provider
        elif settings.openai_verification_enabled:
            try:
                self.model_provider = OpenAIVerificationProvider()
            except Exception:
                self.model_provider = None
                self._model_setup_failed = True
        else:
            self.model_provider = None
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
        change_summary: str = "",
    ) -> VerificationResult:
        product = self._product(request.product_id, request.category_id)
        product_data = self.store.find_by_id("products.json", "product_id", request.product_id)
        parsed = self._parse(request.category_id, request.conditions, request.raw_query)
        artifact, evidence_by_id, analysis_mode = self._artifact(
            product,
            request.category_id,
            parsed,
        )
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
            analysis_mode=analysis_mode,
            change_summary=change_summary,
            demo_insights=(
                self.demo_scenario_provider.build(
                    product,
                    request.category_id,
                    request.conditions,
                    request.raw_query,
                    product_data,
                    round_number,
                )
                if settings.demo_insights_enabled
                else None
            ),
        )
        self._results[result.result_id] = result
        self._histories[result.result_id] = set(previously_seen_product_ids) | {product.product_id}
        return result

    def rerun(self, request: RerunRecommendationRequest) -> VerificationResult:
        previous = self._get_previous_result(request)
        conditions = dict(previous.conditions) if request.inherit_previous_needs else {}
        conditions.update(request.conditions_patch)
        raw_query = request.raw_query.strip()
        if request.inherit_previous_needs and not raw_query:
            raw_query = previous.raw_query
        feedback = [
            item.strip()
            for item in [*request.dissatisfaction_reasons, request.dissatisfaction_note]
            if item.strip()
        ]
        raw_query = self._merge_query(raw_query, feedback)

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
                self._parse(request.category_id, conditions, raw_query),
                use_model=False,
            )[0].score,
        )
        change_summary = self._change_summary(
            previous,
            selected,
            request,
            feedback,
            history,
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
            change_summary=change_summary,
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
        *,
        use_model: bool = True,
    ) -> tuple[AnalysisArtifact, dict[str, Evidence], AnalysisMode]:
        artifact, evidence_by_id = self.analyzer.analyze(product, category_id, parsed)
        if not use_model or not self._model_requested:
            return artifact, evidence_by_id, "rule"
        if self.model_provider is None or self._model_setup_failed:
            return self._degraded_artifact(artifact), evidence_by_id, "degraded"

        enhanced, mode = self.fallback_provider.execute(
            lambda: (
                self.model_validator.apply(
                    artifact,
                    self.model_provider.explain(artifact.requirement_analysis),
                ),
                "ai",
            ),
            lambda _error: (self._degraded_artifact(artifact), "degraded"),
            timeout_seconds=settings.openai_timeout_seconds,
        )
        return enhanced, evidence_by_id, mode

    def _build_result(
        self,
        *,
        product: CandidateProduct,
        request: VerificationRequest,
        parsed: ParsedConditions,
        artifact: AnalysisArtifact,
        evidence_by_id: Mapping[str, Evidence],
        round_number: int,
        is_follow_up: bool,
        needs_inherited: bool,
        dissatisfaction_reasons: list[str],
        result_id: str,
        analysis_mode: AnalysisMode,
        change_summary: str,
        demo_insights: DemoInsights | None = None,
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
            requirement_analysis=artifact.requirement_analysis,
            product_facts=artifact.product_facts,
            decision_chain=artifact.decision_chain,
            unknown_items=artifact.unknown_items,
            analysis_mode=analysis_mode,
            change_summary=change_summary,
            summary=summary,
            support=support,
            risks=risks,
            uncertain=uncertain,
            dissatisfaction_reasons=dissatisfaction_reasons,
            purchase_channels=self._purchase_channels(product.product_id),
            demo_insights=demo_insights,
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

    def _parse(
        self,
        category_id: str,
        conditions: Mapping[str, Any],
        raw_query: str,
    ) -> ParsedConditions:
        return self.condition_parser.parse(
            conditions,
            raw_query,
            self._condition_definitions(category_id),
        )

    def _condition_definitions(self, category_id: str) -> dict[str, Mapping[str, Any]]:
        try:
            profile = self.store.find_by_id("category-profiles.json", "category_id", category_id)
        except MockDataNotFound:
            return {}
        fields = profile.get("condition_fields", [])
        if not isinstance(fields, list):
            return {}
        return {
            str(item["key"]): item
            for item in fields
            if isinstance(item, Mapping) and item.get("key")
        }

    @staticmethod
    def _merge_query(raw_query: str, feedback: Iterable[str]) -> str:
        parts: list[str] = []
        for part in [raw_query.strip(), *(item.strip() for item in feedback)]:
            if part and part not in parts:
                parts.append(part)
        return "；".join(parts)

    @staticmethod
    def _change_summary(
        previous: VerificationResult,
        selected: CandidateProduct,
        request: RerunRecommendationRequest,
        feedback: list[str],
        history: Iterable[str],
    ) -> str:
        inherited = (
            f"继承上一轮 {len(previous.requirement_analysis)} 项需求"
            if request.inherit_previous_needs
            else "未继承上一轮需求"
        )
        changed_fields = "、".join(request.conditions_patch) or "无"
        feedback_text = "；".join(feedback) or "无"
        return (
            f"{inherited}；条件修改：{changed_fields}；用户反馈：{feedback_text}；"
            f"已过滤 {len(set(history))} 个看过的商品；候选由"
            f"“{previous.product.product_name}”调整为“{selected.product_name}”。"
        )

    @staticmethod
    def _degraded_artifact(artifact: AnalysisArtifact) -> AnalysisArtifact:
        return AnalysisArtifact(
            score=artifact.score,
            basis=artifact.basis,
            requirement_analysis=artifact.requirement_analysis,
            product_facts=artifact.product_facts,
            decision_chain=artifact.decision_chain,
            unknown_items=artifact.unknown_items,
            support=artifact.support,
            risks=artifact.risks,
            uncertain=artifact.uncertain,
            summary=f"AI 服务不可用，已使用证据约束规则完成降级分析。{artifact.summary}",
        )

    def _purchase_channels(self, product_id: str) -> list[PurchaseChannel]:
        try:
            normalized: list[PurchaseChannel] = []
            channel_type_map = {
                "抖音官方店": "official",
                "抖音授权店": "official",
                "天猫官方店": "official",
                "京东自营": "marketplace",
                "平台自营": "marketplace",
            }
            for item in self.store.list("purchase-channels.json"):
                if item.get("product_id") != product_id:
                    continue
                payload = dict(item)
                channel_type = str(payload.get("channel_type", ""))
                payload["channel_type"] = channel_type_map.get(channel_type, channel_type or "other")
                availability = payload.get("availability")
                if availability not in {"available", "pending", "placeholder"}:
                    status = str(payload.get("status", ""))
                    availability = "available" if status == "现货" else "pending" if "预售" in status else "placeholder"
                payload["availability"] = availability
                payload["note"] = str(payload.get("note") or payload.get("policy") or payload.get("status") or "")
                normalized.append(PurchaseChannel.model_validate(payload))
            return normalized
        except (MockDataNotFound, ValueError):
            return []

    def _initial_result_id(self, product_id: str) -> str:
        try:
            source = self.store.find_by_id("verification-results.json", "product_id", product_id)
            return str(source.get("result_id", f"result_{product_id}"))
        except MockDataNotFound:
            return f"result_{product_id}"
