"""
Models for Prolific studies.
"""
from typing import Optional, List, Dict, Union
from enum import Enum
from pydantic import BaseModel, Field


class StudyStatus(str, Enum):
    UNPUBLISHED = "UNPUBLISHED"
    SCHEDULED = "SCHEDULED"
    PUBLISHING = "PUBLISHING"
    ACTIVE = "ACTIVE"
    AWAITING_REVIEW = "AWAITING_REVIEW"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"


class StudyAction(str, Enum):
    PUBLISH = "PUBLISH"
    START = "START"
    PAUSE = "PAUSE"
    STOP = "STOP"


class ProlificIdOption(str, Enum):
    QUESTION = "question"
    URL_PARAMETERS = "url_parameters"
    NOT_REQUIRED = "not_required"


class DeviceCompatibility(str, Enum):
    DESKTOP = "desktop"
    TABLET = "tablet"
    MOBILE = "mobile"


class PeripheralRequirement(str, Enum):
    AUDIO = "audio"
    CAMERA = "camera"
    DOWNLOAD = "download"
    MICROPHONE = "microphone"


class CompletionCodeType(str, Enum):
    COMPLETED = "COMPLETED"
    FAILED_ATTENTION_CHECK = "FAILED_ATTENTION_CHECK"
    FOLLOW_UP_STUDY = "FOLLOW_UP_STUDY"
    GIVE_BONUS = "GIVE_BONUS"
    INCOMPATIBLE_DEVICE = "INCOMPATIBLE_DEVICE"
    NO_CONSENT = "NO_CONSENT"
    OTHER = "OTHER"
    FIXED_SCREENOUT = "FIXED_SCREENOUT"


class CompletionCodeActionType(str, Enum):
    AUTOMATICALLY_APPROVE = "AUTOMATICALLY_APPROVE"
    ADD_TO_PARTICIPANT_GROUP = "ADD_TO_PARTICIPANT_GROUP"
    REMOVE_FROM_PARTICIPANT_GROUP = "REMOVE_FROM_PARTICIPANT_GROUP"
    MANUALLY_REVIEW = "MANUALLY_REVIEW"
    REQUEST_RETURN = "REQUEST_RETURN"
    DYNAMIC_PAYMENT = "DYNAMIC_PAYMENT"
    FIXED_SCREEN_OUT_PAYMENT = "FIXED_SCREEN_OUT_PAYMENT"


class CompletionCodeActor(str, Enum):
    PARTICIPANT = "participant"
    RESEARCHER = "researcher"


class StudyLabel(str, Enum):
    SURVEY = "survey"
    WRITING_TASK = "writing_task"
    ANNOTATION = "annotation"
    DECISION_MAKING_TASK = "decision_making_task"
    INTERVIEW = "interview"
    OTHER = "other"
    AI_ANNOTATION = "ai_annotation"
    AI_EVALUATION = "ai_evaluation"
    AI_REASONING = "ai_reasoning"
    AI_FACT_CHECKING = "ai_fact_checking"
    AI_SAFETY = "ai_safety"
    AI_DATA_CREATION_TEXT = "ai_data_creation_text"
    AI_DATA_CREATION_AUDIO = "ai_data_creation_audio"
    AI_DATA_CREATION_VIDEO = "ai_data_creation_video"
    AI_DATA_CREATION_IMAGES = "ai_data_creation_images"
    AI_OTHER = "ai_other"


class ContentWarning(str, Enum):
    SENSITIVE = "sensitive"
    EXPLICIT = "explicit"


class AutoRejectionCategory(str, Enum):
    EXCEPTIONALLY_FAST = "EXCEPTIONALLY_FAST"


class DataCollectionMethod(str, Enum):
    DC_TOOL = "DC_TOOL"
    AI_TASK_BUILDER = "AI_TASK_BUILDER"


class AutomaticallyApproveAction(BaseModel):
    action: CompletionCodeActionType = Field(
        CompletionCodeActionType.AUTOMATICALLY_APPROVE,
        description="Automatically approves submission with payment"
    )


class AddToParticipantGroupAction(BaseModel):
    action: CompletionCodeActionType = Field(
        CompletionCodeActionType.ADD_TO_PARTICIPANT_GROUP,
        description="Adds participants to a specific group"
    )
    participant_group: str = Field(..., description="The participant group ID to add to")


