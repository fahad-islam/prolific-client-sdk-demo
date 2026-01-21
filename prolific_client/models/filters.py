"""
Models for Prolific filters and filter sets.
"""
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
from enum import Enum


class FilterType(str, Enum):
    """Filter input types."""
    SELECT = "select"
    RANGE = "range"
    MULTI_SELECT = "multi_select"
    TEXT = "text"


class FilterConstraintType(str, Enum):
    """Filter constraint types."""
    LIST = "list"
    RANGE = "range"


class FilterConstraint(BaseModel):
    """
    Filter constraints defining allowed values.
    
    Attributes:
        type: Constraint type (list or range)
        min: Minimum value for range constraints
        max: Maximum value for range constraints
        list: List of allowed values for list constraints
    """
    type: FilterConstraintType
    min: Optional[Union[int, float]] = None
    max: Optional[Union[int, float]] = None
    list: Optional[List[Dict[str, Any]]] = None


class ProlificFilter(BaseModel):
    """
    Prolific filter/question model.
    
    Represents a single recruiting criterion that can be applied to studies.
    Based on GET /api/v1/filters/
    """
    id: str = Field(..., description="Unique filter identifier")
    title: str = Field(..., description="Human-readable filter name")
    description: str = Field(..., description="Filter description")
    filter_tag: str = Field(..., description="Category/tag for grouping filters")
    type: FilterType = Field(..., description="Input type for this filter")
    
    constraints: Optional[FilterConstraint] = Field(None, description="Allowed values or ranges")
    
    is_new: Optional[bool] = Field(None, description="Whether this is a newly added filter")
    question_html: Optional[str] = Field(None, description="HTML formatted question text")
    help_text: Optional[str] = Field(None, description="Additional help text")
    
    price_per_participant_minor_units: Optional[int] = Field(
        None, 
        description="Additional cost per participant in minor currency units (cents/pence)"
    )
    
    class Config:
        extra = "allow"


class FilterDistributionDataPoint(BaseModel):
    """
    Single data point in filter distribution.
    
    Represents how many participants match a particular filter value.
    """
    label: str = Field(..., description="Value label")
    value: Union[str, int, float] = Field(..., description="Filter value")
    count: int = Field(..., description="Number of participants with this value")
    percentage: Optional[float] = Field(None, description="Percentage of total participants")


class FilterDistribution(BaseModel):
    """
    Distribution data for a filter.
    
    Based on GET /api/v1/filters/{filter_id}/distribution/
    Shows how many participants match each possible value.
    """
    filter_id: str = Field(..., description="Filter identifier")
    total_participants: int = Field(..., description="Total participants in pool")
    distribution: List[FilterDistributionDataPoint] = Field(
        default_factory=list,
        description="Distribution across values"
    )
    
    class Config:
        extra = "allow"


class FilterValue(BaseModel):
    """
    A filter value specification for use in filter sets.
    
    Different filters use different value formats:
    - SELECT: selected_values with list of value IDs
    - RANGE: range_value with min/max
    - MULTI_SELECT: selected_values with list of value IDs
    """
    filter_id: str = Field(..., description="ID of the filter being applied")
    
    selected_values: Optional[List[Union[str, int]]] = Field(
        None,
        description="Selected value IDs for select-type filters"
    )
    
    range_value: Optional[Dict[str, Union[int, float]]] = Field(
        None,
        description="Range specification with 'min' and 'max' keys"
    )
    
    class Config:
        extra = "allow"


class ProlificFilterSet(BaseModel):
    """
    Prolific filter set model.
    
    Represents a reusable collection of recruiting criteria.
    Based on GET /api/v1/filter-sets/{filter_set_id}/
    """
    id: str = Field(..., description="Unique filter set identifier")
    name: str = Field(..., description="Filter set name")
    workspace_id: str = Field(..., description="Workspace this filter set belongs to")
    
    filters: List[FilterValue] = Field(
        default_factory=list,
        description="List of filter values in this set"
    )
    
    version: int = Field(..., description="Filter set version number (increments on update)")
    
    created_at: str = Field(..., description="ISO 8601 creation timestamp")
    updated_at: Optional[str] = Field(None, description="ISO 8601 last update timestamp")
    
    estimated_participants: Optional[int] = Field(
        None,
        description="Estimated number of participants matching these criteria"
    )
    
    class Config:
        extra = "allow"


class FilterSetCreateRequest(BaseModel):
    """
    Request model for creating a filter set.
    
    Based on POST /api/v1/filter-sets/
    
    Example:
        {
            "name": "US Adults 25-45",
            "workspace_id": "workspace_id",
            "filters": [
                {
                    "filter_id": "age_range_filter_id",
                    "range_value": {"min": 25, "max": 45}
                },
                {
                    "filter_id": "country_filter_id",
                    "selected_values": ["US"]
                }
            ]
        }
    """
    name: str = Field(
        ...,
        description="Filter set name",
        min_length=1,
        max_length=255
    )
    workspace_id: str = Field(..., description="Workspace ID where filter set will be created")
    filters: List[FilterValue] = Field(
        ...,
        description="List of filter values to include in this set",
        min_length=1
    )
    
    class Config:
        extra = "forbid"


class FilterSetUpdateRequest(BaseModel):
    """
    Request model for updating a filter set.
    
    Based on PATCH /api/v1/filter-sets/{filter_set_id}/
    All fields are optional - only provided fields are updated.
    
    Example:
        {
            "name": "Updated Name",
            "filters": [
                {
                    "filter_id": "age_range_filter_id",
                    "range_value": {"min": 30, "max": 50}
                }
            ]
        }
    """
    name: Optional[str] = Field(
        None,
        description="New filter set name",
        min_length=1,
        max_length=255
    )
    filters: Optional[List[FilterValue]] = Field(
        None,
        description="Updated filter list (replaces entire list)",
        min_length=1
    )
    
    class Config:
        extra = "forbid"


class FilterListResponse(BaseModel):
    """
    Response model for listing filters.
    
    Based on GET /api/v1/filters/?workspace_id={workspace_id}
    Returns all available filters for a workspace.
    """
    results: List[ProlificFilter] = Field(
        default_factory=list,
        description="List of available filters"
    )
    
    class Config:
        extra = "allow"


class FilterSetListResponse(BaseModel):
    """
    Response model for listing filter sets.
    
    Based on GET /api/v1/workspaces/{workspace_id}/filter-sets/
    Returns all filter sets in a workspace.
    """
    results: List[ProlificFilterSet] = Field(
        default_factory=list,
        description="List of filter sets in workspace"
    )
    
    class Config:
        extra = "allow"


FilterID = str
FilterSetID = str
WorkspaceID = str