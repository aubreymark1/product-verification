from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from app.schemas.contracts import (
    CandidateProduct,
    Conclusion,
    RecommendationDimension,
)
from app.services.verification.evidence_ranker import RankedEvidence


@dataclass(frozen=True)
class RecommendationArtifact:
    score: float
    basis: list[RecommendationDimension]
    support: list[Conclusion]
    risks: list[Conclusion]
    uncertain: list[Conclusion]
    summary: str


class RecommendationGenerator:
    """Explainable MVP scorer; a model-backed generator can replace this boundary later."""

    def generate(
        self,
        product: CandidateProduct,
        conditions: Mapping[str, Any],
        raw_query: str,
        ranked_evidence: Sequence[RankedEvidence],
        expected_condition_count: int,
    ) -> RecommendationArtifact:
        evidence_score = self._average(item.relevance_score for item in ranked_evidence)
        condition_score = self._condition_score(conditions, raw_query, expected_condition_count)
        visual_score = product.confidence
        score = round((evidence_score * 0.45) + (condition_score * 0.35) + (visual_score * 0.20), 4)

        source_ids = [item.evidence.evidence_id for item in ranked_evidence]
        basis = [
            RecommendationDimension(
                key="evidence_fit",
                label="证据匹配",
                score=evidence_score,
                rationale=f"当前商品有 {len(ranked_evidence)} 条同商品证据，按来源关系和证据强度重排。",
                source_ids=source_ids,
            ),
            RecommendationDimension(
                key="condition_fit",
                label="需求匹配",
                score=condition_score,
                rationale=f"根据已填写的 {len(conditions)} 项结构化条件和文字需求进行匹配。",
            ),
            RecommendationDimension(
                key="visual_confidence",
                label="识别候选置信度",
                score=visual_score,
                rationale="沿用视觉候选的识别置信度，仅作为综合匹配度的一个维度。",
            ),
        ]

        support: list[Conclusion] = []
        risks: list[Conclusion] = []
        uncertain: list[Conclusion] = []
        for item in ranked_evidence[:5]:
            conclusion = Conclusion(
                id=f"conclusion_{item.evidence.evidence_id}",
                claim=item.evidence.summary,
                source_ids=[item.evidence.evidence_id],
                confidence=item.relevance_score,
            )
            if item.evidence.dimension == "support":
                support.append(conclusion)
            elif item.evidence.dimension == "risk":
                risks.append(conclusion)
            else:
                uncertain.append(conclusion)

        if ranked_evidence:
            summary = f"当前综合匹配度为 {score:.2f}，结论仅基于已绑定证据，仍需结合用户条件确认。"
        else:
            summary = "当前没有可绑定到该商品的证据，暂不输出商品事实结论。"
        return RecommendationArtifact(score, basis, support, risks, uncertain, summary)

    def fallback(
        self,
        product: CandidateProduct,
        conditions: Mapping[str, Any],
        raw_query: str,
        expected_condition_count: int,
    ) -> RecommendationArtifact:
        condition_score = self._condition_score(conditions, raw_query, expected_condition_count)
        score = round((condition_score * 0.5) + (product.confidence * 0.1), 4)
        return RecommendationArtifact(
            score=score,
            basis=[
                RecommendationDimension(
                    key="fallback_condition_fit",
                    label="需求匹配（降级）",
                    score=condition_score,
                    rationale="AI 服务不可用，暂按已填写需求保留待确认结果。",
                )
            ],
            support=[],
            risks=[],
            uncertain=[],
            summary="AI 服务暂不可用，已切换为待确认结果；当前没有可绑定证据的商品事实结论。",
        )

    @staticmethod
    def _average(values: Iterable[float]) -> float:
        values_list = list(values)
        return round(sum(values_list) / len(values_list), 4) if values_list else 0.0

    @staticmethod
    def _condition_score(conditions: Mapping[str, Any], raw_query: str, expected_count: int) -> float:
        provided = len(conditions) + (1 if raw_query else 0)
        if expected_count > 0:
            return round(min(1.0, provided / expected_count), 4)
        return 1.0 if provided else 0.0
