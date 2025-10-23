"""Pydantic models/schemas for organization, department, and team management."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from productivity_tracker.models.auth import UserResponse

# ============================================================================
# Organization Schemas
# ============================================================================


class OrganizationBase(BaseModel):
    """Base organization schema with common fields."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=500)
    slug: str = Field(..., min_length=1, max_length=100)


class OrganizationCreate(OrganizationBase):
    """Schema for organization creation."""

    pass


class OrganizationUpdate(BaseModel):
    """Schema for organization update."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=500)
    slug: str | None = Field(None, min_length=1, max_length=100)


class OrganizationResponse(OrganizationBase):
    """Schema for organization response."""

    id: UUID
    created_at: datetime
    updated_at: datetime | None = None
    member_count: int = 0
    department_count: int = 0

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Department Schemas
# ============================================================================


class DepartmentBase(BaseModel):
    """Base department schema with common fields."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=500)


class DepartmentCreate(DepartmentBase):
    """Schema for department creation."""

    organization_id: UUID


class DepartmentUpdate(BaseModel):
    """Schema for department update."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=500)
    organization_id: UUID | None = None


class DepartmentResponse(DepartmentBase):
    """Schema for department response."""

    id: UUID
    organization_id: UUID
    created_at: datetime
    updated_at: datetime | None = None
    team_count: int = 0
    member_count: int = 0

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Team Schemas
# ============================================================================


class TeamBase(BaseModel):
    """Base team schema with common fields."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=500)


class TeamCreate(TeamBase):
    """Schema for team creation."""

    department_id: UUID
    lead_id: UUID | None = None


class TeamUpdate(BaseModel):
    """Schema for team update."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=500)
    department_id: UUID | None = None
    lead_id: UUID | None = None


class TeamMemberAdd(BaseModel):
    """Schema for adding a member to a team."""

    user_id: UUID


class TeamMemberRemove(BaseModel):
    """Schema for removing a member from a team."""

    user_id: UUID


class TeamResponse(TeamBase):
    """Schema for team response."""

    id: UUID
    department_id: UUID
    lead_id: UUID | None = None
    created_at: datetime
    updated_at: datetime | None = None
    member_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class TeamWithLeadResponse(TeamResponse):
    """Schema for team response with lead information."""

    lead: "UserResponse | None" = None

    model_config = ConfigDict(from_attributes=True)


TeamWithLeadResponse.model_rebuild()
