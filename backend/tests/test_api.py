from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_mock_flow_contract() -> None:
    video = client.get("/api/videos/demo_video_001")
    assert video.status_code == 200
    payload = video.json()["data"]
    selection = {"video_id": "demo_video_001", "timestamp": 0, "selection": payload["objects"][0]["bbox"]}

    identify = client.post("/api/vision/identify", json=selection)
    assert identify.status_code == 200
    candidate = identify.json()["data"]["candidates"][0]

    profile = client.get("/api/categories/gaming_mouse/profile")
    assert profile.status_code == 200
    assert profile.json()["data"]["condition_fields"]

    result = client.post(
        "/api/verification/run",
        json={
            "video_id": "demo_video_001",
            "product_id": candidate["product_id"],
            "category_id": "gaming_mouse",
            "conditions": {"usage_scene": "场景A"},
            "raw_query": "",
        },
    )
    assert result.status_code == 200
    assert result.json()["data"]["summary"]
    assert 0 <= result.json()["data"]["recommendation_score"] <= 1
    assert result.json()["data"]["round"] == 1

    rerun = client.post(
        "/api/recommendations/rerun",
        json={
            "video_id": "demo_video_001",
            "product_id": candidate["product_id"],
            "category_id": "gaming_mouse",
            "previous_result_id": result.json()["data"]["result_id"],
            "dissatisfaction_reasons": ["预算不合适"],
            "dissatisfaction_note": "希望更轻便",
            "inherit_previous_needs": True,
            "conditions_patch": {},
            "raw_query": "",
        },
    )
    assert rerun.status_code == 200
    assert rerun.json()["data"]["round"] == 2
    assert rerun.json()["data"]["is_follow_up"] is True
    assert rerun.json()["data"]["needs_inherited"] is True

    channels = client.get(f"/api/purchase-channels/{candidate['product_id']}")
    assert channels.status_code == 200
    assert isinstance(channels.json()["data"], list)
    assert len(channels.json()["data"]) >= 1


def test_unknown_entity_returns_api_error() -> None:
    response = client.get("/api/videos/unknown")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


# ── 成员C 新增测试 ──

def test_evidence_detail_returns_valid() -> None:
    response = client.get("/api/evidence/ev_video_002")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["evidence_id"] == "ev_video_002"
    assert data["source_type"] == "demo_mock"


def test_evidence_not_found_returns_error() -> None:
    response = client.get("/api/evidence/nonexistent")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_conclusion_source_ids_filtering() -> None:
    """验证：结论中 source_ids 为空的不输出"""
    response = client.post("/api/verification/run", json={
        "video_id": "demo_video_001",
        "product_id": "atk_a9_ultimate",
        "category_id": "gaming_mouse",
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
    result = search_evidence("atk_a9_ultimate", category_id="gaming_mouse")
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
    result = search_evidence("atk_a9_ultimate", dimensions=["risk"])
    assert result["total"] == 1
    assert result["risks"][0]["evidence_id"] == "ev_risk_001"


def test_comparison_add() -> None:
    response = client.post("/api/comparison/add", json={
        "product_id": "atk_a9_ultimate",
        "category_id": "gaming_mouse",
    })
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] == "placeholder"


# ── 成员C 新增测试：结果持久化 ──

def test_get_result_returns_cached() -> None:
    """验证运行后可恢复结果"""
    result = client.post(
        "/api/verification/run",
        json={
            "video_id": "demo_video_001",
            "product_id": "atk_a9_ultimate",
            "category_id": "gaming_mouse",
            "conditions": {},
            "raw_query": "",
        },
    )
    assert result.status_code == 200
    result_id = result.json()["data"]["result_id"]

    # 通过 GET /api/results/{result_id} 恢复
    response = client.get(f"/api/results/{result_id}")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["result_id"] == result_id
    # VerificationResult 的 product 字段嵌套在 product 键下
    assert data["product"]["product_id"] == "atk_a9_ultimate"
    assert "summary" in data


def test_get_result_not_found() -> None:
    """不存在的 result_id 返回 404"""
    response = client.get("/api/results/nonexistent_result")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


# ── 成员C 新增测试：购买渠道 ──

def test_purchase_channels_structure() -> None:
    """验证购买渠道返回结构正确"""
    response = client.get("/api/purchase-channels/atk_a9_ultimate")
    assert response.status_code == 200
    channels = response.json()["data"]
    assert isinstance(channels, list)
    assert len(channels) > 0, "ATK A9 Ultimate 应有购买渠道"
    for ch in channels:
        assert "channel_id" in ch
        assert "product_id" in ch
        assert ch["product_id"] == "atk_a9_ultimate"
        assert "channel_name" in ch
        assert "channel_type" in ch
        assert ch["channel_type"] in ("official", "marketplace", "retail", "other")
        assert "availability" in ch


def test_purchase_channels_empty_for_unknown() -> None:
    """未知商品返回空列表"""
    response = client.get("/api/purchase-channels/unknown_product")
    assert response.status_code == 200
    channels = response.json()["data"]
    assert channels == []
