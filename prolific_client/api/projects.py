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
    """
    List all projects in a workspace.

    Based on: GET /api/v1/projects/?workspace={workspace_id}

    Args:
        client: HTTP client instance
        workspace_id: Workspace ID to list projects from

    Returns:
        List of ProlificProject instances

    Raises:
        ProlificAPIError: On API errors

    Example:
        >>> projects = list_projects(client, "workspace_id")
        >>> for project in projects:
        ...     print(f"{project.title}: {len(project.users)} users")
    """
    response = client.get(
        f"/api/v1/workspaces/{workspace_id}/projects/",
    )
    project_response = ProjectListResponse(**response)
    return project_response.results


def get_project(client: ProlificHttpClient, project_id: str) -> ProlificProject:
    """
    Get a specific project by ID.

    Based on: GET /api/v1/projects/{project_id}/

    Args:
        client: HTTP client instance
        project_id: Project ID to retrieve

    Returns:
        ProlificProject instance

    Raises:
        ProlificAPIError: On API errors
        ProlificNotFoundError: If project doesn't exist

    Example:
        >>> project = get_project(client, "project_id")
        >>> print(f"Title: {project.title}")
        >>> print(f"Created: {project.created_at}")
    """
    response = client.get(f"/api/v1/projects/{project_id}/")
    return ProlificProject(**response)


def create_project(
    client: ProlificHttpClient,
    workspace_id: str,
    title: str,
    description: Optional[str] = None,
    naivety_distribution_rate: Optional[int] = None,
) -> ProlificProject:
    """
    Create a new project.

    Based on: POST /api/v1/projects/

    Args:
        client: HTTP client instance
        workspace_id: Workspace ID to create project in
        title: Project title (1-255 characters)
        description: Optional project description
        naivety_distribution_rate: Optional naivety distribution rate (0-100)

    Returns:
        Created ProlificProject instance

    Raises:
        ProlificAPIError: On API errors
        ProlificValidationError: If validation fails

    Example:
        >>> project = create_project(
        ...     client=client,
        ...     workspace_id="workspace_id",
        ...     title="User Research Study 2024",
        ...     description="Researching user behavior patterns",
        ...     naivety_distribution_rate=50
        ... )
        >>> print(f"Created project: {project.id}")
    """
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
    """
    Update an existing project.

    Based on: PATCH /api/v1/projects/{project_id}/
    Only provided fields are updated.

    Args:
        client: HTTP client instance
        project_id: Project ID to update
        title: New title (optional)
        description: New description (optional)
        naivety_distribution_rate: New naivety distribution rate (optional, 0-100)

    Returns:
        Updated ProlificProject instance

    Raises:
        ProlificAPIError: On API errors
        ProlificNotFoundError: If project doesn't exist
        ProlificValidationError: If validation fails

    Example:
        >>> # Update title only
        >>> project = update_project(
        ...     client=client,
        ...     project_id="project_id",
        ...     title="Updated Title"
        ... )
        >>>
        >>> # Update multiple fields
        >>> project = update_project(
        ...     client=client,
        ...     project_id="project_id",
        ...     title="New Title",
        ...     description="New description",
        ...     naivety_distribution_rate=75
        ... )
    """
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
    """
    Find a project by exact title match.

    Args:
        client: HTTP client instance
        workspace_id: Workspace ID to search in
        title: Exact title to match

    Returns:
        ProlificProject if found, None otherwise

    Example:
        >>> project = find_project_by_title(client, "ws_id", "My Project")
        >>> if project:
        ...     print(f"Found: {project.id}")
    """
    projects = list_projects(client, workspace_id)

    for project in projects:
        if project.title == title:
            return project

    return None
