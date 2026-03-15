import logging

from app.services.crawlers.base import BaseCrawler, PaperMeta

logger = logging.getLogger(__name__)

OPENALEX_API_BASE = "https://api.openalex.org"

# 常见缩写到全称的映射，用于提升搜索相关性
ABBREVIATION_MAP = {
    "LLM": "large language model",
    "NLP": "natural language processing",
    "CV": "computer vision",
    "RL": "reinforcement learning",
    "GNN": "graph neural network",
    "GAN": "generative adversarial network",
    "CNN": "convolutional neural network",
    "RNN": "recurrent neural network",
    "BERT": "bidirectional encoder representations transformers",
    "GPT": "generative pre-trained transformer",
    "VAE": "variational autoencoder",
    "RAG": "retrieval augmented generation",
    "RLHF": "reinforcement learning human feedback",
    "VLM": "vision language model",
    "MLLMs": "multimodal large language models",
    "AGI": "artificial general intelligence",
    "NAS": "neural architecture search",
    "SSL": "self-supervised learning",
    "PINN": "physics-informed neural network",
    "PINNs": "physics-informed neural networks",
}


class OpenAlexCrawler(BaseCrawler):
    """OpenAlex API 爬虫

    完全免费开放的学术数据源，数据量大，引用关系完整。
    无需 API Key，但建议在请求中包含 mailto 参数以获得更快的响应。
    """

    def __init__(self, email: str = "", rate_limit: float = 1.0):
        super().__init__(rate_limit=rate_limit, rate_jitter=0.3, use_browser_headers=False)
        self.email = email  # 用于 polite pool

    async def search_papers(
        self, query: str, year_from: int = 2016, year_to: int = 2026,
        min_citations: int = 100, limit: int = 100,
    ) -> list[PaperMeta]:
        """搜索高被引论文（使用 OpenAlex 官方 search.title_and_abstract 参数）"""
        papers = []
        page = 1
        per_page = min(limit, 200)

        # 缩写展开：LLM → "LLM large language model"
        search_query = self._expand_query_for_search(query)

        while len(papers) < limit:
            if self.is_cancelled:
                break

            # 使用 OpenAlex 官方格式：search.title_and_abstract + filter
            filter_parts = [
                f"publication_year:{year_from}-{year_to}",
                f"cited_by_count:{min_citations}-",  # X- 表示 >=X
                "type:article",
            ]

            filter_str = ",".join(filter_parts)
            params = {
                "search.title_and_abstract": search_query,
                "filter": filter_str,
                "sort": "cited_by_count:desc",
                "per_page": str(per_page),
                "page": str(page),
            }

            if self.email:
                params["mailto"] = self.email

            logger.info(f"[OpenAlex] search.title_and_abstract={search_query}&filter={filter_str}&sort=cited_by_count:desc&per_page={per_page}&page={page}")
            data = await self.fetch(f"{OPENALEX_API_BASE}/works", params=params)

            if not data or "results" not in data:
                break

            results = data["results"]
            if not results:
                break

            for item in results:
                paper = self._parse_work(item)
                if paper:
                    papers.append(paper)

            total = data.get("meta", {}).get("count", 0)
            page += 1

            logger.info(
                f"[OpenAlex] '{query}': fetched {len(papers)}/{min(total, limit)} papers"
            )

            if len(results) < per_page or len(papers) >= limit:
                break

        return papers[:limit]

    async def get_paper_details(self, paper_id: str) -> PaperMeta | None:
        """通过 OpenAlex ID 获取论文详情"""
        params = {}
        if self.email:
            params["mailto"] = self.email

        data = await self.fetch(f"{OPENALEX_API_BASE}/works/{paper_id}", params=params)
        if not data:
            return None
        return self._parse_work(data)

    async def get_references(self, openalex_id: str, limit: int = 100) -> list[str]:
        """获取论文的参考文献 OpenAlex ID 列表"""
        params = {
            "filter": f"cites:{openalex_id}",
            "per_page": str(min(limit, 200)),
            "select": "id",
        }
        if self.email:
            params["mailto"] = self.email

        data = await self.fetch(f"{OPENALEX_API_BASE}/works", params=params)
        if not data or "results" not in data:
            return []
        return [w["id"] for w in data["results"] if w.get("id")]

    def _parse_work(self, data: dict) -> PaperMeta | None:
        """解析 OpenAlex work 对象"""
        if not isinstance(data, dict):
            return None

        title = data.get("title")
        if not title:
            return None

        # 提取作者
        authors = []
        for authorship in data.get("authorships") or []:
            author = authorship.get("author", {})
            name = author.get("display_name")
            if name:
                authors.append(name)

        # 提取 DOI
        doi = data.get("doi")
        if doi and doi.startswith("https://doi.org/"):
            doi = doi[len("https://doi.org/"):]

        # 提取外部 ID
        ids = data.get("ids") or {}
        openalex_id = ids.get("openalex") or data.get("id")

        # 提取 arXiv ID（如果有）
        arxiv_id = None
        locations = data.get("locations") or []
        for loc in locations:
            source = loc.get("source") or {}
            if "arxiv" in (source.get("display_name") or "").lower():
                landing_url = loc.get("landing_page_url") or ""
                if "/abs/" in landing_url:
                    arxiv_id = landing_url.split("/abs/")[-1]

        # 提取开放获取 PDF
        pdf_url = None
        oa = data.get("open_access") or {}
        if oa.get("is_oa"):
            pdf_url = oa.get("oa_url")

        # 提取发表场所
        venue = None
        primary_loc = data.get("primary_location") or {}
        source = primary_loc.get("source") or {}
        venue = source.get("display_name")

        # 提取领域
        fields = []
        for concept in data.get("concepts") or []:
            if concept.get("level", 99) <= 1 and concept.get("display_name"):
                fields.append(concept["display_name"])

        # 引用关系 ID 列表
        references = []
        for ref_id in data.get("referenced_works") or []:
            if ref_id:
                references.append(ref_id)

        def safe_int(val, default=0):
            try:
                return int(val) if val is not None else default
            except (ValueError, TypeError):
                return default

        return PaperMeta(
            title=title.strip(),
            abstract=self._reconstruct_abstract(data.get("abstract_inverted_index")),
            authors=authors[:20],
            year=safe_int(data.get("publication_year"), None),
            venue=venue,
            doi=doi,
            arxiv_id=arxiv_id,
            s2_id=None,
            url=openalex_id,
            pdf_url=pdf_url,
            citation_count=safe_int(data.get("cited_by_count"), 0),
            influential_citation_count=0,  # OpenAlex 不提供此指标
            references=references[:200],
            fields_of_study=fields,
        )

    @staticmethod
    def _reconstruct_abstract(inverted_index: dict | None) -> str | None:
        """从 OpenAlex 倒排索引重建摘要文本"""
        if not inverted_index or not isinstance(inverted_index, dict):
            return None

        try:
            word_positions = []
            for word, positions in inverted_index.items():
                for pos in positions:
                    word_positions.append((pos, word))
            word_positions.sort()
            return " ".join(w for _, w in word_positions)
        except Exception:
            return None

    @staticmethod
    def _expand_query_for_search(query: str) -> str:
        """展开查询：如果输入是常见缩写，扩展为 '缩写 全称' 提升搜索召回率
        用于 search.title_and_abstract 参数（不支持 | 语法，使用空格连接）"""
        q = query.strip()
        expanded = ABBREVIATION_MAP.get(q.upper())
        if expanded:
            return f"{q} {expanded}"
        return q
