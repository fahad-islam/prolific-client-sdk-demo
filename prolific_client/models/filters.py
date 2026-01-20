"""
Models for Prolific filters and filter sets.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ProlificFilter(BaseModel):
    """
    Prolific filter model.
    
    Represents a single recruiting criterion/filter.
    """
    id: str = Field(..., description="Filter identifier")
    title: str = Field(..., description="Filter display name")
    filter_tag: Optional[str] = Field(None, description="Filter category/tag")
    type: Optional[str] = Field(None, description="Filter type (select, range, etc)")
    
    description: Optional[str] = Field(None, description="Filter description")
    
    class Config:
        extra = "allow"


class FilterSetFilter(BaseModel):
    """Filter specification within a filter set."""
    filter_id: str = Field(..., description="ID of the filter to apply")
    selected_values: Optional[List[Any]] = Field(None, description="Selected values for select-type filters")
    range_value: Optional[Dict[str, Any]] = Field(None, description="Range specification for range-type filters")
    
    class Config:
        extra = "allow"


class ProlificFilterSet(BaseModel):
    """
    Prolific filter set model.
    
    Represents a reusable collection of recruiting criteria.
    """
    id: str = Field(..., description="Filter set identifier")
    name: str = Field(..., description="Filter set name")
    version: int = Field(..., description="Filter set version number")
    workspace_id: str = Field(..., description="Workspace this filter set belongs to")
    
    filters: List[FilterSetFilter] = Field(default_factory=list, description="List of filters in this set")
    
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")
    
    class Config:
        extra = "allow"


class FilterSetCreateRequest(BaseModel):
    """Request model for creating a filter set."""
    name: str = Field(..., description="Filter set name", min_length=1, max_length=255)
    workspace_id: str = Field(..., description="Workspace ID")
    filters: List[FilterSetFilter] = Field(..., description="List of filters to include")
    
    class Config:
        extra = "allow"


class FilterSetUpdateRequest(BaseModel):
    """Request model for updating a filter set."""
    name: Optional[str] = Field(None, description="New filter set name")
    filters: Optional[List[FilterSetFilter]] = Field(None, description="Updated filter list")
    
    class Config:
        exclude_none = True
        extra = "allow"


class FilterListResponse(BaseModel):
    """Response model for listing filters."""
    results: List[ProlificFilter] = Field(default_factory=list, description="List of available filters")
    
    class Config:
        extra = "allow"
