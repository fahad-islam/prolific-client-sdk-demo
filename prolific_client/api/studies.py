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
    StudyListResponse, DataCollectionMethod, StudyLabel, StudyFilter,
)


def list_studies(
    client: ProlificHttpClient,
    project_id: Optional[str] = None,
    workspace_id: Optional[str] = None
) -> List[ProlificStudy]:
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
    response = client.get(f"/api/v1/studies/{study_id}/")
    return ProlificStudy(**response)


def create_study(
    client: ProlificHttpClient,
    name: str,
    description: str,
    external_study_url: str,
    prolific_id_option: str,
    completion_codes: List[Dict[str, Any]],
    total_available_places: float,
    estimated_completion_time: float,
    reward: float,
    internal_name: Optional[str] = None,
    project: Optional[str] = None,
    device_compatibility: Optional[List[str]] = None,
    peripheral_requirements: Optional[List[str]] = None,
    filters: Optional[List[Dict[str, Any]]] = None,
    filter_set_id: Optional[str] = None,
    filter_set_version: Optional[int] = None,
    naivety_distribution_rate: Optional[float] = None,
    submissions_config: Optional[Dict[str, Any]] = None,
    study_labels: Optional[List[str]] = None,
    content_warnings: Optional[List[str]] = None,
    content_warning_details: Optional[str] = None,
    metadata: Optional[str] = None,
    maximum_allowed_time: Optional[float] = None,
    **kwargs: Any
) -> ProlificStudy:
    
    payload: Dict[str, Any] = {
        "name": name,
        "description": description,
        "external_study_url": external_study_url,
        "prolific_id_option": prolific_id_option,
        "completion_codes": completion_codes,
        "total_available_places": total_available_places,
        "estimated_completion_time": estimated_completion_time,
        "reward": reward,
    }
    
    if internal_name is not None:
        payload["internal_name"] = internal_name
    if project is not None:
        payload["project"] = project
    if device_compatibility is not None:
        payload["device_compatibility"] = device_compatibility
    if peripheral_requirements is not None:
        payload["peripheral_requirements"] = peripheral_requirements
    if filters is not None:
        payload["filters"] = filters
    if filter_set_id is not None:
        payload["filter_set_id"] = filter_set_id
    if filter_set_version is not None:
        payload["filter_set_version"] = filter_set_version
    if naivety_distribution_rate is not None:
        payload["naivety_distribution_rate"] = naivety_distribution_rate
    if submissions_config is not None:
        payload["submissions_config"] = submissions_config
    if study_labels is not None:
        payload["study_labels"] = study_labels
    if content_warnings is not None:
        payload["content_warnings"] = content_warnings
    if content_warning_details is not None:
        payload["content_warning_details"] = content_warning_details
    if metadata is not None:
        payload["metadata"] = metadata
    if maximum_allowed_time is not None:
        payload["maximum_allowed_time"] = maximum_allowed_time
    
    payload.update(kwargs)
    
    request = StudyCreateRequest(**payload)
    
    response = client.post(
        "/api/v1/studies/",
        json=request.model_dump(exclude_none=True)
    )
    
    return ProlificStudy(**response)


