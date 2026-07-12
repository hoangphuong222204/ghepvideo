"""Thread-safe template cache supporting TTL and max size eviction policy."""

import datetime
import threading
from typing import Any, Dict, Optional, Tuple


class TemplateCache:
    """High-performance, thread-safe memory cache with TTL expiration and item capacity limits."""

    def __init__(self, max_size: int = 1000, default_ttl_seconds: int = 300) -> None:
        """Initializes the TemplateCache.

        Args:
            max_size: Maximum items allowed in cache before eviction.
            default_ttl_seconds: Default Time-To-Live for cache keys.
        """
        self._max_size = max_size
        self._default_ttl = default_ttl_seconds
        # Structure: key -> (value, expires_at, last_accessed_at)
        self._cache: Dict[str, Tuple[Any, datetime.datetime, datetime.datetime]] = {}
        self._lock = threading.Lock()
        
        # Cache metrics
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[Any]:
        """Retrieves an item from cache if it exists and hasn't expired."""
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None

            value, expires_at, _ = self._cache[key]
            now = datetime.datetime.utcnow()

            # Evict if expired
            if now > expires_at:
                del self._cache[key]
                self._misses += 1
                return None

            # Update last accessed and hit counts
            self._cache[key] = (value, expires_at, now)
            self._hits += 1
            return value

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """Saves a key-value pair into the cache with a specified or default TTL."""
        ttl = ttl_seconds if ttl_seconds is not None else self._default_ttl
        now = datetime.datetime.utcnow()
        expires_at = now + datetime.timedelta(seconds=ttl)

        with self._lock:
            # Enforce max size limit (evict Least Recently Used)
            if len(self._cache) >= self._max_size and key not in self._cache:
                self._evict_lru()

            self._cache[key] = (value, expires_at, now)

    def delete(self, key: str) -> bool:
        """Manually removes a key from cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self) -> None:
        """Wipes the entire cache and resets performance metrics."""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0

    def get_stats(self) -> Dict[str, Any]:
        """Returns statistics for caching activities."""
        with self._lock:
            total = self._hits + self._misses
            hit_ratio = (self._hits / total) if total > 0 else 0.0
            return {
                "size": len(self._cache),
                "hits": self._hits,
                "misses": self._misses,
                "hit_ratio": round(hit_ratio, 2),
                "max_size": self._max_size,
            }

    def _evict_lru(self) -> None:
        """Evicts the least recently accessed item. Internal helper, assumes lock is held."""
        if not self._cache:
            return

        # Find key with the oldest last_accessed_at timestamp
        lru_key = min(self._cache.keys(), key=lambda k: self._cache[k][2])
        del self._cache[lru_key]
