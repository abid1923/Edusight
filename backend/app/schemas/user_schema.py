"""
User request/response schemas.
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str | None = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdateRequest(BaseModel):
    full_name: str | None = Field(None, max_length=100)
    email: EmailStr | None = Field(None)
    username: str | None = Field(None, max_length=50)
    password: str | None = Field(None, min_length=6)


class DashboardResponse(BaseModel):
    username: str
    learning_type: str
    reason: str
    strength: str
    weakness: str
    motivation: str
    progress_summary: dict
    recommendation_summary: list[dict]
    features: dict[str, float] | None = None

