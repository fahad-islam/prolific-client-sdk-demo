"""
Prolific API Client for Python.

A production-ready client for integrating with Prolific's v1 API.
"""
from .config import ProlificConfig
from .http import ProlificHttpClient
from .errors import (
    ProlificAPIError,
    ProlificAuthenticationError,
    ProlificAuthorizationError,
    ProlificNotFoundError,
    ProlificRateLimitError,
    ProlificValidationError,
    ProlificServerError,
    ProlificConnectionError,
    ProlificTimeoutError
)

__version__ = "0.1.0"
__all__ = [
    "ProlificConfig",
    "ProlificHttpClient",
    "ProlificAPIError",
    "ProlificAuthenticationError",
    "ProlificAuthorizationError",
    "ProlificNotFoundError",
    "ProlificRateLimitError",
    "ProlificValidationError",
    "ProlificServerError",
    "ProlificConnectionError",
    "ProlificTimeoutError",
]
