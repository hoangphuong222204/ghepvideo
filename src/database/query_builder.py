"""Fluent, dynamic query builder helper for building SQLAlchemy 2.x select statements."""

from typing import Any, Dict, List, Type, TypeVar, Generic, Optional
from sqlalchemy import select, or_, and_, Column

T = TypeVar("T")


class DynamicQueryBuilder(Generic[T]):
    """A fluent, dynamic query builder facilitating custom select criteria on any model."""

    def __init__(self, model: Type[T]) -> None:
        """Initializes the builder with the target SQLAlchemy model.

        Args:
            model: The declarative model class (e.g. Campaign).
        """
        self.model = model
        self._stmt: Any = select(self.model)

    def filter_equal(self, field_name: str, value: Any) -> "DynamicQueryBuilder[T]":
        """Adds a standard equality constraint (column == value).

        Args:
            field_name: The target column name on the model.
            value: The target value.

        Returns:
            The builder instance for fluent chaining.
        """
        if hasattr(self.model, field_name) and value is not None:
            column = getattr(self.model, field_name)
            self._stmt = self._stmt.where(column == value)
        return self

    def filter_like(self, field_name: str, pattern: str) -> "DynamicQueryBuilder[T]":
        """Adds an SQL LIKE/ILIKE substring match constraint (column.ilike(%pattern%)).

        Args:
            field_name: The target column name.
            pattern: The search text string.

        Returns:
            The builder instance.
        """
        if hasattr(self.model, field_name) and pattern:
            column = getattr(self.model, field_name)
            self._stmt = self._stmt.where(column.ilike(f"%{pattern}%"))
        return self

    def filter_in(self, field_name: str, values: List[Any]) -> "DynamicQueryBuilder[T]":
        """Adds an IN constraint (column.in_(values)).

        Args:
            field_name: The target column name.
            values: List of valid values.

        Returns:
            The builder instance.
        """
        if hasattr(self.model, field_name) and values:
            column = getattr(self.model, field_name)
            self._stmt = self._stmt.where(column.in_(values))
        return self

    def filter_greater_than(self, field_name: str, value: Any) -> "DynamicQueryBuilder[T]":
        """Adds a greater-than constraint (column > value).

        Args:
            field_name: The target column name.
            value: The threshold value.

        Returns:
            The builder instance.
        """
        if hasattr(self.model, field_name) and value is not None:
            column = getattr(self.model, field_name)
            self._stmt = self._stmt.where(column > value)
        return self

    def filter_less_than(self, field_name: str, value: Any) -> "DynamicQueryBuilder[T]":
        """Adds a less-than constraint (column < value).

        Args:
            field_name: The target column name.
            value: The threshold value.

        Returns:
            The builder instance.
        """
        if hasattr(self.model, field_name) and value is not None:
            column = getattr(self.model, field_name)
            self._stmt = self._stmt.where(column < value)
        return self

    def order_by(self, field_name: str, descending: bool = False) -> "DynamicQueryBuilder[T]":
        """Applies dynamic ordering based on a column name.

        Args:
            field_name: The column name to sort by.
            descending: If True, sorts in DESC order. Else ASC.

        Returns:
            The builder instance.
        """
        if hasattr(self.model, field_name):
            column = getattr(self.model, field_name)
            order_clause = column.desc() if descending else column.asc()
            self._stmt = self._stmt.order_by(order_clause)
        return self

    def paginate(self, offset: int = 0, limit: Optional[int] = None) -> "DynamicQueryBuilder[T]":
        """Applies SQL OFFSET and LIMIT clauses.

        Args:
            offset: The query starting offset.
            limit: Maximum records to pull.

        Returns:
            The builder instance.
        """
        self._stmt = self._stmt.offset(offset)
        if limit is not None:
            self._stmt = self._stmt.limit(limit)
        return self

    def build(self) -> Any:
        """Returns the fully constructed Select query statement.

        Returns:
            The final SQLAlchemy Select statement.
        """
        return self._stmt
