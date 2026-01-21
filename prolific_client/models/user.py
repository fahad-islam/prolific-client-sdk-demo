from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr


class User(BaseModel):
    """
    DefaultProlific user model.
    
    Represents a user in Prolific.
    Based on GET /api/v1/users/
    
    Attributes:
        id: Unique user identifier
        name: User's name
        email: User's email address
        roles: List of roles assigned to the user
    """
    id: str = Field(..., min_length=1)
    name: Optional[str]
    email: Optional[EmailStr]
    roles: Optional[List[str]]

    class Config:
        extra = "allow"
