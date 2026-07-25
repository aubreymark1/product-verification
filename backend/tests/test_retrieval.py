"""
测试: 证据检索服务 — search_evidence
"""
import pytest
from repository import MockRepository, reset_repository
from services.retrieval import search_evidence


@pytest.fixture(autouse=True)
def reset():
    reset_repository()


@pytest.fixture
def repo():
    return MockRepository()


def test_search_exact_product(repo):
    result = search_evidence("prod_001", repo=repo)
    assert result["total"] == 5
    assert result["insufficient"] is False
    assert len(result["source_ids"]) > 0


def test_search_with_type_filter(repo):
    result = search_evidence("prod_001", evidence_types=["professional_review"], repo=repo)
    assert all(e["type"] == "professional_review" for e in result["supporting"] + result["risks"])


def test_search_with_dimensions(repo):
    """验证维度筛选：关键词匹配"""
    result = search_evidence("prod_001", dimensions=["续航"], repo=repo)
    # 续航相关证据应该排在前面（evd_002 提到续航）
    assert result["total"] > 0


def test_search_classifies_evidence(repo):
    """验证证据分类为 support / risk / pending"""
    result = search_evidence("prod_001", repo=repo)
    for e in result["supporting"]:
        assert e["evidence_level"] in ("strong_support", "support")
    for e in result["risks"]:
        assert e["evidence_level"] in ("oppose", "mixed")


def test_search_no_evidence(repo):
    """无证据时标记 insufficient"""
    result = search_evidence("prod_999", repo=repo)
    assert result["total"] == 0
    assert result["insufficient"] is True


def test_search_with_category_fallback(repo):
    """同类降级：当精确产品证据不足时，fallback 到同类"""
    # prod_006 只有 3 条精确证据，同类参考可补充
    result = search_evidence("prod_006", category_id="家电", repo=repo)
    assert result["total"] > 0


def test_search_limit(repo):
    """验证 limit 截断"""
    result = search_evidence("prod_001", limit=2, repo=repo)
    assert result["total"] <= 2
