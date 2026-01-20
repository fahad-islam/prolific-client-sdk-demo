"""
Models for Prolific projects.
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class ProlificProject(BaseModel):
    """
    Prolific project model.
    
    Represents a project in Prolific that can contain multiple studies.
    """
    id: str = Field(..., description="Unique project identifier")
    title: str = Field(..., description="Project title")
    description: Optional[str] = Field(None, description="Project description")
    workspace: str = Field(..., description="Workspace ID this project belongs to")
    owner: Optional[str] = Field(None, description="Owner user ID")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")
    
    naive_id: Optional[str] = Field(None, description="Naive/simple ID if used")
    
    class Config:
        extra = "allow"


class ProjectCreateRequest(BaseModel):
    """Request model for creating a project."""
    title: str = Field(..., description="Project title", min_length=1, max_length=255)
    description: Optional[str] = Field(None, description="Project description", max_length=1000)
    workspace: str = Field(..., description="Workspace ID")
    naive_id: Optional[str] = Field(None, description="Optional naive ID for tracking")


class ProjectUpdateRequest(BaseModel):
    """Request model for updating a project."""
    title: Optional[str] = Field(None, description="New project title", min_length=1, max_length=255)
    description: Optional[str] = Field(None, description="New project description", max_length=1000)
    
    class Config:
        exclude_none = True


class ProjectListResponse(BaseModel):
    """Response model for listing projects."""
    results: List[ProlificProject] = Field(default_factory=list, description="List of projects")
    
    class Config:
        extra = "allow"
