import logging
import traceback
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import Paper, Author, Relation, CrawlTask, gen_id
from app.services.crawlers.base import BaseCrawler, PaperMeta
from app.services.crawlers.semantic_scholar import SemanticScholarCrawler
from app.services.crawlers.openalex_crawler import OpenAlexCrawler
from app.core.config import settings

logger = logging.getLogger(__name__)

# 活跃的爬虫实例，支持外部取消
_active_crawlers: dict[str, BaseCrawler] = {}

# 计算机科学子领域搜索关键词
CS_SUBDOMAIN_QUERIES = {
    "deep_learning": [
        "deep learning",
        "neural network architecture",
        "transformer model",
        "representation learning",
    ],
    "nlp": [
        "large language model",
        "natural language processing",
        "text generation",
        "machine translation",
    ],
    "computer_vision": [
        "image recognition",
        "object detection",
        "visual transformer",
        "image generation diffusion",
    ],
    "reinforcement_learning": [
        "reinforcement learning",
        "policy optimization",
        "multi-agent reinforcement",
    ],
    "graph_neural_networks": [
        "graph neural network",
        "graph convolution",
        "knowledge graph embedding",
    ],
    "generative_models": [
        "generative adversarial network",
        "diffusion model",
        "variational autoencoder",
        "flow matching generative",
    ],
    "systems": [
        "distributed systems consensus",
        "database query optimization",
        "cloud computing serverless",
    ],
}


def _create_crawler(source: str = "openalex") -> BaseCrawler:
    """根据指定数据源创建爬虫实例。"""
    if source == "semantic_scholar":
        return SemanticScholarCrawler(
            api_key=settings.SEMANTIC_SCHOLAR_API_KEY,
            rate_limit=settings.CRAWLER_RATE_LIMIT,
        )
    elif source == "arxiv":
        from app.services.crawlers.arxiv_crawler import ArxivCrawler
        return ArxivCrawler(rate_limit=0.5)
    # 默认 OpenAlex：无严格速率限制，响应快
    return OpenAlexCrawler(
        email=getattr(settings, "OPENALEX_EMAIL", ""),
        rate_limit=0.5,
    )


def compute_impact_score(paper: PaperMeta) -> float:
    """计算论文综合影响力评分 (0-100)"""
    score = 0.0
    current_year = datetime.now().year
    paper_year = paper.year or current_year

    # 引用量 (40%)
    citation_score = min(paper.citation_count / 2000, 1.0) * 40
    score += citation_score

    # 年均引用增长 (30%)
    years = max(current_year - paper_year, 1)
    annual_citations = paper.citation_count / years
    growth_score = min(annual_citations / 500, 1.0) * 30
    score += growth_score

    # 有影响力引用比例 (20%)
    if paper.citation_count > 0:
        ratio = paper.influential_citation_count / paper.citation_count
        score += min(ratio / 0.1, 1.0) * 20

    # 近年发表加分 (10%) — 鼓励发现新兴工作
    recency = max(0, 5 - (current_year - paper_year)) / 5
    score += recency * 10

    return round(score, 2)


async def import_paper_meta(db: AsyncSession, meta: PaperMeta) -> Paper | None:
    """将爬取到的论文元数据导入数据库，返回 Paper 对象或 None（已存在/无效）"""
    # 基本有效性检查
    if not meta.title or len(meta.title.strip()) < 3:
        logger.debug(f"Skipping paper with invalid title: '{meta.title}'")
        return None

    # 去重检查：按 s2_id / doi / arxiv_id / url（OpenAlex ID）
    for field_name, value in [("s2_id", meta.s2_id), ("doi", meta.doi), ("arxiv_id", meta.arxiv_id), ("url", meta.url)]:
        if value:
            result = await db.execute(
                select(Paper).where(getattr(Paper, field_name) == value)
            )
            existing = result.scalar_one_or_none()
            if existing:
                logger.debug(f"Paper already exists: {meta.title[:50]} ({field_name}={value})")
                return None

    paper = Paper(
        id=gen_id(),
        title=meta.title.strip(),
        abstract=meta.abstract,
        year=meta.year,
        venue=meta.venue,
        doi=meta.doi,
        arxiv_id=meta.arxiv_id,
        s2_id=meta.s2_id,
        url=meta.url,
        citation_count=meta.citation_count,
        influential_citation_count=meta.influential_citation_count,
        impact_score=compute_impact_score(meta),
        fields_of_study=", ".join(meta.fields_of_study[:5]) if meta.fields_of_study else None,
    )

    # 处理作者（限制数量，防御异常数据）
    for author_name in meta.authors[:20]:
        if not author_name or len(author_name.strip()) < 1:
            continue
        clean_name = author_name.strip()[:200]
        result = await db.execute(select(Author).where(Author.name == clean_name))
        author = result.scalar_one_or_none()
        if not author:
            author = Author(id=gen_id(), name=clean_name)
            db.add(author)
        paper.authors.append(author)

    db.add(paper)
    return paper


