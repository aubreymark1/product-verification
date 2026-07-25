from collections.abc import Iterable
from dataclasses import dataclass

from app.schemas.contracts import Evidence


@dataclass(frozen=True)
class RankedEvidence:
    evidence: Evidence
    relevance_score: float


class EvidenceRanker:
    _RELATION_WEIGHTS = {
        "exact_product": 1.0,
        "likely_same_product": 0.8,
        "similar_product": 0.5,
    }

    def rank(self, evidence: Iterable[Evidence], product_id: str, category_id: str) -> list[RankedEvidence]:
        ranked: list[RankedEvidence] = []
        for item in evidence:
            if item.product_id != product_id or item.category_id != category_id:
                continue
            relation_weight = self._RELATION_WEIGHTS[item.relation_level]
            ranked.append(
                RankedEvidence(
                    evidence=item,
                    relevance_score=round(relation_weight * item.confidence, 4),
                )
            )
        return sorted(ranked, key=lambda item: item.relevance_score, reverse=True)
