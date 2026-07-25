from fastapi.testclient import TestClient

from app.main import app


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
    assert 0 <= result.json()["data"]["recommendation_score"] <= 1
    assert result.json()["data"]["round"] == 1

    rerun = client.post(
        "/api/recommendations/rerun",
        json={
            "video_id": "video_demo",
            "product_id": candidate["product_id"],
            "category_id": "demo_category",
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
    assert channels.json()["data"] == []


def test_unknown_entity_returns_api_error() -> None:
    response = client.get("/api/videos/unknown")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"

