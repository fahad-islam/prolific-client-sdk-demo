"""
Unit tests for error handling.
"""
import pytest

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from prolific_client.errors import (
    ProlificAPIError,
    ProlificAuthenticationError,
    ProlificAuthorizationError,
    ProlificNotFoundError,
    ProlificRateLimitError,
    ProlificValidationError,
    ProlificServerError,
    create_error_from_response
)


class TestProlificAPIError:
    
    def test_basic_error(self):
        error = ProlificAPIError(
            status_code=400,
            message="Bad request"
        )
        
        assert error.status_code == 400
        assert error.message == "Bad request"
        assert error.payload == {}
        assert error.correlation_id is None
    
    def test_error_with_payload(self):
        payload = {"field": "email", "error": "Invalid format"}
        error = ProlificAPIError(
            status_code=422,
            message="Validation failed",
            payload=payload
        )
        
        assert error.payload == payload
    
    def test_error_with_correlation_id(self):
        error = ProlificAPIError(
            status_code=500,
            message="Server error",
            correlation_id="abc-123"
        )
        
        assert error.correlation_id == "abc-123"
        assert "abc-123" in str(error)
    
    def test_error_string_representation(self):
        error = ProlificAPIError(
            status_code=404,
            message="Not found",
            correlation_id="xyz-789"
        )
        
        error_str = str(error)
        assert "404" in error_str
        assert "Not found" in error_str
        assert "xyz-789" in error_str


class TestSpecificErrors:
    
    def test_authentication_error(self):
        error = ProlificAuthenticationError()
        assert error.status_code == 401
        assert "Authentication failed" in error.message
    
    def test_authorization_error(self):
        error = ProlificAuthorizationError()
        assert error.status_code == 403
        assert "Access forbidden" in error.message
    
    def test_not_found_error(self):
        error = ProlificNotFoundError("Resource xyz not found")
        assert error.status_code == 404
        assert "xyz" in error.message
    
    def test_rate_limit_error(self):
        error = ProlificRateLimitError(retry_after=60)
        assert error.status_code == 429
        assert error.retry_after == 60
    
    def test_validation_error(self):
        error = ProlificValidationError("Invalid email format")
        assert error.status_code == 400
        assert "Invalid email" in error.message
    
    def test_server_error(self):
        error = ProlificServerError(status_code=503)
        assert error.status_code == 503
        assert "Server error" in error.message


class TestErrorFactory:
    
    def test_create_404_error(self):
        error = create_error_from_response(
            status_code=404,
            response_data={"error": "Project not found"}
        )
        
        assert isinstance(error, ProlificNotFoundError)
        assert "Project not found" in error.message
    
    def test_create_401_error(self):
        error = create_error_from_response(
            status_code=401,
            response_data={"error": "Invalid token"}
        )
        
        assert isinstance(error, ProlificAuthenticationError)
        assert "Invalid token" in error.message
    
    def test_create_403_error(self):
        error = create_error_from_response(
            status_code=403,
            response_data={"error": "Insufficient permissions"}
        )
        
        assert isinstance(error, ProlificAuthorizationError)
    
    def test_create_429_error(self):
        error = create_error_from_response(
            status_code=429,
            response_data={"error": "Too many requests", "retry_after": 30}
        )
        
        assert isinstance(error, ProlificRateLimitError)
        assert error.retry_after == 30
    
    def test_create_validation_error_400(self):
        error = create_error_from_response(
            status_code=400,
            response_data={"detail": "Missing required field"}
        )
        
        assert isinstance(error, ProlificValidationError)
        assert error.status_code == 400
    
    def test_create_validation_error_422(self):
        error = create_error_from_response(
            status_code=422,
            response_data={"message": "Validation failed"}
        )
        
        assert isinstance(error, ProlificValidationError)
        assert error.status_code == 422
    
    def test_create_server_error_500(self):
        error = create_error_from_response(
            status_code=500,
            response_data={"error": "Internal server error"}
        )
        
        assert isinstance(error, ProlificServerError)
        assert error.status_code == 500
    
    def test_create_server_error_503(self):
        error = create_error_from_response(
            status_code=503,
            response_data={"error": "Service unavailable"}
        )
        
        assert isinstance(error, ProlificServerError)
        assert error.status_code == 503
    
    def test_create_generic_error(self):
        error = create_error_from_response(
            status_code=418,
            response_data={"error": "Teapot error"}
        )
        
        assert isinstance(error, ProlificAPIError)
        assert error.status_code == 418
        assert "Teapot" in error.message
    
    def test_create_error_no_response_data(self):
        error = create_error_from_response(status_code=500)
        
        assert isinstance(error, ProlificServerError)
        assert error.message == "Unknown error"
    
    def test_create_error_with_correlation_id(self):
        error = create_error_from_response(
            status_code=404,
            response_data={"error": "Not found"},
            correlation_id="test-123"
        )
        
        assert error.correlation_id == "test-123"
    
    def test_extract_message_from_different_fields(self):
        error1 = create_error_from_response(
            status_code=400,
            response_data={"error": "Error message"}
        )
        assert "Error message" in error1.message
        
        
        error2 = create_error_from_response(
            status_code=400,
            response_data={"message": "Message text"}
        )
        assert "Message text" in error2.message
        
        error3 = create_error_from_response(
            status_code=400,
            response_data={"detail": "Detail text"}
        )
        assert "Detail text" in error3.message


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
