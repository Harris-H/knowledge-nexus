"""
Shared fixtures for knowledge-nexus tests.

Design principles:
  - Factory fixtures return callables with overrides
  - Database uses in-memory SQLite (fast, isolated)
  - Crawler fixtures pre-configure mocked fetch() to avoid HTTP + rate-limit delays
  - New tests only need fixture additions; existing tests unaffected
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.database import Base, get_db
from app.services.crawlers.base import PaperMeta
from app.services.crawlers.openalex_crawler import OpenAlexCrawler


# ──────────────────────────────────────────────
# Database fixtures
# ──────────────────────────────────────────────


@pytest.fixture()
async def db_engine():
    """In-memory async SQLite engine with all tables created."""
    engine = create_async_engine("sqlite+aiosqlite://", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture()
async def db_session(db_engine):
    """Async database session for direct DB operations."""
    factory = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session


@pytest.fixture()
async def test_client(db_engine):
    """FastAPI test client with overridden DB dependency."""
    from httpx import AsyncClient, ASGITransport
    from app.main import app

    factory = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)

    async def _override_get_db():
        async with factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = _override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


# ──────────────────────────────────────────────
# Crawler fixtures
# ──────────────────────────────────────────────


@pytest.fixture()
def crawler() -> OpenAlexCrawler:
    """OpenAlexCrawler with mocked internals (no HTTP, no delay)."""
    c = OpenAlexCrawler(email="test@test.com", rate_limit=0)
    c._client = AsyncMock()
    return c


# ──────────────────────────────────────────────
# Test data factories
# ──────────────────────────────────────────────

_OPENALEX_WORK = {
    "id": "https://openalex.org/W2741809807",
    "title": "Attention Is All You Need",
    "publication_year": 2017,
    "cited_by_count": 120000,
    "doi": "https://doi.org/10.5555/3295222.3295349",
    "authorships": [
        {"author": {"display_name": "Ashish Vaswani"}},
        {"author": {"display_name": "Noam Shazeer"}},
    ],
    "ids": {"openalex": "https://openalex.org/W2741809807"},
    "open_access": {"is_oa": True, "oa_url": "https://arxiv.org/pdf/1706.03762"},
    "primary_location": {"source": {"display_name": "NeurIPS"}},
    "locations": [
        {
            "source": {"display_name": "arXiv"},
            "landing_page_url": "https://arxiv.org/abs/1706.03762",
        }
    ],
    "concepts": [
        {"display_name": "Computer Science", "level": 0},
        {"display_name": "Artificial Intelligence", "level": 1},
    ],
    "referenced_works": [
        "https://openalex.org/W1234",
        "https://openalex.org/W5678",
    ],
    "abstract_inverted_index": {
        "The": [0],
        "dominant": [1],
        "sequence": [2],
        "models": [3],
    },
}


@pytest.fixture()
def make_openalex_work():
    """Factory for OpenAlex work dicts with overrides."""

    def _factory(**overrides: Any) -> dict:
        data = {**_OPENALEX_WORK, **overrides}
        return data

    return _factory


@pytest.fixture()
def make_paper_meta():
    """Factory for PaperMeta objects with overrides."""

    def _factory(**overrides: Any) -> PaperMeta:
        defaults = {
            "title": "Test Paper",
            "abstract": "This is a test.",
            "authors": ["Author A"],
            "year": 2023,
            "citation_count": 100,
            "influential_citation_count": 10,
        }
        return PaperMeta(**{**defaults, **overrides})

    return _factory


def _openalex_search_response(works: list[dict], total: int | None = None) -> dict:
    """Build an OpenAlex /works search response."""
    return {
        "meta": {"count": total or len(works)},
        "results": works,
    }


def _openalex_authors_response(authors: list[dict]) -> dict:
    """Build an OpenAlex /authors search response."""
    return {
        "meta": {"count": len(authors)},
        "results": authors,
    }
