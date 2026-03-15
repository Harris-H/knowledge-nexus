import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import httpx

logger = logging.getLogger(__name__)


@dataclass
class PaperMeta:
    """爬虫返回的论文元数据"""
    title: str
    abstract: str | None = None
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    venue: str | None = None
    doi: str | None = None
    arxiv_id: str | None = None
    s2_id: str | None = None
    url: str | None = None
    pdf_url: str | None = None
    citation_count: int = 0
    influential_citation_count: int = 0
    references: list[str] = field(default_factory=list)  # 被引论文 ID 列表
    fields_of_study: list[str] = field(default_factory=list)


class BaseCrawler(ABC):
    """爬虫基类：提供限流、重试、HTTP 客户端管理"""

    def __init__(self, rate_limit: float = 1.0, max_retries: int = 3):
        self.rate_limit = rate_limit
        self.max_retries = max_retries
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(
            timeout=30.0,
            headers={"User-Agent": "KnowledgeNexus/0.1 (Academic Research Tool)"},
        )
        return self

    async def __aexit__(self, *args):
        if self._client:
            await self._client.aclose()

    @property
    def client(self) -> httpx.AsyncClient:
        if not self._client:
            raise RuntimeError("Crawler must be used as async context manager")
        return self._client

    async def fetch(self, url: str, params: dict | None = None) -> dict | None:
        """带限流和重试的 HTTP GET"""
        for attempt in range(self.max_retries):
            try:
                await asyncio.sleep(self.rate_limit)
                resp = await self.client.get(url, params=params)

                if resp.status_code == 429:
                    wait = float(resp.headers.get("Retry-After", 10))
                    logger.warning(f"Rate limited, waiting {wait}s...")
                    await asyncio.sleep(wait)
                    continue

                resp.raise_for_status()
                return resp.json()

            except httpx.HTTPStatusError as e:
                logger.warning(f"HTTP {e.response.status_code} on attempt {attempt+1}: {url}")
                if attempt == self.max_retries - 1:
                    return None
                await asyncio.sleep(2 ** attempt)

            except (httpx.RequestError, Exception) as e:
                logger.error(f"Request failed on attempt {attempt+1}: {e}")
                if attempt == self.max_retries - 1:
                    return None
                await asyncio.sleep(2 ** attempt)

        return None

    @abstractmethod
    async def search_papers(
        self, query: str, year_from: int = 2016, year_to: int = 2026,
        min_citations: int = 100, limit: int = 100,
    ) -> list[PaperMeta]:
        """搜索论文"""
        ...

    @abstractmethod
    async def get_paper_details(self, paper_id: str) -> PaperMeta | None:
        """获取论文详情"""
        ...
