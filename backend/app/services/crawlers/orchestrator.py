import logging
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import Paper, Author, Relation, CrawlTask, gen_id
from app.services.crawlers.base import PaperMeta
from app.services.crawlers.semantic_scholar import SemanticScholarCrawler
from app.core.config import settings

logger = logging.getLogger(__name__)

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


def compute_impact_score(paper: PaperMeta) -> float:
    """计算论文综合影响力评分 (0-100)"""
    score = 0.0
    current_year = datetime.now().year

    # 引用量 (40%)
    citation_score = min(paper.citation_count / 2000, 1.0) * 40
    score += citation_score

    # 年均引用增长 (30%)
    years = max(current_year - (paper.year or current_year), 1)
    annual_citations = paper.citation_count / years
    growth_score = min(annual_citations / 500, 1.0) * 30
    score += growth_score

    # 有影响力引用比例 (20%)
    if paper.citation_count > 0:
        ratio = paper.influential_citation_count / paper.citation_count
        score += min(ratio / 0.1, 1.0) * 20

    # 近年发表加分 (10%) — 鼓励发现新兴工作
    recency = max(0, 5 - (current_year - (paper.year or current_year))) / 5
    score += recency * 10

    return round(score, 2)


async def import_paper_meta(db: AsyncSession, meta: PaperMeta) -> Paper | None:
    """将爬取到的论文元数据导入数据库，返回 Paper 对象或 None（已存在）"""
    # 去重检查：按 s2_id / doi / arxiv_id
    for field, value in [("s2_id", meta.s2_id), ("doi", meta.doi), ("arxiv_id", meta.arxiv_id)]:
        if value:
            result = await db.execute(select(Paper).where(getattr(Paper, field) == value))
            existing = result.scalar_one_or_none()
            if existing:
                logger.debug(f"Paper already exists: {meta.title[:50]} ({field}={value})")
                return None

    paper = Paper(
        id=gen_id(),
        title=meta.title,
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
    )

    # 处理作者
    for author_name in meta.authors[:20]:  # 限制作者数
        result = await db.execute(select(Author).where(Author.name == author_name))
        author = result.scalar_one_or_none()
        if not author:
            author = Author(id=gen_id(), name=author_name)
            db.add(author)
        paper.authors.append(author)

    db.add(paper)
    return paper


async def build_citation_relations(db: AsyncSession, paper: Paper, references: list[str]):
    """根据参考文献 ID 创建引用关系"""
    for ref_s2_id in references:
        if not ref_s2_id:
            continue
        result = await db.execute(select(Paper).where(Paper.s2_id == ref_s2_id))
        ref_paper = result.scalar_one_or_none()
        if ref_paper:
            # 检查关系是否已存在
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


async def run_crawl_task(task_id: str, db: AsyncSession):
    """执行爬取任务"""
    result = await db.execute(select(CrawlTask).where(CrawlTask.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        return

    task.status = "running"
    task.started_at = datetime.utcnow()
    await db.commit()

    try:
        queries = []
        if task.subdomain and task.subdomain in CS_SUBDOMAIN_QUERIES:
            queries = CS_SUBDOMAIN_QUERIES[task.subdomain]
        else:
            # 所有子领域
            for sub_queries in CS_SUBDOMAIN_QUERIES.values():
                queries.extend(sub_queries)

        papers_per_query = max(task.max_papers // len(queries), 10) if queries else task.max_papers
        all_papers: list[PaperMeta] = []
        seen_ids: set[str] = set()

        async with SemanticScholarCrawler(
            api_key=settings.SEMANTIC_SCHOLAR_API_KEY,
            rate_limit=settings.CRAWLER_RATE_LIMIT,
        ) as crawler:
            for query in queries:
                logger.info(f"Crawling: '{query}' (year: {task.year_from}-{task.year_to})")

                papers = await crawler.search_papers(
                    query=query,
                    year_from=task.year_from,
                    year_to=task.year_to,
                    min_citations=task.min_citations,
                    limit=papers_per_query,
                )

                for p in papers:
                    dedup_key = p.s2_id or p.doi or p.title
                    if dedup_key and dedup_key not in seen_ids:
                        seen_ids.add(dedup_key)
                        all_papers.append(p)

                task.searched += len(papers)
                await db.commit()

        # 按影响力排序，取 top N
        all_papers.sort(key=lambda p: compute_impact_score(p), reverse=True)
        candidates = all_papers[:task.max_papers]
        task.candidates = len(candidates)
        await db.commit()

        # 导入数据库
        imported_papers = []
        for meta in candidates:
            try:
                paper = await import_paper_meta(db, meta)
                if paper:
                    imported_papers.append((paper, meta))
                    task.imported += 1
                else:
                    task.imported += 0  # 已存在，跳过
            except Exception as e:
                logger.error(f"Failed to import '{meta.title[:50]}': {e}")
                task.failed += 1
            await db.commit()

        # 建立引用关系
        for paper, meta in imported_papers:
            try:
                await build_citation_relations(db, paper, meta.references)
            except Exception as e:
                logger.warning(f"Failed to build relations for {paper.id}: {e}")
        await db.commit()

        task.status = "completed"
        task.finished_at = datetime.utcnow()
        logger.info(
            f"Crawl task {task_id} completed: "
            f"searched={task.searched}, candidates={task.candidates}, "
            f"imported={task.imported}, failed={task.failed}"
        )

    except Exception as e:
        logger.error(f"Crawl task {task_id} failed: {e}")
        task.status = "failed"

    await db.commit()
