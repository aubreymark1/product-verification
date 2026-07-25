"""
测试: 购买渠道接口
"""
import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from repository import reset_repository


@pytest.fixture(autouse=True)
def reset():
    reset_repository()


@pytest.mark.asyncio
async def test_get_channels():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/purchase/channels/prod_001")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 3
        assert data["lowest_price"] == 3499.0
        # 验证按价格升序
        prices = [ch["price"] for ch in data["channels"]]
        assert prices == sorted(prices)


@pytest.mark.asyncio
async def test_get_lowest():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/purchase/lowest/prod_001")
        assert resp.status_code == 200
        data = resp.json()
        assert data["lowest"] is not None
        assert data["lowest"]["price"] == 3499.0


@pytest.mark.asyncio
async def test_channels_product_not_found():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/purchase/channels/nonexistent")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_lowest_product_not_found():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/purchase/lowest/nonexistent")
        assert resp.status_code == 404
