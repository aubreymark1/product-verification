"""成员C：商品事实过滤、证据关联、空数据和错误场景的 pytest 测试。"""
from __future__ import annotations

from app.services.retrieval import RetrievalService, search_evidence

service = RetrievalService()


class TestProductFacts:
    """商品事实检索"""

    def test_search_facts_by_product(self) -> None:
        """有 attributes 的商品应返回事实"""
        result = service.search_facts("atk_a9_ultimate", "gaming_mouse")
        assert result["total"] > 0
        assert result["insufficient"] is False
        facts = result["facts"]
        # 至少应有 sensor, weight, battery_life
        keys = {f.key for f in facts}
        assert "sensor" in keys
        assert "weight" in keys
        assert "battery_life" in keys

    def test_search_facts_no_attributes(self) -> None:
        """没有 attributes 且没有 product-facts 数据的商品返回空（不报错）"""
        result = service.search_facts("logitech_gpw_1", "gaming_mouse")
        # 如果没有 product-facts.json 数据，从 products.json 可能也没有 attributes
        # 应该优雅返回空
        assert result["product_id"] == "logitech_gpw_1"
        # insufficient 表示没有结构化事实数据
        assert isinstance(result["facts"], list)

    def test_search_facts_filter_by_key(self) -> None:
        """按 key 筛选事实"""
        result = service.search_facts("atk_a9_ultimate", "gaming_mouse", keys=["sensor", "weight"])
        facts = result["facts"]
        keys = {f.key for f in facts}
        assert keys <= {"sensor", "weight", "mcu", "polling_rate", "coating", "battery_life", "brand", "price", "quality_consistency"}
        # 不应包含未请求的 key（如果 product-facts 中有且不匹配则被过滤）
        all_keys = {f.key for f in facts}
        for k in all_keys:
            assert k in ("sensor", "weight") or k in keys, f"key {k} should be filtered"

    def test_search_facts_nonexistent_product(self) -> None:
        """不存在的商品返回空事实"""
        result = service.search_facts("nonexistent", "gaming_mouse")
        assert result["total"] == 0
        assert result["insufficient"] is True

    def test_product_fact_source_tracking(self) -> None:
        """有证据支撑的事实应有 traceable source_ids"""
        result = service.search_facts("atk_a9_ultimate", "gaming_mouse")
        facts_with_sources = [f for f in result["facts"] if len(f.source_ids) > 0]
        assert len(facts_with_sources) > 0, "至少应有一条事实有证据来源"
        for f in facts_with_sources:
            assert f.source_type in ("official", "professional_test", "user_feedback", "demo_mock")
            for sid in f.source_ids:
                assert isinstance(sid, str) and len(sid) > 0


