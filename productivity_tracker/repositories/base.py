"""Base repository class with common CRUD operations."""

from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy.orm import Session

from productivity_tracker.database.entities.base import BaseEntity

ModelType = TypeVar("ModelType", bound=BaseEntity)


class BaseRepository(Generic[ModelType]):
    """Base repository with common database operations."""

    def __init__(self, model: type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get_by_id(self, id: UUID, include_deleted: bool = False) -> ModelType | None:
        """Get a single record by ID."""
        query = self.db.query(self.model).filter(self.model.id == id)
        if not include_deleted:
            query = query.filter(self.model.is_deleted is False)
        return query.first()

    def get_all(
        self, skip: int = 0, limit: int = 100, include_deleted: bool = False
    ) -> list[ModelType]:
        """Get all records with pagination."""
        query = self.db.query(self.model)
        if not include_deleted:
            query = query.filter(self.model.is_deleted is False)
        return query.offset(skip).limit(limit).all()

    def create(self, obj: ModelType) -> ModelType:
        """Create a new record."""
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, obj: ModelType) -> ModelType:
        """Update an existing record."""
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, id: UUID, soft: bool = True) -> bool:
        """Delete a record (soft delete by default)."""
        obj = self.get_by_id(id)
        if not obj:
            return False

        if soft:
            obj.soft_delete()
            self.db.commit()
        else:
            self.db.delete(obj)
            self.db.commit()
        return True

    def restore(self, id: UUID) -> ModelType | None:
        """Restore a soft-deleted record."""
        obj = self.get_by_id(id, include_deleted=True)
        if obj and obj.is_deleted:
            obj.restore()
            self.db.commit()
            self.db.refresh(obj)
            return obj
        return None

    def count(self, include_deleted: bool = False) -> int:
        """Count total records."""
        query = self.db.query(self.model)
        if not include_deleted:
            query = query.filter(self.model.is_deleted is False)
        return query.count()
