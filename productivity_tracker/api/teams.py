"""API routes for team management."""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from productivity_tracker.core.dependencies import get_current_user
from productivity_tracker.database import get_db
from productivity_tracker.database.entities.user import User
from productivity_tracker.models.auth import UserResponse
from productivity_tracker.models.organization import (
    TeamCreate,
    TeamMemberAdd,
    TeamUpdate,
    TeamWithLeadResponse,
)
from productivity_tracker.repositories.team_repository import TeamRepository
from productivity_tracker.services.team_service import TeamService

router = APIRouter()


@router.post(
    "/teams",
    response_model=TeamWithLeadResponse,
    status_code=status.HTTP_201_CREATED,
    operation_id="createTeam",
)
def create_team(
    team_data: TeamCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new team."""
    team_service = TeamService(db)
    new_team = team_service.create_team(team_data)

    # Enrich response with counts
    team_repo = TeamRepository(db)
    response = TeamWithLeadResponse.model_validate(new_team)
    response.member_count = team_repo.get_member_count(new_team.id)

    return response


@router.get(
    "/teams",
    response_model=list[TeamWithLeadResponse],
    operation_id="getAllTeams",
)
def get_all_teams(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all teams."""
    team_service = TeamService(db)
    teams = team_service.get_all_teams(skip, limit)

    # Enrich responses with counts
    team_repo = TeamRepository(db)
    responses = []
    for team in teams:
        response = TeamWithLeadResponse.model_validate(team)
        response.member_count = team_repo.get_member_count(team.id)
        responses.append(response)

    return responses


@router.get(
    "/teams/{team_id}",
    response_model=TeamWithLeadResponse,
    operation_id="getTeam",
)
def get_team(
    team_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get team by ID."""
    team_service = TeamService(db)
    team = team_service.get_team(team_id)

    # Enrich response with counts
    team_repo = TeamRepository(db)
    response = TeamWithLeadResponse.model_validate(team)
    response.member_count = team_repo.get_member_count(team.id)

    return response


@router.get(
    "/departments/{dept_id}/teams",
    response_model=list[TeamWithLeadResponse],
    operation_id="getTeamsByDepartment",
)
def get_teams_by_department(
    dept_id: UUID,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all teams for a specific department."""
    team_service = TeamService(db)
    teams = team_service.get_teams_by_department(dept_id, skip, limit)

    # Enrich responses with counts
    team_repo = TeamRepository(db)
    responses = []
    for team in teams:
        response = TeamWithLeadResponse.model_validate(team)
        response.member_count = team_repo.get_member_count(team.id)
        responses.append(response)

    return responses


@router.put(
    "/teams/{team_id}",
    response_model=TeamWithLeadResponse,
    operation_id="updateTeam",
)
def update_team(
    team_id: UUID,
    team_data: TeamUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update team."""
    team_service = TeamService(db)
    updated_team = team_service.update_team(team_id, team_data)

    # Enrich response with counts
    team_repo = TeamRepository(db)
    response = TeamWithLeadResponse.model_validate(updated_team)
    response.member_count = team_repo.get_member_count(updated_team.id)

    return response


@router.delete(
    "/teams/{team_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="deleteTeam",
)
def delete_team(
    team_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete team."""
    team_service = TeamService(db)
    team_service.delete_team(team_id)
    return None


@router.post(
    "/teams/{team_id}/members",
    response_model=TeamWithLeadResponse,
    status_code=status.HTTP_200_OK,
    operation_id="addTeamMember",
)
def add_team_member(
    team_id: UUID,
    member_data: TeamMemberAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a member to a team."""
    team_service = TeamService(db)
    team_service.add_member(team_id, member_data.user_id)

    # Return updated team
    team = team_service.get_team(team_id)
    team_repo = TeamRepository(db)
    response = TeamWithLeadResponse.model_validate(team)
    response.member_count = team_repo.get_member_count(team.id)
    return response


@router.delete(
    "/teams/{team_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="removeTeamMember",
)
def remove_team_member(
    team_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a member from a team."""
    team_service = TeamService(db)
    team_service.remove_member(team_id, user_id)
    return None


@router.get(
    "/teams/{team_id}/members",
    response_model=list[UserResponse],
    operation_id="getTeamMembers",
)
def get_team_members(
    team_id: UUID,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all members of a team."""
    team_service = TeamService(db)
    members = team_service.get_members(team_id, skip, limit)
    return members


@router.put(
    "/teams/{team_id}/lead/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="setTeamLead",
)
def set_team_lead(
    team_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Set or update the team lead."""
    team_service = TeamService(db)
    team_service.set_lead(team_id, user_id)
    return None


@router.delete(
    "/teams/{team_id}/lead",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="removeTeamLead",
)
def remove_team_lead(
    team_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove the team lead."""
    team_service = TeamService(db)
    team_service.set_lead(team_id, None)
    return None
