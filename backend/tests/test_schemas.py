"""Tests for Pydantic schemas: CrawlRequest and CrawlTaskResponse."""

from __future__ import annotations

from datetime import datetime


from app.schemas.schemas import CrawlRequest, CrawlTaskResponse


class TestCrawlRequest:
    def test_defaults(self):
        req = CrawlRequest()
        assert req.mode == "keyword"
        assert req.domain == "computer_science"
        assert req.source == "openalex"
        assert req.max_papers == 100
        assert req.min_citations == 0
        assert req.author_id is None
        assert req.institution_id is None
        assert req.preset_name is None

    def test_keyword_mode(self):
        req = CrawlRequest(
            mode="keyword",
            subdomain="deep learning",
            min_citations=500,
            max_papers=50,
        )
        assert req.mode == "keyword"
        assert req.subdomain == "deep learning"
        assert req.min_citations == 500

    def test_author_mode(self):
        req = CrawlRequest(mode="author", author_id="A5100450462")
        assert req.mode == "author"
        assert req.author_id == "A5100450462"

    def test_institution_mode(self):
        req = CrawlRequest(mode="institution", institution_id="I97018004")
        assert req.mode == "institution"
        assert req.institution_id == "I97018004"

    def test_preset_mode(self):
        req = CrawlRequest(mode="elite_preset", preset_name="top_ai_labs")
        assert req.mode == "elite_preset"
        assert req.preset_name == "top_ai_labs"

    def test_year_range(self):
        req = CrawlRequest(year_from=2020, year_to=2024)
        assert req.year_from == 2020
        assert req.year_to == 2024


class TestCrawlTaskResponse:
    def test_minimal(self):
        resp = CrawlTaskResponse(
            id="test123",
            status="queued",
            domain="computer_science",
            created_at=datetime(2024, 1, 1),
        )
        assert resp.id == "test123"
        assert resp.status == "queued"
        assert resp.mode == "keyword"
        assert resp.searched == 0
        assert resp.imported == 0

    def test_elite_fields(self):
        resp = CrawlTaskResponse(
            id="test456",
            status="running",
            mode="author",
            domain="computer_science",
            author_id="A5100450462",
            created_at=datetime(2024, 6, 1),
        )
        assert resp.mode == "author"
        assert resp.author_id == "A5100450462"
        assert resp.institution_id is None
