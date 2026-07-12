"""Generic Type-Safe Base Repository for standard CRUD database operations."""

from typing import Generic, TypeVar, Type, List, Optional, Dict, Any
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from src.database.exceptions import ModelNotFoundError, DatabaseError

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Generic Base Repository implementing standard CRUD operations with SQLAlchemy 2.x."""

    def __init__(self, model: Type[T], session: Session) -> None:
        """Initializes the repository with the target model type and active session.

        Args:
            model: The SQLAlchemy declarative model class (e.g. Campaign).
            session: The active SQLAlchemy Session.
        """
        self.model = model
        self.session = session

    def get_by_id(self, entity_id: Any) -> T:
        """Retrieves a single entity by its unique ID.

        Args:
            entity_id: The primary key of the record.

        Returns:
            The found model instance.

        Raises:
            ModelNotFoundError: If no record matches the primary key.
        """
        result = self.session.get(self.model, entity_id)
        if result is None:
            raise ModelNotFoundError(
                f"Record of type '{self.model.__name__}' with id {entity_id} not found."
            )
        return result

    def get_by_id_optional(self, entity_id: Any) -> Optional[T]:
        """Retrieves a single entity by its unique ID, returning None if not found.

        Args:
            entity_id: The primary key of the record.

        Returns:
            The model instance, or None.
        """
        return self.session.get(self.model, entity_id)

    def get_all(
        self,
        filters: Optional[Dict[str, Any]] = None,
        offset: int = 0,
        limit: Optional[int] = None,
        order_by: Optional[Any] = None,
    ) -> List[T]:
        """Retrieves multiple entities matching optional filters, offset, and limit constraints.

        Args:
            filters: Dictionary of column name to value matching filters.
            offset: The pagination offset index.
            limit: The maximum number of records to return.
            order_by: The SQLAlchemy ordering statement (e.g. Campaign.created_at.desc()).

        Returns:
            A list of model instances.
        """
        stmt = select(self.model)

        # Apply simple filters
        if filters:
            for field_name, value in filters.items():
                if hasattr(self.model, field_name):
                    column = getattr(self.model, field_name)
                    stmt = stmt.where(column == value)

        # Apply ordering
        if order_by is not None:
            stmt = stmt.order_by(order_by)

        # Apply pagination bounds
        stmt = stmt.offset(offset)
        if limit is not None:
            stmt = stmt.limit(limit)

        try:
            return list(self.session.scalars(stmt).all())
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to retrieve list of {self.model.__name__}: {e}") from e

    def create(self, data: Dict[str, Any]) -> T:
        """Inserts a new record into the database.

        Args:
            data: Key-value dictionary matching the model columns.

        Returns:
            The instantiated and persisted model instance.
        """
        try:
            instance = self.model(**data)
            self.session.add(instance)
            # Flush to database to populate auto-incrementing ID
            self.session.flush()
            return instance
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to create new {self.model.__name__}: {e}") from e

    def update(self, entity_id: Any, data: Dict[str, Any]) -> T:
        """Updates attributes of an existing record.

        Args:
            entity_id: The primary key of the target record.
            data: Key-value dictionary of attributes to update.

        Returns:
            The updated model instance.

        Raises:
            ModelNotFoundError: If the target record does not exist.
        """
        instance = self.get_by_id(entity_id)
        
        try:
            for key, value in data.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            self.session.flush()
            return instance
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to update {self.model.__name__} id {entity_id}: {e}") from e

    def delete(self, entity_id: Any) -> None:
        """Deletes a record from the database.

        Args:
            entity_id: The primary key of the target record.

        Raises:
            ModelNotFoundError: If the target record does not exist.
        """
        instance = self.get_by_id(entity_id)
        try:
            self.session.delete(instance)
            self.session.flush()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to delete {self.model.__name__} id {entity_id}: {e}") from e

    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Counts the total records matching optional filters.

        Args:
            filters: Dictionary of column name to value matching filters.

        Returns:
            The integer count of records.
        """
        stmt = select(func.count()).select_from(self.model)

        if filters:
            for field_name, value in filters.items():
                if hasattr(self.model, field_name):
                    column = getattr(self.model, field_name)
                    stmt = stmt.where(column == value)

        try:
            return self.session.scalar(stmt) or 0
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to count {self.model.__name__}: {e}") from e
