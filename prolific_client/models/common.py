"""
Common models used across Prolific client.
"""
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class ToolResult:
    """
    Standard result object for tool operations.
    
    Attributes:
        ok: Whether operation succeeded
        warnings: List of warning messages
        raw: Raw response data from API
        data: Processed/transformed data (optional)
    """
    ok: bool
    warnings: List[str] = field(default_factory=list)
    raw: Optional[Dict[str, Any]] = None
    data: Optional[Any] = None
    
    def add_warning(self, warning: str):
        """Add a warning message."""
        self.warnings.append(warning)
    
    def has_warnings(self) -> bool:
        """Check if result has warnings."""
        return len(self.warnings) > 0
    
    def __bool__(self) -> bool:
        """Allow truthiness check based on ok status."""
        return self.ok
    
    @classmethod
    def success(cls, data: Any = None, raw: Optional[Dict[str, Any]] = None, warnings: Optional[List[str]] = None) -> "ToolResult":
        """
        Create a successful result.
        
        Args:
            data: Processed data
            raw: Raw API response
            warnings: Optional warnings
        
        Returns:
            ToolResult with ok=True
        """
        return cls(
            ok=True,
            data=data,
            raw=raw,
            warnings=warnings or []
        )
    
    @classmethod
    def failure(cls, raw: Optional[Dict[str, Any]] = None, warnings: Optional[List[str]] = None) -> "ToolResult":
        """
        Create a failed result.
        
        Args:
            raw: Raw API response
            warnings: Optional warnings/error messages
        
        Returns:
            ToolResult with ok=False
        """
        return cls(
            ok=False,
            raw=raw,
            warnings=warnings or []
        )
