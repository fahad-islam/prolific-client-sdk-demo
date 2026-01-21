"""
API operations for Prolific studies.
"""
from typing import List, Dict, Any, Optional
from ..http import ProlificHttpClient
from ..models.study import (
    ProlificStudy,
    StudyCreateRequest,
    StudyUpdateRequest,
    StudyTransitionRequest,
    StudyAction,
    StudyStatus,
    DeviceCompatibility,
    PeripheralRequirement,
    StudyListResponse,
)


def list_studies(
    client: ProlificHttpClient,
    project_id: Optional[str] = None,
    workspace_id: Optional[str] = None
) -> List[ProlificStudy]:
    """
    List studies, optionally filtered by project or workspace.
    
    Based on: GET /api/v1/studies/
    
    Args:
        client: HTTP client instance
        project_id: Optional project ID to filter by
        workspace_id: Optional workspace ID to filter by
    
    Returns:
        List of ProlificStudy instances
    
    Example:
        >>> # List all studies in a project
        >>> studies = list_studies(client, project_id="project_id")
        >>> for study in studies:
        ...     print(f"{study.name}: {study.status}")
    """
    params = {}
    if project_id:
        params["project"] = project_id
    if workspace_id:
        params["workspace"] = workspace_id
    
    response = client.get("/api/v1/studies/", params=params if params else None)
    
    study_response = StudyListResponse(**response)
    return study_response.results


def get_study(
    client: ProlificHttpClient,
    study_id: str
) -> ProlificStudy:
    """
    Get a specific study by ID.
    
    Based on: GET /api/v1/studies/{study_id}/
    
    Args:
        client: HTTP client instance
        study_id: Study ID to retrieve
    
    Returns:
        ProlificStudy instance
    
    Raises:
        ProlificNotFoundError: If study doesn't exist
    
    Example:
        >>> study = get_study(client, "study_id")
        >>> print(f"Status: {study.status}")
        >>> print(f"Places: {study.places_taken}/{study.total_available_places}")
    """
    response = client.get(f"/api/v1/studies/{study_id}/")
    return ProlificStudy(**response)


def create_study(
    client: ProlificHttpClient,
    project_id: str,
    name: str,
    internal_name: str,
    description: str,
    external_study_url: str,
    total_available_places: int,
    estimated_completion_time: int,
    reward: int,
    prolific_id_option: str = "url_parameters",
    completion_option: str = "url",
    completion_code: Optional[str] = None,
    device_compatibility: Optional[List[DeviceCompatibility]] = None,
    peripheral_requirements: Optional[List[PeripheralRequirement]] = None,
    filter_set_id: Optional[str] = None,
    filters: Optional[List[Dict[str, Any]]] = None
) -> ProlificStudy:
    """
    Create a new study.
    
    Based on: POST /api/v1/studies/
    
    Args:
        client: HTTP client instance
        project_id: Project ID to create study in
        name: Study name shown to participants
        internal_name: Internal tracking name (not shown to participants)
        description: Study description shown to participants
        external_study_url: URL to your external survey
        total_available_places: Number of participants needed
        estimated_completion_time: Estimated time in minutes
        reward: Reward in pence/cents (e.g., 150 = £1.50 or $1.50)
        prolific_id_option: How to pass Prolific ID ('url_parameters' or 'not_required')
        completion_option: Completion verification ('url' or 'code')
        completion_code: Completion code (required if completion_option='code')
        device_compatibility: List of compatible devices
        peripheral_requirements: List of required peripherals
        filter_set_id: Filter set ID for recruiting criteria
        filters: Direct filter specifications
    
    Returns:
        Created ProlificStudy instance
    
    Raises:
        ProlificValidationError: If validation fails
    
    Example:
        >>> study = create_study(
        ...     client=client,
        ...     project_id="project_id",
        ...     name="User Experience Survey",
        ...     internal_name="ux_survey_2024_q1",
        ...     description="Help us improve our product",
        ...     external_study_url="https://survey.example.com/abc123",
        ...     total_available_places=100,
        ...     estimated_completion_time=10,
        ...     reward=150,  # £1.50 or $1.50
        ...     device_compatibility=[DeviceCompatibility.DESKTOP],
        ...     peripheral_requirements=[]
        ... )
        >>> print(f"Created study: {study.id}")
    """
    request = StudyCreateRequest(
        name=name,
        internal_name=internal_name,
        description=description,
        external_study_url=external_study_url,
        total_available_places=total_available_places,
        estimated_completion_time=estimated_completion_time,
        reward=reward,
        project=project_id,
        prolific_id_option=prolific_id_option,
        completion_option=completion_option,
        completion_code=completion_code,
        device_compatibility=device_compatibility or [DeviceCompatibility.DESKTOP],
        peripheral_requirements=peripheral_requirements or [],
        filter_set_id=filter_set_id,
        filters=filters
    )
    
    response = client.post(
        "/api/v1/studies/",
        json=request.model_dump(exclude_none=True)
    )
    
    return ProlificStudy(**response)


