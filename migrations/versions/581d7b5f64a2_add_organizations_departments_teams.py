"""add_organizations_departments_teams

Revision ID: 581d7b5f64a2
Revises: 4400ca3b2b4a
Create Date: 2025-10-23 21:26:10.957941

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '581d7b5f64a2'
down_revision: Union[str, Sequence[str], None] = '4400ca3b2b4a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create organizations table
    op.create_table(
        'organizations',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_organizations_id'), 'organizations', ['id'], unique=False)
    op.create_index(op.f('ix_organizations_is_deleted'), 'organizations', ['is_deleted'], unique=False)
    op.create_index(op.f('ix_organizations_name'), 'organizations', ['name'], unique=False)
    op.create_index(op.f('ix_organizations_slug'), 'organizations', ['slug'], unique=True)

    # Create departments table
    op.create_table(
        'departments',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_departments_id'), 'departments', ['id'], unique=False)
    op.create_index(op.f('ix_departments_is_deleted'), 'departments', ['is_deleted'], unique=False)
    op.create_index(op.f('ix_departments_name'), 'departments', ['name'], unique=False)
    op.create_index(op.f('ix_departments_organization_id'), 'departments', ['organization_id'], unique=False)

    # Create teams table
    op.create_table(
        'teams',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('department_id', sa.UUID(), nullable=False),
        sa.Column('lead_id', sa.UUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['lead_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_teams_id'), 'teams', ['id'], unique=False)
    op.create_index(op.f('ix_teams_is_deleted'), 'teams', ['is_deleted'], unique=False)
    op.create_index(op.f('ix_teams_name'), 'teams', ['name'], unique=False)
    op.create_index(op.f('ix_teams_department_id'), 'teams', ['department_id'], unique=False)
    op.create_index(op.f('ix_teams_lead_id'), 'teams', ['lead_id'], unique=False)

    # Create user_organizations junction table
    op.create_table(
        'user_organizations',
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'organization_id')
    )

    # Create user_teams junction table
    op.create_table(
        'user_teams',
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('team_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'team_id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop junction tables first
    op.drop_table('user_teams')
    op.drop_table('user_organizations')

    # Drop teams table
    op.drop_index(op.f('ix_teams_lead_id'), table_name='teams')
    op.drop_index(op.f('ix_teams_department_id'), table_name='teams')
    op.drop_index(op.f('ix_teams_name'), table_name='teams')
    op.drop_index(op.f('ix_teams_is_deleted'), table_name='teams')
    op.drop_index(op.f('ix_teams_id'), table_name='teams')
    op.drop_table('teams')

    # Drop departments table
    op.drop_index(op.f('ix_departments_organization_id'), table_name='departments')
    op.drop_index(op.f('ix_departments_name'), table_name='departments')
    op.drop_index(op.f('ix_departments_is_deleted'), table_name='departments')
    op.drop_index(op.f('ix_departments_id'), table_name='departments')
    op.drop_table('departments')

    # Drop organizations table
    op.drop_index(op.f('ix_organizations_slug'), table_name='organizations')
    op.drop_index(op.f('ix_organizations_name'), table_name='organizations')
    op.drop_index(op.f('ix_organizations_is_deleted'), table_name='organizations')
    op.drop_index(op.f('ix_organizations_id'), table_name='organizations')
    op.drop_table('organizations')
