import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from app.routes.redirect import redirect_bp

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = Flask(__name__)
    app.register_blueprint(redirect_bp)
    return app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

## --- Test Cases ---

@patch('app.routes.redirect.redis')
def test_redirect_cache_hit(mock_redis, client):
    """Test when the URL is found in Redis (Cache Hit)."""
    # Setup mock
    mock_redis.get.return_value = "https://google.com"

    # Execute
    response = client.get('/goog')

    # Assert
    assert response.status_code == 302
    assert response.headers['Location'] == "https://google.com"
    mock_redis.get.assert_called_once_with('goog')

@patch('app.routes.redirect.URL')
@patch('app.routes.redirect.redis')
def test_redirect_cache_miss_db_hit(mock_redis, mock_url_model, client):
    """Test when Redis is empty but Postgres has the data (Cache Miss)."""
    # Setup mocks
    mock_redis.get.return_value = None
    
    mock_link = MagicMock()
    mock_link.full_url = "https://openai.com"
    mock_link.short_code = "ai"
    mock_url_model.get.return_value = mock_link

    # Execute
    response = client.get('/ai')

    # Assert
    assert response.status_code == 302
    assert response.headers['Location'] == "https://openai.com"
    
    # Verify it saved back to Redis
    mock_redis.setex.assert_any_call('ai', 3600, "https://openai.com")
    mock_url_model.get.assert_called()

@patch('app.routes.redirect.URL')
@patch('app.routes.redirect.redis')
def test_redirect_not_found(mock_redis, mock_url_model, client):
    """Test when neither Redis nor Postgres has the code (404)."""
    from app.models.url import URL # Import for the Exception
    
    # Setup mocks
    mock_redis.get.return_value = None
    mock_url_model.DoesNotExist = URL.DoesNotExist # Ensure mock handles the exception class
    mock_url_model.get.side_effect = URL.DoesNotExist

    # Execute
    response = client.get('/badcode')

    # Assert
    assert response.status_code == 404
    assert b"URL not found" in response.data