class RemoveFromParticipantGroupAction(BaseModel):
    action: CompletionCodeActionType = Field(
        CompletionCodeActionType.REMOVE_FROM_PARTICIPANT_GROUP,
        description="Removes participants from specific groups"
    )
    participant_group: str = Field(..., description="The participant group ID to remove from")


class ManuallyReviewAction(BaseModel):
    action: CompletionCodeActionType = Field(
        CompletionCodeActionType.MANUALLY_REVIEW,
        description="Moves submission for manual review"
    )


class RequestReturnAction(BaseModel):
    action: CompletionCodeActionType = Field(
        CompletionCodeActionType.REQUEST_RETURN,
        description="Requests the participant to return their study"
    )
    return_reason: str = Field(..., description="The reason for requesting a return")


class DynamicPaymentAction(BaseModel):
    action: CompletionCodeActionType = Field(
        CompletionCodeActionType.DYNAMIC_PAYMENT,
        description="Use this for dynamic payment studies (workspace feature)"
    )


class FixedScreenOutAction(BaseModel):
    action: CompletionCodeActionType = Field(
        CompletionCodeActionType.FIXED_SCREEN_OUT_PAYMENT,
        description="Fixed screen out reward for participants who don't qualify"
    )
    fixed_screen_out_reward: int = Field(
        ...,
        description="Amount in pence/cents for screen-out (less than study reward)"
    )
    slots: int = Field(
        ...,
        description="Maximum number of screen-outs before study pauses"
    )


CompletionCodeAction = Union[
    AutomaticallyApproveAction,
    AddToParticipantGroupAction,
    RemoveFromParticipantGroupAction,
    ManuallyReviewAction,
    RequestReturnAction,
    DynamicPaymentAction,
    FixedScreenOutAction
]


class CompletionCode(BaseModel):
    code: Optional[str] = Field(
        None,
        description="Completion code (null if no code required)"
    )
    code_type: CompletionCodeType = Field(
        ...,
        description="Type of completion code"
    )
    actions: List[CompletionCodeAction] = Field(
        default_factory=list,
        description="Actions to perform when this code is used"
    )
    actor: CompletionCodeActor = Field(
        CompletionCodeActor.PARTICIPANT,
        description="Who can provide this completion code"
    )
    
    class Config:
        extra = "allow"
        use_enum_values = True


class SelectFilter(BaseModel):
    filter_id: str = Field(..., description="Filter ID")
    selected_values: List[str] = Field(
        ...,
        description="Selected value IDs from filter choices"
    )
    weightings: Optional[Dict[str, float]] = Field(
        None,
        description="Distribution weightings for selected values"
    )
    
    class Config:
        extra = "allow"


class RangeFilterSelectedRange(BaseModel):
    lower: Optional[Union[int, float, str]] = Field(
        None,
        description="Lower bound (null for minimum)"
    )
    upper: Optional[Union[int, float, str]] = Field(
        None,
        description="Upper bound (null for maximum)"
    )


class RangeFilterWeighting(BaseModel):
    selected_range: RangeFilterSelectedRange
    weighting: float


class RangeFilter(BaseModel):
    filter_id: str = Field(..., description="Filter ID")
    selected_range: RangeFilterSelectedRange = Field(
        ...,
        description="Range specification with lower/upper bounds"
    )
    weightings: Optional[RangeFilterWeighting] = Field(
        None,
        description="Distribution weightings"
    )
    
    class Config:
        extra = "allow"


StudyFilter = Union[SelectFilter, RangeFilter]


class SubmissionsConfig(BaseModel):
    max_submissions_per_participant: Optional[int] = Field(
        1,
        description="Max submissions per participant (1=default, -1=unlimited)"
    )
    max_concurrent_submissions: Optional[int] = Field(
        -1,
        description="Max concurrent active/reserved submissions (-1=unlimited)"
    )
    auto_rejection_categories: Optional[List[AutoRejectionCategory]] = Field(
        None,
        description="Categories that trigger automatic rejection"
    )
    
    class Config:
        extra = "allow"
        use_enum_values = True


class DataCollectionMetadata(BaseModel):
    annotators_per_task: Optional[int] = Field(
        1,
        description="Number of annotators per task (min: 1, default: 1)",
        ge=1
    )
    
    class Config:
        extra = "allow"


class AccessDetail(BaseModel):
    external_url: str = Field(..., description="URL for this taskflow path")
    total_allocation: float = Field(
        ...,
        description="Number of places allocated to this URL"
    )
    
    class Config:
        extra = "allow"



