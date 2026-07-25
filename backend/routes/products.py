"""
商品接口 —— 成员C
"""
from fastapi import APIRouter, HTTPException, Query
from repository import get_repository
from schemas.models import ProductBrief, ProductListResponse, ApiResponse

router = APIRouter(prefix="/products", tags=["products"])


@router.get("")
async def list_products(
    category: str = Query(None, description="按品类筛选"),
    keyword: str = Query(None, description="按名称/品牌/标签搜索"),
):
    """获取所有商品列表，支持按品类和关键词筛选"""
    repo = get_repository()
    products = repo.get_all_products()

    if category:
        products = [p for p in products if p.get("category") == category]

    if keyword:
        kw = keyword.lower()
        products = [
            p for p in products
            if kw in p.get("name", "").lower()
            or kw in p.get("brand", "").lower()
            or any(kw in tag.lower() for tag in p.get("tags", []))
        ]

    briefs = [
        ProductBrief(
            id=p["id"],
            name=p["name"],
            category=p.get("category", ""),
            brand=p.get("brand", ""),
            price_range=p.get("price_range", []),
            tags=p.get("tags", []),
        )
        for p in products
    ]

    return ProductListResponse(products=briefs, total=len(briefs))


@router.get("/{product_id}")
async def get_product(product_id: str):
    """获取单个商品详情"""
    repo = get_repository()
    product = repo.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    return ApiResponse(success=True, data=product)
