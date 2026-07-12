"""Custom exceptions for the AIMS Pro Database Layer."""

class DatabaseError(Exception):
    """Base exception for all database-related issues in AIMS Pro."""
    pass


class DatabaseConnectionError(DatabaseError):
    """Raised when a connection to the database cannot be established or is lost."""
    pass


class DatabaseTransactionError(DatabaseError):
    """Raised during transaction-related failures (e.g., commit or rollback errors)."""
    pass


class DatabaseMigrationError(DatabaseError):
    """Raised when migrations fail to apply, or schema verification fails."""
    pass


class DatabaseBackupError(DatabaseError):
    """Raised when a database backup operation fails."""
    pass


class DatabaseRestoreError(DatabaseError):
    """Raised when a database restore operation fails."""
    pass


class ModelNotFoundError(DatabaseError):
    """Raised when a requested record or entity is not found in the database."""
    pass
