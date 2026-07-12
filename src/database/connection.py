"""Database Connection Engine builder and connection pool manager."""

import os
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union
from sqlalchemy import create_engine, text, event
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from src.database.constants import (
    DIALECT_SQLITE,
    DIALECT_POSTGRESQL,
    DEFAULT_SQLITE_PATH,
    DEFAULT_POOL_SIZE,
    DEFAULT_MAX_OVERFLOW,
    DEFAULT_POOL_TIMEOUT,
    DEFAULT_POOL_RECYCLE,
    SQLITE_PRAGMAS,
)
from src.database.exceptions import DatabaseConnectionError
from src.config.config_manager import ConfigManager

logger = logging.getLogger("AIMSPro.Database.Connection")


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection: Any, connection_record: Any) -> None:
    """Listens for engine connection events and applies high-performance SQLite pragmas.

    Only applies pragmas to standard SQLite connections.
    """
    # Check if the connection has a cursor method (standard dbapi)
    if hasattr(dbapi_connection, "cursor"):
        cursor = dbapi_connection.cursor()
        try:
            # Check if it is sqlite (the module name is sqlite3 or similar)
            module_name = type(dbapi_connection).__module__
            if "sqlite" in module_name.lower():
                for pragma_name, pragma_value in SQLITE_PRAGMAS:
                    cursor.execute(f"PRAGMA {pragma_name}={pragma_value};")
                dbapi_connection.commit()
        except Exception as e:
            logger.warning(f"Failed to apply SQLite performance pragmas: {e}")
        finally:
            cursor.close()


class ConnectionFactory:
    """Factory for building fully-configured SQLAlchemy Engines with connection pooling."""

    @staticmethod
    def get_connection_url() -> str:
        """Resolves the database connection URL from Module 01 Config Manager.

        Defaults to SQLite if no PostgreSQL environment override is present.

        Returns:
            The formatted connection URL.
        """
        # Read from config manager
        try:
            config = ConfigManager().config
            sqlite_path = config.database.sqlite_path
        except Exception as e:
            logger.warning(f"Could not load ConfigManager: {e}. Falling back to default SQLite path.")
            sqlite_path = DEFAULT_SQLITE_PATH

        # Allow environment overrides (ideal for PostgreSQL or custom SQLite paths in production)
        env_url = os.getenv("DATABASE_URL")
        if env_url:
            # SQLite protocol fix for multi-slash paths if needed
            return env_url

        # Ensure sqlite directory exists
        path_obj = Path(sqlite_path)
        if not path_obj.is_absolute():
            # Place database relative to current working directory
            path_obj = Path.cwd() / path_obj
        
        path_obj.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{path_obj.as_posix()}"

    @classmethod
    def create_engine_instance(
        cls,
        connection_url: Optional[str] = None,
        pool_size: int = DEFAULT_POOL_SIZE,
        max_overflow: int = DEFAULT_MAX_OVERFLOW,
        pool_timeout: int = DEFAULT_POOL_TIMEOUT,
        pool_recycle: int = DEFAULT_POOL_RECYCLE,
    ) -> Engine:
        """Constructs and returns a unified SQLAlchemy Engine instance.

        Adapts pool settings automatically depending on the target database dialect.

        Args:
            connection_url: Optional explicit URL. If omitted, resolved automatically.
            pool_size: Number of connections to keep in the pool.
            max_overflow: Maximum excess connections allowed above pool_size.
            pool_timeout: Seconds to wait for a free connection from the pool.
            pool_recycle: Connection lifetime recycle threshold.

        Returns:
            A configured SQLAlchemy Engine.
        """
        url = connection_url or cls.get_connection_url()
        
        # Determine dialect from URL
        is_sqlite = url.startswith("sqlite")
        
        engine_args: Dict[str, Any] = {
            "pool_recycle": pool_recycle,
        }

        # Apply dialect-specific parameters
        if is_sqlite:
            # SQLite does not support standard pool_size/max_overflow in standard StaticPool
            if ":memory:" in url:
                # In-memory requires SingletonThreadPool or StaticPool to keep connection alive
                from sqlalchemy.pool import StaticPool
                engine_args["poolclass"] = StaticPool
                engine_args["connect_args"] = {"check_same_thread": False}
            else:
                engine_args["connect_args"] = {"check_same_thread": False, "timeout": pool_timeout}
        else:
            # PostgreSQL or standard client-server relational databases
            engine_args["pool_size"] = pool_size
            engine_args["max_overflow"] = max_overflow
            engine_args["pool_timeout"] = pool_timeout

        try:
            logger.info(f"Initializing database engine on dialect: {'SQLite' if is_sqlite else 'Relational Server'}")
            engine = create_engine(url, **engine_args)
            return engine
        except Exception as e:
            raise DatabaseConnectionError(f"Failed to create SQLAlchemy engine instance: {e}") from e

    @staticmethod
    def ping_engine(engine: Engine) -> bool:
        """Performs a lightweight ping health check to verify active connectivity.

        Args:
            engine: The target SQLAlchemy Engine.

        Returns:
            True if database is alive and responsive, False otherwise.
        """
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except SQLAlchemyError as e:
            logger.error(f"Database health check ping failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during database ping: {e}")
            return False
