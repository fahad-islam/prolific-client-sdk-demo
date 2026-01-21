"""
API operations for Prolific filters and filter sets.
"""
from typing import List, Dict, Any, Optional
from ..http import ProlificHttpClient
from ..models.filters import (
    ProlificFilter,
    ProlificFilterSet,
    FilterDistribution,
    FilterSetCreateRequest,
    FilterSetUpdateRequest,
    FilterListResponse,
    FilterSetListResponse,
    FilterValue,
)


def list_filters(client: ProlificHttpClient, workspace_id: str) -> List[ProlificFilter]:
    """
    List available recruiting filters for a workspace.

    Based on: GET /api/v1/filters/?workspace_id={workspace_id}

    Args:
        client: HTTP client instance
        workspace_id: Workspace ID to get filters for

    Returns:
        List of ProlificFilter instances

    Example:
        >>> filters = list_filters(client, "workspace_id")
        >>> age_filter = [f for f in filters if f.filter_tag == "demographics"][0]
    """
    params = {"workspace_id": workspace_id}
    response = client.get("/api/v1/filters/", params=params)

    filter_response = FilterListResponse(**response)
    return filter_response.results


def get_filter_distribution(
    client: ProlificHttpClient, filter_id: str, workspace_id: str
) -> FilterDistribution:
    """
    Get distribution data for a specific filter.

    Based on: GET /api/v1/filters/{filter_id}/distribution/?workspace_id={workspace_id}

    Shows how many participants match each possible value of the filter.
    Useful for estimating reach before creating a study.

    Args:
        client: HTTP client instance
        filter_id: Filter ID to get distribution for
        workspace_id: Workspace ID

    Returns:
        FilterDistribution with participant counts per value

    Example:
        >>> dist = get_filter_distribution(client, "age_filter_id", "workspace_id")
        >>> print(f"Total participants: {dist.total_participants}")
        >>> for point in dist.distribution:
        ...     print(f"{point.label}: {point.count} participants")
    """
    params = {"workspace_id": workspace_id}
    response = client.get(f"/api/v1/filters/{filter_id}/distribution/", params=params)

    return FilterDistribution(**response)


def list_filter_sets(
    client: ProlificHttpClient,
    workspace_id: Optional[str] = None,
    organisation_id: Optional[str] = None,
) -> List[ProlificFilterSet]:
    """
    List all filter sets in a workspace.

    Based on: GET /api/v1/filter-sets/

    Args:
        client: HTTP client instance
        workspace_id: Workspace ID

    Returns:
        List of ProlificFilterSet instances

    Example:
        >>> filter_sets = list_filter_sets(client, "workspace_id")
        >>> for fs in filter_sets:
        ...     print(f"{fs.name} (v{fs.version})")
    """
    params = {}

    if workspace_id is not None:
        params["workspace_id"] = workspace_id

    if organisation_id is not None:
        params["organisation_id"] = organisation_id

    response = client.get(f"/api/v1/filter-sets/", params=params)

    filter_set_response = FilterSetListResponse(**response)
    return filter_set_response.results


def get_filter_set(
    client: ProlificHttpClient, filter_set_id: str, version_number: Optional[int] = None
) -> ProlificFilterSet:
    """
    Get a specific filter set by ID.

    Based on: GET /api/v1/filter-sets/{filter_set_id}/

    Args:
        client: HTTP client instance
        filter_set_id: Filter set ID to retrieve

    Returns:
        ProlificFilterSet instance

    Example:
        >>> filter_set = get_filter_set(client, "filter_set_id")
        >>> print(f"Filters: {len(filter_set.filters)}")
        >>> print(f"Estimated reach: {filter_set.estimated_participants}")
    """
    params = {}

    if version_number is not None:
        params["version_number"] = version_number

    response = client.get(
        f"/api/v1/filter-sets/{filter_set_id}/", params=params if params else None
    )
    return ProlificFilterSet(**response)


def create_filter_set(
    client: ProlificHttpClient,
    name: Optional[str] = None,
    workspace_id: Optional[str] = None,
    organisation_id: Optional[str] = None,
    filters: Optional[List[FilterValue]] = None,
) -> ProlificFilterSet:
    """
    Create a new filter set.

    Based on: POST /api/v1/filter-sets/

    Args:
        client: HTTP client instance
        name: Name for the filter set
        workspace_id: Workspace ID where filter set will be created
        filters: List of FilterValue objects defining the criteria

    Returns:
        Created ProlificFilterSet instance

    Raises:
        ProlificValidationError: If validation fails

    Example:
        >>> from prolific_client.models.filters import FilterValue
        >>>
        >>> filters = [
        ...     FilterValue(
        ...         filter_id="age_range_filter_id",
        ...         range_value={"min": 25, "max": 45}
        ...     ),
        ...     FilterValue(
        ...         filter_id="country_filter_id",
        ...         selected_values=["US", "UK", "CA"]
        ...     )
        ... ]
        >>>
        >>> filter_set = create_filter_set(
        ...     client=client,
        ...     name="US/UK/CA Adults 25-45",
        ...     workspace_id="workspace_id",
        ...     filters=filters
        ... )
        >>> print(f"Created filter set: {filter_set.id} (v{filter_set.version})")
    """
    request = FilterSetCreateRequest(
        name=name, workspace_id=workspace_id, filters=filters, organisation_id=organisation_id
    )

    response = client.post(
        "/api/v1/filter-sets/", json=request.model_dump(exclude_none=True)
    )

    return ProlificFilterSet(**response)


