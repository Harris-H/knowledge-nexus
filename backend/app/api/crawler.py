import asyncio
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db, async_session
from app.models.models import CrawlTask, gen_id
from app.schemas.schemas import CrawlRequest, CrawlTaskResponse
from app.services.crawlers.orchestrator import run_crawl_task

router = APIRouter()
logger = logging.getLogger(__name__)


async def _run_crawl_background(task_id: str):
    """后台运行爬取任务"""
    async with async_session() as db:
        try:
            await run_crawl_task(task_id, db)
        except Exception as e:
            logger.error(f"Background crawl task failed: {e}")
            result = await db.execute(select(CrawlTask).where(CrawlTask.id == task_id))
            task = result.scalar_one_or_none()
            if task:
                task.status = "failed"
                await db.commit()


@router.post("/start", response_model=CrawlTaskResponse, status_code=202)
async def start_crawl(data: CrawlRequest, db: AsyncSession = Depends(get_db)):
    """启动爬取任务"""
    task = CrawlTask(
        id=gen_id(),
        domain=data.domain,
        subdomain=data.subdomain,
        year_from=data.year_from,
        year_to=data.year_to,
        min_citations=data.min_citations,
        max_papers=data.max_papers,
        status="queued",
    )
    db.add(task)
    await db.flush()

    # 后台运行爬取
    asyncio.create_task(_run_crawl_background(task.id))

    return CrawlTaskResponse.model_validate(task)


@router.get("/tasks/{task_id}", response_model=CrawlTaskResponse)
async def get_crawl_task(task_id: str, db: AsyncSession = Depends(get_db)):
    """查询爬取任务状态"""
    result = await db.execute(select(CrawlTask).where(CrawlTask.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return CrawlTaskResponse.model_validate(task)


@router.get("/tasks", response_model=list[CrawlTaskResponse])
async def list_crawl_tasks(db: AsyncSession = Depends(get_db)):
    """列出所有爬取任务"""
    result = await db.execute(select(CrawlTask).order_by(CrawlTask.created_at.desc()))
    tasks = result.scalars().all()
    return [CrawlTaskResponse.model_validate(t) for t in tasks]
