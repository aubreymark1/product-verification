"""
测试: 产品接口
"""
import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from repository import reset_repository


@pytest.fixture(autouse=True)
def reset():
    reset_repository()


@pytest.mark.asyncio
async def test_list_all_products():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/products")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 6
        assert len(data["products"]) == 6


@pytest.mark.asyncio
async def test_filter_by_category():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/products", params={"category": "数码"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2


@pytest.mark.asyncio
async def test_filter_by_keyword():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/products", params={"keyword": "戴森"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        assert any("戴森" in p["name"] for p in data["products"])


@pytest.mark.asyncio
async def test_get_product_detail():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/products/prod_001")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["name"] == "戴森V15 Detect无绳吸尘器"


@pytest.mark.asyncio
async def test_product_not_found():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/products/nonexistent")
        assert resp.status_code == 404
