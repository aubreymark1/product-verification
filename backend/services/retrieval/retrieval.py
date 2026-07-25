"""
证据检索服务
成员C负责 —— 提供通用检索能力，支撑推荐接口

策略：
  - 精确商品优先
  - 疑似同款次之
  - 同类参考最后
  - 按验证维度筛选
  - 按 source_name / type 筛选
  - 支持/风险/待确认分类
  - 返回稳定的 source_ids
  - 证据不足时明确返回不足，不制造结论
"""
from __future__ import annotations

from typing import Optional
from repository import MockRepository, get_repository


def search_evidence(
    product_id: str,
    category_id: str | None = None,
    dimensions: list[str] | None = None,
    evidence_types: list[str] | None = None,
    source_types: list[str] | None = None,
    limit: int = 20,
    repo: MockRepository | None = None,
) -> dict:
    """
    通用证据检索

    参数:
        product_id: 目标商品 ID（精确优先）
        category_id: 品类 ID（同类参考降级时使用）
        dimensions: 验证维度，如 ["续航", "性价比"]
        evidence_types: 证据类型筛选，如 ["professional_review"]
        source_types: 来源类型筛选，如 ["家电实验室"]
        limit: 返回上限
        repo: 仓库实例（测试时可注入）

    返回:
        {
            "product_id": ...,
            "total": ...,
            "supporting": [...],   # 支持证据 (strong_support, support)
            "risks": [...],        # 风险证据 (oppose, mixed)
            "pending": [...],      # 其他
            "source_ids": [...],
            "insufficient": bool,  # 证据不足标记
        }
    """
    repo = repo or get_repository()

    # 1. 精确商品证据
    exact = repo.get_evidences_by_product(product_id)

    # 2. 同类参考（降级）
    related: list[dict] = []
    if len(exact) < 3 and category_id is not None:
        products = repo.get_products_by_category(category_id)
        for p in products:
            if p["id"] == product_id:
                continue
            related.extend(repo.get_evidences_by_product(p["id"]))

    # 合并并按优先级排序
    all_evidences = exact + related
    # 去重
    seen: set[str] = set()
    unique: list[dict] = []
    for e in all_evidences:
        if e["id"] not in seen:
            seen.add(e["id"])
            unique.append(e)
    all_evidences = unique

    # 3. 筛选
    if evidence_types:
        all_evidences = [e for e in all_evidences if e.get("type") in evidence_types]

    if source_types:
        all_evidences = [e for e in all_evidences if e.get("source_name") in source_types]

    # 4. 按维度匹配度排序（标签 + 标题关键词）
    if dimensions:
        def _dimension_score(evidence: dict) -> float:
            score = 0.0
            text = (evidence.get("title", "") + " " +
                    " ".join(evidence.get("tags", []))).lower()
            for dim in dimensions:
                if dim.lower() in text:
                    score += 1.0
            return score

        # 先按维度匹配度降序，再按 relevance_score 降序
        all_evidences.sort(
            key=lambda e: (_dimension_score(e), e.get("relevance_score", 0)),
            reverse=True
        )
    else:
        all_evidences.sort(key=lambda e: e.get("relevance_score", 0), reverse=True)

    # 5. 截断
    all_evidences = all_evidences[:limit]

    # 6. 分类
    supporting = [e for e in all_evidences if e.get("evidence_level") in ("strong_support", "support")]
    risks = [e for e in all_evidences if e.get("evidence_level") in ("oppose", "mixed")]
    pending = [e for e in all_evidences if e.get("evidence_level") not in
               ("strong_support", "support", "oppose", "mixed")]

    # 7. 收集 source_ids
    source_ids = list({e.get("source_name", "") for e in all_evidences if e.get("source_name")})

    return {
        "product_id": product_id,
        "total": len(all_evidences),
        "supporting": supporting,
        "risks": risks,
        "pending": pending,
        "source_ids": source_ids,
        "insufficient": len(all_evidences) == 0,
    }
