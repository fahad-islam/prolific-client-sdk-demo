"""
Models for Prolific projects.
"""
from prolific_client.models.user import User
from typing import Optional, List, Any
from pydantic import BaseModel, Field, EmailStr


class ProlificProject(BaseModel):
    """
    Prolific project model.
    
    Represents a project in Prolific that can contain multiple studies.
    Based on GET /api/v1/projects/?workspace={workspace_id}
    
    Attributes:
        id: Unique project identifier
        title: Project title (1-255 characters)
        description: Optional project description
        workspace: Workspace ID this project belongs to
        owner: Owner user ID
        users: List of user IDs with access to the project
        naivety_distribution_rate: Rate for naivety distribution (0-100)
        created_at: ISO 8601 creation timestamp
        updated_at: ISO 8601 last update timestamp
    """
    id: str = Field(..., description="Unique project identifier")
    title: str = Field(..., description="Project title")
    description: Optional[str] = Field(None, description="Project description")
    workspace: Optional[str] = Field(None, description="Workspace ID this project belongs to")
    owner: Optional[str] = Field(None, description="Owner user ID")
    
    users: Optional[List[Any]] = Field(
        default_factory=list,
        description="List of user IDs with access to the project"
    )
    
    naivety_distribution_rate: Optional[float] = Field(
        None,
        description="Naivety distribution rate (0-1)",
    )
    
    created_at: Optional[str] = Field(None, description="ISO 8601 creation timestamp")
    updated_at: Optional[str] = Field(None, description="ISO 8601 last update timestamp")
    
    class Config:
        extra = "allow"


class ProjectCreateRequest(BaseModel):
    """
    Request model for creating a project.
    
    Based on POST /api/v1/projects/
    
    Example:
        {
            "title": "My Research Project",
            "description": "A study on user behavior",
            "workspace": "workspace_id",
            "naivety_distribution_rate": 50
        }
    """
    title: str = Field(
        ...,
        description="Project title",
        min_length=1,
        max_length=255
    )
    description: Optional[str] = Field(
        None,
        description="Project description"
    )
    workspace: str = Field(..., description="Workspace ID")
    naivety_distribution_rate: Optional[int] = Field(
        None,
        description="Naivety distribution rate (0-100)",
        ge=0,
        le=100
    )
    
    class Config:
        extra = "forbid"


class ProjectUpdateRequest(BaseModel):
    """
    Request model for updating a project.
    
    Based on PATCH /api/v1/projects/{project_id}/
    All fields are optional - only provided fields are updated.
    
    Example:
        {
            "title": "Updated Project Title",
            "description": "Updated description"
        }
    """
    title: Optional[str] = Field(
        None,
        description="New project title",
        min_length=1,
        max_length=255
    )
    description: Optional[str] = Field(
        None,
        description="New project description"
    )
    owner: Optional[str] = Field(
        None,
        description="New project owner"
    )
    workspace: Optional[str] = Field(
        None,
        description="New project workspace"
    )
    users: Optional[List[User]] = Field(
        None,
        description="List of users to add to the project"
    )
    naivety_distribution_rate: Optional[float] = Field(
        None,
        description="New naivety distribution rate",
    )
    
    class Config:
        extra = "forbid"


class ProjectListResponse(BaseModel):
    """
    Response model for listing projects.
    
    Based on GET /api/v1/projects/?workspace={workspace_id}
    Returns paginated list of projects.
    """
    results: List[ProlificProject] = Field(
        default_factory=list,
        description="List of projects"
    )
    
    class Config:
        extra = "allow"

ProjectID = str
WorkspaceID = str