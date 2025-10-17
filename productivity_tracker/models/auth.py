"""Pydantic models/schemas for authentication and authorization."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

# ============================================================================
# Token Schemas
# ============================================================================


class Token(BaseModel):
    """Schema for access token response."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token payload data."""

    user_id: UUID | None = None


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request."""

    refresh_token: str


# ============================================================================
# User Schemas
# ============================================================================


class UserBase(BaseModel):
    """Base user schema with common fields."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)


class UserCreate(UserBase):
    """Schema for user creation."""

    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    """Schema for user update."""

    email: EmailStr | None = None
    username: str | None = Field(None, min_length=3, max_length=100)
    is_active: bool | None = None


class UserPasswordUpdate(BaseModel):
    """Schema for updating user password."""

    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)


class UserResponse(UserBase):
    """Schema for user response."""

    id: UUID
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime | None = None
    roles: list["RoleResponse"] = []

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    """Schema for user list response."""

    id: UUID
    username: str
    email: str
    is_active: bool
    is_superuser: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Role Schemas
# ============================================================================


class RoleBase(BaseModel):
    """Base role schema."""

    name: str = Field(..., min_length=1, max_length=50)
    description: str | None = Field(None, max_length=255)


class RoleCreate(RoleBase):
    """Schema for role creation."""

    permission_ids: list[UUID] = []


class RoleUpdate(BaseModel):
    """Schema for role update."""

    name: str | None = Field(None, min_length=1, max_length=50)
    description: str | None = Field(None, max_length=255)
    permission_ids: list[UUID] | None = None


class RoleResponse(RoleBase):
    """Schema for role response."""

    id: UUID
    created_at: datetime
    updated_at: datetime | None = None
    permissions: list["PermissionResponse"] = []

    model_config = ConfigDict(from_attributes=True)


class RoleListResponse(BaseModel):
    """Schema for role list response."""

    id: UUID
    name: str
    description: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Permission Schemas
# ============================================================================


class PermissionBase(BaseModel):
    """Base permission schema."""

    name: str = Field(..., min_length=1, max_length=100)
    resource: str = Field(..., min_length=1, max_length=50)
    action: str = Field(..., min_length=1, max_length=50)
    description: str | None = Field(None, max_length=255)


class PermissionCreate(PermissionBase):
    """Schema for permission creation."""

    pass


class PermissionUpdate(BaseModel):
    """Schema for permission update."""

    name: str | None = Field(None, min_length=1, max_length=100)
    resource: str | None = Field(None, min_length=1, max_length=50)
    action: str | None = Field(None, min_length=1, max_length=50)
    description: str | None = Field(None, max_length=255)


class PermissionResponse(PermissionBase):
    """Schema for permission response."""

    id: UUID
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Assignment Schemas
# ============================================================================


class AssignRolesToUser(BaseModel):
    """Schema for assigning roles to a user."""

    role_ids: list[UUID]


class AssignPermissionsToRole(BaseModel):
    """Schema for assigning permissions to a role."""

    permission_ids: list[UUID]


# ============================================================================
# Login Schemas
# ============================================================================


class LoginRequest(BaseModel):
    """Schema for login request."""

    username: str
    password: str


class LoginResponse(BaseModel):
    """Schema for login response."""

    message: str
    user: UserListResponse
    refresh_token: str


# Resolve forward references
UserResponse.model_rebuild()
RoleResponse.model_rebuild()
