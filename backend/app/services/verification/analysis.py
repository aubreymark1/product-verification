import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from app.database.mock_store import MockDataNotFound, MockStore
from app.schemas.contracts import (
    CandidateProduct,
    Conclusion,
    DecisionTrace,
    Evidence,
    MatchStatus,
    ProductFact,
    RecommendationDimension,
    RequirementAnalysisItem,
    UnknownItem,
)
from app.services.retrieval import search_evidence
from app.services.verification.condition_parser import NormalizedRequirement, ParsedConditions


@dataclass(frozen=True)
class AnalysisArtifact:
    score: float
    basis: list[RecommendationDimension]
    requirement_analysis: list[RequirementAnalysisItem]
    product_facts: list[ProductFact]
    decision_chain: list[DecisionTrace]
    unknown_items: list[UnknownItem]
    support: list[Conclusion]
    risks: list[Conclusion]
    uncertain: list[Conclusion]
    summary: str


class EvidenceConstrainedAnalyzer:
    """Builds requirement-level decisions from evidence returned by retrieval."""

    _STATUS_SCORES: dict[MatchStatus, float] = {
        "satisfied": 1.0,
        "conflict": 0.0,
        "unknown": 0.35,
    }
    _SUPPORT_DIMENSIONS = {"support", "identity", "fit"}
    _STOP_TOKENS = {
        "一个",
        "一些",
        "可以",
        "不能",
        "不要",
        "商品",
        "希望",
        "需要",
        "必须",
        "最好",
        "适合",
        "优先",
        "更加",
        "更好",
    }
    _TOLERANCE_MARKERS = ("能接受", "可接受", "不介意", "可以接受")

    def __init__(self, store: MockStore) -> None:
        self.store = store

    def analyze(
        self,
        product: CandidateProduct,
        category_id: str,
        parsed: ParsedConditions,
    ) -> tuple[AnalysisArtifact, dict[str, Evidence]]:
        dimension_labels = self._dimension_labels(category_id)
        analyses: list[RequirementAnalysisItem] = []
        all_evidence = self._all_product_evidence(product.product_id, category_id)
        evidence_by_id: dict[str, Evidence] = {
            item.evidence_id: item for item in all_evidence
        }

        for requirement in parsed.requirements:
            relevant = self._evidence_for_requirement(
                product.product_id,
                category_id,
                requirement,
            )
            evidence_by_id.update({item.evidence_id: item for item in relevant})
            analyses.append(self._analyze_requirement(requirement, relevant, dimension_labels))

        facts = self._unique_facts(
            fact
            for analysis in analyses
            for fact in analysis.product_facts
        )
        basis = [
            RecommendationDimension(
                key=analysis.key,
                label=analysis.label,
                score=self._STATUS_SCORES[analysis.status],
                rationale=analysis.rationale,
                source_ids=analysis.source_ids,
            )
            for analysis in analyses
        ]
        score = self._weighted_score(analyses)
        support, risks, uncertain = self._conclusions(analyses, all_evidence)
        unknown_items = [
            UnknownItem(
                requirement_id=analysis.requirement_id,
                label=f"{analysis.label}：{analysis.value}",
                reason=analysis.rationale,
                needed_evidence="需要当前商品与该需求直接相关的事实或证据。",
            )
            for analysis in analyses
            if analysis.status == "unknown"
        ]
        decision_chain = [
            DecisionTrace(
                requirement_id=analysis.requirement_id,
                requirement=f"{analysis.label}：{analysis.value}",
                fact_ids=[fact.fact_id for fact in analysis.product_facts],
                source_ids=analysis.source_ids,
                status=analysis.status,
                conclusion=analysis.rationale,
            )
            for analysis in analyses
        ]
        summary = self._summary(score, analyses)
        return (
            AnalysisArtifact(
                score=score,
                basis=basis,
                requirement_analysis=analyses,
                product_facts=facts,
                decision_chain=decision_chain,
                unknown_items=unknown_items,
                support=support,
                risks=risks,
                uncertain=uncertain,
                summary=summary,
            ),
            evidence_by_id,
        )

    def _evidence_for_requirement(
        self,
        product_id: str,
        category_id: str,
        requirement: NormalizedRequirement,
    ) -> list[Evidence]:
        try:
            result = search_evidence(
                product_id,
                category_id=category_id,
                limit=100,
                store=self.store,
            )
        except (MockDataNotFound, ValueError):
            return []
        raw_items: list[Mapping[str, Any]] = []
        for group in ("supporting", "risks", "pending"):
            items = result.get(group, [])
            if isinstance(items, list):
                raw_items.extend(item for item in items if isinstance(item, Mapping))

        relevant: list[tuple[Evidence, float]] = []
        for raw_item in raw_items:
            try:
                evidence = Evidence.model_validate(raw_item)
            except ValueError:
                continue
            if evidence.product_id != product_id or evidence.category_id != category_id:
                continue
            relevance = self._relevance(requirement, evidence)
            if relevance > 0:
                relevant.append((evidence, relevance))
        relevant.sort(key=lambda item: item[1], reverse=True)
        return [item[0] for item in relevant]

    def _all_product_evidence(self, product_id: str, category_id: str) -> list[Evidence]:
        try:
            result = search_evidence(
                product_id,
                category_id=category_id,
                limit=100,
                store=self.store,
            )
        except (MockDataNotFound, ValueError):
            return []
        evidence_by_id: dict[str, Evidence] = {}
        for group in ("supporting", "risks", "pending"):
            items = result.get(group, [])
            if not isinstance(items, list):
                continue
            for raw_item in items:
                if not isinstance(raw_item, Mapping):
                    continue
                try:
                    evidence = Evidence.model_validate(raw_item)
                except ValueError:
                    continue
                if evidence.product_id == product_id and evidence.category_id == category_id:
                    evidence_by_id.setdefault(evidence.evidence_id, evidence)
        return list(evidence_by_id.values())

    def _analyze_requirement(
        self,
        requirement: NormalizedRequirement,
        evidence: list[Evidence],
        dimension_labels: Mapping[str, str],
    ) -> RequirementAnalysisItem:
        facts = [
            ProductFact(
                fact_id=f"fact_{item.evidence_id}",
                key=item.dimension,
                label=dimension_labels.get(item.dimension, item.dimension),
                value=item.summary,
                source_ids=[item.evidence_id],
                confidence=self._evidence_strength(item),
            )
            for item in evidence
        ]
        support_strength = sum(
            self._evidence_strength(item)
            for item in evidence
            if item.dimension in self._SUPPORT_DIMENSIONS
        )
        risk_strength = sum(
            self._evidence_strength(item)
            for item in evidence
            if item.dimension == "risk"
        )
        source_ids = [item.evidence_id for item in evidence]

        if not evidence or (support_strength == 0 and risk_strength == 0):
            status: MatchStatus = "unknown"
            rationale = "当前检索结果中没有足以判断该需求的同商品证据，暂时标记为待确认。"
        elif risk_strength > support_strength and not self._accepts_risk(requirement.value):
            status = "conflict"
            rationale = f"与该需求最相关的证据指出潜在风险，当前有 {len(source_ids)} 条同商品来源支持此判断。"
        else:
            status = "satisfied"
            rationale = f"与该需求相关的商品事实得到 {len(source_ids)} 条同商品证据支持。"

        return RequirementAnalysisItem(
            requirement_id=requirement.requirement_id,
            key=requirement.key,
            label=requirement.label,
            value=requirement.value,
            priority=requirement.priority,
            weight=requirement.weight,
            status=status,
            rationale=rationale,
            product_facts=facts,
            source_ids=source_ids,
        )

    def _relevance(self, requirement: NormalizedRequirement, evidence: Evidence) -> float:
        requirement_tokens = self._tokens(
            " ".join([requirement.key, requirement.label, requirement.value])
        )
        evidence_tokens = self._tokens(
            " ".join([evidence.dimension, evidence.summary, evidence.content])
        )
        overlap = requirement_tokens & evidence_tokens
        if not overlap:
            return 0.0
        token_ratio = len(overlap) / max(1, len(requirement_tokens))
        return max(0.35, token_ratio) * self._evidence_strength(evidence)

    @classmethod
    def _tokens(cls, text: str) -> set[str]:
        lowered = text.lower()
        tokens = set(re.findall(r"[a-z0-9_]+", lowered))
        for chunk in re.findall(r"[\u4e00-\u9fff]+", lowered):
            if len(chunk) <= 4:
                tokens.add(chunk)
            for size in range(2, min(4, len(chunk)) + 1):
                tokens.update(chunk[index:index + size] for index in range(len(chunk) - size + 1))
        return {token for token in tokens if token not in cls._STOP_TOKENS}

    @staticmethod
    def _evidence_strength(evidence: Evidence) -> float:
        relation_weight = {
            "exact_product": 1.0,
            "likely_same_product": 0.8,
            "similar_product": 0.5,
        }[evidence.relation_level]
        return round(evidence.confidence * relation_weight, 4)

    @classmethod
    def _accepts_risk(cls, requirement_value: str) -> bool:
        return any(marker in requirement_value for marker in cls._TOLERANCE_MARKERS)

    @classmethod
    def _weighted_score(cls, analyses: Iterable[RequirementAnalysisItem]) -> float:
        items = list(analyses)
        total_weight = sum(item.weight for item in items)
        if total_weight == 0:
            return 0.0
        weighted = sum(item.weight * cls._STATUS_SCORES[item.status] for item in items)
        return round(weighted / total_weight, 4)

    @staticmethod
    def _unique_facts(facts: Iterable[ProductFact]) -> list[ProductFact]:
        unique: dict[str, ProductFact] = {}
        for fact in facts:
            unique.setdefault(fact.fact_id, fact)
        return list(unique.values())

    @staticmethod
    def _conclusions(
        analyses: Iterable[RequirementAnalysisItem],
        all_evidence: Iterable[Evidence],
    ) -> tuple[list[Conclusion], list[Conclusion], list[Conclusion]]:
        support: list[Conclusion] = []
        risks: list[Conclusion] = []
        uncertain: list[Conclusion] = []
        used_source_ids: set[str] = set()
        for analysis in analyses:
            if not analysis.source_ids:
                continue
            used_source_ids.update(analysis.source_ids)
            confidence = round(
                sum(fact.confidence for fact in analysis.product_facts)
                / max(1, len(analysis.product_facts)),
                4,
            )
            conclusion = Conclusion(
                id=f"conclusion_{analysis.requirement_id}",
                claim=f"{analysis.label}（{analysis.value}）：{analysis.rationale}",
                source_ids=analysis.source_ids,
                confidence=confidence,
            )
            if analysis.status == "satisfied":
                support.append(conclusion)
            elif analysis.status == "conflict":
                risks.append(conclusion)
            else:
                uncertain.append(conclusion)

        for evidence in all_evidence:
            if evidence.evidence_id in used_source_ids:
                continue
            conclusion = Conclusion(
                id=f"conclusion_{evidence.evidence_id}",
                claim=evidence.summary,
                source_ids=[evidence.evidence_id],
                confidence=EvidenceConstrainedAnalyzer._evidence_strength(evidence),
            )
            if evidence.dimension in EvidenceConstrainedAnalyzer._SUPPORT_DIMENSIONS:
                support.append(conclusion)
            elif evidence.dimension == "risk":
                risks.append(conclusion)
            else:
                uncertain.append(conclusion)
        return support, risks, uncertain

    @staticmethod
    def _summary(score: float, analyses: list[RequirementAnalysisItem]) -> str:
        if not analyses:
            return "尚未提供可分析的具体需求，当前不生成商品匹配结论。"
        counts = {
            status: sum(item.status == status for item in analyses)
            for status in ("satisfied", "conflict", "unknown")
        }
        return (
            f"逐项需求匹配度为 {score:.2f}：满足 {counts['satisfied']} 项，"
            f"冲突 {counts['conflict']} 项，待确认 {counts['unknown']} 项。"
            "结论仅使用当前商品已绑定的事实和证据。"
        )

    def _dimension_labels(self, category_id: str) -> dict[str, str]:
        try:
            profile = self.store.find_by_id("category-profiles.json", "category_id", category_id)
        except MockDataNotFound:
            return {}
        dimensions = profile.get("verification_dimensions", [])
        if not isinstance(dimensions, list):
            return {}
        return {
            str(item["key"]): str(item["label"])
            for item in dimensions
            if isinstance(item, Mapping) and item.get("key") and item.get("label")
        }
