"""
API operations for Prolific projects.
"""
from typing import List, Dict, Any, Optional
from ..http import ProlificHttpClient
from ..models.project import (
    ProlificProject,
    ProjectCreateRequest,
    ProjectUpdateRequest,
    ProjectListResponse
)


def list_projects(
    client: ProlificHttpClient,
    workspace_id: str
) -> List[ProlificProject]:
    """
    List all projects in a workspace.
    
    Args:
        client: HTTP client instance
        workspace_id: Workspace ID to list projects from
    
    Returns:
        List of ProlificProject instances
    
    Raises:
        ProlificAPIError: On API errors
    """
    response = client.get(
        "/api/v1/projects/",
        params={"workspace": workspace_id}
    )
    
    if "results" in response:
        projects = [ProlificProject(**project) for project in response["results"]]
    else:
        projects = [ProlificProject(**project) for project in response] if isinstance(response, list) else []
    
    return projects


def get_project(
    client: ProlificHttpClient,
    project_id: str
) -> ProlificProject:
    """
    Get a specific project by ID.
    
    Args:
        client: HTTP client instance
        project_id: Project ID to retrieve
    
    Returns:
        ProlificProject instance
    
    Raises:
        ProlificAPIError: On API errors
        ProlificNotFoundError: If project doesn't exist
    """
    response = client.get(f"/api/v1/projects/{project_id}/")
    return ProlificProject(**response)


def create_project(
    client: ProlificHttpClient,
    workspace_id: str,
    title: str,
    description: Optional[str] = None,
    naive_id: Optional[str] = None
) -> ProlificProject:
    """
    Create a new project.
    
    Args:
        client: HTTP client instance
        workspace_id: Workspace ID to create project in
        title: Project title
        description: Optional project description
        naive_id: Optional naive ID for tracking
    
    Returns:
        Created ProlificProject instance
    
    Raises:
        ProlificAPIError: On API errors
        ProlificValidationError: If validation fails
    """
    request = ProjectCreateRequest(
        workspace=workspace_id,
        title=title,
        description=description,
        naive_id=naive_id
    )
    
    response = client.post(
        "/api/v1/projects/",
        json=request.model_dump(exclude_none=True)
    )
    
    return ProlificProject(**response)


def patch_project(
    client: ProlificHttpClient,
    project_id: str,
    patch: Dict[str, Any]
) -> ProlificProject:
    """
    Update an existing project.
    
    Args:
        client: HTTP client instance
        project_id: Project ID to update
        patch: Dictionary of fields to update (e.g., {"title": "New Title"})
    
    Returns:
        Updated ProlificProject instance
    
    Raises:
        ProlificAPIError: On API errors
        ProlificNotFoundError: If project doesn't exist
    """
    update_request = ProjectUpdateRequest(**patch)
    
    response = client.patch(
        f"/api/v1/projects/{project_id}/",
        json=update_request.model_dump(exclude_none=True)
    )
    
    return ProlificProject(**response)


def update_project(
    client: ProlificHttpClient,
    project_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> ProlificProject:
    """
    Update project with specific fields (convenience method).
    
    Args:
        client: HTTP client instance
        project_id: Project ID to update
        title: New title (optional)
        description: New description (optional)
    
    Returns:
        Updated ProlificProject instance
    
    Raises:
        ProlificAPIError: On API errors
    """
    patch = {}
    if title is not None:
        patch["title"] = title
    if description is not None:
        patch["description"] = description
    
    if not patch:
        return get_project(client, project_id)
    
    return patch_project(client, project_id, patch)


def find_project_by_title(
    client: ProlificHttpClient,
    workspace_id: str,
    title: str
) -> Optional[ProlificProject]:
    """
    Find a project by exact title match.
    
    Args:
        client: HTTP client instance
        workspace_id: Workspace ID to search in
        title: Exact title to match
    
    Returns:
        ProlificProject if found, None otherwise
    """
    projects = list_projects(client, workspace_id)
    
    for project in projects:
        if project.title == title:
            return project
    
    return None
