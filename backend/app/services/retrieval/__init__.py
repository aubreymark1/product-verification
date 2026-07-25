"""
证据检索服务 — 成员C（接入现有 backend/app/services/retrieval/）

策略：
  - 精确商品优先、同品类别次之
  - 按验证维度筛选
  - 支持/风险/待确认分类
  - 返回稳定的 source_ids
  - 证据不足时明确返回不足，不制造结论
"""
from __future__ import annotations

from typing import Optional
from app.database.mock_store import mock_store, MockStore


def search_evidence(
    product_id: str,
    category_id: str | None = None,
    dimensions: list[str] | None = None,
    source_types: list[str] | None = None,
    limit: int = 20,
    store: MockStore | None = None,
) -> dict:
    """
    通用证据检索

    参数:
        product_id: 目标商品 ID（精确优先）
        category_id: 品类 ID（同类参考降级时使用）
        dimensions: 验证维度，如 ["support", "risk"]
        source_types: 来源类型筛选
        limit: 返回上限
        store: 数据源（测试时可注入）

    返回:
        {
            "product_id": ...,
            "total": ...,
            "supporting": [...],
            "risks": [...],
            "pending": [...],
            "source_ids": [...],
            "insufficient": bool,
        }
    """
    store = store or mock_store

    # 1. 精确商品证据
    exact = [e for e in store.list("evidence.json") if e.get("product_id") == product_id]

    # 2. 同类参考（降级）
    related: list[dict] = []
    if len(exact) < 3 and category_id is not None:
        for p in store.list("products.json"):
            if p.get("category_id") == category_id and p.get("product_id") != product_id:
                related.extend(
                    e for e in store.list("evidence.json")
                    if e.get("product_id") == p.get("product_id")
                )

    # 合并去重
    all_evidences = exact + related
    seen: set[str] = set()
    unique: list[dict] = []
    for e in all_evidences:
        eid = e.get("evidence_id", "")
        if eid and eid not in seen:
            seen.add(eid)
            unique.append(e)

    # 3. 筛选
    if source_types:
        unique = [e for e in unique if e.get("source_type") in source_types]

    # 4. 排序（按 confidence 降序）
    unique.sort(key=lambda e: e.get("confidence", 0), reverse=True)

    # 5. 截断
    unique = unique[:limit]

    # 6. 分类
    supporting = [e for e in unique if e.get("dimension") in ("support", "identity", "fit")]
    risks = [e for e in unique if e.get("dimension") == "risk"]
    pending = [e for e in unique if e.get("dimension") not in ("support", "identity", "fit", "risk")]

    # 7. source_ids
    source_ids = list({e.get("source_title", "") for e in unique if e.get("source_title")})

    return {
        "product_id": product_id,
        "total": len(unique),
        "supporting": supporting,
        "risks": risks,
        "pending": pending,
        "source_ids": source_ids,
        "insufficient": len(unique) == 0,
    }