async def build_citation_relations(db: AsyncSession, paper: Paper, references: list[str]):
    """根据参考文献 ID 创建引用关系"""
    created = 0
    for ref_s2_id in references:
        if not ref_s2_id:
            continue
        result = await db.execute(select(Paper).where(Paper.s2_id == ref_s2_id))
        ref_paper = result.scalar_one_or_none()
        if ref_paper:
            existing = await db.execute(
                select(Relation).where(
                    Relation.source_id == paper.id,
                    Relation.target_id == ref_paper.id,
                    Relation.relation_type == "CITES",
                )
            )
            if not existing.scalar_one_or_none():
                relation = Relation(
                    id=gen_id(),
                    source_id=paper.id,
                    source_type="paper",
                    target_id=ref_paper.id,
                    target_type="paper",
                    relation_type="CITES",
                    confidence=1.0,
                    ai_generated=False,
                    status="confirmed",
                )
                db.add(relation)
                created += 1

    if created > 0:
        logger.debug(f"Created {created} citation relations for paper {paper.id}")
    return created


def cancel_crawl_task(task_id: str) -> bool:
    """取消正在进行的爬取任务"""
    crawler = _active_crawlers.get(task_id)
    if crawler:
        crawler.cancel()
        logger.info(f"Cancellation sent for task {task_id}")
        return True
    return False


async def run_crawl_task(task_id: str, db: AsyncSession):
    """执行爬取任务"""
    result = await db.execute(select(CrawlTask).where(CrawlTask.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        logger.error(f"Crawl task not found: {task_id}")
        return

    task.status = "running"
    task.started_at = datetime.utcnow()
    await db.commit()

    crawler = None
    try:
        # 确定搜索关键词
        queries = []
        if task.subdomain:
            if task.subdomain in CS_SUBDOMAIN_QUERIES:
                # 预设子领域 → 使用预定义关键词
                queries = CS_SUBDOMAIN_QUERIES[task.subdomain]
            else:
                # 自定义文本输入 → 直接作为搜索关键词（下划线转空格）
                queries = [task.subdomain.strip().replace("_", " ")]
        else:
            for sub_queries in CS_SUBDOMAIN_QUERIES.values():
                queries.extend(sub_queries)

        if not queries:
            logger.error(f"No queries for task {task_id}")
            task.status = "failed"
            await db.commit()
            return

        # 每个查询多取一些，最终混合排序取 top N（确保高引用论文不被低引用查询挤掉）
        papers_per_query = max(task.max_papers, 20)
        all_papers: list[PaperMeta] = []
        seen_ids: set[str] = set()

        crawler = _create_crawler(source=task.source)
        _active_crawlers[task_id] = crawler

        async with crawler:
            for i, query in enumerate(queries):
                if crawler.is_cancelled:
                    logger.info(f"Task {task_id} cancelled during search phase")
                    break

                logger.info(
                    f"[Task {task_id}] Query {i+1}/{len(queries)}: '{query}' "
                    f"(year: {task.year_from}-{task.year_to}, min_citations: {task.min_citations})"
                )

                try:
                    papers = await crawler.search_papers(
                        query=query,
                        year_from=task.year_from,
                        year_to=task.year_to,
                        min_citations=task.min_citations,
                        limit=papers_per_query,
                    )
                except Exception as e:
                    logger.error(f"Search failed for query '{query}': {e}")
                    papers = []

                for p in papers:
                    dedup_key = p.s2_id or p.doi or p.url or p.title
                    if dedup_key and dedup_key not in seen_ids:
                        seen_ids.add(dedup_key)
                        all_papers.append(p)

                task.searched += len(papers)
                await db.commit()

            # 输出爬虫统计
            logger.info(f"[Task {task_id}] Crawler stats: {crawler.stats.summary()}")

        # 按影响力排序，取 top N
        all_papers.sort(key=lambda p: compute_impact_score(p), reverse=True)
        candidates = all_papers[:task.max_papers]
        task.candidates = len(candidates)
        await db.commit()

        logger.info(
            f"[Task {task_id}] Searched {task.searched} papers, "
            f"{len(all_papers)} unique, top {len(candidates)} selected"
        )

        # 导入数据库
        imported_papers = []
        skipped = 0
        for meta in candidates:
            if crawler.is_cancelled:
                break
            try:
                paper = await import_paper_meta(db, meta)
                if paper:
                    imported_papers.append((paper, meta))
                    task.imported += 1
                else:
                    skipped += 1
            except Exception as e:
                logger.error(
                    f"Failed to import '{meta.title[:50]}': {e}\n"
                    f"{traceback.format_exc()}"
                )
                task.failed += 1

            # 每 10 篇提交一次，避免大事务
            if (task.imported + task.failed) % 10 == 0:
                await db.commit()

        await db.commit()

        # 建立引用关系
        relations_created = 0
        for paper, meta in imported_papers:
            if crawler.is_cancelled:
                break
            try:
                count = await build_citation_relations(db, paper, meta.references)
                relations_created += count
            except Exception as e:
                logger.warning(f"Failed to build relations for {paper.id}: {e}")
        await db.commit()

        if crawler.is_cancelled:
            task.status = "cancelled"
        else:
            task.status = "completed"

        task.finished_at = datetime.utcnow()
        elapsed = (task.finished_at - task.started_at).total_seconds()

        logger.info(
            f"[Task {task_id}] {'Completed' if not crawler.is_cancelled else 'Cancelled'}: "
            f"searched={task.searched}, candidates={task.candidates}, "
            f"imported={task.imported}, skipped={skipped}, failed={task.failed}, "
            f"relations={relations_created}, elapsed={elapsed:.1f}s"
        )

    except Exception as e:
        logger.error(f"Crawl task {task_id} failed with exception: {e}\n{traceback.format_exc()}")
        task.status = "failed"

    finally:
        _active_crawlers.pop(task_id, None)
        await db.commit()
