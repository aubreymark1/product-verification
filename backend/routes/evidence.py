"""
证据接口 —— 成员C
支持证据检索、详情、类型筛选和排序
"""
from fastapi import APIRouter, HTTPException, Query
from repository import get_repository
from schemas.models import EvidenceItem, EvidenceListResponse, ApiResponse

router = APIRouter(prefix="/evidence", tags=["evidence"])


@router.get("/{product_id}")
async def get_evidence(
    product_id: str,
    evidence_type: str = Query(None, description="证据类型: professional_review | user_review"),
    sort_by: str = Query("relevance_score", description="排序: relevance_score | source_credibility"),
):
    """获取指定商品的验证证据，支持按类型筛选和排序"""
    repo = get_repository()

    # 校验商品存在
    if not repo.get_product_by_id(product_id):
        raise HTTPException(status_code=404, detail="商品不存在")

    evidences = repo.get_evidences_by_product(product_id)

    if evidence_type:
        evidences = [e for e in evidences if e.get("type") == evidence_type]

    if sort_by in ("relevance_score", "source_credibility"):
        evidences = sorted(evidences, key=lambda e: e.get(sort_by, 0), reverse=True)

    evidence_items = [
        EvidenceItem(
            id=e["id"],
            product_id=e.get("product_id", ""),
            type=e.get("type", ""),
            source_name=e.get("source_name", ""),
            source_credibility=e.get("source_credibility", 0),
            title=e.get("title", ""),
            summary=e.get("summary", ""),
            content=e.get("content", ""),
            evidence_level=e.get("evidence_level", "support"),
            relevance_score=e.get("relevance_score", 0),
            tags=e.get("tags", []),
            created_at=e.get("created_at", ""),
        )
        for e in evidences
    ]

    return EvidenceListResponse(
        evidences=evidence_items,
        total=len(evidence_items),
        product_id=product_id,
    )


@router.get("/detail/{evidence_id}")
async def get_evidence_detail(evidence_id: str):
    """获取单条证据详情"""
    repo = get_repository()
    evidence = repo.get_evidence_by_id(evidence_id)
    if not evidence:
        raise HTTPException(status_code=404, detail="证据不存在")
    return ApiResponse(success=True, data=evidence)
