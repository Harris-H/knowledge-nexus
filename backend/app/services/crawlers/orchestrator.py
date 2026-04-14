import logging
import traceback
from datetime import datetime
from pathlib import Path

import httpx
import yaml
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import Paper, Author, Relation, CrawlTask, gen_id
from app.services.crawlers.base import BaseCrawler, PaperMeta
from app.services.crawlers.semantic_scholar import SemanticScholarCrawler
from app.services.crawlers.openalex_crawler import OpenAlexCrawler
from app.core.config import settings

logger = logging.getLogger(__name__)

# PDF 存储目录
PDF_STORAGE_DIR = Path(__file__).resolve().parent.parent.parent.parent / "storage" / "papers"
PDF_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

# 活跃的爬虫实例，支持外部取消
_active_crawlers: dict[str, BaseCrawler] = {}

# 计算机科学子领域搜索关键词
CS_SUBDOMAIN_QUERIES = {
    "deep learning": [
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
    "computer vision": [
        "image recognition",
        "object detection",
        "visual transformer",
        "image generation diffusion",
    ],
    "reinforcement learning": [
        "reinforcement learning",
        "policy optimization",
        "multi-agent reinforcement",
    ],
    "graph neural networks": [
        "graph neural network",
        "graph convolution",
        "knowledge graph embedding",
    ],
    "generative models": [
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


def _load_elite_profiles() -> dict:
    """加载 elite_profiles.yaml 预设配置"""
    yaml_path = Path(__file__).parent / "elite_profiles.yaml"
    if not yaml_path.exists():
        logger.warning(f"Elite profiles not found: {yaml_path}")
        return {}
    with open(yaml_path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get_elite_presets() -> dict[str, dict]:
    """返回可用的预设配置列表（供 API 展示）"""
    profiles = _load_elite_profiles()
    return profiles.get("presets", {})


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


async def download_pdf(pdf_url: str, paper_id: str) -> str | None:
    """下载论文 PDF 文件，返回保存路径或 None"""
    if not pdf_url:
        return None

    # 构建文件名（使用 paper_id 避免冲突）
    filename = f"{paper_id}.pdf"
    filepath = PDF_STORAGE_DIR / filename

    if filepath.exists():
        return str(filepath.relative_to(PDF_STORAGE_DIR.parent.parent))

    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(60.0, connect=10.0),
            follow_redirects=True,
        ) as client:
            resp = await client.get(pdf_url)
            if resp.status_code == 200 and len(resp.content) > 1000:
                content_type = resp.headers.get("content-type", "")
                if "pdf" in content_type or resp.content[:5] == b"%PDF-":
                    filepath.write_bytes(resp.content)
                    rel_path = str(filepath.relative_to(PDF_STORAGE_DIR.parent.parent))
                    logger.info(f"  📄 PDF 下载成功: {rel_path} ({len(resp.content) // 1024}KB)")
                    return rel_path
                else:
                    logger.info(f"  ⚠️ PDF URL 返回非 PDF 内容: {content_type}")
            else:
                logger.info(f"  ⚠️ PDF 下载失败: status={resp.status_code} size={len(resp.content)}")
    except Exception as e:
        logger.info(f"  ⚠️ PDF 下载异常: {e}")

    return None


async def import_paper_meta(
    db: AsyncSession, meta: PaperMeta, pdf_path: str | None = None
) -> Paper | None:
    """将爬取到的论文元数据导入数据库，返回 Paper 对象或 None（已存在/无效）"""
    # 基本有效性检查
    if not meta.title or len(meta.title.strip()) < 3:
        logger.debug(f"Skipping paper with invalid title: '{meta.title}'")
        return None

    # 去重检查：按 s2_id / doi / arxiv_id / url（OpenAlex ID）
    for field_name, value in [
        ("s2_id", meta.s2_id),
        ("doi", meta.doi),
        ("arxiv_id", meta.arxiv_id),
        ("url", meta.url),
    ]:
        if value:
            result = await db.execute(select(Paper).where(getattr(Paper, field_name) == value))
            existing = result.scalar_one_or_none()
            if existing:
                logger.debug(f"Paper already exists: {meta.title[:50]} ({field_name}={value})")
                return None

    paper_id = gen_id()
    paper = Paper(
        id=paper_id,
        title=meta.title.strip(),
        abstract=meta.abstract,
        year=meta.year,
        venue=meta.venue,
        doi=meta.doi,
        arxiv_id=meta.arxiv_id,
        s2_id=meta.s2_id,
        url=meta.url,
        pdf_path=pdf_path,
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
    """执行爬取任务（支持 keyword / author / institution / elite_preset 模式）"""
    result = await db.execute(select(CrawlTask).where(CrawlTask.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        logger.error(f"Crawl task not found: {task_id}")
        return

    task.status = "running"
    task.started_at = datetime.utcnow()
    await db.commit()

    mode = getattr(task, "mode", "keyword") or "keyword"

    logger.info(
        f"🚀 [Task {task_id}] 开始爬取 | mode={mode} | "
        f"领域={task.domain} 子领域={task.subdomain} 数据源={task.source} "
        f"年份={task.year_from}-{task.year_to} 最低引用={task.min_citations} "
        f"最大论文数={task.max_papers}"
    )

    crawler = None
    try:
        all_papers: list[PaperMeta] = []
        seen_ids: set[str] = set()

        crawler = _create_crawler(source=task.source)
        _active_crawlers[task_id] = crawler

        async with crawler:
            if mode == "author":
                all_papers, seen_ids = await _crawl_by_author(crawler, task, seen_ids)
            elif mode == "institution":
                all_papers, seen_ids = await _crawl_by_institution(crawler, task, seen_ids)
            elif mode == "elite_preset":
                all_papers, seen_ids = await _crawl_by_preset(crawler, task, seen_ids)
            else:
                all_papers, seen_ids = await _crawl_by_keyword(crawler, task, seen_ids)

            logger.info(f"📊 [Task {task_id}] 网络统计: {crawler.stats.summary()}")

        # 按影响力排序，取 top N
        all_papers.sort(key=lambda p: compute_impact_score(p), reverse=True)
        candidates = all_papers[: task.max_papers]
        task.candidates = len(candidates)

        logger.info(
            f"📊 [Task {task_id}] 搜索完成: API返回 {task.searched} 篇, "
            f"去重后 {len(all_papers)} 篇, 选取 Top {len(candidates)} 篇"
        )

        if candidates:
            logger.info(
                f"  🏆 引用量最高: [{candidates[0].citation_count}] {candidates[0].title[:60]}"
            )
            logger.info(
                f"  📉 引用量最低: [{candidates[-1].citation_count}] {candidates[-1].title[:60]}"
            )

        # 序列化候选论文数据，存入 task 供前端预览
        import json
        from dataclasses import asdict

        candidates_json = []
        for meta in candidates:
            d = asdict(meta)
            d["impact_score"] = compute_impact_score(meta)
            candidates_json.append(d)
        task.candidates_data = json.dumps(candidates_json, ensure_ascii=False)
        task.status = "preview_ready"
        await db.commit()

        logger.info(f"👁️ [Task {task_id}] 候选论文已准备就绪，等待用户确认入库")

    except Exception as e:
        logger.error(f"❌ [Task {task_id}] 异常终止: {e}\n{traceback.format_exc()}")
        task.status = "failed"

    finally:
        _active_crawlers.pop(task_id, None)
        await db.commit()


async def confirm_crawl_task(task_id: str, selected_indices: list[int] | None, db: AsyncSession):
    """用户确认入库：将选中的候选论文导入数据库"""
    import json

    result = await db.execute(select(CrawlTask).where(CrawlTask.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise ValueError(f"Task not found: {task_id}")
    if task.status != "preview_ready":
        raise ValueError(f"Task {task_id} is not in preview_ready status (current: {task.status})")
    if not task.candidates_data:
        raise ValueError(f"Task {task_id} has no candidates data")

    all_candidates = json.loads(task.candidates_data)

    # If selected_indices is None, import all; otherwise import only selected
    if selected_indices is not None:
        candidates = [all_candidates[i] for i in selected_indices if 0 <= i < len(all_candidates)]
    else:
        candidates = all_candidates

    task.status = "running"
    await db.commit()

    logger.info(f"📥 [Task {task_id}] 开始导入 {len(candidates)}/{len(all_candidates)} 篇论文")

    imported_papers = []
    skipped = 0
    pdf_downloaded = 0
    for meta_dict in candidates:
        try:
            meta = PaperMeta(
                title=meta_dict["title"],
                abstract=meta_dict.get("abstract"),
                authors=meta_dict.get("authors", []),
                year=meta_dict.get("year"),
                venue=meta_dict.get("venue"),
                doi=meta_dict.get("doi"),
                arxiv_id=meta_dict.get("arxiv_id"),
                s2_id=meta_dict.get("s2_id"),
                url=meta_dict.get("url"),
                pdf_url=meta_dict.get("pdf_url"),
                citation_count=meta_dict.get("citation_count", 0),
                influential_citation_count=meta_dict.get("influential_citation_count", 0),
                references=meta_dict.get("references", []),
                fields_of_study=meta_dict.get("fields_of_study", []),
            )

            # 下载 PDF（如果有可用的 URL）
            pdf_path = None
            if meta.pdf_url:
                logger.info(f"  📥 尝试下载 PDF: {meta.pdf_url[:80]}")
                temp_id = gen_id()
                pdf_path = await download_pdf(meta.pdf_url, temp_id)
                if pdf_path:
                    pdf_downloaded += 1
            else:
                logger.info(f"  ℹ️ 无 PDF URL: {meta.title[:50]}")

            paper = await import_paper_meta(db, meta, pdf_path=pdf_path)
            if paper:
                imported_papers.append((paper, meta))
                task.imported += 1
                pdf_tag = " 📄" if pdf_path else ""
                logger.info(f"  ✅ 入库{pdf_tag}: [{meta.citation_count}] {meta.title[:60]}")
            else:
                skipped += 1
                # 如果论文已存在但下载了 PDF，删除多余的 PDF 文件
                if pdf_path:
                    pdf_file = PDF_STORAGE_DIR.parent.parent / pdf_path
                    pdf_file.unlink(missing_ok=True)
                logger.debug(f"  ⏭️ 跳过(已存在): {meta.title[:60]}")
        except Exception as e:
            logger.error(f"  ❌ 导入失败 '{meta_dict.get('title', '?')[:50]}': {e}")
            task.failed += 1

        if (task.imported + task.failed) % 10 == 0:
            await db.commit()

    await db.commit()

    # 建立引用关系
    relations_created = 0
    for paper, meta in imported_papers:
        try:
            count = await build_citation_relations(db, paper, meta.references)
            relations_created += count
        except Exception as e:
            logger.warning(f"Failed to build relations for {paper.id}: {e}")
    await db.commit()

    task.status = "completed"
    task.candidates_data = None  # 清理临时数据
    task.finished_at = datetime.utcnow()
    elapsed = (task.finished_at - task.started_at).total_seconds() if task.started_at else 0
    await db.commit()

    logger.info(
        f"✅ [Task {task_id}] COMPLETED | "
        f"耗时 {elapsed:.1f}s | "
        f"搜索={task.searched} 候选={task.candidates} "
        f"入库={task.imported} 跳过={skipped} 失败={task.failed} "
        f"PDF={pdf_downloaded} 新建关系={relations_created}"
    )

    return {
        "imported": task.imported,
        "skipped": skipped,
        "failed": task.failed,
        "pdf_downloaded": pdf_downloaded,
        "relations": relations_created,
    }


# ──────────────────────────────────────────────
# 各模式的爬取逻辑
# ──────────────────────────────────────────────


async def _crawl_by_keyword(
    crawler: BaseCrawler,
    task: CrawlTask,
    seen_ids: set[str],
) -> tuple[list[PaperMeta], set[str]]:
    """keyword 模式：按关键词搜索论文"""
    queries = []
    if task.subdomain:
        if task.subdomain in CS_SUBDOMAIN_QUERIES:
            queries = CS_SUBDOMAIN_QUERIES[task.subdomain]
        else:
            queries = [task.subdomain.strip().replace("_", " ")]
    else:
        for sub_queries in CS_SUBDOMAIN_QUERIES.values():
            queries.extend(sub_queries)

    if not queries:
        logger.error(f"❌ [Task {task.id}] 无可用搜索关键词")
        return [], seen_ids

    logger.info(f"📋 [Task {task.id}] keyword模式 关键词: {queries}")

    papers_per_query = max(task.max_papers, 20) if task.min_citations < 1000 else task.max_papers
    all_papers: list[PaperMeta] = []

    for i, query in enumerate(queries):
        if crawler.is_cancelled:
            break

        logger.info(
            f"🔍 [Task {task.id}] 查询 {i + 1}/{len(queries)}: '{query}' "
            f"(引用>={task.min_citations}, 限制{papers_per_query}篇)"
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
            logger.error(f"❌ [Task {task.id}] 查询失败 '{query}': {e}")
            papers = []

        for p in papers:
            dedup_key = p.s2_id or p.doi or p.url or p.title
            if dedup_key and dedup_key not in seen_ids:
                seen_ids.add(dedup_key)
                all_papers.append(p)

        logger.info(f"  📄 查询 '{query}' 返回 {len(papers)} 篇, 去重后累计 {len(all_papers)} 篇")

        task.searched += len(papers)

    return all_papers, seen_ids


async def _crawl_by_author(
    crawler: BaseCrawler,
    task: CrawlTask,
    seen_ids: set[str],
) -> tuple[list[PaperMeta], set[str]]:
    """author 模式：按作者 ID 搜索论文"""
    author_id = task.author_id
    if not author_id:
        logger.error(f"❌ [Task {task.id}] author 模式缺少 author_id")
        return [], seen_ids

    if not isinstance(crawler, OpenAlexCrawler):
        logger.error(f"❌ [Task {task.id}] author 模式仅支持 openalex 数据源")
        return [], seen_ids

    logger.info(f"👤 [Task {task.id}] author模式: {author_id}")

    all_papers: list[PaperMeta] = []
    try:
        papers = await crawler.search_by_author(
            author_id=author_id,
            year_from=task.year_from,
            year_to=task.year_to,
            min_citations=task.min_citations,
            limit=task.max_papers * 2,  # 多取以保证去重后够数
        )
    except Exception as e:
        logger.error(f"❌ [Task {task.id}] author 搜索失败: {e}")
        papers = []

    for p in papers:
        dedup_key = p.s2_id or p.doi or p.url or p.title
        if dedup_key and dedup_key not in seen_ids:
            seen_ids.add(dedup_key)
            all_papers.append(p)

    task.searched += len(papers)
    logger.info(f"  📄 author '{author_id}' 返回 {len(papers)} 篇, 去重后 {len(all_papers)} 篇")
    return all_papers, seen_ids


async def _crawl_by_institution(
    crawler: BaseCrawler,
    task: CrawlTask,
    seen_ids: set[str],
) -> tuple[list[PaperMeta], set[str]]:
    """institution 模式：按机构 ID 搜索论文"""
    institution_id = task.institution_id
    if not institution_id:
        logger.error(f"❌ [Task {task.id}] institution 模式缺少 institution_id")
        return [], seen_ids

    if not isinstance(crawler, OpenAlexCrawler):
        logger.error(f"❌ [Task {task.id}] institution 模式仅支持 openalex 数据源")
        return [], seen_ids

    logger.info(f"🏛️ [Task {task.id}] institution模式: {institution_id}")

    all_papers: list[PaperMeta] = []
    try:
        papers = await crawler.search_by_institution(
            institution_id=institution_id,
            year_from=task.year_from,
            year_to=task.year_to,
            min_citations=task.min_citations,
            limit=task.max_papers * 2,
        )
    except Exception as e:
        logger.error(f"❌ [Task {task.id}] institution 搜索失败: {e}")
        papers = []

    for p in papers:
        dedup_key = p.s2_id or p.doi or p.url or p.title
        if dedup_key and dedup_key not in seen_ids:
            seen_ids.add(dedup_key)
            all_papers.append(p)

    task.searched += len(papers)
    logger.info(
        f"  📄 institution '{institution_id}' 返回 {len(papers)} 篇, 去重后 {len(all_papers)} 篇"
    )
    return all_papers, seen_ids


async def _crawl_by_preset(
    crawler: BaseCrawler,
    task: CrawlTask,
    seen_ids: set[str],
) -> tuple[list[PaperMeta], set[str]]:
    """elite_preset 模式：使用预设配置批量爬取"""
    preset_name = task.preset_name
    if not preset_name:
        logger.error(f"❌ [Task {task.id}] elite_preset 模式缺少 preset_name")
        return [], seen_ids

    if not isinstance(crawler, OpenAlexCrawler):
        logger.error(f"❌ [Task {task.id}] elite_preset 模式仅支持 openalex 数据源")
        return [], seen_ids

    profiles = _load_elite_profiles()
    presets = profiles.get("presets", {})
    preset = presets.get(preset_name)
    if not preset:
        logger.error(
            f"❌ [Task {task.id}] 预设 '{preset_name}' 不存在, 可选: {list(presets.keys())}"
        )
        return [], seen_ids

    logger.info(
        f"⭐ [Task {task.id}] elite_preset模式: {preset_name} — {preset.get('description', '')}"
    )

    min_cit = preset.get("min_citations", task.min_citations)
    year_from = preset.get("year_from", task.year_from)
    all_papers: list[PaperMeta] = []

    # 按研究者搜索
    for author_id in preset.get("researchers", []):
        if crawler.is_cancelled:
            break
        logger.info(f"  👤 搜索研究者: {author_id}")
        try:
            papers = await crawler.search_by_author(
                author_id=author_id,
                year_from=year_from,
                year_to=task.year_to,
                min_citations=min_cit,
                limit=50,
            )
            for p in papers:
                dedup_key = p.s2_id or p.doi or p.url or p.title
                if dedup_key and dedup_key not in seen_ids:
                    seen_ids.add(dedup_key)
                    all_papers.append(p)
            task.searched += len(papers)
            logger.info(f"    📄 {author_id}: {len(papers)} 篇")
        except Exception as e:
            logger.error(f"    ❌ {author_id} 失败: {e}")

    # 按机构搜索
    for inst_id in preset.get("institutions", []):
        if crawler.is_cancelled:
            break
        logger.info(f"  🏛️ 搜索机构: {inst_id}")
        try:
            papers = await crawler.search_by_institution(
                institution_id=inst_id,
                year_from=year_from,
                year_to=task.year_to,
                min_citations=min_cit,
                limit=50,
            )
            for p in papers:
                dedup_key = p.s2_id or p.doi or p.url or p.title
                if dedup_key and dedup_key not in seen_ids:
                    seen_ids.add(dedup_key)
                    all_papers.append(p)
            task.searched += len(papers)
            logger.info(f"    📄 {inst_id}: {len(papers)} 篇")
        except Exception as e:
            logger.error(f"    ❌ {inst_id} 失败: {e}")

    logger.info(f"  ⭐ 预设 '{preset_name}' 共搜索 {task.searched} 篇, 去重后 {len(all_papers)} 篇")
    return all_papers, seen_ids
