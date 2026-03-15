from datetime import datetime

from pydantic import BaseModel, Field


# ---- Paper ----

class PaperCreate(BaseModel):
    title: str
    abstract: str | None = None
    year: int | None = None
    venue: str | None = None
    domain_id: str | None = None
    authors: list[str] = []
    tags: list[str] = []
    url: str | None = None
    doi: str | None = None
    arxiv_id: str | None = None

class PaperUpdate(BaseModel):
    title: str | None = None
    abstract: str | None = None
    year: int | None = None
    venue: str | None = None
    domain_id: str | None = None
    key_contributions: list[str] | None = None

class PaperResponse(BaseModel):
    id: str
    title: str
    abstract: str | None = None
    year: int | None = None
    venue: str | None = None
    domain_id: str | None = None
    url: str | None = None
    doi: str | None = None
    arxiv_id: str | None = None
    s2_id: str | None = None
    citation_count: int = 0
    influential_citation_count: int = 0
    impact_score: float = 0.0
    key_contributions: str | None = None
    summary: str | None = None
    ai_status: str = "pending"
    pdf_path: str | None = None
    authors: list[str] = []
    created_at: datetime

    model_config = {"from_attributes": True}

class PaperList(BaseModel):
    items: list[PaperResponse]
    total: int
    page: int
    size: int


# ---- Graph ----

class GraphNode(BaseModel):
    id: str
    type: str  # paper / concept / domain
    label: str
    properties: dict = {}

class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    type: str  # CITES, IMPROVES, ANALOGOUS_TO ...
    properties: dict = {}

class SubgraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]

class RelationCreate(BaseModel):
    source_id: str
    target_id: str
    relation_type: str
    description: str | None = None
    confidence: float = 1.0


# ---- Crawler ----

class CrawlRequest(BaseModel):
    domain: str = "computer_science"
    subdomain: str | None = None
    year_from: int = 2016
    year_to: int = 2026
    min_citations: int = 500
    source: str = "openalex"  # openalex（默认，快速免费）/ semantic_scholar / arxiv
    max_papers: int = 100
    auto_download_pdf: bool = False

class CrawlTaskResponse(BaseModel):
    id: str
    status: str
    domain: str
    subdomain: str | None = None
    source: str = "openalex"
    searched: int = 0
    candidates: int = 0
    imported: int = 0
    failed: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


# ---- Search ----

class SearchRequest(BaseModel):
    q: str
    mode: str = "keyword"  # keyword / semantic / hybrid
    domain: str | None = None
    year_from: int | None = None
    year_to: int | None = None
    limit: int = 20

class SearchResult(BaseModel):
    id: str
    type: str
    title: str
    snippet: str | None = None
    score: float = 0.0

class SearchResponse(BaseModel):
    results: list[SearchResult]
    total: int
