"""Lightweight, metadata-driven database migration system for AIMS Pro."""

import logging
from sqlalchemy import text
from sqlalchemy.engine import Engine, Connection
from sqlalchemy.exc import SQLAlchemyError

from src.database.models import Base
from src.database.exceptions import DatabaseMigrationError

logger = logging.getLogger("AIMSPro.Database.Migrations")

CURRENT_SCHEMA_VERSION = 1


class MigrationManager:
    """Manages schema validation, creation, and incremental schema version migrations."""

    def __init__(self, engine: Engine) -> None:
        """Initializes with the active database Engine.

        Args:
            engine: The SQLAlchemy Engine instance.
        """
        self._engine = engine

    def check_and_apply_migrations(self) -> None:
        """Entry point to run migrations.

        Creates base schema tables, checks the current schema version,
        and applies any pending updates.
        """
        try:
            # 1. Create all declarative tables defined in models if they don't exist
            logger.info("Verifying/creating core database tables using metadata...")
            Base.metadata.create_all(self._engine)
            
            # 2. Check and initialize/upgrade the migration version table
            with self._engine.begin() as conn:
                self._initialize_migration_table(conn)
                current_version = self._get_current_version(conn)
                logger.info(f"Current database schema version: {current_version}")

                if current_version < CURRENT_SCHEMA_VERSION:
                    logger.info(f"Upgrading database schema from version {current_version} to {CURRENT_SCHEMA_VERSION}...")
                    self._apply_incremental_migrations(conn, current_version, CURRENT_SCHEMA_VERSION)
                else:
                    logger.info("Database schema is fully up to date.")
        except Exception as e:
            logger.error(f"Migration run failed: {e}")
            raise DatabaseMigrationError(f"Database migrations failed: {e}") from e

    def _initialize_migration_table(self, conn: Connection) -> None:
        """Creates the schema_version table if it does not exist, initializing to v1."""
        # Query if the table exists (dialect independent check or simple CREATE TABLE IF NOT EXISTS)
        conn.execute(
            text(
                "CREATE TABLE IF NOT EXISTS schema_version ("
                "   id INTEGER PRIMARY KEY DEFAULT 1,"
                "   version INTEGER NOT NULL"
                ")"
            )
        )
        
        # Check if we have an active version record
        result = conn.execute(text("SELECT version FROM schema_version WHERE id = 1")).fetchone()
        if result is None:
            conn.execute(text("INSERT INTO schema_version (id, version) VALUES (1, 1)"))
            logger.info("Initialized schema_version table with version 1.")

    def _get_current_version(self, conn: Connection) -> int:
        """Retrieves the current schema version integer from the database."""
        result = conn.execute(text("SELECT version FROM schema_version WHERE id = 1")).fetchone()
        if result:
            return int(result[0])
        return 1

    def _update_schema_version(self, conn: Connection, target_version: int) -> None:
        """Updates the tracked schema version integer."""
        conn.execute(
            text("UPDATE schema_version SET version = :version WHERE id = 1"),
            {"version": target_version}
        )
        logger.info(f"Schema version successfully updated to v{target_version}.")

    def _apply_incremental_migrations(self, conn: Connection, current_version: int, target_version: int) -> None:
        """Applies sequential schema scripts/statements from current to target version."""
        # Map version steps to lists of migration SQL commands
        # Example: version 1 -> 2 adds a new column or index
        migrations_map = {
            # 2: [
            #     "ALTER TABLE campaigns ADD COLUMN notes TEXT",
            #     "CREATE INDEX idx_campaigns_active ON campaigns(is_active)"
            # ]
        }

        for version in range(current_version + 1, target_version + 1):
            if version in migrations_map:
                logger.info(f"Applying migration scripts for version {version}...")
                statements = migrations_map[version]
                for statement in statements:
                    try:
                        conn.execute(text(statement))
                    except SQLAlchemyError as stmt_err:
                        logger.error(f"Failed to execute migration statement: '{statement}'. Error: {stmt_err}")
                        raise DatabaseMigrationError(f"Migration to v{version} failed: {stmt_err}") from stmt_err
            
            # Step the database version forward
            self._update_schema_version(conn, version)
