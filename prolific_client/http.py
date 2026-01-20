"""
HTTP client for Prolific API with retry logic and observability.
"""
import time
import uuid
import logging
from typing import Optional, Dict, Any, Literal
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import ProlificConfig
from .errors import (
    ProlificAPIError,
    ProlificConnectionError,
    ProlificTimeoutError,
    ProlificRateLimitError,
    ProlificServerError,
    create_error_from_response
)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProlificHttpClient:
    """
    HTTP client for Prolific API with retry logic and observability.
    
    Features:
    - Automatic retries for transient failures (429, 5xx)
    - Exponential backoff
    - Correlation ID tracking
    - Structured logging with credential redaction
    - Typed error handling
    """
    
    def __init__(self, config: ProlificConfig):
        """
        Initialize HTTP client.
        
        Args:
            config: Prolific configuration
        """
        self.config = config
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """
        Create requests session with retry configuration.
        
        Returns:
            Configured requests.Session
        """
        session = requests.Session()
        
        # Configure retry strategy
        # We'll handle retries manually for better control over backoff
        # But set up basic adapter for connection pooling
        adapter = HTTPAdapter(
            pool_connections=10,
            pool_maxsize=10,
            max_retries=0
        )
        
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        return session
    
    def _calculate_backoff(self, attempt: int) -> float:
        """
        Calculate exponential backoff delay.
        
        Args:
            attempt: Current retry attempt (0-indexed)
        
        Returns:
            Delay in seconds
        """
        # Exponential backoff: 1s, 2s, 4s, 8s, ...
        base_delay = 1.0
        max_delay = 60.0
        
        delay = min(base_delay * (2 ** attempt), max_delay)
        
        # Add jitter (±25%)
        import random
        jitter = delay * 0.25 * (2 * random.random() - 1)
        
        return delay + jitter
    
    def _should_retry(self, error: Exception, attempt: int) -> bool:
        """
        Determine if request should be retried.
        
        Args:
            error: Exception that occurred
            attempt: Current attempt number (0-indexed)
        
        Returns:
            True if should retry, False otherwise
        """
        if attempt >= self.config.max_retries:
            return False
        
        # Retry on rate limits (429)
        if isinstance(error, ProlificRateLimitError):
            return True
        
        # Retry on server errors (5xx)
        if isinstance(error, ProlificServerError):
            return True
        
        if isinstance(error, (ProlificConnectionError, ProlificTimeoutError)):
            return True
        
        return False
    
    def _redact_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Redact sensitive information from data for logging.
        
        Args:
            data: Dictionary that may contain sensitive data
        
        Returns:
            Dictionary with sensitive fields redacted
        """
        if not data:
            return data
        
        redacted = data.copy()
        sensitive_keys = {'token', 'password', 'api_key', 'secret', 'authorization'}
        
        for key in redacted:
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                redacted[key] = "***REDACTED***"
        
        return redacted
    
    def _request(
        self,
        method: Literal["GET", "POST", "PATCH", "DELETE", "PUT"],
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to Prolific API with retry logic.
        
        Args:
            method: HTTP method
            path: API path (e.g., "/api/v1/workspaces/")
            params: Query parameters
            json: JSON request body
            correlation_id: Optional correlation ID for tracking
        
        Returns:
            Response JSON data
        
        Raises:
            ProlificAPIError: On API errors
            ProlificConnectionError: On connection failures
            ProlificTimeoutError: On timeout
        """
        if correlation_id is None:
            correlation_id = str(uuid.uuid4())
        
        url = f"{self.config.base_url}{path}"
        
        headers = self.config.get_headers()
        headers['X-Correlation-ID'] = correlation_id
        
        logger.info(
            f"[{correlation_id}] {method} {path}",
            extra={
                'correlation_id': correlation_id,
                'method': method,
                'path': path,
                'params': self._redact_sensitive_data(params or {}),
                'token': self.config.redacted_token()
            }
        )
        
        attempt = 0
        last_error = None
        
        while attempt <= self.config.max_retries:
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json,
                    timeout=self.config.timeout_s
                )
                
                logger.info(
                    f"[{correlation_id}] Response: {response.status_code}",
                    extra={
                        'correlation_id': correlation_id,
                        'status_code': response.status_code,
                        'attempt': attempt
                    }
                )
                
                if 200 <= response.status_code < 300:
                    try:
                        return response.json() if response.content else {}
                    except ValueError:
                        return {"status": "success", "raw_response": response.text}
                
                try:
                    error_data = response.json() if response.content else None
                except ValueError:
                    error_data = {"raw_response": response.text}
                
                error = create_error_from_response(
                    status_code=response.status_code,
                    response_data=error_data,
                    correlation_id=correlation_id
                )
                
                if self._should_retry(error, attempt):
                    last_error = error
                    backoff = self._calculate_backoff(attempt)
                    
                    if isinstance(error, ProlificRateLimitError) and error.retry_after:
                        backoff = max(backoff, error.retry_after)
                    
                    logger.warning(
                        f"[{correlation_id}] Retrying after {backoff:.2f}s (attempt {attempt + 1}/{self.config.max_retries})",
                        extra={
                            'correlation_id': correlation_id,
                            'error': str(error),
                            'backoff_seconds': backoff,
                            'attempt': attempt
                        }
                    )
                    
                    time.sleep(backoff)
                    attempt += 1
                    continue
                
                logger.error(
                    f"[{correlation_id}] API error: {error}",
                    extra={
                        'correlation_id': correlation_id,
                        'error': str(error),
                        'status_code': response.status_code
                    }
                )
                raise error
            
            except requests.exceptions.Timeout as e:
                last_error = ProlificTimeoutError(
                    f"Request timed out after {self.config.timeout_s}s",
                    timeout_s=self.config.timeout_s
                )
                
                if self._should_retry(last_error, attempt):
                    backoff = self._calculate_backoff(attempt)
                    logger.warning(
                        f"[{correlation_id}] Timeout, retrying after {backoff:.2f}s",
                        extra={'correlation_id': correlation_id, 'attempt': attempt}
                    )
                    time.sleep(backoff)
                    attempt += 1
                    continue
                
                logger.error(f"[{correlation_id}] Timeout: {e}")
                raise last_error
            
            except requests.exceptions.RequestException as e:
                last_error = ProlificConnectionError(
                    f"Connection error: {str(e)}",
                    original_error=e
                )
                
                if self._should_retry(last_error, attempt):
                    backoff = self._calculate_backoff(attempt)
                    logger.warning(
                        f"[{correlation_id}] Connection error, retrying after {backoff:.2f}s",
                        extra={'correlation_id': correlation_id, 'attempt': attempt}
                    )
                    time.sleep(backoff)
                    attempt += 1
                    continue
                
                logger.error(f"[{correlation_id}] Connection error: {e}")
                raise last_error
        
        logger.error(
            f"[{correlation_id}] Max retries exceeded",
            extra={'correlation_id': correlation_id, 'max_retries': self.config.max_retries}
        )
        raise last_error
    
    def get(self, path: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Convenience method for GET requests."""
        return self._request("GET", path, params=params, **kwargs)
    
    def post(self, path: str, json: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Convenience method for POST requests."""
        return self._request("POST", path, json=json, **kwargs)
    
    def patch(self, path: str, json: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Convenience method for PATCH requests."""
        return self._request("PATCH", path, json=json, **kwargs)
    
    def delete(self, path: str, **kwargs) -> Dict[str, Any]:
        """Convenience method for DELETE requests."""
        return self._request("DELETE", path, **kwargs)
    
    def close(self):
        """Close the HTTP session."""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
