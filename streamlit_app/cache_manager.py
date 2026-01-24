# cache_manager.py - Response caching system for API calls

import json
import hashlib
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional, Union
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Represents a cached API response."""
    key: str
    data: Any
    timestamp: float
    expires_at: float
    metadata: Dict[str, Any]

class CacheManager:
    """
    Manages API response caching with configurable expiration and persistence.

    Features:
    - Automatic cache expiration
    - Persistent storage (JSON files)
    - Memory caching for performance
    - Cache statistics and management
    - Configurable cache sizes and TTL
    """

    def __init__(self, cache_dir: str = "./cache", max_memory_entries: int = 1000):
        """
        Initialize cache manager.

        Args:
            cache_dir: Directory to store persistent cache files
            max_memory_entries: Maximum entries to keep in memory
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.max_memory_entries = max_memory_entries

        # In-memory cache for fast access
        self.memory_cache: Dict[str, CacheEntry] = {}

        # Cache statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'expired_cleanups': 0
        }

        # Load persistent cache on startup
        self._load_persistent_cache()

        logger.info(f"CacheManager initialized with cache dir: {cache_dir}")

    def _generate_cache_key(self, namespace: str, params: Dict[str, Any]) -> str:
        """
        Generate a unique cache key from namespace and parameters.

        Args:
            namespace: Cache namespace (e.g., 'gemini_meaning', 'google_image_search')
            params: Parameters that uniquely identify the request

        Returns:
            SHA256 hash of the combined namespace and sorted parameters
        """
        # Sort parameters for consistent key generation
        sorted_params = json.dumps(params, sort_keys=True, default=str)
        key_content = f"{namespace}:{sorted_params}"
        return hashlib.sha256(key_content.encode()).hexdigest()

    def _get_cache_file_path(self, key: str) -> Path:
        """Get the file path for a cache entry."""
        return self.cache_dir / f"{key}.json"

    def _load_persistent_cache(self):
        """Load cache entries from disk into memory."""
        loaded_count = 0
        expired_count = 0

        try:
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    entry = CacheEntry(
                        key=data['key'],
                        data=data['data'],
                        timestamp=data['timestamp'],
                        expires_at=data['expires_at'],
                        metadata=data.get('metadata', {})
                    )

                    # Check if entry is still valid
                    if time.time() < entry.expires_at:
                        if len(self.memory_cache) < self.max_memory_entries:
                            self.memory_cache[entry.key] = entry
                            loaded_count += 1
                        else:
                            # Remove file if we can't keep it in memory
                            cache_file.unlink()
                    else:
                        # Remove expired file
                        cache_file.unlink()
                        expired_count += 1

                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(f"Invalid cache file {cache_file}: {e}")
                    cache_file.unlink()

        except Exception as e:
            logger.error(f"Error loading persistent cache: {e}")

        logger.info(f"Loaded {loaded_count} cache entries, removed {expired_count} expired")

    def _save_to_disk(self, entry: CacheEntry):
        """Save a cache entry to disk."""
        try:
            cache_file = self._get_cache_file_path(entry.key)
            data = {
                'key': entry.key,
                'data': entry.data,
                'timestamp': entry.timestamp,
                'expires_at': entry.expires_at,
                'metadata': entry.metadata
            }

            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)

        except Exception as e:
            logger.error(f"Error saving cache entry {entry.key}: {e}")

    def _cleanup_expired(self):
        """Remove expired entries from memory and disk."""
        current_time = time.time()
        expired_keys = []

        for key, entry in self.memory_cache.items():
            if current_time >= entry.expires_at:
                expired_keys.append(key)

        for key in expired_keys:
            del self.memory_cache[key]
            cache_file = self._get_cache_file_path(key)
            if cache_file.exists():
                cache_file.unlink()
            self.stats['expired_cleanups'] += 1

        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")

    def get(self, namespace: str, params: Dict[str, Any], ttl_seconds: Optional[int] = None) -> Optional[Any]:
        """
        Get cached data if available and not expired.

        Args:
            namespace: Cache namespace
            params: Parameters that identify the request
            ttl_seconds: Override TTL for this get operation

        Returns:
            Cached data if available, None otherwise
        """
        key = self._generate_cache_key(namespace, params)

        # Check memory cache first
        entry = self.memory_cache.get(key)
        if entry:
            current_time = time.time()
            if current_time < entry.expires_at:
                self.stats['hits'] += 1
                logger.debug(f"Cache hit for {namespace}: {key}")
                return entry.data
            else:
                # Entry expired, remove it
                del self.memory_cache[key]
                cache_file = self._get_cache_file_path(key)
                if cache_file.exists():
                    cache_file.unlink()
                self.stats['expired_cleanups'] += 1

        # Check disk cache
        cache_file = self._get_cache_file_path(key)
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                entry = CacheEntry(
                    key=data['key'],
                    data=data['data'],
                    timestamp=data['timestamp'],
                    expires_at=data['expires_at'],
                    metadata=data.get('metadata', {})
                )

                current_time = time.time()
                if current_time < entry.expires_at:
                    # Load into memory cache
                    if len(self.memory_cache) < self.max_memory_entries:
                        self.memory_cache[key] = entry
                    self.stats['hits'] += 1
                    logger.debug(f"Cache hit from disk for {namespace}: {key}")
                    return entry.data
                else:
                    # Remove expired file
                    cache_file.unlink()
                    self.stats['expired_cleanups'] += 1

            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Invalid cache file {cache_file}: {e}")
                cache_file.unlink()

        self.stats['misses'] += 1
        logger.debug(f"Cache miss for {namespace}: {key}")
        return None

    def set(self, namespace: str, params: Dict[str, Any], data: Any,
            ttl_seconds: int = 3600, metadata: Optional[Dict[str, Any]] = None):
        """
        Cache data with specified TTL.

        Args:
            namespace: Cache namespace
            params: Parameters that identify the request
            data: Data to cache
            ttl_seconds: Time to live in seconds (default 1 hour)
            metadata: Optional metadata about the cached entry
        """
        key = self._generate_cache_key(namespace, params)
        current_time = time.time()

        entry = CacheEntry(
            key=key,
            data=data,
            timestamp=current_time,
            expires_at=current_time + ttl_seconds,
            metadata=metadata or {}
        )

        # Store in memory
        if len(self.memory_cache) >= self.max_memory_entries:
            # Remove oldest entry if at capacity
            oldest_key = min(self.memory_cache.keys(),
                           key=lambda k: self.memory_cache[k].timestamp)
            del self.memory_cache[oldest_key]

        self.memory_cache[key] = entry

        # Store on disk
        self._save_to_disk(entry)

        self.stats['sets'] += 1
        logger.debug(f"Cached {namespace} data: {key} (TTL: {ttl_seconds}s)")

    def delete(self, namespace: str, params: Dict[str, Any]) -> bool:
        """
        Delete a specific cache entry.

        Args:
            namespace: Cache namespace
            params: Parameters that identify the request

        Returns:
            True if entry was deleted, False if not found
        """
        key = self._generate_cache_key(namespace, params)

        # Remove from memory
        if key in self.memory_cache:
            del self.memory_cache[key]

        # Remove from disk
        cache_file = self._get_cache_file_path(key)
        if cache_file.exists():
            cache_file.unlink()
            self.stats['deletes'] += 1
            logger.debug(f"Deleted cache entry {namespace}: {key}")
            return True

        return False

    def clear_namespace(self, namespace: str) -> int:
        """
        Clear all cache entries for a specific namespace.

        Args:
            namespace: Cache namespace to clear

        Returns:
            Number of entries deleted
        """
        deleted_count = 0

        # Remove from memory
        keys_to_remove = []
        for key, entry in self.memory_cache.items():
            if entry.metadata.get('namespace') == namespace:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del self.memory_cache[key]
            deleted_count += 1

        # Remove from disk
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    if data.get('metadata', {}).get('namespace') == namespace:
                        cache_file.unlink()
                        deleted_count += 1

                except (json.JSONDecodeError, KeyError):
                    pass

        except Exception as e:
            logger.error(f"Error clearing namespace {namespace}: {e}")

        self.stats['deletes'] += deleted_count
        logger.info(f"Cleared {deleted_count} entries for namespace {namespace}")
        return deleted_count

    def clear_all(self) -> int:
        """
        Clear all cache entries.

        Returns:
            Number of entries deleted
        """
        deleted_count = len(self.memory_cache)
        self.memory_cache.clear()

        # Remove all cache files
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
                deleted_count += 1
        except Exception as e:
            logger.error(f"Error clearing all cache: {e}")

        self.stats['deletes'] += deleted_count
        logger.info(f"Cleared all {deleted_count} cache entries")
        return deleted_count

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_entries = len(self.memory_cache)
        disk_entries = 0

        try:
            disk_entries = len(list(self.cache_dir.glob("*.json")))
        except Exception:
            pass

        return {
            'memory_entries': total_entries,
            'disk_entries': disk_entries,
            'total_entries': total_entries + disk_entries,
            'cache_dir': str(self.cache_dir),
            'max_memory_entries': self.max_memory_entries,
            **self.stats
        }

    def cleanup(self):
        """Perform maintenance cleanup (called periodically)."""
        self._cleanup_expired()

