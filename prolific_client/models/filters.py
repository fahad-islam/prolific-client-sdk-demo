"""
Models for Prolific filters and filter sets.
"""
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
from enum import Enum


class FilterType(str, Enum):
    SELECT = "select"
    RANGE = "range"


class SelectFilterDataType(str, Enum):
    CHOICE_ID = "ChoiceID"
    PARTICIPANT_ID = "ParticipantID"
    STUDY_ID = "StudyID"
    PARTICIPANT_GROUP_ID = "ParticipantGroupID"


class RangeFilterDataType(str, Enum):
    DATE = "date"
    INTEGER = "integer"
    FLOAT = "float"


class SelectFilter(BaseModel):
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
    label: str = Field(..., description="Value label")
    value: Union[str, int, float] = Field(..., description="Filter value")
    count: int = Field(..., description="Number of participants with this value")
    percentage: Optional[float] = Field(None, description="Percentage of total participants")


class FilterDistribution(BaseModel):
    filter_id: str = Field(..., description="Filter identifier")
    total_participants: int = Field(..., description="Total participants in pool")
    distribution: List[FilterDistributionDataPoint] = Field(
        default_factory=list,
        description="Distribution across values"
    )
    
    class Config:
        extra = "allow"


class FilterValue(BaseModel):
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
        extra = "forbid" 


class FilterSetUpdateRequest(BaseModel):
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
    results: List[Union[SelectFilter, RangeFilter, GenericFilter]] = Field(
        default_factory=list,
        description="List of available filters (mix of select, range, and generic)"
    )
    
    class Config:
        extra = "allow"


class FilterSetListResponse(BaseModel):
    results: List[ProlificFilterSet] = Field(
        default_factory=list,
        description="List of filter sets in workspace"
    )
    
    class Config:
        extra = "allow"


FilterID = str
FilterSetID = str
WorkspaceID = str