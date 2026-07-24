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


def test_unknown_entity_returns_api_error() -> None:
    response = client.get("/api/videos/unknown")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"

