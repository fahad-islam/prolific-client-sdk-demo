"""
Common models used across Prolific client.
"""
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class ToolResult:
    ok: bool
    warnings: List[str] = field(default_factory=list)
    raw: Optional[Dict[str, Any]] = None
    data: Optional[Any] = None
    
    def add_warning(self, warning: str):
        self.warnings.append(warning)
    
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0
    
    def __bool__(self) -> bool:
        return self.ok
    
    @classmethod
    def success(cls, data: Any = None, raw: Optional[Dict[str, Any]] = None, warnings: Optional[List[str]] = None) -> "ToolResult":
        return cls(
            ok=True,
            data=data,
            raw=raw,
            warnings=warnings or []
        )
    
    @classmethod
    def failure(cls, raw: Optional[Dict[str, Any]] = None, warnings: Optional[List[str]] = None) -> "ToolResult":
        return cls(
            ok=False,
            raw=raw,
            warnings=warnings or []
        )
