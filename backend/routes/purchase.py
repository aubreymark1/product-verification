"""
购买渠道接口 —— 成员C
"""
from fastapi import APIRouter, HTTPException
from repository import get_repository
from schemas.models import (
    PurchaseChannel, ChannelListResponse, LowestPriceResponse, ApiResponse,
)

router = APIRouter(prefix="/purchase", tags=["purchase"])


@router.get("/channels/{product_id}")
async def get_purchase_channels(product_id: str):
    """获取指定商品的购买渠道，按价格升序排列"""
    repo = get_repository()

    if not repo.get_product_by_id(product_id):
        raise HTTPException(status_code=404, detail="商品不存在")

    channels = repo.get_channels_by_product(product_id)
    channels = sorted(channels, key=lambda c: c["price"])

    purchase_channels = [
        PurchaseChannel(
            id=ch.get("id", ""),
            product_id=ch.get("product_id", ""),
            platform=ch.get("platform", ""),
            shop_name=ch.get("shop_name", ""),
            price=ch.get("price", 0),
            url=ch.get("url", ""),
            in_stock=ch.get("in_stock", True),
            tags=ch.get("tags", []),
            delivery_estimate=ch.get("delivery_estimate", ""),
        )
        for ch in channels
    ]

    lowest_price = channels[0]["price"] if channels else None

    return ChannelListResponse(
        product_id=product_id,
        channels=purchase_channels,
        total=len(purchase_channels),
        lowest_price=lowest_price,
    )


@router.get("/lowest/{product_id}")
async def get_lowest_price(product_id: str):
    """获取全网最低价渠道"""
    repo = get_repository()

    if not repo.get_product_by_id(product_id):
        raise HTTPException(status_code=404, detail="商品不存在")

    channels = repo.get_channels_by_product(product_id)
    if not channels:
        return LowestPriceResponse(product_id=product_id, lowest=None)

    lowest = min(channels, key=lambda c: c["price"])
    lowest_channel = PurchaseChannel(
        id=lowest.get("id", ""),
        product_id=lowest.get("product_id", ""),
        platform=lowest.get("platform", ""),
        shop_name=lowest.get("shop_name", ""),
        price=lowest.get("price", 0),
        url=lowest.get("url", ""),
        in_stock=lowest.get("in_stock", True),
        tags=lowest.get("tags", []),
        delivery_estimate=lowest.get("delivery_estimate", ""),
    )

    return LowestPriceResponse(product_id=product_id, lowest=lowest_channel)
