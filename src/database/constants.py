"""Constants and default configurations for the AIMS Pro Database Layer."""

# Supported Database Dialects
DIALECT_SQLITE = "sqlite"
DIALECT_POSTGRESQL = "postgresql"

# Default filenames and folders as fallback
DEFAULT_SQLITE_PATH = "database.db"
DEFAULT_BACKUP_FOLDER = "backups"

# Connection Pool Defaults (PostgreSQL and SQLite)
DEFAULT_POOL_SIZE = 10
DEFAULT_MAX_OVERFLOW = 20
DEFAULT_POOL_TIMEOUT = 30  # seconds
DEFAULT_POOL_RECYCLE = 1800  # seconds (30 minutes)

# SQLite Specific Performance Pragmas
SQLITE_PRAGMAS = [
    ("foreign_keys", "ON"),           # Enforce referential integrity
    ("journal_mode", "WAL"),          # Write-Ahead Logging for concurrent read/write
    ("synchronous", "NORMAL"),        # Balance safety and speed
    ("busy_timeout", "5000"),         # Wait up to 5 seconds before locking error
    ("cache_size", "-2000"),          # 2000 pages of cache (~2MB)
    ("temp_store", "MEMORY"),         # Temp tables in memory
]
