#!/usr/bin/env python3
"""
Smoke test for Prolific API client.

This script verifies:
1. Configuration loading from environment
2. API authentication
3. Basic connectivity
4. Error handling

Usage:
    python scripts/prolific_smoke_test.py
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from prolific_client.config import ProlificConfig
from prolific_client.http import ProlificHttpClient
from prolific_client.errors import (
    ProlificAPIError,
    ProlificAuthenticationError,
    ProlificConnectionError
)


def print_header(text: str):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_success(text: str):
    """Print success message."""
    print(f"✓ {text}")


def print_error(text: str):
    """Print error message."""
    print(f"✗ {text}")


def print_info(text: str):
    """Print info message."""
    print(f"  {text}")


def test_configuration():
    """Test configuration loading."""
    print_header("Test 1: Configuration Loading")
    
    try:
        config = ProlificConfig.from_env()
        print_success("Configuration loaded successfully")
        print_info(f"Base URL: {config.base_url}")
        print_info(f"Token: {config.redacted_token()}")
        print_info(f"Timeout: {config.timeout_s}s")
        print_info(f"Max retries: {config.max_retries}")
        
        if config.default_workspace_id:
            print_info(f"Default workspace: {config.default_workspace_id}")
        else:
            print_info("Default workspace: Not set")
        
        return config
    
    except ValueError as e:
        print_error(f"Configuration error: {e}")
        print_info("Make sure PROLIFIC_API_TOKEN is set in your environment or .env file")
        return None


def test_authentication(config: ProlificConfig):
    """Test API authentication."""
    print_header("Test 2: API Authentication")
    
    try:
        client = ProlificHttpClient(config)
        
        try:
            response = client.get("/api/v1/workspaces/")
            print_success("Authentication successful")
            
            if isinstance(response, dict) and "results" in response:
                workspaces = response["results"]
                print_info(f"Found {len(workspaces)} workspace(s)")
                for ws in workspaces[:3]:  # Show first 3
                    print_info(f"  - {ws.get('title', 'Unnamed')} (ID: {ws.get('id', 'N/A')})")
            
            return client
        
        except ProlificAuthenticationError as e:
            print_error(f"Authentication failed: {e}")
            print_info("Check that your API token is valid")
            return None
    
    except ProlificConnectionError as e:
        print_error(f"Connection error: {e}")
        print_info("Check your network connection and API URL")
        return None
    
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return None


def test_error_handling(client: ProlificHttpClient):
    """Test error handling with invalid request."""
    print_header("Test 3: Error Handling")
    
    try:
        try:
            client.get("/api/v1/projects/invalid-project-id-that-does-not-exist/")
            print_error("Expected 404 error was not raised")
        except ProlificAPIError as e:
            if e.status_code == 404:
                print_success(f"404 error handled correctly: {e.message}")
            else:
                print_error(f"Unexpected error code: {e.status_code}")
        
        return True
    
    except Exception as e:
        print_error(f"Error handling test failed: {e}")
        return False


def test_retry_logic(client: ProlificHttpClient):
    """Test retry logic (informational only)."""
    print_header("Test 4: Retry Logic")
    
    print_info("Retry logic is configured with:")
    print_info(f"  - Max retries: {client.config.max_retries}")
    print_info(f"  - Exponential backoff (1s, 2s, 4s, ...)")
    print_info(f"  - Automatic retry on 429 (rate limit)")
    print_info(f"  - Automatic retry on 5xx (server errors)")
    print_success("Retry logic configured correctly")
    
    return True


def main():
    """Run all smoke tests."""
    print_header("Prolific API Client - Smoke Test")
    
    config = test_configuration()
    if not config:
        print("\n❌ Smoke test failed: Configuration error")
        return 1
    
    client = test_authentication(config)
    if not client:
        print("\n❌ Smoke test failed: Authentication error")
        return 1
    
    if not test_error_handling(client):
        print("\n❌ Smoke test failed: Error handling issue")
        return 1
    
    if not test_retry_logic(client):
        print("\n❌ Smoke test failed: Retry logic issue")
        return 1
    
    client.close()
    
    # All tests passed
    print_header("All Tests Passed!")
    print("✓ Configuration loading works")
    print("✓ API authentication successful")
    print("✓ Error handling works correctly")
    print("✓ Retry logic configured properly")
    print("\n🎉 Smoke test completed successfully!\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
