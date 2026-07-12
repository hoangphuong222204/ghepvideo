"""Database Session Manager implementing thread-safe transaction control."""

import logging
from contextlib import contextmanager
from typing import Generator, Optional
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from sqlalchemy.exc import SQLAlchemyError

from src.database.exceptions import DatabaseTransactionError

logger = logging.getLogger("AIMSPro.Database.Session")


class SessionManager:
    """Orchestrates SQLAlchemy sessionmaker and provides scoped thread-safe sessions."""

    def __init__(self, engine: Engine) -> None:
        """Initializes the SessionManager with a configured Engine.

        Args:
            engine: The active SQLAlchemy Engine instance.
        """
        self._engine = engine
        # Thread-safe session factory
        self._session_factory = sessionmaker(
            bind=self._engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )
        self._scoped_session = scoped_session(self._session_factory)

    @property
    def session_factory(self) -> sessionmaker:
        """Returns the raw session factory."""
        return self._session_factory

    @property
    def scoped_session(self) -> scoped_session:
        """Returns the thread-scoped session registry."""
        return self._scoped_session

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """Context manager for managing a transactional database session scope.

        Performs automatic commit on success and automatic rollback on exception,
        with guaranteed session closing.

        Yields:
            An active SQLAlchemy Session.

        Raises:
            DatabaseTransactionError: Wrapped exception if a transaction commit or rollback fails.
        """
        # Create a new session from the factory
        session: Session = self._session_factory()
        try:
            yield session
            if session.in_transaction():
                session.commit()
        except Exception as e:
            logger.error(f"Transaction failed, rolling back session. Error: {e}")
            try:
                session.rollback()
            except SQLAlchemyError as rollback_err:
                logger.error(f"Rollback failed: {rollback_err}")
                raise DatabaseTransactionError(
                    f"Transaction rolled back due to error: {e}, but subsequent rollback also failed: {rollback_err}"
                ) from rollback_err
            
            # If the original error is already a Database error, propagate it
            if isinstance(e, DatabaseTransactionError):
                raise e
            raise DatabaseTransactionError(f"Database transaction failed and was rolled back: {e}") from e
        finally:
            session.close()

    @contextmanager
    def scoped_session_scope(self) -> Generator[Session, None, None]:
        """Context manager using the thread-scoped session registry.

        Particularly useful in web request contexts (e.g., FastAPI middleware)
        to reuse a single session across the same thread.

        Yields:
            The scoped SQLAlchemy Session.
        """
        session: Session = self._scoped_session()
        try:
            yield session
            if session.in_transaction():
                session.commit()
        except Exception as e:
            logger.error(f"Scoped transaction failed, rolling back. Error: {e}")
            try:
                session.rollback()
            except SQLAlchemyError as rollback_err:
                logger.error(f"Scoped rollback failed: {rollback_err}")
                raise DatabaseTransactionError(
                    f"Scoped transaction rolled back due to error: {e}, but subsequent rollback also failed: {rollback_err}"
                ) from rollback_err
            raise DatabaseTransactionError(f"Scoped database transaction failed: {e}") from e
        finally:
            # Removes the thread-scoped session completely from registry
            self._scoped_session.remove()
