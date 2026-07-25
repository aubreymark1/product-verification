"""
推荐/验证降级逻辑 — 成员C
接入 backend/app/services/verification/

当 AI 引擎不可用时，基于证据检索提供可靠的降级结果
"""
from __future__ import annotations

from typing import Any
from app.schemas.contracts import (
    CandidateProduct, Conclusion, VerificationResult,
)
from app.services.retrieval import search_evidence


def build_fallback_verification(
    product_id: str,
    category_id: str,
    conditions: dict[str, Any],
    product_name: str | None = None,
    confidence: float = 0.85,
    image_url: str | None = None,
) -> VerificationResult:
    """
    降级验证：基于证据检索构造可用的验证结果
    所有证据结论必须带有效 source_ids，没有来源时不输出
    """
    result = search_evidence(product_id, category_id=category_id)
    evs = result["supporting"] + result["risks"] + result["pending"]

    def _build_conclusions(items: list[dict[str, Any]]) -> list[Conclusion]:
        conclusions: list[Conclusion] = []
        for evidence in items:
            source_id = evidence.get("evidence_id", "")
            if not source_id:
                continue  # 没有来源时不输出
            conclusions.append(Conclusion(
                id=source_id,
                claim=evidence.get("summary", evidence.get("content", "")),
                source_ids=[source_id],
                confidence=evidence.get("confidence", 0.5),
            ))
        return conclusions

    support = _build_conclusions(result["supporting"])
    risks = _build_conclusions(result["risks"])
    uncertain = _build_conclusions(result["pending"])

    import uuid
    total = len(evs)
    summary = (
        f"已分析 {total} 条验证信息。"
        f"{len(support)} 条支持、{len(risks)} 条风险、{len(uncertain)} 条待确认。"
        + ("建议谨慎评估。" if len(risks) > 0 else "")
    )

    return VerificationResult(
        result_id=str(uuid.uuid4())[:8],
        product=CandidateProduct(
            product_id=product_id,
            product_name=product_name or product_id,
            confidence=confidence,
            image_url=image_url,
        ),
        conditions=conditions,
        summary=summary,
        support=support,
        risks=risks,
        uncertain=uncertain,
        recommendation_score=0.7 if support else 0.5,
    )
