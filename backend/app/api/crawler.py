import asyncio
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, text

from app.core.database import get_db, async_session
from app.models.models import CrawlTask, gen_id
from app.schemas.schemas import CrawlRequest, CrawlTaskResponse
from app.services.crawlers.orchestrator import (
    run_crawl_task,
    cancel_crawl_task,
    confirm_crawl_task,
)
from app.services.crawlers.openalex_crawler import OpenAlexCrawler

router = APIRouter()
logger = logging.getLogger(__name__)


# crawl_tasks 表可能缺少的列（模型新增字段时需同步更新此列表）
_CRAWL_TASKS_EXPECTED_COLUMNS: dict[str, str] = {
    "mode": "VARCHAR(50) DEFAULT 'keyword'",
    "author_id": "VARCHAR(100)",
    "institution_id": "VARCHAR(100)",
    "preset_name": "VARCHAR(100)",
    "candidates_data": "TEXT",
}


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


async def _ensure_crawl_tasks_schema():
    """检查 crawl_tasks 表是否缺少新增列，自动 ALTER TABLE 补齐"""
    async with async_session() as db:
        result = await db.execute(text("PRAGMA table_info(crawl_tasks)"))
        existing_cols = {row[1] for row in result.fetchall()}
        for col, typedef in _CRAWL_TASKS_EXPECTED_COLUMNS.items():
            if col not in existing_cols:
                await db.execute(text(f"ALTER TABLE crawl_tasks ADD COLUMN {col} {typedef}"))
                logger.warning(f"Auto-migrated: added column '{col}' to crawl_tasks")
        await db.commit()


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
    await _ensure_crawl_tasks_schema()
    await _cleanup_zombie_tasks()


@router.post("/start", response_model=CrawlTaskResponse, status_code=202)
async def start_crawl(data: CrawlRequest, db: AsyncSession = Depends(get_db)):
    """启动爬取任务"""
    task = CrawlTask(
        id=gen_id(),
        mode=data.mode,
        domain=data.domain,
        subdomain=data.subdomain,
        source=data.source,
        year_from=data.year_from,
        year_to=data.year_to,
        min_citations=data.min_citations,
        max_papers=data.max_papers,
        author_id=data.author_id,
        institution_id=data.institution_id,
        preset_name=data.preset_name,
        status="queued",
    )
    db.add(task)
    try:
        await db.commit()
    except Exception as e:
        logger.error(f"Failed to create crawl task: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"创建任务失败: {e}")
    await db.refresh(task)

    logger.info(
        f"📝 Created crawl task {task.id} | mode={data.mode} "
        f"preset={data.preset_name} author={data.author_id} "
        f"institution={data.institution_id}"
    )

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


@router.get("/tasks/{task_id}/candidates")
async def get_task_candidates(task_id: str, db: AsyncSession = Depends(get_db)):
    """获取爬取任务的候选论文列表（预览用）"""
    import json

    result = await db.execute(select(CrawlTask).where(CrawlTask.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    if task.status != "preview_ready":
        raise HTTPException(
            status_code=400, detail=f"任务状态不是 preview_ready (当前: {task.status})"
        )
    if not task.candidates_data:
        return []
    return json.loads(task.candidates_data)


@router.post("/tasks/{task_id}/confirm")
async def confirm_task_import(
    task_id: str,
    body: dict | None = None,
    db: AsyncSession = Depends(get_db),
):
    """确认入库：将选中的候选论文导入数据库

    body: {"selected_indices": [0, 1, 3, ...]} 或 null/空表示全部导入
    """
    selected = None
    if body and "selected_indices" in body:
        selected = body["selected_indices"]
    try:
        result = await confirm_crawl_task(task_id, selected, db)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tasks", response_model=list[CrawlTaskResponse])
async def list_crawl_tasks(db: AsyncSession = Depends(get_db)):
    """列出所有爬取任务"""
    result = await db.execute(select(CrawlTask).order_by(CrawlTask.created_at.desc()))
    tasks = result.scalars().all()
    return [CrawlTaskResponse.model_validate(t) for t in tasks]


# ──────────────────────────────────────────────
# Elite Profile 辅助 API
# ──────────────────────────────────────────────


@router.get("/elite/presets")
async def list_elite_presets():
    """列出所有可用的 Elite 预设配置"""
    from app.services.crawlers.orchestrator import _load_elite_profiles

    profiles = _load_elite_profiles()
    presets = profiles.get("presets", {})

    # Build ID→name lookup maps
    inst_map = {inst["id"]: inst["name"] for inst in profiles.get("institutions", [])}
    researcher_map = {r["id"]: r["name"] for r in profiles.get("researchers", [])}

    result = {}
    for name, preset in presets.items():
        researcher_ids = preset.get("researchers", [])
        institution_ids = preset.get("institutions", [])
        result[name] = {
            "description": preset.get("description", ""),
            "researchers": len(researcher_ids),
            "institutions": len(institution_ids),
            "researcher_names": [researcher_map.get(rid, rid) for rid in researcher_ids],
            "institution_names": [inst_map.get(iid, iid) for iid in institution_ids],
            "min_citations": preset.get("min_citations", 0),
            "year_from": preset.get("year_from", 2016),
        }
    return result


@router.get("/elite/authors/search")
async def search_authors(q: str):
    """搜索学者（按姓名，返回 OpenAlex 匹配结果，YAML 中的 affiliation 覆盖 OpenAlex 错误数据）"""
    if not q or len(q.strip()) < 2:
        raise HTTPException(status_code=400, detail="搜索关键词至少 2 个字符")

    from app.services.crawlers.orchestrator import _load_elite_profiles

    async with OpenAlexCrawler(rate_limit=0.3) as crawler:
        results = await crawler.resolve_author_id(q.strip())

    # Override affiliation with curated data from elite_profiles.yaml
    profiles = _load_elite_profiles()
    affiliation_overrides = {
        r["id"]: r["affiliation"] for r in profiles.get("researchers", []) if r.get("affiliation")
    }
    for r in results:
        if r["id"] in affiliation_overrides:
            r["affiliation"] = affiliation_overrides[r["id"]]

    return results


@router.get("/elite/institutions/search")
async def search_institutions(q: str):
    """搜索机构（按名称，返回 OpenAlex 匹配结果）"""
    if not q or len(q.strip()) < 2:
        raise HTTPException(status_code=400, detail="搜索关键词至少 2 个字符")

    async with OpenAlexCrawler(rate_limit=0.3) as crawler:
        results = await crawler.resolve_institution_id(q.strip())
    return results


@router.get("/elite/authors/top")
async def discover_top_authors(institution_id: str, min_h_index: int = 50, limit: int = 20):
    """发现指定机构的高 h-index 学者"""
    if not institution_id.startswith("I"):
        raise HTTPException(status_code=400, detail="无效的机构 ID，应以 'I' 开头")

    async with OpenAlexCrawler(rate_limit=0.3) as crawler:
        results = await crawler.discover_top_authors(
            institution_id=institution_id,
            min_h_index=min_h_index,
            limit=limit,
        )
    return results
