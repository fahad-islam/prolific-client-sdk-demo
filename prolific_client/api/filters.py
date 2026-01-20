"""
API operations for Prolific filters and filter sets.
"""
from typing import List, Dict, Any, Optional
from ..http import ProlificHttpClient
from ..models.filters import (
    ProlificFilter,
    ProlificFilterSet,
    FilterSetCreateRequest,
    FilterSetUpdateRequest,
    FilterListResponse
)


def list_filters(
    client: ProlificHttpClient,
    workspace_id: str,
    filter_tag: Optional[str] = None
) -> List[ProlificFilter]:
    """
    List available recruiting filters.
    
    Args:
        client: HTTP client instance
        workspace_id: Workspace ID
        filter_tag: Optional tag to filter by category
    
    Returns:
        List of ProlificFilter instances
    """
    params = {"workspace": workspace_id}
    if filter_tag:
        params["filter_tag"] = filter_tag
    
    response = client.get("/api/v1/filters/", params=params)
    
    # Parse response
    if "results" in response:
        filters = [ProlificFilter(**f) for f in response["results"]]
    else:
        filters = [ProlificFilter(**f) for f in response] if isinstance(response, list) else []
    
    return filters


def get_filter(
    client: ProlificHttpClient,
    filter_id: str
) -> ProlificFilter:
    """
    Get a specific filter by ID.
    
    Args:
        client: HTTP client instance
        filter_id: Filter ID to retrieve
    
    Returns:
        ProlificFilter instance
    """
    response = client.get(f"/api/v1/filters/{filter_id}/")
    return ProlificFilter(**response)


def list_filter_sets(
    client: ProlificHttpClient,
    workspace_id: str
) -> List[ProlificFilterSet]:
    """
    List all filter sets in a workspace.
    
    Args:
        client: HTTP client instance
        workspace_id: Workspace ID
    
    Returns:
        List of ProlificFilterSet instances
    """
    params = {"workspace": workspace_id}
    response = client.get("/api/v1/filter-sets/", params=params)
    
    if "results" in response:
        filter_sets = [ProlificFilterSet(**fs) for fs in response["results"]]
    else:
        filter_sets = [ProlificFilterSet(**fs) for fs in response] if isinstance(response, list) else []
    
    return filter_sets


def get_filter_set(
    client: ProlificHttpClient,
    filter_set_id: str
) -> ProlificFilterSet:
    """
    Get a specific filter set by ID.
    
    Args:
        client: HTTP client instance
        filter_set_id: Filter set ID to retrieve
    
    Returns:
        ProlificFilterSet instance
    """
    response = client.get(f"/api/v1/filter-sets/{filter_set_id}/")
    return ProlificFilterSet(**response)


def create_filter_set(
    client: ProlificHttpClient,
    payload: Dict[str, Any]
) -> ProlificFilterSet:
    """
    Create a new filter set.
    
    Args:
        client: HTTP client instance
        payload: Filter set creation payload (validated against FilterSetCreateRequest)
    
    Returns:
        Created ProlificFilterSet instance
    
    Raises:
        ProlificValidationError: If validation fails
    """
    request = FilterSetCreateRequest(**payload)
    
    response = client.post(
        "/api/v1/filter-sets/",
        json=request.model_dump(exclude_none=True)
    )
    
    return ProlificFilterSet(**response)


def patch_filter_set(
    client: ProlificHttpClient,
    filter_set_id: str,
    payload: Dict[str, Any]
) -> ProlificFilterSet:
    """
    Update an existing filter set (creates a new version).
    
    Args:
        client: HTTP client instance
        filter_set_id: Filter set ID to update
        payload: Update payload (validated against FilterSetUpdateRequest)
    
    Returns:
        Updated ProlificFilterSet instance with incremented version
    
    Raises:
        ProlificValidationError: If validation fails
    """
    update_request = FilterSetUpdateRequest(**payload)
    
    response = client.patch(
        f"/api/v1/filter-sets/{filter_set_id}/",
        json=update_request.model_dump(exclude_none=True)
    )
    
    return ProlificFilterSet(**response)


def find_filter_set_by_name(
    client: ProlificHttpClient,
    workspace_id: str,
    name: str
) -> Optional[ProlificFilterSet]:
    """
    Find a filter set by exact name match.
    
    Args:
        client: HTTP client instance
        workspace_id: Workspace ID to search in
        name: Exact name to match
    
    Returns:
        ProlificFilterSet if found (latest version), None otherwise
    """
    filter_sets = list_filter_sets(client, workspace_id)
    
    matches = [fs for fs in filter_sets if fs.name == name]
    
    if not matches:
        return None
    
    return max(matches, key=lambda fs: fs.version)


def find_filter_by_tag(
    client: ProlificHttpClient,
    workspace_id: str,
    filter_tag: str
) -> List[ProlificFilter]:
    """
    Find filters by tag (convenience method).
    
    Args:
        client: HTTP client instance
        workspace_id: Workspace ID
        filter_tag: Filter tag to search for
    
    Returns:
        List of matching ProlificFilter instances
    """
    return list_filters(client, workspace_id, filter_tag=filter_tag)
