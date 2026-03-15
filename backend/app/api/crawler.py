import asyncio
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.core.database import get_db, async_session
from app.models.models import CrawlTask, gen_id
from app.schemas.schemas import CrawlRequest, CrawlTaskResponse
from app.services.crawlers.orchestrator import run_crawl_task, cancel_crawl_task

router = APIRouter()
logger = logging.getLogger(__name__)


async def _run_crawl_background(task_id: str):
    """后台运行爬取任务"""
    async with async_session() as db:
        try:
            await run_crawl_task(task_id, db)
        except Exception as e:
            logger.error(f"Background crawl task {task_id} failed: {e}")
            try:
                result = await db.execute(select(CrawlTask).where(CrawlTask.id == task_id))
                task = result.scalar_one_or_none()
                if task and task.status not in ("completed", "cancelled", "failed"):
                    task.status = "failed"
                    await db.commit()
            except Exception:
                pass


async def _cleanup_zombie_tasks():
    """清理上次服务器关闭后遗留的 running/queued 僵尸任务"""
    async with async_session() as db:
        result = await db.execute(
            update(CrawlTask)
            .where(CrawlTask.status.in_(["running", "queued"]))
            .values(status="failed")
        )
        if result.rowcount > 0:
            await db.commit()
            logger.info(f"Cleaned up {result.rowcount} zombie crawl tasks from previous run")


@router.on_event("startup")
async def on_startup():
    await _cleanup_zombie_tasks()


@router.post("/start", response_model=CrawlTaskResponse, status_code=202)
async def start_crawl(data: CrawlRequest, db: AsyncSession = Depends(get_db)):
    """启动爬取任务"""
    task = CrawlTask(
        id=gen_id(),
        domain=data.domain,
        subdomain=data.subdomain,
        source=data.source,
        year_from=data.year_from,
        year_to=data.year_to,
        min_citations=data.min_citations,
        max_papers=data.max_papers,
        status="queued",
    )
    db.add(task)
    # 必须 commit 而非 flush，确保后台任务能读到此记录
    await db.commit()
    await db.refresh(task)

    asyncio.create_task(_run_crawl_background(task.id))

    return CrawlTaskResponse.model_validate(task)


@router.post("/tasks/{task_id}/cancel")
async def cancel_task(task_id: str, db: AsyncSession = Depends(get_db)):
    """取消正在进行的爬取任务"""
    result = await db.execute(select(CrawlTask).where(CrawlTask.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if task.status not in ("queued", "running"):
        raise HTTPException(status_code=400, detail=f"任务状态为 {task.status}，无法取消")

    cancelled = cancel_crawl_task(task_id)
    if not cancelled:
        task.status = "cancelled"
        await db.flush()

    return {"status": "cancelling", "task_id": task_id}


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
