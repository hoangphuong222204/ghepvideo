"""AIMS Pro Database Layer Package.

Provides a production-ready, thread-safe, and singleton database manager supporting
transactions, connection pooling, repository pattern, unit of work, schema migrations,
and hot backup/restore systems.
"""

from src.database.database_manager import DatabaseManager, UnitOfWork
from src.database.models import Base, Campaign, MarketingAsset, AuditLog
from src.database.schema import (
    CampaignCreate,
    CampaignSchema,
    MarketingAssetCreate,
    MarketingAssetSchema,
    AuditLogSchema,
)
from src.database.exceptions import (
    DatabaseError,
    DatabaseConnectionError,
    DatabaseTransactionError,
    DatabaseMigrationError,
    DatabaseBackupError,
    DatabaseRestoreError,
    ModelNotFoundError,
)
from src.database.constants import (
    DIALECT_SQLITE,
    DIALECT_POSTGRESQL,
)

__all__ = [
    "DatabaseManager",
    "UnitOfWork",
    "Base",
    "Campaign",
    "MarketingAsset",
    "AuditLog",
    "CampaignCreate",
    "CampaignSchema",
    "MarketingAssetCreate",
    "MarketingAssetSchema",
    "AuditLogSchema",
    "DatabaseError",
    "DatabaseConnectionError",
    "DatabaseTransactionError",
    "DatabaseMigrationError",
    "DatabaseBackupError",
    "DatabaseRestoreError",
    "ModelNotFoundError",
    "DIALECT_SQLITE",
    "DIALECT_POSTGRESQL",
]
