"""Database restore engine for AIMS Pro supporting safe SQLite replacements."""

import os
import shutil
import logging
import sqlite3
from pathlib import Path
from sqlalchemy.engine import Engine

from src.database.exceptions import DatabaseRestoreError

logger = logging.getLogger("AIMSPro.Database.Restore")


class RestoreManager:
    """Manages restoring the SQLite database from a previously generated backup file."""

    def __init__(self, engine: Engine) -> None:
        """Initializes RestoreManager.

        Args:
            engine: The active SQLAlchemy Engine.
        """
        self._engine = engine

    def restore_backup(self, backup_file_path: str) -> None:
        """Restores the database from a backup file path.

        Shuts down current database connections to release locks, verifies the
        backup, and performs replacement.

        Args:
            backup_file_path: The file path of the backup file to restore.

        Raises:
            DatabaseRestoreError: If the restore operation fails.
        """
        backup_path = Path(backup_file_path)
        if not backup_path.exists():
            raise DatabaseRestoreError(f"Backup file not found at: {backup_file_path}")

        # Get database URL details
        url = str(self._engine.url)
        if not url.startswith("sqlite"):
            raise DatabaseRestoreError("Local file restores are only supported on SQLite databases.")

        # Parse SQLite file path from connection URL
        sqlite_file_path_str = url.replace("sqlite:///", "")
        if not sqlite_file_path_str:
            raise DatabaseRestoreError("Could not resolve SQLite database file path from Engine URL.")

        active_db_path = Path(sqlite_file_path_str)

        # 1. Validate that the backup file is a valid, readable SQLite database
        try:
            conn = sqlite3.connect(backup_path)
            cursor = conn.cursor()
            # Try running a basic sqlite master query to verify integrity
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            cursor.fetchall()
            conn.close()
        except Exception as integrity_err:
            raise DatabaseRestoreError(f"Target backup is not a valid SQLite database file: {integrity_err}")

        # 2. Safely close all current active database connections
        try:
            logger.info("Disposing active database connection pool to release file locks...")
            self._engine.dispose()
        except Exception as dispose_err:
            logger.warning(f"Failed to dispose engine connection pool safely: {dispose_err}")

        # 3. Perform file swap
        try:
            logger.info(f"Restoring database. Swapping active file '{active_db_path}' with '{backup_path}'...")
            
            # Backup the active database as a temporary safeguard before overwriting
            temp_safeguard = active_db_path.parent / f"{active_db_path.name}.tmp_safeguard"
            if active_db_path.exists():
                shutil.copy2(active_db_path, temp_safeguard)

            try:
                # Replace active database with the backup file
                shutil.copy2(backup_path, active_db_path)
                logger.info("Database file restored successfully.")
                
                # Cleanup the safeguard backup on successful restore
                if temp_safeguard.exists():
                    temp_safeguard.unlink()
            except Exception as swap_err:
                # Rollback to the safeguard if copy failed
                if temp_safeguard.exists():
                    logger.error(f"Restore failed mid-operation. Restoring safety rollback file: {swap_err}")
                    shutil.copy2(temp_safeguard, active_db_path)
                    temp_safeguard.unlink()
                raise DatabaseRestoreError(f"Failed to copy backup file over active database: {swap_err}") from swap_err

        except Exception as e:
            logger.error(f"Database restore operation failed: {e}")
            raise DatabaseRestoreError(f"Database restore failed: {e}") from e
