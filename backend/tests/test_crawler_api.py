"""Tests for crawler API endpoints."""

from __future__ import annotations

from unittest.mock import patch, AsyncMock


class TestHealthAndRoot:
    async def test_health(self, test_client):
        resp = await test_client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    async def test_root(self, test_client):
        resp = await test_client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert "name" in data
        assert "version" in data


class TestStartCrawl:
    @patch("app.api.crawler._run_crawl_background", new_callable=AsyncMock)
    async def test_creates_task_keyword(self, mock_bg, test_client):
        resp = await test_client.post(
            "/api/v1/crawler/start",
            json={
                "mode": "keyword",
                "domain": "computer_science",
                "subdomain": "deep learning",
                "min_citations": 100,
                "max_papers": 10,
            },
        )
        assert resp.status_code == 202
        data = resp.json()
        assert data["status"] == "queued"
        assert data["mode"] == "keyword"
        assert data["domain"] == "computer_science"

    @patch("app.api.crawler._run_crawl_background", new_callable=AsyncMock)
    async def test_creates_task_author(self, mock_bg, test_client):
        resp = await test_client.post(
            "/api/v1/crawler/start",
            json={
                "mode": "author",
                "author_id": "A5100450462",
            },
        )
        assert resp.status_code == 202
        data = resp.json()
        assert data["mode"] == "author"
        assert data["author_id"] == "A5100450462"

    @patch("app.api.crawler._run_crawl_background", new_callable=AsyncMock)
    async def test_creates_task_preset(self, mock_bg, test_client):
        resp = await test_client.post(
            "/api/v1/crawler/start",
            json={
                "mode": "elite_preset",
                "preset_name": "top_ai_labs",
            },
        )
        assert resp.status_code == 202
        data = resp.json()
        assert data["mode"] == "elite_preset"
        assert data["preset_name"] == "top_ai_labs"


class TestGetTask:
    @patch("app.api.crawler._run_crawl_background", new_callable=AsyncMock)
    async def test_get_existing_task(self, mock_bg, test_client):
        # Create a task first
        create_resp = await test_client.post(
            "/api/v1/crawler/start",
            json={"domain": "cs"},
        )
        task_id = create_resp.json()["id"]

        resp = await test_client.get(f"/api/v1/crawler/tasks/{task_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == task_id

    async def test_get_nonexistent_task(self, test_client):
        resp = await test_client.get("/api/v1/crawler/tasks/nonexistent")
        assert resp.status_code == 404


class TestListTasks:
    async def test_empty_list(self, test_client):
        resp = await test_client.get("/api/v1/crawler/tasks")
        assert resp.status_code == 200
        assert resp.json() == []

    @patch("app.api.crawler._run_crawl_background", new_callable=AsyncMock)
    async def test_list_after_create(self, mock_bg, test_client):
        await test_client.post(
            "/api/v1/crawler/start",
            json={"domain": "cs"},
        )
        await test_client.post(
            "/api/v1/crawler/start",
            json={"domain": "bio"},
        )

        resp = await test_client.get("/api/v1/crawler/tasks")
        assert resp.status_code == 200
        assert len(resp.json()) == 2


class TestElitePresets:
    async def test_list_presets(self, test_client):
        resp = await test_client.get("/api/v1/crawler/elite/presets")
        assert resp.status_code == 200
        data = resp.json()
        assert "top_ai_labs" in data
        assert "description" in data["top_ai_labs"]

    @patch("app.api.crawler.OpenAlexCrawler")
    async def test_search_authors(self, mock_cls, test_client):
        mock_crawler = AsyncMock()
        mock_crawler.resolve_author_id = AsyncMock(
            return_value=[
                {
                    "id": "A123",
                    "name": "Test",
                    "h_index": 50,
                    "affiliation": "MIT",
                    "cited_by_count": 1000,
                }
            ]
        )
        mock_crawler.__aenter__ = AsyncMock(return_value=mock_crawler)
        mock_crawler.__aexit__ = AsyncMock(return_value=False)
        mock_cls.return_value = mock_crawler

        resp = await test_client.get("/api/v1/crawler/elite/authors/search?q=Test")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["id"] == "A123"

    async def test_search_authors_short_query(self, test_client):
        resp = await test_client.get("/api/v1/crawler/elite/authors/search?q=a")
        assert resp.status_code == 400

    @patch("app.api.crawler.OpenAlexCrawler")
    async def test_search_institutions(self, mock_cls, test_client):
        mock_crawler = AsyncMock()
        mock_crawler.resolve_institution_id = AsyncMock(
            return_value=[
                {
                    "id": "I123",
                    "name": "MIT",
                    "country": "US",
                    "works_count": 500,
                    "cited_by_count": 1000,
                }
            ]
        )
        mock_crawler.__aenter__ = AsyncMock(return_value=mock_crawler)
        mock_crawler.__aexit__ = AsyncMock(return_value=False)
        mock_cls.return_value = mock_crawler

        resp = await test_client.get("/api/v1/crawler/elite/institutions/search?q=MIT")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    async def test_search_institutions_short_query(self, test_client):
        resp = await test_client.get("/api/v1/crawler/elite/institutions/search?q=M")
        assert resp.status_code == 400

    async def test_top_authors_invalid_id(self, test_client):
        resp = await test_client.get("/api/v1/crawler/elite/authors/top?institution_id=BAD123")
        assert resp.status_code == 400