class ProlificStudy(BaseModel):
    id: str = Field(..., description="Unique study identifier")
    status: StudyStatus = Field(..., description="Current study status")
    
    name: str = Field(..., description="Public study name shown to participants")
    internal_name: Optional[str] = Field(
        None,
        description="Internal tracking name (not shown to participants)"
    )
    description: str = Field(..., description="Study description (supports limited HTML)")
    
    external_study_url: Optional[str] = Field(
        None,
        description="URL to external survey/experiment"
    )
    is_external_study_url_secure: Optional[bool] = Field(
        None,
        description="Whether external URL is signed with JWT"
    )
    
    prolific_id_option: ProlificIdOption = Field(
        ...,
        description="How to pass Prolific ID to study"
    )
    
    completion_codes: List[CompletionCode] = Field(
        default_factory=list,
        description="Completion codes and their actions"
    )
    
    total_available_places: Optional[float] = Field(
        None,
        description="Number of participants needed (optional for AI Task Builder)"
    )
    estimated_completion_time: float = Field(
        ...,
        description="Estimated time in minutes"
    )
    maximum_allowed_time: Optional[float] = Field(
        None,
        description="Max time in minutes before timeout"
    )
    reward: float = Field(..., description="Reward in pence/cents")
    
    device_compatibility: List[DeviceCompatibility] = Field(
        default_factory=list,
        description="Compatible devices (empty = all)"
    )
    peripheral_requirements: List[PeripheralRequirement] = Field(
        default_factory=list,
        description="Required peripherals (empty = none)"
    )
    
    filters: Optional[List[StudyFilter]] = Field(
        None,
        description="Direct filter specifications (empty array = everyone)"
    )
    filter_set_id: Optional[str] = Field(
        None,
        description="Filter set ID (mutually exclusive with filters)"
    )
    filter_set_version: Optional[int] = Field(
        None,
        description="Filter set version (defaults to latest)"
    )
    
    naivety_distribution_rate: Optional[float] = Field(
        None,
        description="Balance between speed and naivety (0-100, null=auto)"
    )
    project: str = Field(..., description="Project ID")
    
    submissions_config: Optional[SubmissionsConfig] = Field(
        None,
        description="Advanced submission configuration"
    )
    
    study_labels: Optional[List[StudyLabel]] = Field(
        None,
        description="Study type/topic labels"
    )
    content_warnings: Optional[List[ContentWarning]] = Field(
        None,
        description="Content warnings"
    )
    content_warning_details: Optional[str] = Field(
        None,
        description="Additional content warning details"
    )
    
    metadata: Optional[str] = Field(
        None,
        description="Custom metadata for system integration"
    )
    
    credential_pool_id: Optional[str] = Field(
        None,
        description="Credential pool ID for distributing credentials"
    )
    has_credentials: Optional[bool] = Field(
        None,
        description="Whether study requires credentials"
    )
    
    data_collection_method: Optional[DataCollectionMethod] = Field(
        None,
        description="Data collection method (DC_TOOL or AI_TASK_BUILDER)"
    )
    data_collection_id: Optional[str] = Field(
        None,
        description="Task Builder batch/project ID"
    )
    data_collection_metadata: Optional[DataCollectionMetadata] = Field(
        None,
        description="AI Task Builder metadata"
    )
    
    access_details: Optional[List[AccessDetail]] = Field(
        None,
        description="Taskflow access details"
    )
    
    places_taken: Optional[int] = Field(0, description="Number of completed submissions")
    created_at: Optional[str] = Field(None, description="ISO 8601 creation timestamp")
    published_at: Optional[str] = Field(None, description="ISO 8601 publication timestamp")
    
    class Config:
        extra = "allow"
        use_enum_values = True



