"""
API operations for Prolific projects.
"""
from prolific_client.models.user import User
from typing import List, Dict, Any, Optional
from ..http import ProlificHttpClient
from ..models.project import (
    ProlificProject,
    ProjectCreateRequest,
    ProjectUpdateRequest,
    ProjectListResponse,
)


def list_projects(
    client: ProlificHttpClient, workspace_id: str
) -> List[ProlificProject]:
    response = client.get(
        f"/api/v1/workspaces/{workspace_id}/projects/",
    )
    project_response = ProjectListResponse(**response)
    return project_response.results


def get_project(client: ProlificHttpClient, project_id: str) -> ProlificProject:
    response = client.get(f"/api/v1/projects/{project_id}/")
    return ProlificProject(**response)


def create_project(
    client: ProlificHttpClient,
    workspace_id: str,
    title: str,
    description: Optional[str] = None,
    naivety_distribution_rate: Optional[int] = None,
) -> ProlificProject:
    request = ProjectCreateRequest(
        workspace=workspace_id,
        title=title,
        description=description,
        naivety_distribution_rate=naivety_distribution_rate,
    )

    response = client.post(
        f"/api/v1/workspaces/{workspace_id}/projects/",
        json=request.model_dump(exclude_none=True),
    )

    return ProlificProject(**response)


def update_project(
    client: ProlificHttpClient,
    project_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    naivety_distribution_rate: Optional[int] = None,
    owner: Optional[str] = None,
    workspace: Optional[str] = None,
    users: Optional[List[User]] = None,
    extra_body_params: Optional[Dict[str, Any]] = None,
) -> ProlificProject:
    update_data = {**(extra_body_params or {})}
    if title is not None:
        update_data["title"] = title
    if description is not None:
        update_data["description"] = description
    if owner is not None:
        update_data["owner"] = owner
    if workspace is not None:
        update_data["workspace"] = workspace
    if naivety_distribution_rate is not None:
        update_data["naivety_distribution_rate"] = naivety_distribution_rate
    if users is not None:
        update_data["users"] = users

    if not update_data:
        return get_project(client, project_id)

    update_request = ProjectUpdateRequest(**update_data)

    response = client.patch(
        f"/api/v1/projects/{project_id}/",
        json={**update_request.model_dump(exclude_none=True), **extra_body_params},
    )

    return ProlificProject(**response)


def find_project_by_title(
    client: ProlificHttpClient, workspace_id: str, title: str
) -> Optional[ProlificProject]:
    projects = list_projects(client, workspace_id)

    for project in projects:
        if project.title == title:
            return project

    return None
