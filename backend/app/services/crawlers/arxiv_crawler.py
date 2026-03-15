import logging
import re

from app.services.crawlers.base import BaseCrawler, PaperMeta

logger = logging.getLogger(__name__)

ARXIV_API_BASE = "http://export.arxiv.org/api/query"

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
    """arXiv API 爬虫

    arXiv API 返回 Atom XML，但通过参数控制可获取结构化数据。
    主要用于：获取 PDF 下载链接、补充 Semantic Scholar 缺失的论文。
    建议请求间隔 >= 3 秒。
    """

    def __init__(self, rate_limit: float = 3.0):
        super().__init__(rate_limit=rate_limit, rate_jitter=0.5, use_browser_headers=False)

    async def search_papers(
        self, query: str, year_from: int = 2016, year_to: int = 2026,
        min_citations: int = 0, limit: int = 100,
    ) -> list[PaperMeta]:
        """搜索 arXiv 论文

        注意：arXiv API 不支持按引用量筛选，需要后续通过其他数据源补充。
        """
        papers = []
        batch_size = min(limit, 100)
        start = 0

        while len(papers) < limit:
            if self.is_cancelled:
                break

            # arXiv API 返回 XML，我们用 httpx 获取后手动解析
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
                    # 过滤年份
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
