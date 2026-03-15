import asyncio
import logging

from app.services.crawlers.base import BaseCrawler, PaperMeta

logger = logging.getLogger(__name__)

S2_API_BASE = "https://api.semanticscholar.org/graph/v1"

# 分离 search 和 detail 字段，减少搜索时的数据传输量
S2_SEARCH_FIELDS = "title,abstract,authors,year,venue,externalIds,citationCount,influentialCitationCount,s2FieldsOfStudy,url,openAccessPdf"
S2_DETAIL_FIELDS = "title,abstract,authors,year,venue,externalIds,citationCount,influentialCitationCount,s2FieldsOfStudy,url,openAccessPdf,references"

# Semantic Scholar API offset 上限
S2_MAX_OFFSET = 9999


class SemanticScholarCrawler(BaseCrawler):
    """Semantic Scholar API 爬虫

    使用官方 API，遵守速率限制：
    - 无 key: 100 次/5 分钟
    - 有 key: 按分配配额
    """

    def __init__(self, api_key: str = "", rate_limit: float = 1.0):
        # S2 API 是合法接口调用，使用 API 专用头即可
        super().__init__(rate_limit=rate_limit, rate_jitter=0.3, use_browser_headers=False)
        self.api_key = api_key

    async def __aenter__(self):
        await super().__aenter__()
        if self.api_key and self._client:
            self._client.headers["x-api-key"] = self.api_key
        return self

    async def search_papers(
        self, query: str, year_from: int = 2016, year_to: int = 2026,
        min_citations: int = 100, limit: int = 100,
    ) -> list[PaperMeta]:
        """搜索高引用论文

        注意：S2 API 的 offset 上限为 9999，超过部分无法获取。
        对于超大结果集，需要拆分查询条件（如按年份分批）。
        """
        papers = []
        offset = 0
        batch_size = min(limit, 100)
        consecutive_empty = 0

        while len(papers) < limit:
            if self.is_cancelled:
                logger.info(f"Search cancelled for '{query}'")
                break

            # S2 API offset 上限保护
            if offset >= S2_MAX_OFFSET:
                logger.warning(f"Reached S2 API offset limit ({S2_MAX_OFFSET}) for '{query}'")
                break

            actual_limit = min(batch_size, S2_MAX_OFFSET - offset)

            data = await self.fetch(
                f"{S2_API_BASE}/paper/search",
                params={
                    "query": query,
                    "year": f"{year_from}-{year_to}",
                    "minCitationCount": str(min_citations),
                    "fields": S2_SEARCH_FIELDS,
                    "offset": str(offset),
                    "limit": str(actual_limit),
                },
            )

            if not data:
                consecutive_empty += 1
                if consecutive_empty >= 3:
                    logger.warning(f"3 consecutive empty responses, stopping search for '{query}'")
                    break
                continue

            if "data" not in data or not data["data"]:
                break

            consecutive_empty = 0
            batch_count = 0
            for item in data["data"]:
                paper = self._parse_paper(item)
                if paper:
                    papers.append(paper)
                    batch_count += 1

            total = data.get("total", 0)
            offset += actual_limit

            logger.info(
                f"[S2] '{query}': fetched {batch_count} papers "
                f"(total: {len(papers)}/{min(total, limit)}, offset: {offset})"
            )

            if offset >= total:
                break

        return papers[:limit]

    async def get_paper_details(self, paper_id: str) -> PaperMeta | None:
        """获取单篇论文详情（含引用列表）"""
        data = await self.fetch(
            f"{S2_API_BASE}/paper/{paper_id}",
            params={"fields": S2_DETAIL_FIELDS},
        )
        if not data:
            return None
        return self._parse_paper(data)

    async def get_references(self, paper_id: str, limit: int = 100) -> list[str]:
        """获取论文的参考文献 ID 列表"""
        data = await self.fetch(
            f"{S2_API_BASE}/paper/{paper_id}/references",
            params={"fields": "paperId", "limit": str(limit)},
        )
        if not data or "data" not in data:
            return []
        return [
            ref["citedPaper"]["paperId"]
            for ref in data["data"]
            if ref.get("citedPaper", {}).get("paperId")
        ]

    async def get_citations(self, paper_id: str, limit: int = 100) -> list[str]:
        """获取引用了该论文的论文 ID 列表"""
        data = await self.fetch(
            f"{S2_API_BASE}/paper/{paper_id}/citations",
            params={"fields": "paperId", "limit": str(limit)},
        )
        if not data or "data" not in data:
            return []
        return [
            cit["citingPaper"]["paperId"]
            for cit in data["data"]
            if cit.get("citingPaper", {}).get("paperId")
        ]

    async def batch_get_papers(self, paper_ids: list[str]) -> list[PaperMeta]:
        """批量获取论文信息（使用 S2 batch endpoint，减少请求次数）"""
        if not paper_ids:
            return []

        results = []
        # S2 batch API 每次最多 500 篇
        for i in range(0, len(paper_ids), 500):
            if self.is_cancelled:
                break
            batch = paper_ids[i:i + 500]
            data = await self._post_json(
                f"{S2_API_BASE}/paper/batch",
                params={"fields": S2_SEARCH_FIELDS},
                json_body={"ids": batch},
            )
            if data:
                for item in data:
                    if item:
                        paper = self._parse_paper(item)
                        if paper:
                            results.append(paper)
        return results

    async def _post_json(self, url: str, params: dict | None = None, json_body: dict | None = None) -> list | None:
        """POST JSON 请求（用于 batch API）"""
        if self.is_cancelled:
            return None

        self.stats.requests_total += 1
        try:
            await self._smart_delay()
            resp = await self.client.post(url, params=params, json=json_body)

            if resp.status_code == 429:
                self.stats.requests_rate_limited += 1
                wait = float(resp.headers.get("Retry-After", 30))
                logger.warning(f"Rate limited on batch request, waiting {wait}s")
                await asyncio.sleep(min(wait, 120))
                # 重试一次
                resp = await self.client.post(url, params=params, json=json_body)

            if resp.status_code >= 400:
                self.stats.requests_failed += 1
                logger.warning(f"Batch request failed: {resp.status_code}")
                return None

            self.stats.requests_success += 1
            return resp.json()

        except Exception as e:
            self.stats.requests_failed += 1
            logger.error(f"Batch request error: {e}")
            return None

    def _parse_paper(self, data: dict) -> PaperMeta | None:
        """解析 Semantic Scholar API 返回的论文数据，带防御性检查"""
        if not isinstance(data, dict):
            return None
        if not data.get("title"):
            return None

        external_ids = data.get("externalIds") or {}
        if not isinstance(external_ids, dict):
            external_ids = {}

        pdf_info = data.get("openAccessPdf") or {}
        if not isinstance(pdf_info, dict):
            pdf_info = {}

        authors = []
        for a in data.get("authors") or []:
            if isinstance(a, dict) and a.get("name"):
                name = a["name"].strip()
                if name and len(name) < 200:
                    authors.append(name)

        refs = []
        for ref in data.get("references") or []:
            if isinstance(ref, dict) and ref.get("paperId"):
                refs.append(ref["paperId"])

        fields = []
        for f in data.get("s2FieldsOfStudy") or []:
            if isinstance(f, dict) and f.get("category"):
                fields.append(f["category"])

        # 安全解析数值字段
        def safe_int(val, default=0) -> int:
            if val is None:
                return default
            try:
                return int(val)
            except (ValueError, TypeError):
                return default

        return PaperMeta(
            title=data["title"].strip(),
            abstract=(data.get("abstract") or "").strip() or None,
            authors=authors,
            year=safe_int(data.get("year"), None),
            venue=(data.get("venue") or "").strip() or None,
            doi=external_ids.get("DOI"),
            arxiv_id=external_ids.get("ArXiv"),
            s2_id=data.get("paperId"),
            url=data.get("url"),
            pdf_url=pdf_info.get("url"),
            citation_count=safe_int(data.get("citationCount"), 0),
            influential_citation_count=safe_int(data.get("influentialCitationCount"), 0),
            references=refs,
            fields_of_study=fields,
        )
