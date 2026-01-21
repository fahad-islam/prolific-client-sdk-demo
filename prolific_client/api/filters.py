"""
API operations for Prolific filters and filter sets.
"""
from typing import List, Optional
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
    params = {"workspace_id": workspace_id}
    response = client.get("/api/v1/filters/", params=params)

    filter_response = FilterListResponse(**response)
    return filter_response.results


def get_filter_distribution(
    client: ProlificHttpClient, filter_id: str, workspace_id: str
) -> FilterDistribution:
    params = {"workspace_id": workspace_id}
    response = client.get(f"/api/v1/filters/{filter_id}/distribution/", params=params)

    return FilterDistribution(**response)


def list_filter_sets(
    client: ProlificHttpClient,
    workspace_id: Optional[str] = None,
    organisation_id: Optional[str] = None,
) -> List[ProlificFilterSet]:
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
    filter_sets = list_filter_sets(client, workspace_id)

    matches = [fs for fs in filter_sets if fs.name == name]

    if not matches:
        return None

    return max(matches, key=lambda fs: fs.version)


def estimate_participant_pool(
    client: ProlificHttpClient, workspace_id: str, filters: List[FilterValue]
) -> int:
    temp_name = f"_temp_estimate_{hash(str(filters))}"
    filter_set = create_filter_set(
        client=client, name=temp_name, workspace_id=workspace_id, filters=filters
    )

    return filter_set.estimated_participants or 0


def get_custom_groups(
    client: ProlificHttpClient, workspace_id: str
) -> List[ProlificFilter]:
    params = {"workspace_id": workspace_id, "filter_tag": "custom-group"}
    response = client.get("/api/v1/filters/", params=params)
    filter_response = FilterListResponse(**response)
    return filter_response.results


def search_filters_by_title(
    client: ProlificHttpClient, title_query: str, workspace_id: str
) -> List[ProlificFilter]:
    all_filters = list_filters(client, workspace_id)
    query_lower = title_query.lower()
    return [f for f in all_filters if query_lower in f.title.lower()]
