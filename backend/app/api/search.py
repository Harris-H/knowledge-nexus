from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.models import Paper
from app.schemas.schemas import SearchResponse, SearchResult

router = APIRouter()


@router.get("/", response_model=SearchResponse)
async def search_papers(
    q: str = Query(..., description="搜索关键词"),
    mode: str = Query("keyword", description="搜索模式: keyword / semantic / hybrid"),
    domain: str | None = None,
    year_from: int | None = None,
    year_to: int | None = None,
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """搜索论文 — 当前实现为关键词搜索，后续扩展语义搜索"""
    query = select(Paper).where(Paper.title.ilike(f"%{q}%") | Paper.abstract.ilike(f"%{q}%"))

    if domain:
        query = query.where(Paper.domain_id == domain)
    if year_from:
        query = query.where(Paper.year >= year_from)
    if year_to:
        query = query.where(Paper.year <= year_to)

    query = query.order_by(Paper.impact_score.desc()).limit(limit)
    result = await db.execute(query)
    papers = result.scalars().all()

    results = []
    for p in papers:
        snippet = p.abstract[:200] + "..." if p.abstract and len(p.abstract) > 200 else p.abstract
        results.append(
            SearchResult(
                id=p.id,
                type="paper",
                title=p.title,
                snippet=snippet,
                score=p.impact_score,
            )
        )

    return SearchResponse(results=results, total=len(results))