def update_study(
    client: ProlificHttpClient,
    study_id: str,
    name: Optional[str] = None,
    internal_name: Optional[str] = None,
    description: Optional[str] = None,
    external_study_url: Optional[str] = None,
    total_available_places: Optional[int] = None,
    estimated_completion_time: Optional[int] = None,
    reward: Optional[int] = None,
    completion_option: Optional[str] = None,
    completion_code: Optional[str] = None,
    device_compatibility: Optional[List[DeviceCompatibility]] = None,
    peripheral_requirements: Optional[List[PeripheralRequirement]] = None,
    filter_set_id: Optional[str] = None,
    filters: Optional[List[Dict[str, Any]]] = None
) -> ProlificStudy:
    """
    Update an existing study.
    
    Based on: PATCH /api/v1/studies/{study_id}/
    
    Note: Many fields can only be updated while study is UNPUBLISHED.
    After publishing, only total_available_places can be modified (and only increased).
    
    Args:
        client: HTTP client instance
        study_id: Study ID to update
        name: New study name (before publish only)
        internal_name: New internal name (before publish only)
        description: New description (before publish only)
        external_study_url: New survey URL (before publish only)
        total_available_places: New total places (can increase after publish)
        estimated_completion_time: New estimated time (before publish only)
        reward: New reward amount (before publish only)
        completion_option: New completion option (before publish only)
        completion_code: New completion code (before publish only)
        device_compatibility: New device compatibility (before publish only)
        peripheral_requirements: New peripheral requirements (before publish only)
        filter_set_id: New filter set ID (before publish only)
        filters: New direct filters (before publish only)
    
    Returns:
        Updated ProlificStudy instance
    
    Raises:
        ProlificValidationError: If validation fails or update not allowed
    
    Example (before publish):
        >>> study = update_study(
        ...     client=client,
        ...     study_id="study_id",
        ...     name="Updated Study Name",
        ...     reward=200
        ... )
    
    Example (after publish - only increase places):
        >>> study = update_study(
        ...     client=client,
        ...     study_id="study_id",
        ...     total_available_places=150  # Increased from 100
        ... )
    """
    update_data = {}
    if name is not None:
        update_data["name"] = name
    if internal_name is not None:
        update_data["internal_name"] = internal_name
    if description is not None:
        update_data["description"] = description
    if external_study_url is not None:
        update_data["external_study_url"] = external_study_url
    if total_available_places is not None:
        update_data["total_available_places"] = total_available_places
    if estimated_completion_time is not None:
        update_data["estimated_completion_time"] = estimated_completion_time
    if reward is not None:
        update_data["reward"] = reward
    if completion_option is not None:
        update_data["completion_option"] = completion_option
    if completion_code is not None:
        update_data["completion_code"] = completion_code
    if device_compatibility is not None:
        update_data["device_compatibility"] = device_compatibility
    if peripheral_requirements is not None:
        update_data["peripheral_requirements"] = peripheral_requirements
    if filter_set_id is not None:
        update_data["filter_set_id"] = filter_set_id
    if filters is not None:
        update_data["filters"] = filters
    
    if not update_data:
        return get_study(client, study_id)
    
    update_request = StudyUpdateRequest(**update_data)
    
    response = client.patch(
        f"/api/v1/studies/{study_id}/",
        json=update_request.model_dump(exclude_none=True)
    )
    
    return ProlificStudy(**response)


def transition_study(
    client: ProlificHttpClient,
    study_id: str,
    action: StudyAction
) -> ProlificStudy:
    """
    Transition study state (publish, start, pause, stop).
    
    Based on: POST /api/v1/studies/{study_id}/transition/
    
    Valid transitions:
    - UNPUBLISHED -> ACTIVE: action=StudyAction.PUBLISH
    - PAUSED -> ACTIVE: action=StudyAction.START (resume recruiting)
    - ACTIVE -> PAUSED: action=StudyAction.PAUSE
    - ACTIVE/PAUSED -> COMPLETED: action=StudyAction.STOP
    
    Args:
        client: HTTP client instance
        study_id: Study ID to transition
        action: Transition action (PUBLISH, START, PAUSE, STOP)
    
    Returns:
        Updated ProlificStudy instance
    
    Raises:
        ProlificValidationError: If transition not allowed from current state
    
    Example:
        >>> # Publish a draft study
        >>> study = transition_study(client, "study_id", StudyAction.PUBLISH)
        >>> assert study.status == StudyStatus.ACTIVE
    """
    request = StudyTransitionRequest(action=action)
    
    response = client.post(
        f"/api/v1/studies/{study_id}/transition/",
        json=request.model_dump()
    )
    
    return ProlificStudy(**response)


