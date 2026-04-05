import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture
def app():
    from app import create_app

    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    return app.test_client()


class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_json(self, client):
        response = client.get("/health")
        assert response.is_json
        assert response.json["status"] == "ok"


class TestShortenEndpoint:
    @patch("app.routes.shorten.redis")
    @patch("app.routes.shorten.URL")
    def test_shorten_valid_url_returns_200(self, mock_url, mock_redis, client):
        mock_redis.get.return_value = None
        mock_url.get_or_none.return_value = None
        mock_url.generate_code.return_value = "abc123"

        response = client.post("/shorten", json={"url": "https://example.com"})
        assert response.status_code == 201

    @patch("app.routes.shorten.redis")
    @patch("app.routes.shorten.URL")
    def test_shorten_returns_short_url(self, mock_url, mock_redis, client):
        mock_redis.get.return_value = None
        mock_url.get_or_none.return_value = None
        mock_url.generate_code.return_value = "abc123"

        response = client.post("/shorten", json={"url": "https://example.com"})
        assert response.status_code == 201
        assert "short_url" in response.json

    def test_shorten_missing_url_returns_400(self, client):
        response = client.post("/shorten", json={})
        assert response.status_code == 400
        assert response.json["error"] == "invalid URL"

    def test_shorten_invalid_url_returns_400(self, client):
        response = client.post("/shorten", json={"url": "not-a-valid-url"})
        assert response.status_code == 400

    def test_shorten_empty_url_returns_400(self, client):
        response = client.post("/shorten", json={"url": ""})
        assert response.status_code == 400


class TestRedirectEndpoint:
    @patch("app.routes.redirect.redis")
    @patch("app.routes.redirect.URL")
    def test_redirect_nonexistent_code_returns_404(self, mock_url, mock_redis, client):
        mock_redis.get.return_value = None

        mock_does_not_exist = type("DoesNotExist", (Exception,), {})
        mock_url.DoesNotExist = mock_does_not_exist
        mock_url.get.side_effect = mock_does_not_exist("DoesNotExist")

        response = client.get("/invalidcode123")
        assert response.status_code == 404


class TestShortenIntegration:
    def test_shorten_creates_db_entry(self, client):
        url = "https://integration-test-unique.com"
        response = client.post("/shorten", json={"url": url})

        assert response.status_code == 201
        assert "short_url" in response.json

        from app.models.url import URL
        entry = URL.get_or_none(URL.full_url == url)
        assert entry is not None
        assert entry.short_code is not None

    def test_shorten_duplicate_returns_same_code(self, client):
        url = "https://duplicate-integration-test.com"
        r1 = client.post("/shorten", json={"url": url})
        r2 = client.post("/shorten", json={"url": url})

        assert r1.json["short_url"] == r2.json["short_url"]

    def test_shorten_and_redirect(self, client):
        url = "https://redirect-integration-test.com"
        shorten_response = client.post("/shorten", json={"url": url})

        assert shorten_response.status_code == 201
        short_url = shorten_response.json["short_url"]
        code = short_url.split("/")[-1]

        redirect_response = client.get(f"/{code}")
        assert redirect_response.status_code == 302