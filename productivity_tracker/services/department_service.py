"""Service for department management."""

from uuid import UUID

from sqlalchemy.orm import Session

from productivity_tracker.core.exceptions import ResourceNotFoundError
from productivity_tracker.core.logging_config import get_logger
from productivity_tracker.database.entities.department import Department
from productivity_tracker.models.organization import DepartmentCreate, DepartmentUpdate
from productivity_tracker.repositories.department_repository import DepartmentRepository
from productivity_tracker.repositories.organization_repository import (
    OrganizationRepository,
)

logger = get_logger(__name__)


class DepartmentService:
    """Service for department-related business logic."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = DepartmentRepository(db)
        self.org_repository = OrganizationRepository(db)

    def create_department(self, dept_data: DepartmentCreate) -> Department:
        """Create a new department."""
        logger.info(f"Creating new department: {dept_data.name}")

        # Verify organization exists
        org = self.org_repository.get_by_id(dept_data.organization_id)
        if not org:
            raise ResourceNotFoundError(
                resource_type="Organization",
                resource_id=str(dept_data.organization_id),
            )

        new_dept = Department(
            name=dept_data.name,
            description=dept_data.description,
            organization_id=dept_data.organization_id,
        )

        created_dept = self.repository.create(new_dept)
        logger.info(f"Department created successfully: {created_dept.name} (ID: {created_dept.id})")
        return created_dept

    def get_department(self, dept_id: UUID) -> Department:
        """Get department by ID."""
        dept = self.repository.get_by_id(dept_id)
        if not dept:
            raise ResourceNotFoundError(resource_type="Department", resource_id=str(dept_id))
        return dept

    def get_all_departments(self, skip: int = 0, limit: int = 100) -> list[Department]:
        """Get all departments."""
        return self.repository.get_all(skip=skip, limit=limit)

    def get_departments_by_organization(
        self, org_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[Department]:
        """Get all departments for a specific organization."""
        # Verify organization exists
        org = self.org_repository.get_by_id(org_id)
        if not org:
            raise ResourceNotFoundError(resource_type="Organization", resource_id=str(org_id))

        return self.repository.get_by_organization(org_id, skip=skip, limit=limit)

    def update_department(self, dept_id: UUID, dept_data: DepartmentUpdate) -> Department:
        """Update a department."""
        logger.info(f"Updating department: {dept_id}")

        dept = self.get_department(dept_id)

        # If organization is being changed, verify it exists
        if dept_data.organization_id and dept_data.organization_id != dept.organization_id:
            org = self.org_repository.get_by_id(dept_data.organization_id)
            if not org:
                raise ResourceNotFoundError(
                    resource_type="Organization",
                    resource_id=str(dept_data.organization_id),
                )

        # Update fields
        if dept_data.name is not None:
            dept.name = dept_data.name
        if dept_data.description is not None:
            dept.description = dept_data.description
        if dept_data.organization_id is not None:
            dept.organization_id = dept_data.organization_id

        updated_dept = self.repository.update(dept)
        logger.info(f"Department updated successfully: {updated_dept.id}")
        return updated_dept

    def delete_department(self, dept_id: UUID, soft: bool = True) -> bool:
        """Delete a department."""
        logger.info(f"Deleting department: {dept_id} (soft={soft})")
        result = self.repository.delete(dept_id, soft=soft)
        if result:
            logger.info(f"Department deleted successfully: {dept_id}")
        return result
