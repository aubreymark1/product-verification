"""
证据检索服务 — 成员C

策略：
  - 精确商品优先、同品类降级
  - 按验证维度筛选
  - 支持/风险/待确认分类
  - 返回稳定的 source_ids
  - 证据不足时明确返回不足，不制造结论
  - 商品事实通过 key/value 模型保持品类无关
"""
from __future__ import annotations

from typing import Any

from app.database.mock_store import MockStore, mock_store
from app.schemas.contracts import ProductFact


class RetrievalService:
    """商品事实、证据检索和结果恢复服务。"""

    def __init__(self, store: MockStore | None = None) -> None:
        self.store = store or mock_store

    # ── 商品事实 ──────────────────────────────────────────

    def search_facts(
        self,
        product_id: str,
        category_id: str,
        keys: list[str] | None = None,
        source_types: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        检索商品事实，兼容类目差异，不写死具体字段。

        参数:
            product_id: 目标商品 ID
            category_id: 品类 ID
            keys: 可选，按 key 筛选（如 ["sensor", "weight"]）
            source_types: 可选，按来源类型筛选

        返回:
            {
                "product_id": str,
                "category_id": str,
                "facts": list[ProductFact],
                "total": int,
                "insufficient": bool,
            }
        """
        # 1. 从 product-facts.json 读取结构化事实
        all_facts: list[dict[str, Any]] = []
        try:
            all_facts = [
                f for f in self.store.list("product-facts.json")
                if f.get("product_id") == product_id
            ]
        except Exception:
            pass

        # 2. 如果 product-facts.json 没有该商品的数据，从 products.json attributes 降级构建
        if not all_facts:
            try:
                product = self.store.find_by_id("products.json", "product_id", product_id)
                attrs = product.get("attributes", {})
                if isinstance(attrs, dict):
                    for attr_key, attr_value in attrs.items():
                        all_facts.append({
                            "fact_id": f"attr_{product_id}_{attr_key}",
                            "product_id": product_id,
                            "category_id": category_id,
                            "key": attr_key,
                            "label": attr_key,
                            "value": str(attr_value),
                            "confidence": 0.5,
                            "source_type": "demo_mock",
                            "source_ids": [],
                        })
            except Exception:
                pass

        # 3. 按 key 筛选
        if keys:
            all_facts = [f for f in all_facts if f.get("key") in keys]

        # 4. 按 source_type 筛选
        if source_types:
            all_facts = [f for f in all_facts if f.get("source_type") in source_types]

        # 5. 构造 ProductFact 模型
        facts = [ProductFact.model_validate(f) for f in all_facts]

        return {
            "product_id": product_id,
            "category_id": category_id,
            "facts": facts,
            "total": len(facts),
            "insufficient": len(facts) == 0,
        }

    # ── 证据检索 ──────────────────────────────────────────

    def search_evidence(
        self,
        product_id: str,
        category_id: str | None = None,
        dimensions: list[str] | None = None,
        source_types: list[str] | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """
        通用证据检索

        参数:
            product_id: 目标商品 ID（精确优先）
            category_id: 品类 ID（同类参考降级时使用）
            dimensions: 验证维度，如 ["support", "fit", "identity", "risk"]
            source_types: 来源类型筛选
            limit: 返回上限

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
        # 1. 精确商品证据
        exact = [e for e in self.store.list("evidence.json") if e.get("product_id") == product_id]

        # 2. 同类参考（降级）
        related: list[dict[str, Any]] = []
        if len(exact) < 3 and category_id is not None:
            for p in self.store.list("products.json"):
                if p.get("category_id") == category_id and p.get("product_id") != product_id:
                    related.extend(
                        e for e in self.store.list("evidence.json")
                        if e.get("product_id") == p.get("product_id")
                    )

        # 合并去重
        all_evidences = exact + related
        seen: set[str] = set()
        unique: list[dict[str, Any]] = []
        for e in all_evidences:
            eid = e.get("evidence_id", "")
            if eid and eid not in seen:
                seen.add(eid)
                unique.append(e)

        # 3. 按 source_type 筛选
        if source_types:
            unique = [e for e in unique if e.get("source_type") in source_types]

        # 4. 按维度筛选
        if dimensions:
            unique = [e for e in unique if e.get("dimension") in dimensions]

        # 5. 排序（按 relation_level 权重 × confidence）
        _relation_weight = {
            "exact_product": 1.0,
            "likely_same_product": 0.8,
            "similar_product": 0.5,
        }
        unique.sort(
            key=lambda e: _relation_weight.get(e.get("relation_level", "similar_product"), 0.5)
            * e.get("confidence", 0),
            reverse=True,
        )

        # 6. 截断
        unique = unique[:limit]

        # 7. 分类
        supporting = [e for e in unique if e.get("dimension") in ("support", "identity", "fit")]
        risks = [e for e in unique if e.get("dimension") == "risk"]
        pending = [e for e in unique if e.get("dimension") not in ("support", "identity", "fit", "risk")]

        # 8. source_ids 使用稳定的证据ID
        source_ids = list({e.get("evidence_id", "") for e in unique if e.get("evidence_id")})

        return {
            "product_id": product_id,
            "total": len(unique),
            "supporting": supporting,
            "risks": risks,
            "pending": pending,
            "source_ids": source_ids,
            "insufficient": len(unique) == 0,
        }

    # ── 品类商品列表 ──────────────────────────────────────

    def search_products(self, category_id: str) -> list[dict[str, Any]]:
        """返回指定品类下的所有商品（含基础信息）。"""
        try:
            return [
                item for item in self.store.list("products.json")
                if item.get("category_id") == category_id
            ]
        except Exception:
            return []

    # ── 结果恢复 ──────────────────────────────────────────

    def get_result(
        self,
        result_id: str,
        cached_results: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """
        按 result_id 恢复验证结果。

        优先级:
        1. 内存缓存（由 VerificationService 维护）
        2. verification-results.json 持久化数据

        返回 None 表示结果不存在。
        """
        # 1. 内存缓存（由调用方注入）
        if cached_results and result_id in cached_results:
            return cached_results[result_id]

        # 2. 持久化存储
        try:
            stored = self.store.find_by_id("verification-results.json", "result_id", result_id)
            return dict(stored)
        except Exception:
            return None


# ── 模块级单例和兼容函数 ──────────────────────────────────

_retrieval_service = RetrievalService()


def search_evidence(
    product_id: str,
    category_id: str | None = None,
    dimensions: list[str] | None = None,
    source_types: list[str] | None = None,
    limit: int = 20,
    store: MockStore | None = None,
) -> dict[str, Any]:
    """
    向后兼容的函数接口 —— 委托给 RetrievalService。

    参数和返回值与原有签名一致，已有调用方无需修改。
    """
    service = RetrievalService(store) if store else _retrieval_service
    return service.search_evidence(
        product_id=product_id,
        category_id=category_id,
        dimensions=dimensions,
        source_types=source_types,
        limit=limit,
    )
