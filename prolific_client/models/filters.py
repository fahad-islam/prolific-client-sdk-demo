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


class SelectFilterDataType(str, Enum):
    """Data types for select filters."""
    CHOICE_ID = "ChoiceID"
    PARTICIPANT_ID = "ParticipantID"
    STUDY_ID = "StudyID"
    PARTICIPANT_GROUP_ID = "ParticipantGroupID"


class RangeFilterDataType(str, Enum):
    """Data types for range filters."""
    DATE = "date"
    INTEGER = "integer"
    FLOAT = "float"


class SelectFilter(BaseModel):
    """
    Select-type filter (single or multi-select).
    
    Based on SelectFilterListResponse schema.
    """
    filter_id: str = Field(..., description="Filter ID (slugified title)")
    title: str = Field(..., description="Filter title")
    description: str = Field(..., description="Filter description")
    type: FilterType = Field(..., description="Filter type (always 'select')")
    question: Optional[str] = Field(None, description="Question asked of participants")
    choices: Dict[str, str] = Field(
        default_factory=dict,
        description="Filter choices as key-value pairs (ID -> text)"
    )
    data_type: SelectFilterDataType = Field(
        ...,
        description="Format of choice keys"
    )
    
    researcher_help_text: Optional[str] = Field(
        None,
        description="Help text for researchers"
    )
    participant_help_text: Optional[str] = Field(
        None,
        description="Help text for participants"
    )
    category: Optional[str] = Field(
        None,
        description="Category for About You section"
    )
    subcategory: Optional[str] = Field(
        None,
        description="Sub-category in prescreening modal"
    )
    display_order: Optional[int] = Field(
        None,
        description="Display order within sub-category"
    )
    tags: Optional[List[str]] = Field(
        None,
        description="Tags (e.g., recommended, new, expiring)"
    )
    
    class Config:
        extra = "allow"


class RangeFilter(BaseModel):
    """
    Range-type filter (numeric or date range).
    
    Based on RangeFilterListResponse schema.
    """
    filter_id: str = Field(..., description="Filter ID (slugified title)")
    title: str = Field(..., description="Filter title")
    description: str = Field(..., description="Filter description")
    type: FilterType = Field(..., description="Filter type (always 'range')")
    question: Optional[str] = Field(None, description="Question asked of participants")
    min: Union[int, float, str] = Field(
        ...,
        description="Minimum valid value (int, float, or ISO date)"
    )
    max: Union[int, float, str] = Field(
        ...,
        description="Maximum valid value (int, float, or ISO date)"
    )
    data_type: RangeFilterDataType = Field(
        ...,
        description="Data type of the range (date, integer, or float)"
    )
    
    researcher_help_text: Optional[str] = Field(
        None,
        description="Help text for researchers"
    )
    participant_help_text: Optional[str] = Field(
        None,
        description="Help text for participants"
    )
    category: Optional[str] = Field(
        None,
        description="Category for About You section"
    )
    subcategory: Optional[str] = Field(
        None,
        description="Sub-category in prescreening modal"
    )
    display_order: Optional[int] = Field(
        None,
        description="Display order within sub-category"
    )
    tags: Optional[List[str]] = Field(
        None,
        description="Tags (e.g., recommended, new, expiring)"
    )
    
    class Config:
        extra = "allow"


class GenericFilter(BaseModel):
    """
    Generic filter for handling edge cases in API responses.
    
    Some filters don't fit the strict select/range schemas.
    """
    filter_id: str = Field(..., description="Filter ID")
    title: str = Field(..., description="Filter title")
    description: str = Field(..., description="Filter description")
    type: str = Field(..., description="Filter type")
    question: Optional[str] = None
    
    choices: Optional[Dict[str, Any]] = None
    data_type: Optional[str] = None
    min: Optional[Union[int, float, str]] = None
    max: Optional[Union[int, float, str]] = None
    
    researcher_help_text: Optional[str] = None
    participant_help_text: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    display_order: Optional[int] = None
    tags: Optional[List[str]] = None
    
    class Config:
        extra = "allow"


ProlificFilter = Union[SelectFilter, RangeFilter, GenericFilter]


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
    - SELECT: selected_values with list of choice IDs
    - RANGE: range_value with min/max
    """
    filter_id: Optional[str] = Field(None, description="ID of the filter being applied")
    
    selected_values: Optional[List[Union[str, int]]] = Field(
        None,
        description="Selected choice IDs for select-type filters"
    )
    
    range_value: Optional[Dict[str, Union[int, float, str]]] = Field(
        None,
        description="Range specification with 'lower' and 'upper' keys"
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
                    "range_value": {"lower": 25, "upper": 45}
                },
                {
                    "filter_id": "country_filter_id",
                    "selected_values": ["US"]
                }
            ]
        }
    """
    name: Optional[str] = Field(
        None,
        description="Filter set name",
        min_length=1,
        max_length=255
    )
    workspace_id: Optional[str] = Field(None, description="Workspace ID where filter set will be created")
    organisation_id: Optional[str] = Field(None, description="Organisation ID where filter set will be created")
    filters: Optional[List[FilterValue]] = Field(
        None,
        description="List of filter values to include in this set",
        min_length=1
    )
    
    class Config:
        extra = "forbid"  # Strict validation for creation


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
                    "range_value": {"lower": 30, "upper": 50}
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
    results: List[Union[SelectFilter, RangeFilter, GenericFilter]] = Field(
        default_factory=list,
        description="List of available filters (mix of select, range, and generic)"
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