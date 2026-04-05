import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from app.routes.shorten import shorten_bp

@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(shorten_bp)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

## --- Test Cases ---

@patch('app.routes.shorten.redis')
def test_shorten_invalid_url(mock_redis, client):
    """Test providing a junk URL returns 400."""
    response = client.post('/shorten', json={'url': 'not-a-url'})
    
    assert response.status_code == 200
    assert response.json['error'] == "invalid URL"

@patch('app.routes.shorten.redis')
def test_shorten_redis_hit(mock_redis, client):
    """Test when the long URL is already cached in Redis."""
    mock_redis.get.return_value = "abcde"
    
    response = client.post('/shorten', json={'url': 'https://google.com'})
    
    assert response.status_code == 200
    assert "abcde" in response.json['short_url']
    assert response.json['cached'] is True
    mock_redis.get.assert_called_with("long:https://google.com")

@patch('app.routes.shorten.URL')
@patch('app.routes.shorten.redis')
def test_shorten_db_hit(mock_redis, mock_url_model, client):
    """Test when Redis misses but the Database has the URL."""
    mock_redis.get.return_value = None
    
    # Mock the DB record found
    mock_entry = MagicMock()
    mock_entry.short_code = "db123"
    mock_url_model.get_or_none.return_value = mock_entry

    response = client.post('/shorten', json={'url': 'https://github.com'})

    assert response.status_code == 200
    assert "db123" in response.json['short_url']
    # Ensure it updated Redis after the DB hit
    mock_redis.setex.assert_any_call("long:https://github.com", 3600, "db123")

@patch('app.routes.shorten.URL')
@patch('app.routes.shorten.redis')
def test_shorten_new_creation(mock_redis, mock_url_model, client):
    """Test when the URL is completely new."""
    mock_redis.get.return_value = None
    mock_url_model.get_or_none.return_value = None
    mock_url_model.generate_code.return_value = "new789"

    response = client.post('/shorten', json={'url': 'https://python.org'})

    assert response.status_code == 201
    assert "new789" in response.json['short_url']
    
    # Verify the DB creation was called
    mock_url_model.create.assert_called_once_with(
        full_url='https://python.org', 
        short_code='new789'
    )