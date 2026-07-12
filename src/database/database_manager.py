"""Central Database Manager orchestrating connections, transactions, and repositories."""

import logging
import threading
from contextlib import contextmanager
from typing import Generator, Optional, Any
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from src.database.connection import ConnectionFactory
from src.database.session import SessionManager
from src.database.migrations import MigrationManager
from src.database.backup import BackupManager
from src.database.restore import RestoreManager
from src.database.repository import CampaignRepository, MarketingAssetRepository, AuditLogRepository
from src.database.exceptions import DatabaseError, DatabaseConnectionError

logger = logging.getLogger("AIMSPro.Database.Manager")


class UnitOfWork:
    """Implements the Unit of Work (UoW) pattern.

    Bundles active repositories together within a single transactional session context.
    """

    def __init__(self, session: Session) -> None:
        """Initializes the Unit of Work with repositories bound to the active session.

        Args:
            session: The active SQLAlchemy Session.
        """
        self.session = session
        self.campaigns = CampaignRepository(session)
        self.assets = MarketingAssetRepository(session)
        self.logs = AuditLogRepository(session)


class DatabaseManager:
    """Thread-safe Singleton DatabaseManager for AI Marketing Studio PRO.

    Coordinates connection pool, transactional sessions, database migrations,
    online hot backups, restores, and Unit of Work repository access.
    """

    _instance: Optional["DatabaseManager"] = None
    _lock = threading.RLock()

    def __new__(cls, *args: Any, **kwargs: Any) -> "DatabaseManager":
        """Ensures that only one instance of DatabaseManager is instantiated."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self, connection_url: Optional[str] = None) -> None:
        """Initializes the connection pool and managers only once."""
        with self._lock:
            if getattr(self, "_initialized", False):
                return

            self._connection_url = connection_url
            self._engine: Optional[Engine] = None
            self._session_manager: Optional[SessionManager] = None
            self._migration_manager: Optional[MigrationManager] = None
            self._backup_manager: Optional[BackupManager] = None
            self._restore_manager: Optional[RestoreManager] = None

            # Establish the core engine and dependent service sub-managers
            self._connect()
            
            self._initialized = True
            logger.info("DatabaseManager successfully initialized.")

    def _connect(self) -> None:
        """Builds or rebuilds the engine and all downstream manager modules."""
        try:
            self._engine = ConnectionFactory.create_engine_instance(self._connection_url)
            self._session_manager = SessionManager(self._engine)
            self._migration_manager = MigrationManager(self._engine)
            self._backup_manager = BackupManager(self._engine)
            self._restore_manager = RestoreManager(self._engine)
        except Exception as e:
            logger.error(f"Failed to establish database connection during startup: {e}")
            raise DatabaseConnectionError(f"Database connection initialization failed: {e}") from e

    @property
    def engine(self) -> Engine:
        """Returns the active SQLAlchemy Engine."""
        if not self._engine:
            raise DatabaseConnectionError("Database engine is not initialized.")
        return self._engine

    @property
    def session_manager(self) -> SessionManager:
        """Returns the active SessionManager."""
        if not self._session_manager:
            raise DatabaseConnectionError("Session manager is not initialized.")
        return self._session_manager

    def health_check(self) -> bool:
        """Performs a live connectivity check against the database connection pool.

        Returns:
            True if the database is active and responsive, False otherwise.
        """
        if not self._engine:
            return False
        return ConnectionFactory.ping_engine(self._engine)

    def reconnect(self) -> None:
        """Safely disposes of the active engine pool and re-establishes a fresh connection.

        Useful for recovery after transient network disconnects or post-database-restores.
        """
        with self._lock:
            logger.info("Reconnecting database layer. Disposing active pools...")
            if self._engine:
                try:
                    self._engine.dispose()
                except Exception as e:
                    logger.warning(f"Error disposing old engine connection pool: {e}")
            
            self._connect()
            logger.info("Database layer successfully reconnected.")

    def initialize_schema(self) -> None:
        """Verifies table structures and applies any pending migrations.

        Should be called during application startup.
        """
        if not self._migration_manager:
            raise DatabaseConnectionError("Migration manager is not initialized.")
        self._migration_manager.check_and_apply_migrations()

    def backup_database(self, custom_dest_folder: Optional[str] = None) -> str:
        """Generates an online hot backup file of the SQLite database.

        Args:
            custom_dest_folder: Optional folder path where backup should be placed.

        Returns:
            The absolute path of the created backup file.
        """
        if not self._backup_manager:
            raise DatabaseConnectionError("Backup manager is not initialized.")
        return self._backup_manager.create_backup(custom_dest_folder)

    def restore_database(self, backup_file_path: str) -> None:
        """Restores the database from a backup file path and re-establishes connection.

        Args:
            backup_file_path: Absolute or relative file path to the target backup.
        """
        if not self._restore_manager:
            raise DatabaseConnectionError("Restore manager is not initialized.")
        
        # Restore replaces the underlying database file
        self._restore_manager.restore_backup(backup_file_path)
        
        # After a file-restore, we must dispose and re-init the connection pools
        self.reconnect()

    @contextmanager
    def unit_of_work(self) -> Generator[UnitOfWork, None, None]:
        """Provides a thread-safe Unit of Work context manager.

        Bundles repository operations into a single session and transaction scope.
        Changes are auto-committed on success, and auto-rolled-back on failure.

        Yields:
            A UnitOfWork wrapper holding campaign, asset, and log repositories.
        """
        if not self._session_manager:
            raise DatabaseConnectionError("Session manager is not initialized.")

        with self._session_manager.session_scope() as session:
            yield UnitOfWork(session)

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """Provides direct access to a thread-safe transaction-aware Session scope.

        Yields:
            An active SQLAlchemy Session.
        """
        if not self._session_manager:
            raise DatabaseConnectionError("Session manager is not initialized.")
        
        with self._session_manager.session_scope() as session:
            yield session
