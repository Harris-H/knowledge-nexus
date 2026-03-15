import logging
import re

from app.services.crawlers.base import BaseCrawler, PaperMeta

logger = logging.getLogger(__name__)

ARXIV_API_BASE = "http://export.arxiv.org/api/query"
OPENALEX_API_BASE = "https://api.openalex.org"

# arXiv CS 子分类映射
ARXIV_CS_CATEGORIES = {
    "deep_learning": "cs.LG",
    "nlp": "cs.CL",
    "computer_vision": "cs.CV",
    "reinforcement_learning": "cs.AI",
    "graph_neural_networks": "cs.LG",
    "generative_models": "cs.LG",
    "systems": "cs.DC",
    "security": "cs.CR",
}


class ArxivCrawler(BaseCrawler):
    """arXiv API 爬虫（含 OpenAlex 引用交叉验证）

    arXiv 用于发现最新前沿预印本，OpenAlex 用于补充引用量数据。
    流程：arXiv 搜索 → OpenAlex 交叉查询引用量 → 过滤低引用论文。
    """

    def __init__(self, rate_limit: float = 3.0, enable_citation_check: bool = True):
        super().__init__(rate_limit=rate_limit, rate_jitter=0.5, use_browser_headers=False)
        self.enable_citation_check = enable_citation_check

    async def search_papers(
        self, query: str, year_from: int = 2016, year_to: int = 2026,
        min_citations: int = 0, limit: int = 100,
    ) -> list[PaperMeta]:
        """搜索 arXiv 论文，并通过 OpenAlex 交叉验证引用量"""
        # 第一阶段：从 arXiv 获取论文列表
        raw_papers = await self._search_arxiv(query, year_from, year_to, limit * 2)

        if not raw_papers:
            return []

        # 第二阶段：通过 OpenAlex 交叉验证引用量
        if self.enable_citation_check and min_citations > 0:
            enriched = await self._enrich_with_openalex(raw_papers)
            # 过滤低引用论文
            enriched = [p for p in enriched if p.citation_count >= min_citations]
            enriched.sort(key=lambda p: p.citation_count, reverse=True)
            logger.info(
                f"[arXiv+OA] '{query}': {len(raw_papers)} from arXiv, "
                f"{len(enriched)} passed citation filter (>={min_citations})"
            )
            return enriched[:limit]

        return raw_papers[:limit]

    async def _search_arxiv(
        self, query: str, year_from: int, year_to: int, limit: int
    ) -> list[PaperMeta]:
        """从 arXiv API 搜索论文"""
        papers = []
        batch_size = min(limit, 100)
        start = 0

        while len(papers) < limit:
            if self.is_cancelled:
                break

            self.stats.requests_total += 1
            await self._smart_delay()

            try:
                resp = await self.client.get(
                    ARXIV_API_BASE,
                    params={
                        "search_query": f"all:{query}",
                        "start": str(start),
                        "max_results": str(batch_size),
                        "sortBy": "relevance",
                        "sortOrder": "descending",
                    },
                )

                if resp.status_code != 200:
                    self.stats.requests_failed += 1
                    logger.warning(f"arXiv API returned {resp.status_code}")
                    break

                self.stats.requests_success += 1
                entries = self._parse_atom_feed(resp.text)

                if not entries:
                    break

                for entry in entries:
                    if entry.year and (entry.year < year_from or entry.year > year_to):
                        continue
                    papers.append(entry)

                start += batch_size
                if len(entries) < batch_size:
                    break

                logger.info(f"[arXiv] '{query}': fetched {len(papers)} papers (offset: {start})")

            except Exception as e:
                self.stats.requests_failed += 1
                logger.error(f"arXiv search error: {e}")
                break

        return papers[:limit]

    async def _enrich_with_openalex(self, papers: list[PaperMeta]) -> list[PaperMeta]:
        """通过 OpenAlex 批量查询引用量，丰富 arXiv 论文的引用数据"""
        enriched = []

        for paper in papers:
            if self.is_cancelled:
                break

            # 优先用 DOI 查询，其次用 arXiv ID
            filter_key = None
            if paper.doi:
                filter_key = f"doi:{paper.doi}"
            elif paper.arxiv_id:
                filter_key = f"ids.openalex:https://arxiv.org/abs/{paper.arxiv_id}"

            if not filter_key:
                enriched.append(paper)
                continue

            try:
                await self._smart_delay()
                self.stats.requests_total += 1

                # 用标题搜索作为后备（更可靠）
                search_title = paper.title[:100].replace('"', '')
                resp = await self.client.get(
                    f"{OPENALEX_API_BASE}/works",
                    params={
                        "search": search_title,
                        "per_page": "1",
                        "select": "id,cited_by_count,referenced_works",
                    },
                )

                if resp.status_code == 200:
                    self.stats.requests_success += 1
                    data = resp.json()
                    results = data.get("results", [])
                    if results:
                        oa_work = results[0]
                        paper.citation_count = oa_work.get("cited_by_count", 0)
                        paper.references = [
                            r for r in (oa_work.get("referenced_works") or [])
                        ][:200]
                else:
                    self.stats.requests_failed += 1

            except Exception as e:
                logger.debug(f"OpenAlex enrichment failed for '{paper.title[:50]}': {e}")

            enriched.append(paper)

        return enriched

    async def get_paper_details(self, paper_id: str) -> PaperMeta | None:
        """通过 arXiv ID 获取论文详情"""
        self.stats.requests_total += 1
        await self._smart_delay()

        try:
            resp = await self.client.get(
                ARXIV_API_BASE,
                params={"id_list": paper_id},
            )
            if resp.status_code != 200:
                self.stats.requests_failed += 1
                return None

            self.stats.requests_success += 1
            entries = self._parse_atom_feed(resp.text)
            return entries[0] if entries else None

        except Exception as e:
            self.stats.requests_failed += 1
            logger.error(f"arXiv detail error: {e}")
            return None

    def get_pdf_url(self, arxiv_id: str) -> str:
        """生成 arXiv PDF 下载链接"""
        clean_id = arxiv_id.replace("arXiv:", "").strip()
        return f"https://arxiv.org/pdf/{clean_id}.pdf"

    def _parse_atom_feed(self, xml_text: str) -> list[PaperMeta]:
        """解析 arXiv Atom XML 响应"""
        papers = []

        # 简单正则解析，避免引入 XML 库依赖
        entries = re.findall(r"<entry>(.*?)</entry>", xml_text, re.DOTALL)

        for entry in entries:
            title = self._extract_tag(entry, "title")
            if not title or title.startswith("Error"):
                continue

            # 清理标题中的换行
            title = " ".join(title.split())

            abstract = self._extract_tag(entry, "summary")
            if abstract:
                abstract = " ".join(abstract.split())

            # 提取 arXiv ID
            arxiv_id = None
            id_match = re.search(r"<id>http://arxiv.org/abs/(.+?)</id>", entry)
            if id_match:
                arxiv_id = id_match.group(1)
                # 去掉版本号 (e.g., "2301.12345v2" -> "2301.12345")
                arxiv_id = re.sub(r"v\d+$", "", arxiv_id)

            # 提取作者
            authors = re.findall(r"<name>(.+?)</name>", entry)

            # 提取发表年份
            published = self._extract_tag(entry, "published")
            year = None
            if published:
                year_match = re.match(r"(\d{4})", published)
                if year_match:
                    year = int(year_match.group(1))

            # 提取 PDF 链接
            pdf_url = None
            pdf_match = re.search(r'<link[^>]*title="pdf"[^>]*href="([^"]+)"', entry)
            if pdf_match:
                pdf_url = pdf_match.group(1)

            # 提取 DOI
            doi = None
            doi_match = re.search(r"<arxiv:doi[^>]*>(.+?)</arxiv:doi>", entry)
            if doi_match:
                doi = doi_match.group(1)

            # 提取分类
            categories = re.findall(r'<category[^>]*term="([^"]+)"', entry)

            papers.append(PaperMeta(
                title=title,
                abstract=abstract,
                authors=authors[:20],
                year=year,
                arxiv_id=arxiv_id,
                doi=doi,
                url=f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else None,
                pdf_url=pdf_url,
                fields_of_study=[c for c in categories if c.startswith("cs.")],
            ))

        return papers

    @staticmethod
    def _extract_tag(text: str, tag: str) -> str | None:
        match = re.search(rf"<{tag}[^>]*>(.*?)</{tag}>", text, re.DOTALL)
        return match.group(1).strip() if match else None
