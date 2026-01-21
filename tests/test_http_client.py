"""
Unit tests for ProlificHttpClient.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import requests

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from prolific_client.config import ProlificConfig
from prolific_client.http import ProlificHttpClient
from prolific_client.errors import (
    ProlificAPIError,
    ProlificAuthenticationError,
    ProlificNotFoundError,
    ProlificRateLimitError,
    ProlificServerError,
    ProlificConnectionError,
    ProlificTimeoutError
)


@pytest.fixture
def config():
    return ProlificConfig(
        base_url="https://api.prolific.test",
        token="test-token-123",
        default_workspace_id="ws-123",
        timeout_s=10,
        max_retries=2
    )


@pytest.fixture
def client(config):
    return ProlificHttpClient(config)


class TestProlificHttpClient:
    
    def test_client_initialization(self, config):
        client = ProlificHttpClient(config)
        assert client.config == config
        assert client.session is not None
    
    def test_context_manager(self, config):
        with ProlificHttpClient(config) as client:
            assert client.session is not None
        # Session should be closed after exiting context
    
    @patch('requests.Session.request')
    def test_successful_get_request(self, mock_request, client):
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "123", "name": "Test"}
        mock_response.content = b'{"id": "123"}'
        mock_request.return_value = mock_response
        
        result = client.get("/api/v1/test/")
        
        assert result == {"id": "123", "name": "Test"}
        mock_request.assert_called_once()
    
    @patch('requests.Session.request')
    def test_successful_post_request(self, mock_request, client):
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "456", "created": True}
        mock_response.content = b'{"id": "456"}'
        mock_request.return_value = mock_response
        
        result = client.post("/api/v1/test/", json={"name": "New Item"})
        
        assert result == {"id": "456", "created": True}
        assert mock_request.call_args[1]["json"] == {"name": "New Item"}
    
    @patch('requests.Session.request')
    def test_404_error(self, mock_request, client):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"error": "Not found"}
        mock_response.content = b'{"error": "Not found"}'
        mock_request.return_value = mock_response
        
        with pytest.raises(ProlificNotFoundError) as exc_info:
            client.get("/api/v1/nonexistent/")
        
        assert exc_info.value.status_code == 404
    
    @patch('requests.Session.request')
    def test_401_authentication_error(self, mock_request, client):
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": "Unauthorized"}
        mock_response.content = b'{"error": "Unauthorized"}'
        mock_request.return_value = mock_response
        
        with pytest.raises(ProlificAuthenticationError) as exc_info:
            client.get("/api/v1/test/")
        
        assert exc_info.value.status_code == 401
    
    @patch('requests.Session.request')
    @patch('time.sleep')  # Mock sleep to speed up tests
    def test_rate_limit_retry(self, mock_sleep, mock_request, client):
        # First call returns 429, second call succeeds
        mock_response_429 = Mock()
        mock_response_429.status_code = 429
        mock_response_429.json.return_value = {"error": "Rate limit exceeded"}
        mock_response_429.content = b'{"error": "Rate limit"}'
        
        mock_response_200 = Mock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = {"success": True}
        mock_response_200.content = b'{"success": true}'
        
        mock_request.side_effect = [mock_response_429, mock_response_200]
        
        result = client.get("/api/v1/test/")
        
        assert result == {"success": True}
        assert mock_request.call_count == 2
        assert mock_sleep.called  # Verify backoff was applied
    
    @patch('requests.Session.request')
    @patch('time.sleep')
    def test_server_error_retry(self, mock_sleep, mock_request, client):
        # First call returns 500, second call succeeds
        mock_response_500 = Mock()
        mock_response_500.status_code = 500
        mock_response_500.json.return_value = {"error": "Internal server error"}
        mock_response_500.content = b'{"error": "Server error"}'
        
        mock_response_200 = Mock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = {"success": True}
        mock_response_200.content = b'{"success": true}'
        
        mock_request.side_effect = [mock_response_500, mock_response_200]
        
        result = client.get("/api/v1/test/")
        
        assert result == {"success": True}
        assert mock_request.call_count == 2
    
    @patch('requests.Session.request')
    @patch('time.sleep')
    def test_max_retries_exceeded(self, mock_sleep, mock_request, client):
        # All calls return 500
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": "Server error"}
        mock_response.content = b'{"error": "Server error"}'
        mock_request.return_value = mock_response
        
        with pytest.raises(ProlificServerError):
            client.get("/api/v1/test/")
        
        # Should try initial + max_retries times
        assert mock_request.call_count == client.config.max_retries + 1
    
    @patch('requests.Session.request')
    def test_timeout_error(self, mock_request, client):
        mock_request.side_effect = requests.exceptions.Timeout("Connection timeout")
        
        with pytest.raises(ProlificTimeoutError):
            client.get("/api/v1/test/")
    
    @patch('requests.Session.request')
    def test_connection_error(self, mock_request, client):
        mock_request.side_effect = requests.exceptions.ConnectionError("Failed to connect")
        
        with pytest.raises(ProlificConnectionError):
            client.get("/api/v1/test/")
    
    def test_backoff_calculation(self, client):
        # Test backoff values (without jitter for predictability)
        backoffs = []
        for attempt in range(5):
            backoff = client._calculate_backoff(attempt)
            backoffs.append(backoff)
        
        # Should be roughly: 1, 2, 4, 8, 16 (with jitter)
        assert 0.75 <= backoffs[0] <= 1.25  # ~1s ±25%
        assert 1.5 <= backoffs[1] <= 2.5    # ~2s ±25%
        assert 3.0 <= backoffs[2] <= 5.0    # ~4s ±25%
    
    def test_credential_redaction(self, client):
        data = {
            "token": "secret-token",
            "api_key": "secret-key",
            "username": "public-user"
        }
        
        redacted = client._redact_sensitive_data(data)
        
        assert redacted["token"] == "***REDACTED***"
        assert redacted["api_key"] == "***REDACTED***"
        assert redacted["username"] == "public-user"
    
    @patch('requests.Session.request')
    def test_correlation_id_injection(self, mock_request, client):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_response.content = b'{}'
        mock_request.return_value = mock_response
        
        client.get("/api/v1/test/")
        
        # Check that correlation ID header was added
        call_kwargs = mock_request.call_args[1]
        assert 'X-Correlation-ID' in call_kwargs['headers']
        assert len(call_kwargs['headers']['X-Correlation-ID']) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
