# Prolific Integration Tool

A Python-native tool for integrating with Prolific's v1 API to programmatically manage participant recruiting workflows.

## Project Structure

```
prolific_client/
├── __init__.py
├── config.py          # Configuration management
├── errors.py          # Custom exception classes
├── http.py            # HTTP client with retry logic
├── models/
│   ├── __init__.py
│   ├── common.py      # Common models (ToolResult, etc.)
│   ├── project.py     # Project models
│   ├── study.py       # Study models
│   └── filters.py     # Filter models
└── api/
    ├── __init__.py
    ├── projects.py    # Project API operations
    ├── studies.py     # Study API operations
    └── filters.py     # Filter API operations

scripts/
└── prolific_smoke_test.py  # Connectivity test

tests/
├── __init__.py
├── test_http_client.py
└── test_error_handling.py
```

## Milestone 0: Bootstrap - Working Prolific API Client

### Features
- ✅ Token-based authentication with Prolific API v1
- ✅ Reliable GET/POST/PATCH requests
- ✅ Typed exceptions for error handling
- ✅ Retry logic with exponential backoff (429, 5xx)
- ✅ Structured logging with credential redaction
- ✅ Correlation ID tracking
- ✅ Smoke tests for connectivity verification

## Setup

### Requirements
```bash
pip install requests pydantic python-dotenv
```

### Configuration
Create a `.env` file:
```
PROLIFIC_API_TOKEN=your_api_token_here
PROLIFIC_WORKSPACE_ID=your_workspace_id
```

### Usage Example
```python
from prolific_client.config import ProlificConfig
from prolific_client.http import ProlificHttpClient

# Initialize
config = ProlificConfig.from_env()
client = ProlificHttpClient(config)

# Make a request
response = client._request("GET", "/api/v1/workspaces/")
```

## Running Tests

```bash
# Smoke test
python scripts/prolific_smoke_test.py

# Unit tests
python -m pytest tests/
```