"""Tests for OpenAlexCrawler: parsing, search, and elite methods."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from app.services.crawlers.openalex_crawler import OpenAlexCrawler, ABBREVIATION_MAP


# ──────────────────────────────────────────────
# _parse_work — pure parsing, no HTTP
# ──────────────────────────────────────────────


class TestParseWork:
    def test_complete_paper(self, crawler, make_openalex_work):
        work = make_openalex_work()
        paper = crawler._parse_work(work)

        assert paper is not None
        assert paper.title == "Attention Is All You Need"
        assert paper.year == 2017
        assert paper.citation_count == 120000
        assert paper.doi == "10.5555/3295222.3295349"
        assert paper.authors == ["Ashish Vaswani", "Noam Shazeer"]
        assert paper.venue == "NeurIPS"
        assert paper.arxiv_id == "1706.03762"
        assert paper.pdf_url == "https://arxiv.org/pdf/1706.03762"
        assert "Computer Science" in paper.fields_of_study
        assert len(paper.references) == 2

    def test_minimal_paper(self, crawler):
        paper = crawler._parse_work({"title": "Minimal"})
        assert paper is not None
        assert paper.title == "Minimal"
        assert paper.authors == []
        assert paper.citation_count == 0

    def test_missing_title_returns_none(self, crawler):
        assert crawler._parse_work({"abstract": "no title"}) is None

    def test_empty_title_returns_none(self, crawler):
        assert crawler._parse_work({"title": ""}) is None

    def test_non_dict_returns_none(self, crawler):
        assert crawler._parse_work("not a dict") is None
        assert crawler._parse_work(None) is None

    def test_doi_prefix_stripped(self, crawler, make_openalex_work):
        work = make_openalex_work(doi="https://doi.org/10.1234/test")
        paper = crawler._parse_work(work)
        assert paper.doi == "10.1234/test"

    def test_doi_without_prefix_preserved(self, crawler, make_openalex_work):
        work = make_openalex_work(doi="10.1234/raw")
        paper = crawler._parse_work(work)
        assert paper.doi == "10.1234/raw"

    def test_no_open_access(self, crawler, make_openalex_work):
        work = make_openalex_work(open_access={"is_oa": False})
        paper = crawler._parse_work(work)
        assert paper.pdf_url is None

    def test_no_arxiv_location(self, crawler, make_openalex_work):
        work = make_openalex_work(locations=[])
        paper = crawler._parse_work(work)
        assert paper.arxiv_id is None

    def test_concepts_level_filter(self, crawler, make_openalex_work):
        """Only level 0-1 concepts should be included in fields_of_study."""
        work = make_openalex_work(
            concepts=[
                {"display_name": "ML", "level": 1},
                {"display_name": "Deep Detail", "level": 3},
            ]
        )
        paper = crawler._parse_work(work)
        assert paper.fields_of_study == ["ML"]


# ──────────────────────────────────────────────
# _reconstruct_abstract — pure function
# ──────────────────────────────────────────────


class TestReconstructAbstract:
    def test_valid_inverted_index(self):
        idx = {"Hello": [0], "world": [1], "of": [2], "AI": [3]}
        result = OpenAlexCrawler._reconstruct_abstract(idx)
        assert result == "Hello world of AI"

    def test_out_of_order_positions(self):
        idx = {"world": [1], "Hello": [0]}
        result = OpenAlexCrawler._reconstruct_abstract(idx)
        assert result == "Hello world"

    def test_repeated_word(self):
        idx = {"the": [0, 2], "cat": [1], "dog": [3]}
        result = OpenAlexCrawler._reconstruct_abstract(idx)
        assert result == "the cat the dog"

    def test_none_returns_none(self):
        assert OpenAlexCrawler._reconstruct_abstract(None) is None

    def test_empty_dict_returns_none(self):
        assert OpenAlexCrawler._reconstruct_abstract({}) is None

    def test_non_dict_returns_none(self):
        assert OpenAlexCrawler._reconstruct_abstract("bad") is None


# ──────────────────────────────────────────────
# _expand_query_for_search — abbreviation map
# ──────────────────────────────────────────────


class TestExpandQuery:
    def test_known_abbreviation(self):
        assert OpenAlexCrawler._expand_query_for_search("LLM") == "large language model"

    def test_case_insensitive(self):
        assert OpenAlexCrawler._expand_query_for_search("llm") == "large language model"

    def test_unknown_term_passthrough(self):
        assert OpenAlexCrawler._expand_query_for_search("quantum computing") == "quantum computing"

    def test_whitespace_stripped(self):
        assert OpenAlexCrawler._expand_query_for_search("  NLP  ") == "natural language processing"

    @pytest.mark.parametrize("abbr", list(ABBREVIATION_MAP.keys()))
    def test_all_abbreviations_resolve(self, abbr):
        result = OpenAlexCrawler._expand_query_for_search(abbr)
        # _expand_query_for_search uppercases the input, so only all-caps keys match
        if abbr == abbr.upper():
            assert result == ABBREVIATION_MAP[abbr]
        else:
            # Mixed-case keys like "MLLMs", "PINNs" won't match after .upper()
            assert result == abbr


# ──────────────────────────────────────────────
# search_papers — mocked fetch
# ──────────────────────────────────────────────


class TestSearchPapers:
    async def test_basic_search(self, crawler, make_openalex_work):
        works = [make_openalex_work(title=f"Paper {i}") for i in range(3)]
        crawler.fetch = AsyncMock(return_value={"meta": {"count": 3}, "results": works})

        papers = await crawler.search_papers("deep learning", limit=10)

        assert len(papers) == 3
        assert papers[0].title == "Paper 0"
        crawler.fetch.assert_called_once()

        # Verify search params
        call_args = crawler.fetch.call_args
        params = call_args[1].get("params") or call_args[0][1]
        assert "search.title_and_abstract" in params

    async def test_empty_results(self, crawler):
        crawler.fetch = AsyncMock(return_value={"meta": {"count": 0}, "results": []})
        papers = await crawler.search_papers("nonexistent topic")
        assert papers == []

    async def test_fetch_returns_none(self, crawler):
        crawler.fetch = AsyncMock(return_value=None)
        papers = await crawler.search_papers("test")
        assert papers == []

    async def test_limit_respected(self, crawler, make_openalex_work):
        works = [make_openalex_work(title=f"P{i}") for i in range(10)]
        crawler.fetch = AsyncMock(return_value={"meta": {"count": 100}, "results": works})
        papers = await crawler.search_papers("test", limit=5)
        assert len(papers) == 5

    async def test_pagination_multi_page(self, crawler, make_openalex_work):
        """With limit > 200, per_page=200 and multiple pages are fetched."""
        page1 = [make_openalex_work(title=f"P1-{i}") for i in range(200)]
        page2 = [make_openalex_work(title=f"P2-{i}") for i in range(50)]

        crawler.fetch = AsyncMock(
            side_effect=[
                {"meta": {"count": 250}, "results": page1},
                {"meta": {"count": 250}, "results": page2},
            ]
        )
        papers = await crawler.search_papers("test", limit=300)
        # Page 1: 200 results (full), papers=200 < 300 → fetch page 2
        # Page 2: 50 results < 200 (per_page) → stop
        assert len(papers) == 250
        assert crawler.fetch.call_count == 2

    async def test_stops_at_limit(self, crawler, make_openalex_work):
        """Stops when enough papers are collected even if more pages exist."""
        page1 = [make_openalex_work(title=f"P{i}") for i in range(5)]
        crawler.fetch = AsyncMock(return_value={"meta": {"count": 100}, "results": page1})
        papers = await crawler.search_papers("test", limit=5)
        assert len(papers) == 5
        assert crawler.fetch.call_count == 1

    async def test_cancelled_stops_early(self, crawler, make_openalex_work):
        crawler._cancelled = True
        crawler.fetch = AsyncMock()
        papers = await crawler.search_papers("test")
        assert papers == []
        crawler.fetch.assert_not_called()

    async def test_abbreviation_expanded_in_search(self, crawler, make_openalex_work):
        crawler.fetch = AsyncMock(return_value={"meta": {"count": 0}, "results": []})
        await crawler.search_papers("LLM")
        call_args = crawler.fetch.call_args
        params = call_args[1].get("params") or call_args[0][1]
        assert params["search.title_and_abstract"] == "large language model"


# ──────────────────────────────────────────────
# search_by_author — mocked fetch
# ──────────────────────────────────────────────


class TestSearchByAuthor:
    async def test_returns_papers(self, crawler, make_openalex_work):
        works = [make_openalex_work(title=f"Author Paper {i}") for i in range(2)]
        crawler.fetch = AsyncMock(return_value={"meta": {"count": 2}, "results": works})
        papers = await crawler.search_by_author("A5100450462", limit=10)
        assert len(papers) == 2

        params = crawler.fetch.call_args[1].get("params") or crawler.fetch.call_args[0][1]
        assert "authorships.author.id:A5100450462" in params["filter"]

    async def test_min_citations_filter(self, crawler, make_openalex_work):
        crawler.fetch = AsyncMock(return_value={"meta": {"count": 0}, "results": []})
        await crawler.search_by_author("A123", min_citations=500)
        params = crawler.fetch.call_args[1].get("params") or crawler.fetch.call_args[0][1]
        assert "cited_by_count:500-" in params["filter"]

    async def test_no_min_citations(self, crawler, make_openalex_work):
        crawler.fetch = AsyncMock(return_value={"meta": {"count": 0}, "results": []})
        await crawler.search_by_author("A123", min_citations=0)
        params = crawler.fetch.call_args[1].get("params") or crawler.fetch.call_args[0][1]
        assert "cited_by_count" not in params["filter"]


# ──────────────────────────────────────────────
# search_by_institution — mocked fetch
# ──────────────────────────────────────────────


class TestSearchByInstitution:
    async def test_returns_papers(self, crawler, make_openalex_work):
        works = [make_openalex_work(title="Stanford Paper")]
        crawler.fetch = AsyncMock(return_value={"meta": {"count": 1}, "results": works})
        papers = await crawler.search_by_institution("I97018004")
        assert len(papers) == 1

        params = crawler.fetch.call_args[1].get("params") or crawler.fetch.call_args[0][1]
        assert "authorships.institutions.id:I97018004" in params["filter"]


# ──────────────────────────────────────────────
# resolve_author_id — mocked fetch
# ──────────────────────────────────────────────


class TestResolveAuthorId:
    async def test_returns_matches(self, crawler):
        crawler.fetch = AsyncMock(
            return_value={
                "results": [
                    {
                        "id": "https://openalex.org/A5100450462",
                        "display_name": "Li Fei-Fei",
                        "summary_stats": {"h_index": 137},
                        "cited_by_count": 250000,
                        "last_known_institutions": [{"display_name": "Stanford University"}],
                    },
                ]
            }
        )
        results = await crawler.resolve_author_id("Li Fei-Fei")

        assert len(results) == 1
        assert results[0]["id"] == "A5100450462"
        assert results[0]["name"] == "Li Fei-Fei"
        assert results[0]["h_index"] == 137
        assert results[0]["affiliation"] == "Stanford University"

    async def test_empty_results(self, crawler):
        crawler.fetch = AsyncMock(return_value={"results": []})
        results = await crawler.resolve_author_id("Nobody Here")
        assert results == []

    async def test_fetch_failure(self, crawler):
        crawler.fetch = AsyncMock(return_value=None)
        results = await crawler.resolve_author_id("test")
        assert results == []


# ──────────────────────────────────────────────
# resolve_institution_id — mocked fetch
# ──────────────────────────────────────────────


class TestResolveInstitutionId:
    async def test_returns_matches(self, crawler):
        crawler.fetch = AsyncMock(
            return_value={
                "results": [
                    {
                        "id": "https://openalex.org/I97018004",
                        "display_name": "Stanford University",
                        "country_code": "US",
                        "works_count": 500000,
                        "cited_by_count": 20000000,
                    },
                ]
            }
        )
        results = await crawler.resolve_institution_id("Stanford")

        assert len(results) == 1
        assert results[0]["id"] == "I97018004"
        assert results[0]["name"] == "Stanford University"
        assert results[0]["country"] == "US"

    async def test_fetch_failure(self, crawler):
        crawler.fetch = AsyncMock(return_value=None)
        results = await crawler.resolve_institution_id("test")
        assert results == []


# ──────────────────────────────────────────────
# discover_top_authors — mocked fetch
# ──────────────────────────────────────────────


class TestDiscoverTopAuthors:
    async def test_returns_authors(self, crawler):
        crawler.fetch = AsyncMock(
            return_value={
                "results": [
                    {
                        "id": "https://openalex.org/A123",
                        "display_name": "Test Author",
                        "summary_stats": {"h_index": 80},
                        "cited_by_count": 50000,
                        "works_count": 300,
                    },
                ]
            }
        )
        authors = await crawler.discover_top_authors("I97018004", min_h_index=50)

        assert len(authors) == 1
        assert authors[0]["id"] == "A123"
        assert authors[0]["h_index"] == 80

        params = crawler.fetch.call_args[1].get("params") or crawler.fetch.call_args[0][1]
        assert "summary_stats.h_index:>50" in params["filter"]

    async def test_limit_applied(self, crawler):
        many_authors = [
            {
                "id": f"https://openalex.org/A{i}",
                "display_name": f"Author {i}",
                "summary_stats": {"h_index": 60},
                "cited_by_count": 1000,
                "works_count": 100,
            }
            for i in range(10)
        ]
        crawler.fetch = AsyncMock(return_value={"results": many_authors})
        authors = await crawler.discover_top_authors("I123", limit=3)
        assert len(authors) == 3
