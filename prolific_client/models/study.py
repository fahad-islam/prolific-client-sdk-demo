"""
Models for Prolific studies.
"""
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


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


class ProlificStudy(BaseModel):
    """
    Prolific study model.
    
    Represents a study/survey in Prolific.
    """
    id: str = Field(..., description="Unique study identifier")
    name: str = Field(..., description="Study name/title")
    description: Optional[str] = Field(None, description="Study description")
    external_study_url: Optional[str] = Field(None, description="External survey URL")
    
    project: Optional[str] = Field(None, description="Project ID this study belongs to")
    
    status: StudyStatus = Field(..., description="Current study status")
    total_available_places: int = Field(..., description="Total participant slots")
    places_taken: int = Field(0, description="Number of completed submissions")
    
    reward: Optional[int] = Field(None, description="Reward in cents/pence")
    estimated_completion_time: Optional[int] = Field(None, description="Estimated time in minutes")
    
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    published_at: Optional[str] = Field(None, description="Publication timestamp")
    completed_at: Optional[str] = Field(None, description="Completion timestamp")
    
    internal_name: Optional[str] = Field(None, description="Internal tracking name")
    
    class Config:
        extra = "allow"
        use_enum_values = True


class StudyCreateRequest(BaseModel):
    """Request model for creating a study."""
    name: str = Field(..., description="Study name", min_length=1, max_length=255)
    description: Optional[str] = Field(None, description="Study description")
    external_study_url: str = Field(..., description="External survey URL")
    
    total_available_places: int = Field(..., description="Number of participants", ge=1)
    estimated_completion_time: int = Field(..., description="Completion time in minutes", ge=1)
    reward: int = Field(..., description="Reward in cents/pence", ge=0)
    
    project: Optional[str] = Field(None, description="Project ID")
    
    internal_name: Optional[str] = Field(None, description="Internal name for tracking")
    
    class Config:
        extra = "allow"


class StudyUpdateRequest(BaseModel):
    """
    Request model for updating a study.
    
    Note: Many fields can only be updated while study is in UNPUBLISHED status.
    After publishing, only certain fields like total_available_places can be increased.
    """
    name: Optional[str] = Field(None, description="Study name", min_length=1, max_length=255)
    description: Optional[str] = Field(None, description="Study description")
    internal_name: Optional[str] = Field(None, description="Internal name")
    total_available_places: Optional[int] = Field(None, description="Participant slots (can only increase after publish)", ge=1)
    
    class Config:
        exclude_none = True
        extra = "allow"


class StudyTransitionRequest(BaseModel):
    """Request model for transitioning study state."""
    action: StudyAction = Field(..., description="Transition action to perform")
    
    class Config:
        use_enum_values = True
