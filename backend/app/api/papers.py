from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.models.models import Paper, Author, gen_id
from app.schemas.schemas import PaperCreate, PaperUpdate, PaperResponse, PaperList

router = APIRouter()


@router.post("/", response_model=PaperResponse, status_code=201)
async def create_paper(data: PaperCreate, db: AsyncSession = Depends(get_db)):
    """创建论文记录"""
    paper = Paper(
        id=gen_id(),
        title=data.title,
        abstract=data.abstract,
        year=data.year,
        venue=data.venue,
        domain_id=data.domain_id,
        url=data.url,
        doi=data.doi,
        arxiv_id=data.arxiv_id,
    )

    # 处理作者
    for author_name in data.authors:
        result = await db.execute(select(Author).where(Author.name == author_name))
        author = result.scalar_one_or_none()
        if not author:
            author = Author(id=gen_id(), name=author_name)
            db.add(author)
        paper.authors.append(author)

    db.add(paper)
    await db.flush()

    return PaperResponse(
        **{c.name: getattr(paper, c.name) for c in paper.__table__.columns},
        authors=[a.name for a in paper.authors],
    )


@router.get("/", response_model=PaperList)
async def list_papers(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    domain_id: str | None = None,
    year: int | None = None,
    sort: str = "impact_score",
    db: AsyncSession = Depends(get_db),
):
    """论文列表（分页、筛选、排序）"""
    query = select(Paper)

    if domain_id:
        query = query.where(Paper.domain_id == domain_id)
    if year:
        query = query.where(Paper.year == year)

    # 排序
    sort_col = getattr(Paper, sort, Paper.impact_score)
    query = query.order_by(sort_col.desc())

    # 总数
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # 分页
    query = query.offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    papers = result.scalars().all()

    items = []
    for p in papers:
        await db.refresh(p, ["authors"])
        items.append(
            PaperResponse(
                **{c.name: getattr(p, c.name) for c in p.__table__.columns},
                authors=[a.name for a in p.authors],
            )
        )

    return PaperList(items=items, total=total, page=page, size=size)


@router.get("/{paper_id}", response_model=PaperResponse)
async def get_paper(paper_id: str, db: AsyncSession = Depends(get_db)):
    """获取论文详情"""
    result = await db.execute(select(Paper).where(Paper.id == paper_id))
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail="论文不存在")

    await db.refresh(paper, ["authors"])
    return PaperResponse(
        **{c.name: getattr(paper, c.name) for c in paper.__table__.columns},
        authors=[a.name for a in paper.authors],
    )


@router.put("/{paper_id}", response_model=PaperResponse)
async def update_paper(
    paper_id: str, data: PaperUpdate, db: AsyncSession = Depends(get_db)
):
    """更新论文信息"""
    result = await db.execute(select(Paper).where(Paper.id == paper_id))
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail="论文不存在")

    update_data = data.model_dump(exclude_unset=True)
    if "key_contributions" in update_data and update_data["key_contributions"]:
        import json
        update_data["key_contributions"] = json.dumps(
            update_data["key_contributions"], ensure_ascii=False
        )

    for field, value in update_data.items():
        setattr(paper, field, value)

    await db.flush()
    await db.refresh(paper, ["authors"])

    return PaperResponse(
        **{c.name: getattr(paper, c.name) for c in paper.__table__.columns},
        authors=[a.name for a in paper.authors],
    )


@router.delete("/{paper_id}", status_code=204)
async def delete_paper(paper_id: str, db: AsyncSession = Depends(get_db)):
    """删除论文"""
    result = await db.execute(select(Paper).where(Paper.id == paper_id))
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail="论文不存在")
    await db.delete(paper)
