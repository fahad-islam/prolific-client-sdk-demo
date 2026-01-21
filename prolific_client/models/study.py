"""
Models for Prolific studies.
"""
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl, field_validator


class StudyStatus(str, Enum):
    """Study status enumeration."""
    UNPUBLISHED = "UNPUBLISHED"
    ACTIVE = "ACTIVE"
    SCHEDULED = "SCHEDULED"
    AWAITING_REVIEW = "AWAITING_REVIEW"
    COMPLETED = "COMPLETED"
    PAUSED = "PAUSED"


class StudyAction(str, Enum):
    """Valid study transition actions."""
    PUBLISH = "PUBLISH"
    START = "START"
    PAUSE = "PAUSE"
    STOP = "STOP"


class DeviceCompatibility(str, Enum):
    """Device compatibility options."""
    DESKTOP = "desktop"
    TABLET = "tablet"
    MOBILE = "mobile"


class PeripheralRequirement(str, Enum):
    """Peripheral requirements."""
    AUDIO = "audio"
    CAMERA = "camera"
    MICROPHONE = "microphone"
    DOWNLOAD = "download"


class CompletionCode(BaseModel):
    """Completion code configuration."""
    code: str = Field(..., description="The completion code")
    code_type: str = Field(
        ...,
        description="Type of code (e.g., 'MANUAL')"
    )
    
    class Config:
        extra = "allow"


class ProlificStudy(BaseModel):
    """
    Prolific study model.
    
    Represents a study/survey in Prolific.
    Based on GET /api/v1/studies/{study_id}/
    
    Attributes:
        id: Unique study identifier
        name: Study name/title (internal name shown to participants)
        internal_name: Internal tracking name (not shown to participants)
        description: Study description shown to participants
        external_study_url: URL to your external survey
        prolific_id_option: How to pass Prolific ID (url_parameters or not_required)
        completion_code: Completion code configuration
        completion_option: How completion is verified (url or code)
        total_available_places: Total participant slots
        estimated_completion_time: Estimated time in minutes
        reward: Reward amount in pence/cents (minor currency units)
        device_compatibility: List of compatible devices
        peripheral_requirements: List of required peripherals
        project: Project ID this study belongs to
        status: Current study status
        places_taken: Number of completed submissions
        created_at: ISO 8601 creation timestamp
        published_at: ISO 8601 publication timestamp (if published)
    """
    id: str = Field(..., description="Unique study identifier")
    name: str = Field(..., description="Study name shown to participants")
    internal_name: str = Field(..., description="Internal tracking name")
    description: str = Field(..., description="Study description shown to participants")
    external_study_url: str = Field(..., description="URL to external survey")
    
    prolific_id_option: str = Field(
        ...,
        description="How to pass Prolific ID: 'url_parameters' or 'not_required'"
    )
    
    completion_code: Optional[CompletionCode] = Field(
        None,
        description="Completion code configuration"
    )
    completion_option: str = Field(
        ...,
        description="Completion verification method: 'url' or 'code'"
    )
    
    total_available_places: int = Field(..., description="Total participant slots")
    estimated_completion_time: int = Field(..., description="Estimated time in minutes")
    reward: int = Field(..., description="Reward in pence/cents (minor currency units)")
    
    device_compatibility: List[DeviceCompatibility] = Field(
        default_factory=list,
        description="Compatible devices"
    )
    peripheral_requirements: List[PeripheralRequirement] = Field(
        default_factory=list,
        description="Required peripherals"
    )
    
    project: str = Field(..., description="Project ID this study belongs to")
    
    status: StudyStatus = Field(..., description="Current study status")
    places_taken: int = Field(0, description="Number of completed submissions")
    
    created_at: str = Field(..., description="ISO 8601 creation timestamp")
    published_at: Optional[str] = Field(None, description="ISO 8601 publication timestamp")
    
    filter_set_id: Optional[str] = Field(None, description="Filter set ID for recruiting criteria")
    filters: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Direct filter specifications"
    )
    
    class Config:
        extra = "allow"
        use_enum_values = True


