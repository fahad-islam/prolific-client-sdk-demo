"""
Models for Prolific users.
"""
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr


class User(BaseModel):
    id: str = Field(..., min_length=1)
    name: Optional[str]
    email: Optional[EmailStr]
    roles: Optional[List[str]]

    class Config:
        extra = "allow"
