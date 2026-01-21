"""
Custom exception classes for Prolific API client.
"""
from typing import Optional, Dict, Any


class ProlificAPIError(Exception):
    
    def __init__(
        self,
        status_code: int,
        message: str,
        payload: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None
    ):
        self.status_code = status_code
        self.message = message
        self.payload = payload or {}
        self.correlation_id = correlation_id
        
        error_msg = f"Prolific API Error {status_code}: {message}"
        if correlation_id:
            error_msg += f" [correlation_id: {correlation_id}]"
        
        super().__init__(error_msg)
    
    def __repr__(self) -> str:
        return (
            f"ProlificAPIError(status_code={self.status_code}, "
            f"message={self.message!r}, "
            f"correlation_id={self.correlation_id!r})"
        )


class ProlificAuthenticationError(ProlificAPIError):
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(status_code=401, message=message, **kwargs)


class ProlificAuthorizationError(ProlificAPIError):
    
    def __init__(self, message: str = "Access forbidden", **kwargs):
        super().__init__(status_code=403, message=message, **kwargs)


class ProlificNotFoundError(ProlificAPIError):
    
    def __init__(self, message: str = "Resource not found", **kwargs):
        super().__init__(status_code=404, message=message, **kwargs)


class ProlificRateLimitError(ProlificAPIError):
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None, **kwargs):
        super().__init__(status_code=429, message=message, **kwargs)
        self.retry_after = retry_after


class ProlificValidationError(ProlificAPIError):
    
    def __init__(self, message: str = "Validation error", **kwargs):
        status_code = kwargs.pop('status_code', 400)
        super().__init__(status_code=status_code, message=message, **kwargs)


class ProlificServerError(ProlificAPIError):
    
    def __init__(self, status_code: int = 500, message: str = "Server error", **kwargs):
        super().__init__(status_code=status_code, message=message, **kwargs)


class ProlificConnectionError(Exception):
    
    def __init__(self, message: str = "Failed to connect to Prolific API", original_error: Optional[Exception] = None):
        self.original_error = original_error
        super().__init__(message)


class ProlificTimeoutError(Exception):
    
    def __init__(self, message: str = "Request timed out", timeout_s: Optional[int] = None):
        self.timeout_s = timeout_s
        super().__init__(message)


def create_error_from_response(
    status_code: int,
    response_data: Optional[Dict[str, Any]] = None,
    correlation_id: Optional[str] = None
) -> ProlificAPIError:
    
    message = "Unknown error"
    
    if response_data:
        message = (
            response_data.get("error") or
            response_data.get("message") or
            response_data.get("detail") or
            str(response_data)
        )
    
    error_map = {
        401: ProlificAuthenticationError,
        403: ProlificAuthorizationError,
        404: ProlificNotFoundError,
        429: ProlificRateLimitError,
        400: ProlificValidationError,
        422: ProlificValidationError,
    }
    
    # Handle specific status codes
    if status_code in error_map:
        error_class = error_map[status_code]
        
        if status_code == 429:
            retry_after = response_data.get("retry_after") if response_data else None
            return error_class(message=message, retry_after=retry_after, payload=response_data, correlation_id=correlation_id)
        
        elif status_code in (400, 422):
            return error_class(message=message, status_code=status_code, payload=response_data, correlation_id=correlation_id)
        
        else:
            return error_class(message=message, payload=response_data, correlation_id=correlation_id)
    
    if 500 <= status_code < 600:
        return ProlificServerError(status_code=status_code, message=message, payload=response_data, correlation_id=correlation_id)
    
    # Default to base error
    return ProlificAPIError(status_code=status_code, message=message, payload=response_data, correlation_id=correlation_id)