class StudyCreateRequest(BaseModel):
    """
    Request model for creating a study.
    
    Based on: POST /api/v1/studies/
    
    Example:
        {
            "name": "User Experience Survey",
            "internal_name": "ux_survey_2024_q1",
            "description": "Help us improve our product",
            "external_study_url": "https://survey.example.com/abc123",
            "prolific_id_option": "url_parameters",
            "completion_option": "url",
            "total_available_places": 100,
            "estimated_completion_time": 10,
            "reward": 150,
            "device_compatibility": ["desktop", "tablet"],
            "peripheral_requirements": [],
            "project": "project_id"
        }
    """
    name: str = Field(
        ...,
        description="Study name shown to participants",
        min_length=1,
        max_length=255
    )
    internal_name: str = Field(
        ...,
        description="Internal tracking name (not shown to participants)",
        min_length=1,
        max_length=255
    )
    description: str = Field(
        ...,
        description="Study description shown to participants",
        min_length=1
    )
    external_study_url: str = Field(
        ...,
        description="URL to your external survey"
    )
    
    prolific_id_option: str = Field(
        ...,
        description="How to pass Prolific ID: 'url_parameters' or 'not_required'"
    )
    
    completion_code: Optional[str] = Field(
        None,
        description="Completion code (required if completion_option='code')"
    )
    completion_option: str = Field(
        ...,
        description="Completion verification method: 'url' or 'code'"
    )
    
    total_available_places: int = Field(
        ...,
        description="Number of participants needed",
        ge=1
    )
    estimated_completion_time: int = Field(
        ...,
        description="Estimated completion time in minutes",
        ge=1
    )
    reward: int = Field(
        ...,
        description="Reward in pence/cents (minor currency units)",
        ge=0
    )
    
    device_compatibility: List[DeviceCompatibility] = Field(
        default_factory=lambda: [DeviceCompatibility.DESKTOP],
        description="Compatible devices"
    )
    peripheral_requirements: List[PeripheralRequirement] = Field(
        default_factory=list,
        description="Required peripherals"
    )
    
    project: str = Field(..., description="Project ID")
    
    filter_set_id: Optional[str] = Field(
        None,
        description="Filter set ID for recruiting criteria"
    )
    filters: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Direct filter specifications"
    )
    
    @field_validator('completion_option')
    @classmethod
    def validate_completion_option(cls, v):
        """Validate completion_option is one of the allowed values."""
        if v not in ('url', 'code'):
            raise ValueError("completion_option must be 'url' or 'code'")
        return v
    
    @field_validator('prolific_id_option')
    @classmethod
    def validate_prolific_id_option(cls, v):
        """Validate prolific_id_option is one of the allowed values."""
        if v not in ('url_parameters', 'not_required'):
            raise ValueError("prolific_id_option must be 'url_parameters' or 'not_required'")
        return v
    
    class Config:
        extra = "forbid"


class StudyUpdateRequest(BaseModel):
    """
    Request model for updating a study.
    
    Based on: PATCH /api/v1/studies/{study_id}/
    
    Note: Many fields can only be updated while study is in UNPUBLISHED status.
    After publishing, only certain fields like total_available_places can be modified
    (and it can only be increased, not decreased).
    
    Example (before publish):
        {
            "name": "Updated Study Name",
            "description": "Updated description",
            "reward": 200
        }
    
    Example (after publish - limited fields):
        {
            "total_available_places": 150  # Can only increase
        }
    """
    name: Optional[str] = Field(
        None,
        description="Study name",
        min_length=1,
        max_length=255
    )
    internal_name: Optional[str] = Field(
        None,
        description="Internal tracking name",
        min_length=1,
        max_length=255
    )
    description: Optional[str] = Field(
        None,
        description="Study description",
        min_length=1
    )
    external_study_url: Optional[str] = Field(
        None,
        description="External survey URL"
    )
    completion_code: Optional[str] = Field(
        None,
        description="Completion code"
    )
    completion_option: Optional[str] = Field(
        None,
        description="Completion verification method: 'url' or 'code'"
    )
    estimated_completion_time: Optional[int] = Field(
        None,
        description="Estimated completion time in minutes",
        ge=1
    )
    reward: Optional[int] = Field(
        None,
        description="Reward in pence/cents",
        ge=0
    )
    device_compatibility: Optional[List[DeviceCompatibility]] = Field(
        None,
        description="Compatible devices"
    )
    peripheral_requirements: Optional[List[PeripheralRequirement]] = Field(
        None,
        description="Required peripherals"
    )
    
    total_available_places: Optional[int] = Field(
        None,
        description="Participant slots (can only increase after publish)",
        ge=1
    )
    
    filter_set_id: Optional[str] = Field(
        None,
        description="Filter set ID"
    )
    filters: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Direct filter specifications"
    )
    
    class Config:
        extra = "forbid"


class StudyTransitionRequest(BaseModel):
    """
    Request model for transitioning study state.
    
    Based on: POST /api/v1/studies/{study_id}/transition/
    
    Example:
        {"action": "PUBLISH"}
    """
    action: StudyAction = Field(..., description="Transition action to perform")
    
    class Config:
        use_enum_values = True


class StudyListResponse(BaseModel):
    """Response model for listing studies."""
    results: List[ProlificStudy] = Field(
        default_factory=list,
        description="List of studies"
    )
    
    class Config:
        extra = "allow"


StudyID = str
ProjectID = str