def patch_filter_set(
    client: ProlificHttpClient,
    filter_set_id: str,
    name: Optional[str] = None,
    filters: Optional[List[FilterValue]] = None,
) -> ProlificFilterSet:
    """
    Update an existing filter set (creates a new version).

    Based on: PATCH /api/v1/filter-sets/{filter_set_id}/

    Note: Updating a filter set increments its version number.
    Only provided fields are updated.

    Args:
        client: HTTP client instance
        filter_set_id: Filter set ID to update
        name: New name (optional)
        filters: New filter list (optional, replaces entire list)

    Returns:
        Updated ProlificFilterSet instance with incremented version

    Raises:
        ProlificValidationError: If validation fails

    Example:
        >>> # Update just the name
        >>> updated = patch_filter_set(
        ...     client=client,
        ...     filter_set_id="filter_set_id",
        ...     name="Updated Name"
        ... )
        >>> print(f"Version incremented: {updated.version}")
        >>>
        >>> # Update filters
        >>> new_filters = [
        ...     FilterValue(
        ...         filter_id="age_range_filter_id",
        ...         range_value={"min": 30, "max": 50}
        ...     )
        ... ]
        >>> updated = patch_filter_set(
        ...     client=client,
        ...     filter_set_id="filter_set_id",
        ...     filters=new_filters
        ... )
    """
    update_data = {}
    if name is not None:
        update_data["name"] = name
    if filters is not None:
        update_data["filters"] = filters

    update_request = FilterSetUpdateRequest(**update_data)

    response = client.patch(
        f"/api/v1/filter-sets/{filter_set_id}/",
        json=update_request.model_dump(exclude_none=True),
    )

    return ProlificFilterSet(**response)


def find_filter_set_by_name(
    client: ProlificHttpClient, workspace_id: str, name: str
) -> Optional[ProlificFilterSet]:
    """
    Find a filter set by exact name match.

    Args:
        client: HTTP client instance
        workspace_id: Workspace ID to search in
        name: Exact name to match

    Returns:
        ProlificFilterSet if found (latest version), None otherwise

    Example:
        >>> filter_set = find_filter_set_by_name(client, "ws_id", "My Filter Set")
        >>> if filter_set:
        ...     print(f"Found: {filter_set.id} (v{filter_set.version})")
    """
    filter_sets = list_filter_sets(client, workspace_id)

    matches = [fs for fs in filter_sets if fs.name == name]

    if not matches:
        return None

    return max(matches, key=lambda fs: fs.version)


def estimate_participant_pool(
    client: ProlificHttpClient, workspace_id: str, filters: List[FilterValue]
) -> int:
    """
    Estimate participant pool size for a set of filters.

    Creates a temporary filter set to get the estimated_participants count,
    then returns the estimate. Does not save the filter set.

    Args:
        client: HTTP client instance
        workspace_id: Workspace ID
        filters: List of filter values to estimate for

    Returns:
        Estimated number of participants (0 if not available)

    Example:
        >>> filters = [
        ...     FilterValue(
        ...         filter_id="country_filter_id",
        ...         selected_values=["US"]
        ...     )
        ... ]
        >>> estimate = estimate_participant_pool(client, "ws_id", filters)
        >>> print(f"Estimated reach: {estimate} participants")
    """
    temp_name = f"_temp_estimate_{hash(str(filters))}"
    filter_set = create_filter_set(
        client=client, name=temp_name, workspace_id=workspace_id, filters=filters
    )

    return filter_set.estimated_participants or 0


def get_custom_groups(
    client: ProlificHttpClient, workspace_id: str
) -> List[ProlificFilter]:
    """
    Get all custom group filters.

    Custom groups are participant groups you've created.
    Uses filter_tag="custom-group" query parameter.

    Args:
        client: HTTP client instance
        workspace_id: Workspace ID

    Returns:
        List of custom group filters

    Example:
        >>> custom_groups = get_custom_groups(client, "workspace_id")
        >>> for group in custom_groups:
        ...     print(f"{group.title}: {group.description}")
    """
    params = {"workspace_id": workspace_id, "filter_tag": "custom-group"}
    response = client.get("/api/v1/filters/", params=params)
    filter_response = FilterListResponse(**response)
    return filter_response.results


def search_filters_by_title(
    client: ProlificHttpClient, title_query: str, workspace_id: str
) -> List[ProlificFilter]:
    """
    Search filters by title (case-insensitive substring match).

    Args:
        client: HTTP client instance
        title_query: Search query for filter title
        workspace_id: Workspace ID

    Returns:
        List of matching filters

    Example:
        >>> # Find all age-related filters
        >>> age_filters = search_filters_by_title(client, "age", "workspace_id")
        >>> for f in age_filters:
        ...     print(f.title)
    """
    all_filters = list_filters(client, workspace_id)
    query_lower = title_query.lower()
    return [f for f in all_filters if query_lower in f.title.lower()]