# Global cache manager instance
_cache_manager = None

def get_cache_manager() -> CacheManager:
    """Get the global cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager

def cached_api_call(namespace: str, ttl_seconds: int = 3600):
    """
    Decorator to cache API call results.

    Args:
        namespace: Cache namespace for this API
        ttl_seconds: Cache TTL in seconds (default 1 hour)

    Returns:
        Decorated function that caches results
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Extract parameters for cache key (exclude API keys and non-serializable params)
            cache_params = {}
            for key, value in kwargs.items():
                if key not in ['google_api_key', 'custom_search_engine_id']:  # Don't cache API keys
                    try:
                        json.dumps(value)  # Check if serializable
                        cache_params[key] = value
                    except (TypeError, ValueError):
                        continue

            # Add positional args to params if they have names
            import inspect
            sig = inspect.signature(func)
            param_names = list(sig.parameters.keys())[1:]  # Skip 'self' if method

            for i, arg in enumerate(args[1:]):  # Skip 'self' if method
                if i < len(param_names):
                    param_name = param_names[i]
                    if param_name not in ['google_api_key', 'custom_search_engine_id']:
                        try:
                            json.dumps(arg)
                            cache_params[param_name] = arg
                        except (TypeError, ValueError):
                            continue

            cache_manager = get_cache_manager()

            # Try to get from cache first
            cached_result = cache_manager.get(namespace, cache_params, ttl_seconds)
            if cached_result is not None:
                logger.info(f"Using cached result for {namespace}")
                return cached_result

            # Call the actual function
            result = func(*args, **kwargs)

            # Cache the result
            metadata = {'namespace': namespace, 'function': func.__name__}
            cache_manager.set(namespace, cache_params, result, ttl_seconds, metadata)

            return result

        return wrapper
    return decorator