import asyncio
import logging
import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import httpx

logger = logging.getLogger(__name__)

# 真实浏览器 User-Agent 池
_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
]

# 真实浏览器请求头
_BROWSER_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Cache-Control": "no-cache",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}

# API 专用请求头（用于合法 API 调用，如 Semantic Scholar）
_API_HEADERS = {
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}


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
    references: list[str] = field(default_factory=list)
    fields_of_study: list[str] = field(default_factory=list)


@dataclass
class CrawlStats:
    """爬取统计信息"""

    requests_total: int = 0
    requests_success: int = 0
    requests_failed: int = 0
    requests_rate_limited: int = 0
    total_wait_seconds: float = 0.0
    start_time: float = field(default_factory=time.monotonic)

    @property
    def elapsed(self) -> float:
        return time.monotonic() - self.start_time

    @property
    def success_rate(self) -> float:
        return self.requests_success / max(self.requests_total, 1) * 100

    def summary(self) -> str:
        return (
            f"Requests: {self.requests_total} total, {self.requests_success} ok, "
            f"{self.requests_failed} failed, {self.requests_rate_limited} rate-limited | "
            f"Elapsed: {self.elapsed:.1f}s | Success rate: {self.success_rate:.1f}%"
        )


class BaseCrawler(ABC):
    """爬虫基类：提供限流、重试、伪装、统计等通用能力"""

    def __init__(
        self,
        rate_limit: float = 1.0,
        rate_jitter: float = 0.5,
        max_retries: int = 3,
        use_browser_headers: bool = False,
    ):
        self.rate_limit = rate_limit
        self.rate_jitter = rate_jitter  # 随机延迟浮动范围
        self.max_retries = max_retries
        self.use_browser_headers = use_browser_headers
        self._original_rate_limit = rate_limit  # 用于自适应恢复
        self._client: httpx.AsyncClient | None = None
        self._cancelled = False
        self.stats = CrawlStats()

    async def __aenter__(self):
        headers = dict(_BROWSER_HEADERS if self.use_browser_headers else _API_HEADERS)
        headers["User-Agent"] = random.choice(_USER_AGENTS)

        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(connect=10.0, read=30.0, write=10.0, pool=5.0),
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
            headers=headers,
            follow_redirects=True,
            http2=False,  # 部分 API 对 HTTP/2 兼容性差，保守使用 HTTP/1.1
        )
        self._cancelled = False
        self.stats = CrawlStats()
        return self

    async def __aexit__(self, *args):
        if self._client:
            await self._client.aclose()
            self._client = None

    @property
    def client(self) -> httpx.AsyncClient:
        if not self._client:
            raise RuntimeError("Crawler must be used as async context manager")
        return self._client

    def cancel(self):
        """取消正在进行的爬取"""
        self._cancelled = True
        logger.info("Crawler cancellation requested")

    @property
    def is_cancelled(self) -> bool:
        return self._cancelled

    async def _smart_delay(self):
        """智能延迟：基础限流 + 随机抖动，模拟人类行为"""
        jitter = random.uniform(-self.rate_jitter, self.rate_jitter)
        delay = max(0.3, self.rate_limit + jitter)
        self.stats.total_wait_seconds += delay
        await asyncio.sleep(delay)

    def _rotate_ua(self):
        """每隔若干请求轮换 User-Agent"""
        if self.stats.requests_total % 20 == 0 and self._client:
            new_ua = random.choice(_USER_AGENTS)
            self._client.headers["User-Agent"] = new_ua

    async def fetch(self, url: str, params: dict | None = None) -> dict | None:
        """带限流、重试、自适应限速的 HTTP GET 请求

        关键设计：
        - 429 有独立的重试计数器（不消耗 max_retries 配额）
        - 收到 429 后自动提升后续所有请求的间隔（自适应限速）
        - 5xx/网络错误使用指数退避重试
        """
        if self._cancelled:
            return None

        self._rotate_ua()
        last_error = None
        error_attempts = 0  # 非 429 错误的重试计数
        rate_limit_hits = 0  # 429 的重试计数
        max_rate_limit_retries = 8  # 429 最多重试 8 次（总等待可达数分钟）

        while error_attempts < self.max_retries:
            if self._cancelled:
                return None

            self.stats.requests_total += 1

            try:
                await self._smart_delay()
                resp = await self.client.get(url, params=params)

                # === 429 Too Many Requests — 独立处理，不消耗重试配额 ===
                if resp.status_code == 429:
                    rate_limit_hits += 1
                    self.stats.requests_rate_limited += 1

                    if rate_limit_hits > max_rate_limit_retries:
                        logger.error(
                            f"Exceeded max rate limit retries ({max_rate_limit_retries}): {url}"
                        )
                        return None

                    # 解析 Retry-After 或使用指数退避
                    retry_after = resp.headers.get("Retry-After")
                    if retry_after:
                        try:
                            wait = float(retry_after)
                        except ValueError:
                            wait = 30.0
                    else:
                        # 指数退避：10s, 20s, 40s, 60s, 60s...
                        wait = min(10.0 * (2 ** (rate_limit_hits - 1)), 60.0)

                    # 自适应：提升后续所有请求的基础间隔
                    old_rate = self.rate_limit
                    self.rate_limit = min(self.rate_limit * 1.5, 10.0)
                    if self.rate_limit != old_rate:
                        logger.info(
                            f"Adaptive rate limit: {old_rate:.1f}s -> {self.rate_limit:.1f}s"
                        )

                    logger.warning(
                        f"Rate limited (429), waiting {wait:.0f}s "
                        f"(429 count: {rate_limit_hits}/{max_rate_limit_retries}): "
                        f"{url.split('?')[0]}"
                    )
                    await asyncio.sleep(wait + random.uniform(0, 3))
                    continue  # 不增加 error_attempts

                # === 5xx 服务端错误 — 可重试 ===
                if resp.status_code >= 500:
                    error_attempts += 1
                    self.stats.requests_failed += 1
                    wait = (2**error_attempts) + random.uniform(0, 1)
                    logger.warning(
                        f"Server error {resp.status_code}, retrying in {wait:.1f}s "
                        f"(attempt {error_attempts}/{self.max_retries}): {url}"
                    )
                    await asyncio.sleep(wait)
                    continue

                # === 4xx 客户端错误（非429）— 不可恢复 ===
                if resp.status_code >= 400:
                    self.stats.requests_failed += 1
                    logger.warning(
                        f"Client error {resp.status_code}: {url.split('?')[0]}"
                    )
                    return None

                # === 成功 ===
                self.stats.requests_success += 1

                # 成功后适当恢复速率（慢恢复）
                if rate_limit_hits > 0 and self.rate_limit > self._original_rate_limit:
                    self.rate_limit = max(
                        self.rate_limit * 0.9,
                        self._original_rate_limit,
                    )

                return resp.json()

            except httpx.TimeoutException as e:
                error_attempts += 1
                last_error = e
                self.stats.requests_failed += 1
                wait = (2**error_attempts) + random.uniform(0, 2)
                logger.warning(
                    f"Timeout (attempt {error_attempts}/{self.max_retries}), "
                    f"retrying in {wait:.1f}s: {url.split('?')[0]}"
                )
                await asyncio.sleep(wait)

            except httpx.RequestError as e:
                error_attempts += 1
                last_error = e
                self.stats.requests_failed += 1
                wait = (2**error_attempts) + random.uniform(0, 2)
                logger.warning(
                    f"Request error (attempt {error_attempts}/{self.max_retries}): {e}"
                )
                await asyncio.sleep(wait)

            except Exception as e:
                error_attempts += 1
                last_error = e
                self.stats.requests_failed += 1
                logger.error(
                    f"Unexpected error (attempt {error_attempts}/{self.max_retries}): {e}"
                )
                await asyncio.sleep(2**error_attempts)

        logger.error(
            f"All retries exhausted for {url.split('?')[0]}: "
            f"errors={error_attempts}, 429s={rate_limit_hits}, last_error={last_error}"
        )
        return None

    async def download_file(self, url: str, save_path: str) -> bool:
        """下载文件（如 PDF），带流式写入"""
        if self._cancelled:
            return False

        self._rotate_ua()
        self.stats.requests_total += 1

        try:
            await self._smart_delay()
            async with self.client.stream("GET", url) as resp:
                if resp.status_code != 200:
                    self.stats.requests_failed += 1
                    logger.warning(f"Download failed {resp.status_code}: {url}")
                    return False

                import aiofiles

                async with aiofiles.open(save_path, "wb") as f:
                    async for chunk in resp.aiter_bytes(chunk_size=8192):
                        await f.write(chunk)

            self.stats.requests_success += 1
            logger.info(f"Downloaded: {save_path}")
            return True

        except Exception as e:
            self.stats.requests_failed += 1
            logger.error(f"Download error: {e}")
            return False

    @abstractmethod
    async def search_papers(
        self,
        query: str,
        year_from: int = 2016,
        year_to: int = 2026,
        min_citations: int = 100,
        limit: int = 100,
    ) -> list[PaperMeta]:
        """搜索论文"""
        ...

    @abstractmethod
    async def get_paper_details(self, paper_id: str) -> PaperMeta | None:
        """获取论文详情"""
        ...
