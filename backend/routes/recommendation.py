"""
推荐接口 —— 成员C
负责数据准备和传入AI引擎，不负责AI算法本身
"""
from fastapi import APIRouter, HTTPException
from repository import get_repository
from schemas.models import (
    UserRequirement, RecommendationResult, ReAnalyzeResponse, ApiResponse,
)
from services.retrieval import search_evidence

router = APIRouter(prefix="/recommendation", tags=["recommendation"])


@router.post("/analyze")
async def analyze_product(requirement: UserRequirement):
    """核心AI分析接口：根据用户需求和商品信息，计算推荐度并输出结论"""
    repo = get_repository()

    product = repo.get_product_by_id(requirement.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    evidences = repo.get_evidences_by_product(requirement.product_id)
    channels = repo.get_channels_by_product(requirement.product_id)

    # 调用AI引擎（成员D负责实现）
    try:
        from ai_engine import recommend
        result = recommend.calculate(product, evidences, channels, requirement.model_dump())
        return result
    except ImportError:
        # AI 引擎未就绪时的降级响应
        return _fallback_recommendation(product, evidences, channels, requirement)
    except Exception as e:
        # 其他异常降级
        return _fallback_recommendation(product, evidences, channels, requirement,
                                        error=str(e))


@router.post("/refine")
async def refine_recommendation(request: dict):
    """
    再推荐接口：根据上一轮条件和不满意原因返回替代候选
    成员C提供数据结构，成员D实现算法
    """
    repo = get_repository()

    product_id = request.get("product_id", "")
    original_requirement = request.get("previous_requirements", {})
    reasons = request.get("reasons", [])

    product = repo.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    try:
        from ai_engine import recommend
        alternatives = recommend.find_alternatives(product_id, original_requirement, reasons)
        return ReAnalyzeResponse(
            product_id=product_id,
            alternatives=alternatives,
            original_requirement=original_requirement,
        )
    except ImportError:
        # AI 引擎未就绪时的降级
        alternatives = _fallback_alternatives(product, repo)
        return ReAnalyzeResponse(
            product_id=product_id,
            alternatives=alternatives,
            original_requirement=original_requirement,
        )
    except Exception:
        alternatives = _fallback_alternatives(product, repo)
        return ReAnalyzeResponse(
            product_id=product_id,
            alternatives=alternatives,
            original_requirement=original_requirement,
        )


@router.get("/reanalyze/{product_id}")
async def re_recommend(product_id: str):
    """再推荐接口（GET）: 为给定商品寻找替代品推荐"""
    repo = get_repository()

    product = repo.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    try:
        from ai_engine import recommend
        alternatives = recommend.find_alternatives(product_id)
        return {"product_id": product_id, "alternatives": alternatives}
    except ImportError:
        alternatives = _fallback_alternatives(product, repo)
        return {"product_id": product_id, "alternatives": alternatives}
    except Exception:
        alternatives = _fallback_alternatives(product, repo)
        return {"product_id": product_id, "alternatives": alternatives}


# ── 降级辅助 ──────────────────────────

def _fallback_recommendation(product: dict, evidences: list[dict], channels: list[dict],
                              requirement: UserRequirement, error: str = "") -> dict:
    """AI引擎不可用时的降级推荐响应"""
    if not evidences:
        return {
            "product_id": product["id"],
            "product_name": product["name"],
            "overall_score": 50.0,
            "verdict": "信息不足",
            "summary": "该商品暂时缺少足够的验证数据，建议参考其他渠道信息后再做决定。",
            "supporting_evidence": [],
            "risk_evidence": [],
            "pending_items": ["缺少用户评价数据", "缺少专业测评数据"],
            "alternatives": [],
            "purchase_advice": None,
        }

    # 简单降级：仅做证据分类
    supporting = [e for e in evidences if e.get("evidence_level") in ("strong_support", "support")][:5]
    risks = [e for e in evidences if e.get("evidence_level") in ("oppose", "mixed")][:3]
    lowest = min(channels, key=lambda c: c["price"]) if channels else None

    return {
        "product_id": product["id"],
        "product_name": product["name"],
        "overall_score": 60.0,
        "verdict": "可以考虑",
        "summary": f"已收集到 {len(evidences)} 条验证信息（降级模式）。{('错误: ' + error) if error else ''}",
        "supporting_evidence": supporting,
        "risk_evidence": risks,
        "pending_items": ["AI引擎未就绪，以下为原始数据展示"] if error else [],
        "alternatives": [],
        "purchase_advice": {
            "lowest_price": lowest,
            "recommended_channel": lowest,
            "all_channels": channels,
        } if lowest else None,
    }


def _fallback_alternatives(product: dict, repo) -> list[dict]:
    """AI引擎不可用时的降级替代推荐"""
    candidates = []
    for cp_id in product.get("candidate_products", []):
        if cp_id == product["id"]:
            continue
        cp = repo.get_product_by_id(cp_id)
        if cp:
            candidates.append({
                "product_id": cp["id"],
                "name": cp["name"],
                "brand": cp.get("brand", ""),
                "price_range": cp.get("price_range", []),
                "quick_score": 60.0,
                "reason": f"同品类替代选择",
                "tags": cp.get("tags", []),
            })
    return candidates[:3]