def publish_study(client: ProlificHttpClient, study_id: str) -> ProlificStudy:
    """
    Publish a draft study.
    
    Convenience method for: transition_study(client, study_id, StudyAction.PUBLISH)
    
    Example:
        >>> study = publish_study(client, "study_id")
        >>> print(f"Published! Status: {study.status}")
    """
    return transition_study(client, study_id, StudyAction.PUBLISH)


def start_recruiting(client: ProlificHttpClient, study_id: str) -> ProlificStudy:
    """
    Start/resume recruiting for a paused study.
    
    Convenience method for: transition_study(client, study_id, StudyAction.START)
    
    Example:
        >>> study = start_recruiting(client, "study_id")
        >>> print(f"Recruiting resumed: {study.status}")
    """
    return transition_study(client, study_id, StudyAction.START)


def pause_recruiting(client: ProlificHttpClient, study_id: str) -> ProlificStudy:
    """
    Pause recruiting for an active study.
    
    Convenience method for: transition_study(client, study_id, StudyAction.PAUSE)
    
    Example:
        >>> study = pause_recruiting(client, "study_id")
        >>> print(f"Recruiting paused: {study.status}")
    """
    return transition_study(client, study_id, StudyAction.PAUSE)


def stop_study(client: ProlificHttpClient, study_id: str) -> ProlificStudy:
    """
    Stop/complete a study.
    
    Convenience method for: transition_study(client, study_id, StudyAction.STOP)
    
    Example:
        >>> study = stop_study(client, "study_id")
        >>> print(f"Study completed: {study.status}")
    """
    return transition_study(client, study_id, StudyAction.STOP)


def increase_available_places(
    client: ProlificHttpClient,
    study_id: str,
    new_total: int
) -> ProlificStudy:
    """
    Increase available participant places.
    
    This can be done even after publishing. The new total must be greater
    than the current total_available_places.
    
    Args:
        client: HTTP client instance
        study_id: Study ID
        new_total: New total number of places (must be greater than current)
    
    Returns:
        Updated ProlificStudy instance
    
    Raises:
        ProlificValidationError: If new_total is not greater than current
    
    Example:
        >>> # Increase from 100 to 150
        >>> study = increase_available_places(client, "study_id", 150)
        >>> print(f"New total: {study.total_available_places}")
    """
    return update_study(client, study_id, total_available_places=new_total)


def find_study_by_name(
    client: ProlificHttpClient,
    name: str,
    project_id: Optional[str] = None
) -> Optional[ProlificStudy]:
    """
    Find a study by exact name match.
    
    Args:
        client: HTTP client instance
        name: Exact name to match
        project_id: Optional project ID to filter by
    
    Returns:
        ProlificStudy if found, None otherwise
    
    Example:
        >>> study = find_study_by_name(client, "User Survey", "project_id")
        >>> if study:
        ...     print(f"Found: {study.id}")
    """
    studies = list_studies(client, project_id=project_id)
    
    for study in studies:
        if study.name == name:
            return study
    
    return None


def find_study_by_internal_name(
    client: ProlificHttpClient,
    internal_name: str,
    project_id: Optional[str] = None
) -> Optional[ProlificStudy]:
    """
    Find a study by exact internal_name match.
    
    Args:
        client: HTTP client instance
        internal_name: Exact internal name to match
        project_id: Optional project ID to filter by
    
    Returns:
        ProlificStudy if found, None otherwise
    
    Example:
        >>> study = find_study_by_internal_name(client, "ux_survey_2024_q1")
        >>> if study:
        ...     print(f"Found: {study.id}")
    """
    studies = list_studies(client, project_id=project_id)
    
    for study in studies:
        if study.internal_name == internal_name:
            return study
    
    return None


def get_study_progress(
    client: ProlificHttpClient,
    study_id: str
) -> Dict[str, Any]:
    """
    Get study progress information.
    
    Args:
        client: HTTP client instance
        study_id: Study ID
    
    Returns:
        Dictionary with progress information
    
    Example:
        >>> progress = get_study_progress(client, "study_id")
        >>> print(f"Progress: {progress['percentage_complete']}%")
        >>> print(f"Remaining: {progress['places_remaining']}")
    """
    study = get_study(client, study_id)
    
    places_remaining = study.total_available_places - study.places_taken
    percentage_complete = (
        (study.places_taken / study.total_available_places * 100)
        if study.total_available_places > 0
        else 0
    )
    
    return {
        "study_id": study.id,
        "status": study.status,
        "places_taken": study.places_taken,
        "total_available_places": study.total_available_places,
        "places_remaining": places_remaining,
        "percentage_complete": round(percentage_complete, 2),
        "is_complete": study.status == StudyStatus.COMPLETED
    }