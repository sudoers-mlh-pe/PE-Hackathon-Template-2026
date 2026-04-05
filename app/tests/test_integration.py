import pytest
from unittest.mock import patch
from flask import Flask, jsonify


@pytest.fixture
def app():
    test_app = Flask(__name__)
    test_app.config["TESTING"] = True

    @test_app.route("/health")
    def health():
        return jsonify(status="ok")

    from app.routes.shorten import shorten_bp
    from app.routes.redirect import redirect_bp

    test_app.register_blueprint(shorten_bp)
    test_app.register_blueprint(redirect_bp)

    return test_app


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
