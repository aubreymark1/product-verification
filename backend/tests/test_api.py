from fastapi.testclient import TestClient

from app.main import app
from app.database.mock_store import MockDataNotFound, mock_store


client = TestClient(app)


def test_health() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_mock_flow_contract() -> None:
    video = client.get("/api/videos/video_demo")
    assert video.status_code == 200
    payload = video.json()["data"]
    selection = {"video_id": "video_demo", "timestamp": 0, "selection": payload["objects"][0]["bbox"]}

    identify = client.post("/api/vision/identify", json=selection)
    assert identify.status_code == 200
    candidate = identify.json()["data"]["candidates"][0]

    profile = client.get("/api/categories/demo_category/profile")
    assert profile.status_code == 200
    assert profile.json()["data"]["condition_fields"]

    result = client.post(
        "/api/verification/run",
        json={
            "video_id": "video_demo",
            "product_id": candidate["product_id"],
            "category_id": "demo_category",
            "conditions": {"usage_scene": "场景A"},
            "raw_query": "",
        },
    )
    assert result.status_code == 200
    assert result.json()["data"]["summary"]


def test_unknown_entity_returns_api_error() -> None:
    response = client.get("/api/videos/unknown")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


# ── 成员C 新增测试 ──

def test_evidence_detail_returns_valid() -> None:
    response = client.get("/api/evidence/evidence_demo_support")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["evidence_id"] == "evidence_demo_support"
    assert data["source_type"] == "demo_mock"


def test_evidence_not_found_returns_error() -> None:
    response = client.get("/api/evidence/nonexistent")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_verification_fallback_when_no_cached_result(monkeypatch) -> None:
    """验证：当没有预置 verification-result 时，走降级逻辑返回结果"""
    original_find_by_id = mock_store.find_by_id

    def find_without_cached_result(filename: str, key: str, value: str):
        if filename == "verification-results.json":
            raise MockDataNotFound("forced fallback test")
        return original_find_by_id(filename, key, value)

    monkeypatch.setattr(mock_store, "find_by_id", find_without_cached_result)
    response = client.post("/api/verification/run", json={
        "video_id": "video_demo",
        "product_id": "demo_product_001",
        "category_id": "demo_category",
        "conditions": {},
        "raw_query": "",
    })
    assert response.status_code == 200
    data = response.json()["data"]
    assert "summary" in data
    assert "support" in data
    assert data["confidence"] == 0.7
    assert data["support"][0]["source_ids"] == ["evidence_demo_support"]


def test_conclusion_source_ids_filtering() -> None:
    """验证：结论中 source_ids 为空的不输出"""
    response = client.post("/api/verification/run", json={
        "video_id": "video_demo",
        "product_id": "demo_product_001",
        "category_id": "demo_category",
        "conditions": {},
        "raw_query": "",
    })
    assert response.status_code == 200
    data = response.json()["data"]
    for key in ("support", "risks", "uncertain"):
        for c in data.get(key, []):
            assert len(c["source_ids"]) > 0, f"{key} conclusion has empty source_ids"


def test_retrieval_service() -> None:
    """验证证据检索服务"""
    from app.services.retrieval import search_evidence
    result = search_evidence("demo_product_001", category_id="demo_category")
    assert result["total"] > 0
    assert len(result["supporting"]) + len(result["risks"]) + len(result["pending"]) == result["total"]


def test_retrieval_insufficient() -> None:
    """无证据时标记 insufficient"""
    from app.services.retrieval import search_evidence
    result = search_evidence("nonexistent_product")
    assert result["insufficient"] is True
    assert result["total"] == 0


def test_retrieval_dimension_filter() -> None:
    """验证按证据维度筛选"""
    from app.services.retrieval import search_evidence
    result = search_evidence("demo_product_001", dimensions=["risk"])
    assert result["total"] == 1
    assert result["risks"][0]["evidence_id"] == "evidence_demo_risk"


def test_comparison_add() -> None:
    response = client.post("/api/comparison/add", json={
        "product_id": "demo_product_001",
        "category_id": "demo_category",
    })
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] == "placeholder"