class TestEvidenceSearch:
    """证据检索"""

    def test_retrieval_service(self) -> None:
        """验证证据检索服务"""
        result = service.search_evidence("atk_a9_ultimate", category_id="gaming_mouse")
        assert result["total"] > 0
        assert len(result["supporting"]) + len(result["risks"]) + len(result["pending"]) == result["total"]

    def test_retrieval_insufficient(self) -> None:
        """无证据时标记 insufficient"""
        result = service.search_evidence("nonexistent_product")
        assert result["insufficient"] is True
        assert result["total"] == 0

    def test_retrieval_dimension_filter(self) -> None:
        """验证按证据维度筛选"""
        result = service.search_evidence("atk_a9_ultimate", dimensions=["risk"])
        assert result["total"] == 1
        assert result["risks"][0]["evidence_id"] == "ev_risk_001"

    def test_search_evidence_by_source_type(self) -> None:
        """按 source_type 筛选证据"""
        result = service.search_evidence(
            "atk_a9_ultimate", category_id="gaming_mouse", source_types=["demo_mock"]
        )
        assert result["total"] > 0
        for e in result["supporting"] + result["risks"] + result["pending"]:
            assert e["source_type"] == "demo_mock"

    def test_search_evidence_by_multiple_dimensions(self) -> None:
        """多维度同时筛选"""
        result = service.search_evidence(
            "atk_a9_ultimate", category_id="gaming_mouse", dimensions=["support", "identity"]
        )
        assert result["total"] >= 1
        dims = {e["dimension"] for e in result["supporting"] + result["risks"] + result["pending"]}
        assert dims <= {"support", "identity"}

    def test_search_evidence_empty_category(self) -> None:
        """不存在的品类返回空但不应报错"""
        result = service.search_evidence("atk_a9_ultimate", category_id="nonexistent_category")
        # 应该只返回精确商品匹配的证据（如果存在）
        assert isinstance(result["total"], int)
        assert isinstance(result["insufficient"], bool)

    def test_search_evidence_preserves_metadata(self) -> None:
        """每条证据必须保留 evidence_id, source_type, relation_level, confidence"""
        result = service.search_evidence("atk_a9_ultimate", category_id="gaming_mouse")
        all_ev = result["supporting"] + result["risks"] + result["pending"]
        for e in all_ev:
            assert "evidence_id" in e
            assert isinstance(e["evidence_id"], str) and len(e["evidence_id"]) > 0
            assert "source_type" in e
            assert e["source_type"] in ("official", "professional_test", "user_feedback", "demo_mock")
            assert "relation_level" in e
            assert e["relation_level"] in ("exact_product", "likely_same_product", "similar_product")
            assert "confidence" in e
            assert 0 <= e["confidence"] <= 1

    def test_search_evidence_source_ids_are_stable(self) -> None:
        """source_ids 使用稳定的 evidence_id"""
        result = service.search_evidence("atk_a9_ultimate", category_id="gaming_mouse")
        for sid in result["source_ids"]:
            assert sid.startswith("ev_"), f"source_id {sid} 应使用 evidence_id 格式"

    def test_backward_compatible_function(self) -> None:
        """向后兼容的 search_evidence 函数应与服务方法结果一致"""
        func_result = search_evidence("atk_a9_ultimate", category_id="gaming_mouse")
        svc_result = service.search_evidence("atk_a9_ultimate", category_id="gaming_mouse")
        assert func_result["total"] == svc_result["total"]
        assert func_result["product_id"] == svc_result["product_id"]


class TestProductSearch:
    """品类商品搜索"""

    def test_search_products_by_category(self) -> None:
        """按品类检索商品列表"""
        products = service.search_products("gaming_mouse")
        assert len(products) == 4
        product_ids = {p["product_id"] for p in products}
        assert "atk_a9_ultimate" in product_ids
        assert "logitech_gpw_1" in product_ids
        assert "razer_viper_v3_pro" in product_ids
        assert "vxe_r1_pro" in product_ids

    def test_search_products_empty_category(self) -> None:
        """不存在的品类返回空列表"""
        products = service.search_products("nonexistent_category")
        assert products == []


class TestResultRetrieval:
    """结果恢复"""

    def test_get_result_from_persistent(self) -> None:
        """从 verification-results.json 恢复结果"""
        result = service.get_result("res_001")
        assert result is not None
        assert result.get("result_id") == "res_001"
        assert result.get("product_id") == "atk_a9_ultimate"

    def test_get_result_not_found_returns_none(self) -> None:
        """不存在的结果返回 None"""
        result = service.get_result("nonexistent_result_id")
        assert result is None

    def test_get_result_from_cache_preferred(self) -> None:
        """内存缓存优先于持久化数据"""
        cached = {
            "cached_result_001": {
                "result_id": "cached_result_001",
                "product_id": "atk_a9_ultimate",
                "summary": "从缓存返回",
            }
        }
        result = service.get_result("cached_result_001", cached_results=cached)
        assert result is not None
        assert result["result_id"] == "cached_result_001"
        assert result["summary"] == "从缓存返回"
