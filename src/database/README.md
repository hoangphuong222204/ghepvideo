# Module 03: Database Layer

The `src/database` package provides a robust, enterprise-grade, thread-safe persistence and transaction management layer for **AI Marketing Studio PRO**. 

Designed with a Local-First approach, it defaults to a highly optimized SQLite database utilizing Write-Ahead Logging (WAL) and foreign keys, while remaining completely ready for a PostgreSQL migration in production.

---

## Features

- **Thread-safe Singleton Manager**: Coordinates connections and transactional sessions across threads securely using standard python lock synchronization.
- **Modern SQLAlchemy 2.x ORM**: Fully leverages modern type mapping (`Mapped` and `mapped_column`) and standard declarative schemas.
- **Repository Pattern**: Segregates business logic from SQL mechanics through generic `BaseRepository` and concrete, specialized repositories.
- **Unit of Work (UoW)**: Bundles transactional logic together, ensuring atomic commits and safe rollbacks for group repository operations.
- **High-Performance SQLite Tuning**: Automatically applies SQLite-specific pragma optimizations (WAL journal mode, synchronous normal, foreign key validation) on connect.
- **Metadata-Driven Auto-Migrations**: Discovers schema definitions automatically, initializes tables, and maintains database version state without external CLI tools.
- **Zero-Downtime Hot Backups**: Safely creates non-blocking database clones online using SQLite's backup API, protecting against file locks and corruption.
- **Secure Hot Restores**: Releases file handles gracefully and replaces active databases with validated backups, incorporating automatic safeguards.
- **Active Health Monitoring**: Performs fast, lightweight connection pool verification (ping) and supports dynamic reconnection.

---

## Directory Structure

```text
src/database/
├── __init__.py             # Public package exports
├── database_manager.py     # Thread-safe Singleton Database Manager & Unit of Work (UoW)
├── connection.py           # Engine initialization and SQLite optimization pragmas
├── session.py              # Scoped thread-safe session lifecycle managers
├── base_repository.py      # Abstract/Generic CRUD repository interface
├── repository.py           # Concrete repositories (Campaigns, Assets, Logs)
├── models.py               # SQLAlchemy Declarative Base and schema tables
├── schema.py               # Dataclass-based DTOs (Data Transfer Objects)
├── query_builder.py        # Fluent dynamic query builder helpers
├── migrations.py           # Version tracking & automatic schema migrator
├── backup.py               # Non-blocking SQLite online backup system
├── restore.py              # Hot-swap database file restore engine
├── exceptions.py           # Database-specific custom exception classes
├── constants.py            # SQLite pragmas and connection defaults
└── README.md               # Package documentation (this file)
```

---

## Core Architecture Design

### 1. Connection Pool & Pragmas (`connection.py`)
Provides the `ConnectionFactory` to assemble the central SQLAlchemy `Engine`. It establishes a robust connection pool while subscribing to engine connection events. If SQLite is detected, it configures standard enterprise pragmas:
*   `foreign_keys = ON` — Enforces relational integrity constraint cascades.
*   `journal_mode = WAL` — Enables concurrent reader and writer operations without thread lock timeouts.
*   `synchronous = NORMAL` — Provides an outstanding balance between raw performance and transaction safety.
*   `busy_timeout = 5000` — Prevents locked errors by waiting up to 5 seconds before timeout.

### 2. Transaction Scope (`session.py`)
`SessionManager` manages transactions. The `session_scope()` context manager creates, manages, commits, and closes a session. In case of any exception, it performs an automatic rollback and wraps the original exception in a clean `DatabaseTransactionError`.

### 3. Unit of Work & Repositories (`database_manager.py`)
The `UnitOfWork` (UoW) represents a single transaction span that groups operations across multiple tables. Instantiated via `database_manager.unit_of_work()`, it exposes:
*   `uow.campaigns` -> `CampaignRepository`
*   `uow.assets` -> `MarketingAssetRepository`
*   `uow.logs` -> `AuditLogRepository`

---

## Database Models & Relationships

The database contains three principal tables:

1.  **`campaigns`**:
    *   Tracks marketing initiatives, target audiences, and budgets.
    *   One-to-Many cascade relationship to `marketing_assets`.
2.  **`marketing_assets`**:
    *   Saves generated videos, voice tracks, and prompt context details.
    *   Contains a foreign key back to the parent campaign ID.
3.  **`audit_logs`**:
    *   Records system-wide transactions, backup histories, and schema alterations.

---

## Usage Examples

### 1. Initialize and Setup Schema on Startup
```python
from src.database import DatabaseManager

# Initialize the manager (singleton instance)
db_manager = DatabaseManager()

# Automatically create tables and apply migrations
db_manager.initialize_schema()
```

### 2. Standard Unit of Work (Repository CRUD)
```python
from src.database import DatabaseManager, CampaignCreate, MarketingAssetCreate

db_manager = DatabaseManager()

# Execute a safe transactional Unit of Work
with db_manager.unit_of_work() as uow:
    # 1. Create a Campaign
    campaign = uow.campaigns.create({
        "title": "Summer Flash Sale",
        "description": "Video ad campaign for summer discounts",
        "target_audience": "Gen Z retail buyers",
        "budget": 1500.00
    })
    
    # 2. Add an Asset attached to that Campaign
    asset = uow.assets.create({
        "campaign_id": campaign.id,
        "title": "Summer Voiceover Track",
        "asset_type": "audio",
        "file_path": "exports/voice/summer_vo.mp3",
        "gemini_prompt": "Create an upbeat product voice promo"
    })
    
    # 3. Log the operation
    uow.logs.log_event(
        event_type="ASSET_GENERATION",
        description=f"Added audio asset ID {asset.id} for Campaign {campaign.id}"
    )

# When the block exits, the transaction is automatically committed!
# If an exception was raised, everything would roll back cleanly.
```

### 3. Connection Health Check and Reconnection
```python
db_manager = DatabaseManager()

if not db_manager.health_check():
    print("Database pool is unresponsive! Attempting reconnect...")
    db_manager.reconnect()
```

### 4. Zero-Downtime Hot Backup & Restore
```python
db_manager = DatabaseManager()

# 1. Back up database online (creates backups/backup_YYYYMMDD_HHMMSS.db)
backup_file = db_manager.backup_database()
print(f"Hot backup created at: {backup_file}")

# 2. Restore database (disposes current pool, swaps files safely, and reconnects)
db_manager.restore_database(backup_file)
print("Database restored and reconnected successfully!")
```
