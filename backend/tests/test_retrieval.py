"""成员C：商品事实过滤、证据关联、空数据和错误场景的 pytest 测试。"""
from __future__ import annotations

from app.services.retrieval import RetrievalService, search_evidence

service = RetrievalService()


class TestProductFacts:
    """商品事实检索"""

    def test_search_facts_by_product(self) -> None:
        """有 product-facts 数据的商品应返回事实"""
        result = service.search_facts("demo_product_001", "demo_category")
        assert isinstance(result["total"], int)
        assert isinstance(result["insufficient"], bool)
        assert isinstance(result["facts"], list)

    def test_search_facts_no_attributes(self) -> None:
        """没有 product-facts 数据的商品返回空（不报错）"""
        result = service.search_facts("demo_product_002", "demo_category")
        assert result["product_id"] == "demo_product_002"
        assert isinstance(result["facts"], list)

    def test_search_facts_filter_by_key(self) -> None:
        """按 key 筛选事实"""
        result = service.search_facts("demo_product_001", "demo_category", keys=["price"])
        assert isinstance(result["facts"], list)

    def test_search_facts_nonexistent_product(self) -> None:
        """不存在的商品返回空事实"""
        result = service.search_facts("nonexistent", "demo_category")
        assert result["total"] == 0
        assert result["insufficient"] is True

    def test_product_fact_source_tracking(self) -> None:
        """有证据支撑的事实应有 traceable source_ids"""
        result = service.search_facts("demo_product_001", "demo_category")
        for f in result["facts"]:
            assert f.source_type in ("official", "professional_test", "user_feedback", "demo_mock")
            for sid in f.source_ids:
                assert isinstance(sid, str) and len(sid) > 0


class TestEvidenceSearch:
    """证据检索"""

    def test_retrieval_service(self) -> None:
        """验证证据检索服务"""
        result = service.search_evidence("demo_product_001", category_id="demo_category")
        assert result["total"] > 0
        assert len(result["supporting"]) + len(result["risks"]) + len(result["pending"]) == result["total"]

    def test_retrieval_insufficient(self) -> None:
        """无证据时标记 insufficient"""
        result = service.search_evidence("nonexistent_product")
        assert result["insufficient"] is True
        assert result["total"] == 0

    def test_retrieval_dimension_filter(self) -> None:
        """验证按证据维度筛选"""
        result = service.search_evidence("demo_product_001", dimensions=["risk"])
        assert result["total"] == 1
        assert result["risks"][0]["evidence_id"] == "evidence_demo_risk"

    def test_search_evidence_by_source_type(self) -> None:
        """按 source_type 筛选证据"""
        result = service.search_evidence(
            "demo_product_001", category_id="demo_category", source_types=["demo_mock"]
        )
        assert result["total"] > 0
        for e in result["supporting"] + result["risks"] + result["pending"]:
            assert e["source_type"] == "demo_mock"

    def test_search_evidence_by_multiple_dimensions(self) -> None:
        """多维度同时筛选"""
        result = service.search_evidence(
            "demo_product_001", category_id="demo_category", dimensions=["support", "identity"]
        )
        assert result["total"] >= 1
        dims = {e["dimension"] for e in result["supporting"] + result["risks"] + result["pending"]}
        assert dims <= {"support", "identity"}

    def test_search_evidence_empty_category(self) -> None:
        """不存在的品类返回空但不应报错"""
        result = service.search_evidence("demo_product_001", category_id="nonexistent_category")
        assert isinstance(result["total"], int)
        assert isinstance(result["insufficient"], bool)

    def test_search_evidence_preserves_metadata(self) -> None:
        """每条证据必须保留 evidence_id, source_type, relation_level, confidence"""
        result = service.search_evidence("demo_product_001", category_id="demo_category")
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
        result = service.search_evidence("demo_product_001", category_id="demo_category")
        for sid in result["source_ids"]:
            assert sid.startswith("evidence_"), f"source_id {sid} 应使用 evidence_id 格式"

    def test_backward_compatible_function(self) -> None:
        """向后兼容的 search_evidence 函数应与服务方法结果一致"""
        func_result = search_evidence("demo_product_001", category_id="demo_category")
        svc_result = service.search_evidence("demo_product_001", category_id="demo_category")
        assert func_result["total"] == svc_result["total"]
        assert func_result["product_id"] == svc_result["product_id"]


class TestProductSearch:
    """品类商品搜索"""

    def test_search_products_by_category(self) -> None:
        """按品类检索商品列表"""
        products = service.search_products("demo_category")
        assert len(products) == 2
        product_ids = {p["product_id"] for p in products}
        assert "demo_product_001" in product_ids
        assert "demo_product_002" in product_ids

    def test_search_products_empty_category(self) -> None:
        """不存在的品类返回空列表"""
        products = service.search_products("nonexistent_category")
        assert products == []
