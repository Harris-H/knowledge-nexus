"""Tests for orchestrator helpers: impact scoring, crawler factory, elite presets."""

from __future__ import annotations

from datetime import datetime


from app.services.crawlers.orchestrator import (
    compute_impact_score,
    _create_crawler,
)
from app.services.crawlers.openalex_crawler import OpenAlexCrawler
from app.services.crawlers.semantic_scholar import SemanticScholarCrawler


class TestComputeImpactScore:
    def test_high_citation_paper(self, make_paper_meta):
        paper = make_paper_meta(
            citation_count=10000,
            influential_citation_count=1000,
            year=2020,
        )
        score = compute_impact_score(paper)
        assert score > 50
        assert score <= 100

    def test_zero_citation_paper(self, make_paper_meta):
        paper = make_paper_meta(citation_count=0, influential_citation_count=0, year=2020)
        score = compute_impact_score(paper)
        assert score >= 0
        assert score < 20

    def test_recent_paper_bonus(self, make_paper_meta):
        """Papers published within last 5 years get a recency bonus."""
        current_year = datetime.now().year
        recent = make_paper_meta(citation_count=500, year=current_year)
        old = make_paper_meta(citation_count=500, year=2010)

        score_recent = compute_impact_score(recent)
        score_old = compute_impact_score(old)
        assert score_recent > score_old

    def test_influential_citations_matter(self, make_paper_meta):
        high_influence = make_paper_meta(
            citation_count=1000, influential_citation_count=200, year=2020
        )
        low_influence = make_paper_meta(
            citation_count=1000, influential_citation_count=0, year=2020
        )
        assert compute_impact_score(high_influence) > compute_impact_score(low_influence)

    def test_score_range(self, make_paper_meta):
        """Score should always be 0-100."""
        # Extreme paper
        paper = make_paper_meta(
            citation_count=200000,
            influential_citation_count=50000,
            year=datetime.now().year,
        )
        score = compute_impact_score(paper)
        assert 0 <= score <= 100

    def test_none_year_uses_current(self, make_paper_meta):
        paper = make_paper_meta(citation_count=100, year=None)
        score = compute_impact_score(paper)
        assert score >= 0


class TestCreateCrawler:
    def test_default_openalex(self):
        crawler = _create_crawler()
        assert isinstance(crawler, OpenAlexCrawler)

    def test_openalex_explicit(self):
        crawler = _create_crawler("openalex")
        assert isinstance(crawler, OpenAlexCrawler)

    def test_semantic_scholar(self):
        crawler = _create_crawler("semantic_scholar")
        assert isinstance(crawler, SemanticScholarCrawler)
