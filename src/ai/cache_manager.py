"""Thread-safe SQLite-backed prompt and response cache system supporting TTL expiration."""

import os
import time
import json
import sqlite3
import hashlib
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger("AIMSPro.AI")

class CacheManager:
    """Thread-safe Cache Manager implementing high-performance local SQLite storage.

    Features automatic schema migrations, automatic TTL expiration, and active
    cache hit/miss metric logs.
    """

    def __init__(self, cache_dir: Optional[Path] = None, ttl: int = 86400) -> None:
        """Initializes the SQLite cache manager.

        Args:
            cache_dir: Base directory to place the cache file. Defaults to ./cache.
            ttl: Default time-to-live in seconds (defaults to 24 hours).
        """
        self._default_ttl = ttl
        
        # Fallback to local 'cache' if not specified
        if cache_dir is None:
            self._cache_dir = Path("./cache")
        else:
            self._cache_dir = cache_dir

        self._db_path = self._cache_dir / "ai_cache.db"
        self._initialize_database()

    def _initialize_database(self) -> None:
        """Assembles the SQLite schema and indexes safely."""
        try:
            self._cache_dir.mkdir(parents=True, exist_ok=True)
            conn = self._get_connection()
            try:
                with conn:
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS ai_cache (
                            cache_key TEXT PRIMARY KEY,
                            prompt_hash TEXT NOT NULL,
                            request_metadata TEXT,
                            response_text TEXT NOT NULL,
                            response_metadata TEXT,
                            expires_at REAL NOT NULL,
                            created_at REAL NOT NULL
                        )
                    """)
                    # Create indexes for high-speed lookups
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_expires_at ON ai_cache(expires_at)")
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_prompt_hash ON ai_cache(prompt_hash)")
            finally:
                conn.close()
        except Exception as e:
            logger.error(f"Failed to initialize SQLite Cache database at {self._db_path}: {e}")

    def _get_connection(self) -> sqlite3.Connection:
        """Gets a new connection.

        Opening new connections thread-locally is the safest way to avoid SQLite
        concurrency issues.
        """
        # Set busy_timeout to 5 seconds to handle parallel lock scenarios gracefully
        conn = sqlite3.connect(str(self._db_path), timeout=5.0)
        conn.row_factory = sqlite3.Row
        return conn

    def generate_key(self, model_name: str, prompt: str, system_instruction: Optional[str] = None, config_dict: Optional[Dict[str, Any]] = None) -> str:
        """Generates a stable SHA-256 string representing the unique signature of this request.

        Args:
            model_name: Active model.
            prompt: User-provided prompt content.
            system_instruction: System prompt role.
            config_dict: Dictionary representation of configuration.
        """
        payload = {
            "model_name": model_name,
            "prompt": prompt,
            "system_instruction": system_instruction or "",
            "config": config_dict or {}
        }
        serialized = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def get(self, key: str) -> Optional[str]:
        """Retrieves a cached response from SQLite if it is not expired.

        Args:
            key: Clean SHA-256 generated key.

        Returns:
            The cached response text or None (Cache Miss).
        """
        conn = self._get_connection()
        try:
            row = conn.execute(
                "SELECT response_text, expires_at FROM ai_cache WHERE cache_key = ?",
                (key,)
            ).fetchone()
            
            if row is None:
                logger.debug(f"Cache MISS [Key: {key[:8]}...]")
                return None

            expires_at = row["expires_at"]
            if time.time() > expires_at:
                logger.debug(f"Cache EXPIRED [Key: {key[:8]}...]")
                # Lazy delete expired entry
                self.delete(key)
                return None

            logger.info(f"Cache HIT [Key: {key[:8]}...]")
            return row["response_text"]
        except Exception as e:
            logger.warning(f"Error querying cache key '{key}': {e}")
            return None
        finally:
            conn.close()

    def set(self, key: str, prompt: str, response_text: str, model_name: str, config_dict: Optional[Dict[str, Any]] = None, ttl: Optional[int] = None) -> None:
        """Caches a response into the SQLite database.

        Args:
            key: SHA-256 generated key.
            prompt: User prompt content.
            response_text: The generated text output.
            model_name: Active model used.
            config_dict: Active parameters configuration.
            ttl: Custom time-to-live in seconds. If None, uses default.
        """
        active_ttl = ttl if ttl is not None else self._default_ttl
        now = time.time()
        expires_at = now + active_ttl
        
        prompt_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        req_meta = json.dumps(config_dict or {})
        resp_meta = json.dumps({"model_name": model_name})

        conn = self._get_connection()
        try:
            with conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO ai_cache 
                    (cache_key, prompt_hash, request_metadata, response_text, response_metadata, expires_at, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (key, prompt_hash, req_meta, response_text, resp_meta, expires_at, now)
                )
            logger.debug(f"Cache SET [Key: {key[:8]}... | TTL: {active_ttl}s]")
        except Exception as e:
            logger.warning(f"Error writing to cache key '{key}': {e}")
        finally:
            conn.close()

    def delete(self, key: str) -> None:
        """Deletes a specific cache key."""
        conn = self._get_connection()
        try:
            with conn:
                conn.execute("DELETE FROM ai_cache WHERE cache_key = ?", (key,))
        except Exception as e:
            logger.warning(f"Error deleting cache key '{key}': {e}")
        finally:
            conn.close()

    def cleanup(self) -> int:
        """Deletes all expired cache entries from SQLite.

        Returns:
            The total count of rows purged.
        """
        now = time.time()
        conn = self._get_connection()
        try:
            with conn:
                cursor = conn.execute("DELETE FROM ai_cache WHERE expires_at < ?", (now,))
                deleted_count = cursor.rowcount
            if deleted_count > 0:
                logger.info(f"Purged {deleted_count} expired entries from SQLite Cache.")
            return deleted_count
        except Exception as e:
            logger.warning(f"Error cleaning up expired cache entries: {e}")
            return 0
        finally:
            conn.close()

    def clear(self) -> None:
        """Completely flushes the entire Cache table."""
        conn = self._get_connection()
        try:
            with conn:
                conn.execute("DELETE FROM ai_cache")
            logger.info("Cleared the entire SQLite Prompt Cache.")
        except Exception as e:
            logger.warning(f"Error clearing cache: {e}")
        finally:
            conn.close()
