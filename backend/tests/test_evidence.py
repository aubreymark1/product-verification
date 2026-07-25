"""
测试: 证据接口
"""
import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from repository import reset_repository


@pytest.fixture(autouse=True)
def reset():
    reset_repository()


@pytest.mark.asyncio
async def test_get_evidence_for_product():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/evidence/prod_001")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 5
        assert data["product_id"] == "prod_001"
        assert all("id" in e for e in data["evidences"])


@pytest.mark.asyncio
async def test_filter_by_evidence_type():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            "/api/evidence/prod_001",
            params={"evidence_type": "professional_review"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert all(e["type"] == "professional_review" for e in data["evidences"])


@pytest.mark.asyncio
async def test_evidence_product_not_found():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/evidence/nonexistent")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_evidence_detail():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/evidence/detail/evd_001")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "戴森" in data["data"]["title"]


@pytest.mark.asyncio
async def test_evidence_detail_not_found():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/evidence/detail/nonexistent")
        assert resp.status_code == 404
