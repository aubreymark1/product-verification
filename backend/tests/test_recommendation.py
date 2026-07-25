"""
测试: 推荐接口
"""
import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from repository import reset_repository


@pytest.fixture(autouse=True)
def reset():
    reset_repository()


@pytest.mark.asyncio
async def test_analyze_product():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/recommendation/analyze", json={
            "product_id": "prod_001",
            "text": "家里有猫，需要强力吸尘",
            "budget": 4000,
            "priorities": ["续航", "性价比"],
            "usage_scenario": "宠物",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["product_id"] == "prod_001"
        assert "overall_score" in data
        assert "verdict" in data
        assert "supporting_evidence" in data
        assert "risk_evidence" in data
        assert "pending_items" in data
        assert "alternatives" in data


@pytest.mark.asyncio
async def test_analyze_product_not_found():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/recommendation/analyze", json={
            "product_id": "nonexistent",
        })
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_reanalyze():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/recommendation/reanalyze/prod_001")
        assert resp.status_code == 200
        data = resp.json()
        assert data["product_id"] == "prod_001"
        assert "alternatives" in data


@pytest.mark.asyncio
async def test_reanalyze_not_found():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/recommendation/reanalyze/nonexistent")
        assert resp.status_code == 404
