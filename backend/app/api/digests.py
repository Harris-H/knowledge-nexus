"""
领域摘要 API — 管理领域知识图谱摘要和基于摘要的跨域分析。
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.schemas import (
    DomainDigestResponse,
    DomainDigestList,
    CrossDomainAnalysisRequest,
    CrossDomainAnalysisResponse,
)
from app.services.digest_service import (
    generate_domain_digest,
    get_or_generate_digest,
    regenerate_all_digests,
    cross_domain_analysis,
    list_all_domains_with_digest,
)

router = APIRouter()


@router.get("/", response_model=DomainDigestList)
async def list_digests(db: AsyncSession = Depends(get_db)):
    """
    📋 列出所有领域及其摘要状态。
    自动发现所有有数据的领域（来自知识节点和论文）。
    """
    domains = await list_all_domains_with_digest(db)
    return DomainDigestList(
        items=[DomainDigestResponse.model_validate(d) for d in domains],
        total=len(domains),
    )


@router.get("/{domain_name}", response_model=DomainDigestResponse)
async def get_digest(
    domain_name: str,
    db: AsyncSession = Depends(get_db),
):
    """
    📖 获取指定领域的摘要。如果摘要不存在或已过期，会自动生成。
    """
    try:
        domain = await get_or_generate_digest(db, domain_name)
        return DomainDigestResponse.model_validate(domain)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取摘要失败: {str(e)}")


@router.post("/{domain_name}/generate", response_model=DomainDigestResponse)
async def generate_digest(
    domain_name: str,
    db: AsyncSession = Depends(get_db),
):
    """
    🔄 强制重新生成指定领域的摘要（无论是否已存在）。
    """
    try:
        domain = await generate_domain_digest(db, domain_name)
        return DomainDigestResponse.model_validate(domain)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成摘要失败: {str(e)}")


@router.post("/generate-all")
async def generate_all_digests(db: AsyncSession = Depends(get_db)):
    """
    🔄 批量重新生成所有领域的摘要。
    """
    try:
        results = await regenerate_all_digests(db)
        ok_count = sum(1 for r in results if r["status"] == "ok")
        return {
            "total": len(results),
            "success": ok_count,
            "failed": len(results) - ok_count,
            "details": results,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量生成失败: {str(e)}")


@router.post("/cross-domain-analysis")
async def api_cross_domain_analysis(
    req: CrossDomainAnalysisRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    🔗 基于两个领域的摘要进行跨域关联分析。
    如果摘要不存在，会先自动生成。
    比传统的全量节点分析更快、更省 token，且能提供更宏观的洞察。
    """
    if req.domain_a == req.domain_b:
        raise HTTPException(status_code=400, detail="请选择两个不同的领域")
    try:
        result = await cross_domain_analysis(db, req.domain_a, req.domain_b)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"跨域分析失败: {str(e)}")
