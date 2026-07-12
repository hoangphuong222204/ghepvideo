"""Database backup engine for AIMS Pro supporting hot SQLite backups."""

import os
import shutil
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional
from sqlalchemy.engine import Engine

from src.config.config_manager import ConfigManager
from src.database.constants import DEFAULT_BACKUP_FOLDER, DEFAULT_SQLITE_PATH
from src.database.exceptions import DatabaseBackupError

logger = logging.getLogger("AIMSPro.Database.Backup")


class BackupManager:
    """Manages hot backups of SQLite database files, with directory rotation capabilities."""

    def __init__(self, engine: Engine) -> None:
        """Initializes BackupManager.

        Args:
            engine: The active SQLAlchemy Engine.
        """
        self._engine = engine

    def create_backup(self, custom_dest_folder: Optional[str] = None) -> str:
        """Executes a non-blocking hot backup of the SQLite database.

        Args:
            custom_dest_folder: Optional path. If omitted, fetched from ConfigManager.

        Returns:
            The absolute path of the created backup file.

        Raises:
            DatabaseBackupError: If backup fails.
        """
        # Resolve backup destination folder
        dest_folder = custom_dest_folder
        if not dest_folder:
            try:
                dest_folder = ConfigManager().config.database.backup_folder
            except Exception:
                dest_folder = DEFAULT_BACKUP_FOLDER

        dest_path = Path(dest_folder)
        dest_path.mkdir(parents=True, exist_ok=True)

        # Get database URL details
        url = str(self._engine.url)
        if not url.startswith("sqlite"):
            # Relational server backups should be managed outside direct file copies
            logger.warning("Hot backup called on non-SQLite database. Skipping local file copy.")
            raise DatabaseBackupError("Local file backups are only supported on SQLite databases.")

        # Parse SQLite file path from connection URL
        # sqlite:///database.db -> database.db
        sqlite_file_path_str = url.replace("sqlite:///", "")
        if not sqlite_file_path_str:
            raise DatabaseBackupError("Could not resolve SQLite database file path from Engine URL.")

        src_file = Path(sqlite_file_path_str)
        if not src_file.exists():
            raise DatabaseBackupError(f"SQLite source file does not exist at: {src_file.resolve()}")

        # Build unique backup filename: backup_YYYYMMDD_HHMMSS.db
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = dest_path / f"backup_{timestamp}.db"

        try:
            logger.info(f"Initiating hot SQLite backup from '{src_file}' to '{backup_file}'...")
            
            # Using Python's sqlite3 online backup API to perform a safe hot backup
            src_conn = sqlite3.connect(src_file)
            dest_conn = sqlite3.connect(backup_file)
            
            try:
                with dest_conn:
                    src_conn.backup(dest_conn)
                logger.info("Online hot SQLite backup completed successfully.")
            finally:
                dest_conn.close()
                src_conn.close()

            return str(backup_file.resolve())
            
        except Exception as e:
            # Fallback to standard shutil copy if online backup fails for some reason
            try:
                logger.warning(f"Online sqlite3 backup failed: {e}. Falling back to copyfile...")
                shutil.copy2(src_file, backup_file)
                logger.info("Standard copyfile backup fallback succeeded.")
                return str(backup_file.resolve())
            except Exception as copy_err:
                logger.error(f"Failed to copy database: {copy_err}")
                raise DatabaseBackupError(f"Database backup failed: {copy_err}") from copy_err