class StudyCreateRequest(BaseModel):
    name: str = Field(
        ...,
        description="Public study name",
        min_length=1,
        max_length=255
    )
    description: str = Field(
        ...,
        description="Study description (supports limited HTML)",
        min_length=1
    )
    
    external_study_url: Optional[str] = Field(
        None,
        description="URL to external survey"
    )
    is_external_study_url_secure: Optional[bool] = Field(
        None,
        description="Sign URL with JWT"
    )
    
    prolific_id_option: ProlificIdOption = Field(
        ...,
        description="How to pass Prolific ID"
    )
    
    completion_codes: List[CompletionCode] = Field(
        ...,
        description="At least one completion code required",
        min_length=1
    )
    
    total_available_places: Optional[float] = Field(
        None,
        description="Number of participants (optional for AI Task Builder)"
    )
    estimated_completion_time: float = Field(
        ...,
        description="Estimated time in minutes",
        ge=1
    )
    maximum_allowed_time: Optional[float] = Field(
        None,
        description="Max time before timeout"
    )
    reward: float = Field(
        ...,
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
    
    filters: Optional[List[StudyFilter]] = Field(
        None,
        description="Direct filters (mutually exclusive with filter_set_id)"
    )
    filter_set_id: Optional[str] = Field(
        None,
        description="Filter set ID (mutually exclusive with filters)"
    )
    filter_set_version: Optional[int] = Field(
        None,
        description="Filter set version"
    )
    
    project: Optional[str] = Field(
        None,
        description="Project ID (uses default if not specified)"
    )
    
    internal_name: Optional[str] = Field(
        None,
        description="Internal tracking name"
    )
    naivety_distribution_rate: Optional[float] = Field(
        None,
        description="Naivety rate (0-100, null=auto)"
    )
    submissions_config: Optional[SubmissionsConfig] = Field(
        None,
        description="Advanced submission config"
    )
    study_labels: Optional[List[StudyLabel]] = Field(
        None,
        description="Study labels"
    )
    content_warnings: Optional[List[ContentWarning]] = Field(
        None,
        description="Content warnings"
    )
    content_warning_details: Optional[str] = Field(
        None,
        description="Content warning details"
    )
    metadata: Optional[str] = Field(
        None,
        description="Custom metadata"
    )
    credential_pool_id: Optional[str] = Field(
        None,
        description="Credential pool ID"
    )
    
    data_collection_method: Optional[DataCollectionMethod] = Field(
        None,
        description="Data collection method"
    )
    data_collection_id: Optional[str] = Field(
        None,
        description="Task Builder ID (required if data_collection_method set)"
    )
    data_collection_metadata: Optional[DataCollectionMetadata] = Field(
        None,
        description="Task Builder metadata"
    )
    
    access_details: Optional[List[AccessDetail]] = Field(
        None,
        description="Taskflow access details"
    )
    
    class Config:
        extra = "forbid"
        use_enum_values = True



class StudyUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    internal_name: Optional[str] = Field(None)
    description: Optional[str] = Field(None, min_length=1)
    external_study_url: Optional[str] = Field(None)
    prolific_id_option: Optional[ProlificIdOption] = Field(None)
    completion_codes: Optional[List[CompletionCode]] = Field(None)
    total_available_places: Optional[float] = Field(
        None,
        description="Can only increase after publish"
    )
    estimated_completion_time: Optional[float] = Field(None, ge=1)
    maximum_allowed_time: Optional[float] = Field(None)
    reward: Optional[float] = Field(None, ge=0)
    device_compatibility: Optional[List[DeviceCompatibility]] = Field(None)
    peripheral_requirements: Optional[List[PeripheralRequirement]] = Field(None)
    
    filters: Optional[List[StudyFilter]] = Field(None)
    filter_set_id: Optional[str] = Field(None)
    filter_set_version: Optional[int] = Field(None)
    
    submissions_config: Optional[SubmissionsConfig] = Field(None)
    study_labels: Optional[List[StudyLabel]] = Field(None)
    content_warnings: Optional[List[ContentWarning]] = Field(None)
    content_warning_details: Optional[str] = Field(None)
    metadata: Optional[str] = Field(None)
    
    credential_pool_id: Optional[str] = Field(None)
    has_credentials: Optional[bool] = Field(None)
    data_collection_method: Optional[DataCollectionMethod] = Field(None)
    data_collection_id: Optional[str] = Field(None)
    data_collection_metadata: Optional[DataCollectionMetadata] = Field(None)
    
    class Config:
        extra = "forbid"
        use_enum_values = True



class StudyTransitionRequest(BaseModel):
    action: StudyAction = Field(..., description="Transition action")
    
    class Config:
        use_enum_values = True



class StudyListResponse(BaseModel):
    results: List[ProlificStudy] = Field(
        default_factory=list,
        description="List of studies"
    )
    
    class Config:
        extra = "allow"


StudyID = str
ProjectID = str