"""
Configuration management for Prolific API client.
"""
import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class ProlificConfig:
    base_url: str
    token: str
    default_workspace_id: Optional[str] = None
    timeout_s: int = 30
    max_retries: int = 3
    
    def __post_init__(self):
        if not self.token:
            raise ValueError("API token is required")
        
        if not self.base_url:
            raise ValueError("Base URL is required")
        
        self.base_url = self.base_url.rstrip('/')
        
        if self.timeout_s <= 0:
            raise ValueError("Timeout must be positive")
        
        if self.max_retries < 0:
            raise ValueError("Max retries cannot be negative")
    
    @classmethod
    def from_env(cls, env_file: Optional[str] = None) -> "ProlificConfig":
        if env_file:
            from dotenv import load_dotenv
            load_dotenv(env_file)
        
        token = os.getenv("PROLIFIC_API_TOKEN")
        if not token:
            raise ValueError(
                "PROLIFIC_API_TOKEN environment variable is required. "
                "Set it in your environment or .env file."
            )
        
        return cls(
            base_url=os.getenv("PROLIFIC_BASE_URL", "https://api.prolific.com"),
            token=token,
            default_workspace_id=os.getenv("PROLIFIC_WORKSPACE_ID"),
            timeout_s=int(os.getenv("PROLIFIC_TIMEOUT", "30")),
            max_retries=int(os.getenv("PROLIFIC_MAX_RETRIES", "3"))
        )
    
    def get_headers(self) -> dict:
        return {
            "Authorization": f"Token {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def redacted_token(self) -> str:
        if len(self.token) <= 4:
            return "***"
        return f"***{self.token[-4:]}"