def patch_study(
    client: ProlificHttpClient,
    study_id: str,
    name: Optional[str] = None,
    internal_name: Optional[str] = None,
    description: Optional[str] = None,
    external_study_url: Optional[str] = None,
    prolific_id_option: Optional[str] = None,
    completion_codes: Optional[List[Dict[str, Any]]] = None,
    total_available_places: Optional[float] = None,
    estimated_completion_time: Optional[float] = None,
    maximum_allowed_time: Optional[float] = None,
    reward: Optional[float] = None,
    device_compatibility: Optional[List[DeviceCompatibility]] = None,
    peripheral_requirements: Optional[List[PeripheralRequirement]] = None,
    filters: Optional[List[StudyFilter]] = None,
    filter_set_id: Optional[str] = None,
    filter_set_version: Optional[int] = None,
    project: Optional[str] = None,
    submissions_config: Optional[Dict[str, Any]] = None,
    study_labels: Optional[List[StudyLabel]] = None,
    content_warnings: Optional[List[str]] = None,
    content_warning_details: Optional[str] = None,
    metadata: Optional[str] = None,
    credential_pool_id: Optional[str] = None,
    has_credentials: Optional[bool] = None,
    data_collection_method: Optional[DataCollectionMethod] = None,
    data_collection_id: Optional[str] = None,
    data_collection_metadata: Optional[Dict[str, Any]] = None,
    **kwargs: Any
) -> ProlificStudy:
    
    update_data: Dict[str, Any] = {}
    
    if name is not None:
        update_data["name"] = name
    if internal_name is not None:
        update_data["internal_name"] = internal_name
    if description is not None:
        update_data["description"] = description
    if external_study_url is not None:
        update_data["external_study_url"] = external_study_url
    if prolific_id_option is not None:
        update_data["prolific_id_option"] = prolific_id_option
    if completion_codes is not None:
        update_data["completion_codes"] = completion_codes
    if total_available_places is not None:
        update_data["total_available_places"] = total_available_places
    if estimated_completion_time is not None:
        update_data["estimated_completion_time"] = estimated_completion_time
    if maximum_allowed_time is not None:
        update_data["maximum_allowed_time"] = maximum_allowed_time
    if reward is not None:
        update_data["reward"] = reward
    if device_compatibility is not None:
        update_data["device_compatibility"] = device_compatibility
    if peripheral_requirements is not None:
        update_data["peripheral_requirements"] = peripheral_requirements
    if filters is not None:
        update_data["filters"] = filters
    if filter_set_id is not None:
        update_data["filter_set_id"] = filter_set_id
    if filter_set_version is not None:
        update_data["filter_set_version"] = filter_set_version
    if submissions_config is not None:
        update_data["submissions_config"] = submissions_config
    if study_labels is not None:
        update_data["study_labels"] = study_labels
    if content_warnings is not None:
        update_data["content_warnings"] = content_warnings
    if content_warning_details is not None:
        update_data["content_warning_details"] = content_warning_details
    if metadata is not None:
        update_data["metadata"] = metadata
    if data_collection_metadata is not None:
        update_data["data_collection_metadata"] = data_collection_metadata
    if credential_pool_id is not None:
        update_data["credential_pool_id"] = credential_pool_id
    if has_credentials is not None:
        update_data["has_credentials"] = has_credentials
    if data_collection_method is not None:
        update_data["data_collection_method"] = data_collection_method
    if data_collection_id is not None:
        update_data["data_collection_id"] = data_collection_id
    
    update_data.update(kwargs)
    
    if not update_data:
        raise ValueError("At least one field must be provided for update")
    
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
    request = StudyTransitionRequest(action=action)
    
    response = client.post(
        f"/api/v1/studies/{study_id}/transition/",
        json=request.model_dump()
    )
    
    return ProlificStudy(**response)


def publish_study(client: ProlificHttpClient, study_id: str) -> ProlificStudy:
    return transition_study(client, study_id, StudyAction.PUBLISH)


def start_recruiting(client: ProlificHttpClient, study_id: str) -> ProlificStudy:
    return transition_study(client, study_id, StudyAction.START)


def pause_recruiting(client: ProlificHttpClient, study_id: str) -> ProlificStudy:
    return transition_study(client, study_id, StudyAction.PAUSE)


def stop_study(client: ProlificHttpClient, study_id: str) -> ProlificStudy:
    return transition_study(client, study_id, StudyAction.STOP)


def increase_available_places(
    client: ProlificHttpClient,
    study_id: str,
    new_total: int
) -> ProlificStudy:
    return patch_study(client, study_id, total_available_places=new_total)


def find_study_by_name(
    client: ProlificHttpClient,
    name: str,
    project_id: Optional[str] = None
) -> Optional[ProlificStudy]:
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
    studies = list_studies(client, project_id=project_id)
    
    for study in studies:
        if study.internal_name == internal_name:
            return study
    
    return None


def get_study_progress(
    client: ProlificHttpClient,
    study_id: str
) -> Dict[str, Any]:
    study = get_study(client, study_id)
    
    total_places = study.total_available_places or 0
    places_taken = study.places_taken or 0
    
    places_remaining = total_places - places_taken
    percentage_complete = (
        (places_taken / total_places * 100)
        if total_places > 0
        else 0
    )
    
    return {
        "study_id": study.id,
        "status": study.status,
        "places_taken": places_taken,
        "total_available_places": total_places,
        "places_remaining": places_remaining,
        "percentage_complete": round(percentage_complete, 2),
        "is_complete": study.status == StudyStatus.COMPLETED
    }