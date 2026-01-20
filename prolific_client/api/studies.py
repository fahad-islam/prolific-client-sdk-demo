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
    StudyStatus
)


def list_studies(
    client: ProlificHttpClient,
    project_id: Optional[str] = None,
    workspace_id: Optional[str] = None
) -> List[ProlificStudy]:
    """
    List studies, optionally filtered by project or workspace.
    
    Args:
        client: HTTP client instance
        project_id: Optional project ID to filter by
        workspace_id: Optional workspace ID to filter by
    
    Returns:
        List of ProlificStudy instances
    """
    params = {}
    if project_id:
        params["project"] = project_id
    if workspace_id:
        params["workspace"] = workspace_id
    
    response = client.get("/api/v1/studies/", params=params if params else None)
    
    if "results" in response:
        studies = [ProlificStudy(**study) for study in response["results"]]
    else:
        studies = [ProlificStudy(**study) for study in response] if isinstance(response, list) else []
    
    return studies


def get_study(
    client: ProlificHttpClient,
    study_id: str
) -> ProlificStudy:
    """
    Get a specific study by ID.
    
    Args:
        client: HTTP client instance
        study_id: Study ID to retrieve
    
    Returns:
        ProlificStudy instance
    
    Raises:
        ProlificNotFoundError: If study doesn't exist
    """
    response = client.get(f"/api/v1/studies/{study_id}/")
    return ProlificStudy(**response)


def create_study(
    client: ProlificHttpClient,
    payload: Dict[str, Any]
) -> ProlificStudy:
    """
    Create a new study.
    
    Args:
        client: HTTP client instance
        payload: Study creation payload (validated against StudyCreateRequest)
    
    Returns:
        Created ProlificStudy instance
    
    Raises:
        ProlificValidationError: If validation fails
    """
    request = StudyCreateRequest(**payload)
    
    response = client.post(
        "/api/v1/studies/",
        json=request.model_dump(exclude_none=True)
    )
    
    return ProlificStudy(**response)


def patch_study(
    client: ProlificHttpClient,
    study_id: str,
    patch: Dict[str, Any]
) -> ProlificStudy:
    """
    Update an existing study.
    
    Note: Many fields can only be updated while study is UNPUBLISHED.
    After publishing, only certain fields like total_available_places can be modified.
    
    Args:
        client: HTTP client instance
        study_id: Study ID to update
        patch: Dictionary of fields to update
    
    Returns:
        Updated ProlificStudy instance
    
    Raises:
        ProlificValidationError: If validation fails or update not allowed
    """
    update_request = StudyUpdateRequest(**patch)
    
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
    
    Valid transitions:
    - UNPUBLISHED -> ACTIVE: action="PUBLISH"
    - ACTIVE -> ACTIVE: action="START" (resume recruiting)
    - ACTIVE -> PAUSED: action="PAUSE"
    - ACTIVE -> COMPLETED: action="STOP"
    
    Args:
        client: HTTP client instance
        study_id: Study ID to transition
        action: Transition action (PUBLISH, START, PAUSE, STOP)
    
    Returns:
        Updated ProlificStudy instance
    
    Raises:
        ProlificValidationError: If transition not allowed
    """
    request = StudyTransitionRequest(action=action)
    
    response = client.post(
        f"/api/v1/studies/{study_id}/transition/",
        json=request.model_dump()
    )
    
    return ProlificStudy(**response)


def publish_study(client: ProlificHttpClient, study_id: str) -> ProlificStudy:
    """Publish a draft study (convenience method)."""
    return transition_study(client, study_id, StudyAction.PUBLISH)


def start_recruiting(client: ProlificHttpClient, study_id: str) -> ProlificStudy:
    """Start/resume recruiting (convenience method)."""
    return transition_study(client, study_id, StudyAction.START)


def pause_recruiting(client: ProlificHttpClient, study_id: str) -> ProlificStudy:
    """Pause recruiting (convenience method)."""
    return transition_study(client, study_id, StudyAction.PAUSE)


def stop_study(client: ProlificHttpClient, study_id: str) -> ProlificStudy:
    """Stop/complete study (convenience method)."""
    return transition_study(client, study_id, StudyAction.STOP)


def increase_available_places(
    client: ProlificHttpClient,
    study_id: str,
    new_total: int
) -> ProlificStudy:
    """
    Increase available participant places (can be done after publishing).
    
    Args:
        client: HTTP client instance
        study_id: Study ID
        new_total: New total number of places (must be greater than current)
    
    Returns:
        Updated ProlificStudy instance
    
    Raises:
        ProlificValidationError: If new_total is not greater than current
    """
    return patch_study(client, study_id, {"total_available_places": new_total})


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
    """
    studies = list_studies(client, project_id=project_id)
    
    for study in studies:
        if study.name == name:
            return study
    
    return None
