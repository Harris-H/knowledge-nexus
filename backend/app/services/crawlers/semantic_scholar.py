import logging

from app.services.crawlers.base import BaseCrawler, PaperMeta

logger = logging.getLogger(__name__)

S2_API_BASE = "https://api.semanticscholar.org/graph/v1"
S2_FIELDS = "title,abstract,authors,year,venue,externalIds,citationCount,influentialCitationCount,s2FieldsOfStudy,url,openAccessPdf,references"


class SemanticScholarCrawler(BaseCrawler):
    """Semantic Scholar API 爬虫"""

    def __init__(self, api_key: str = "", rate_limit: float = 1.0):
        super().__init__(rate_limit=rate_limit)
        self.api_key = api_key

    async def __aenter__(self):
        await super().__aenter__()
        if self.api_key:
            self._client.headers["x-api-key"] = self.api_key
        return self

    async def search_papers(
        self, query: str, year_from: int = 2016, year_to: int = 2026,
        min_citations: int = 100, limit: int = 100,
    ) -> list[PaperMeta]:
        """搜索高引用论文"""
        papers = []
        offset = 0
        batch_size = min(limit, 100)

        while len(papers) < limit:
            data = await self.fetch(
                f"{S2_API_BASE}/paper/search",
                params={
                    "query": query,
                    "year": f"{year_from}-{year_to}",
                    "minCitationCount": min_citations,
                    "fields": S2_FIELDS,
                    "offset": offset,
                    "limit": batch_size,
                },
            )

            if not data or "data" not in data:
                break

            for item in data["data"]:
                paper = self._parse_paper(item)
                if paper:
                    papers.append(paper)

            total = data.get("total", 0)
            offset += batch_size
            if offset >= total or offset >= limit:
                break

            logger.info(f"Fetched {len(papers)}/{min(total, limit)} papers for '{query}'")

        return papers[:limit]

    async def get_paper_details(self, paper_id: str) -> PaperMeta | None:
        """获取单篇论文详情"""
        data = await self.fetch(
            f"{S2_API_BASE}/paper/{paper_id}",
            params={"fields": S2_FIELDS},
        )
        if not data:
            return None
        return self._parse_paper(data)

    async def get_references(self, paper_id: str, limit: int = 100) -> list[str]:
        """获取论文的参考文献 ID 列表"""
        data = await self.fetch(
            f"{S2_API_BASE}/paper/{paper_id}/references",
            params={"fields": "paperId", "limit": limit},
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
            params={"fields": "paperId", "limit": limit},
        )
        if not data or "data" not in data:
            return []
        return [
            cit["citingPaper"]["paperId"]
            for cit in data["data"]
            if cit.get("citingPaper", {}).get("paperId")
        ]

    def _parse_paper(self, data: dict) -> PaperMeta | None:
        """解析 Semantic Scholar API 返回的论文数据"""
        if not data.get("title"):
            return None

        external_ids = data.get("externalIds") or {}
        pdf_info = data.get("openAccessPdf") or {}

        authors = []
        for a in data.get("authors") or []:
            if a.get("name"):
                authors.append(a["name"])

        refs = []
        for ref in data.get("references") or []:
            if isinstance(ref, dict) and ref.get("paperId"):
                refs.append(ref["paperId"])

        fields = []
        for f in data.get("s2FieldsOfStudy") or []:
            if f.get("category"):
                fields.append(f["category"])

        return PaperMeta(
            title=data["title"],
            abstract=data.get("abstract"),
            authors=authors,
            year=data.get("year"),
            venue=data.get("venue"),
            doi=external_ids.get("DOI"),
            arxiv_id=external_ids.get("ArXiv"),
            s2_id=data.get("paperId"),
            url=data.get("url"),
            pdf_url=pdf_info.get("url"),
            citation_count=data.get("citationCount", 0) or 0,
            influential_citation_count=data.get("influentialCitationCount", 0) or 0,
            references=refs,
            fields_of_study=fields,
        )
