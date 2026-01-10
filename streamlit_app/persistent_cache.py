# Persistent API Response Cache
# Provides file-based caching for API responses with TTL and size management

import json
import hashlib
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import logging
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Represents a cached API response with metadata."""
    key: str
    data: Any
    timestamp: float
    expires_at: float
    metadata: Dict[str, Any]
    access_count: int = 0
    last_accessed: float = 0.0

    def is_expired(self) -> bool:
        """Check if the cache entry has expired."""
        return time.time() > self.expires_at

    def update_access(self):
        """Update access statistics."""
        self.access_count += 1
        self.last_accessed = time.time()

class PersistentCache:
    """
    File-based cache for API responses with TTL, size limits, and persistence.

    Features:
    - Automatic expiration and cleanup
    - Size limits with LRU eviction
    - Persistent storage across restarts
    - Compression for large entries
    - Access statistics and monitoring
    """

    def __init__(self,
                 cache_dir: str = "./api_cache",
                 max_entries: int = 1000,
                 default_ttl: int = 3600,  # 1 hour
                 max_file_size: int = 10 * 1024 * 1024,  # 10MB per file
                 cleanup_interval: int = 300):  # 5 minutes
        """
        Initialize persistent cache.

        Args:
            cache_dir: Directory to store cache files
            max_entries: Maximum number of entries to keep in memory
            default_ttl: Default time-to-live in seconds
            max_file_size: Maximum size per cache file
            cleanup_interval: How often to run cleanup in seconds
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)  # Create parent directories too

        self.max_entries = max_entries
        self.default_ttl = default_ttl
        self.max_file_size = max_file_size
        self.cleanup_interval = cleanup_interval

        # In-memory cache for fast access
        self.memory_cache: Dict[str, CacheEntry] = {}

        # Statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "errors": 0,
            "last_cleanup": time.time()
        }

        # Load existing cache entries
        self._load_cache()

        logger.info(f"PersistentCache initialized with {len(self.memory_cache)} entries")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve a value from cache.

        Args:
            key: Cache key
            default: Default value if key not found

        Returns:
            Cached value or default
        """
        try:
            entry = self.memory_cache.get(key)

            if entry is None:
                self.stats["misses"] += 1
                return default

            if entry.is_expired():
                self._remove_entry(key)
                self.stats["misses"] += 1
                return default

            # Update access statistics
            entry.update_access()
            self.stats["hits"] += 1

            return entry.data

        except Exception as e:
            logger.warning(f"Cache get error for key '{key}': {e}")
            self.stats["errors"] += 1
            return default

    def set(self, key: str, value: Any, ttl: Optional[int] = None, metadata: Optional[Dict] = None) -> bool:
        """
        Store a value in cache.

        Args:
            key: Cache key
            value: Value to store
            ttl: Time-to-live in seconds (uses default if None)
            metadata: Additional metadata to store

        Returns:
            True if successful, False otherwise
        """
        try:
            ttl = ttl or self.default_ttl
            expires_at = time.time() + ttl
            metadata = metadata or {}

            entry = CacheEntry(
                key=key,
                data=value,
                timestamp=time.time(),
                expires_at=expires_at,
                metadata=metadata
            )

            # Check size limits
            if len(self.memory_cache) >= self.max_entries:
                self._evict_lru()

            # Store in memory
            self.memory_cache[key] = entry

            # Persist to disk
            self._save_entry(entry)

            return True

        except Exception as e:
            logger.warning(f"Cache set error for key '{key}': {e}")
            self.stats["errors"] += 1
            return False

    def delete(self, key: str) -> bool:
        """
        Remove a key from cache.

        Args:
            key: Cache key to remove

        Returns:
            True if removed, False if not found
        """
        try:
            if key in self.memory_cache:
                self._remove_entry(key)
                return True
            return False
        except Exception as e:
            logger.warning(f"Cache delete error for key '{key}': {e}")
            self.stats["errors"] += 1
            return False

    def clear(self) -> int:
        """
        Clear all cache entries.

        Returns:
            Number of entries cleared
        """
        try:
            count = len(self.memory_cache)
            self.memory_cache.clear()

            # Clear disk files
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    cache_file.unlink()
                except Exception as e:
                    logger.warning(f"Failed to delete cache file {cache_file}: {e}")

            logger.info(f"Cleared {count} cache entries")
            return count
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            self.stats["errors"] += 1
            return 0

    def cleanup(self) -> int:
        """
        Remove expired entries and maintain cache size.

        Returns:
            Number of entries removed
        """
        try:
            removed_count = 0
            current_time = time.time()

            # Remove expired entries
            expired_keys = [
                key for key, entry in self.memory_cache.items()
                if entry.is_expired()
            ]

            for key in expired_keys:
                self._remove_entry(key)
                removed_count += 1

            # Run LRU eviction if still over limit
            while len(self.memory_cache) > self.max_entries:
                self._evict_lru()
                removed_count += 1

            self.stats["last_cleanup"] = current_time

            if removed_count > 0:
                logger.info(f"Cache cleanup removed {removed_count} entries")

            return removed_count

        except Exception as e:
            logger.error(f"Cache cleanup error: {e}")
            self.stats["errors"] += 1
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total_requests) if total_requests > 0 else 0.0

        return {
            "entries": len(self.memory_cache),
            "max_entries": self.max_entries,
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "hit_rate": hit_rate,
            "evictions": self.stats["evictions"],
            "errors": self.stats["errors"],
            "last_cleanup": datetime.fromtimestamp(self.stats["last_cleanup"]).isoformat()
        }

    def _generate_key_hash(self, key: str) -> str:
        """Generate a hash for the cache key."""
        return hashlib.md5(key.encode()).hexdigest()

    def _get_cache_file_path(self, key_hash: str) -> Path:
        """Get the file path for a cache entry."""
        return self.cache_dir / f"{key_hash}.json"

    def _save_entry(self, entry: CacheEntry):
        """Save a cache entry to disk."""
        try:
            key_hash = self._generate_key_hash(entry.key)
            file_path = self._get_cache_file_path(key_hash)

            # Check file size limit
            entry_data = asdict(entry)
            json_data = json.dumps(entry_data, ensure_ascii=False, indent=2)

            if len(json_data.encode('utf-8')) > self.max_file_size:
                logger.warning(f"Cache entry too large for key '{entry.key}', skipping disk storage")
                return

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(json_data)

        except Exception as e:
            logger.warning(f"Failed to save cache entry '{entry.key}': {e}")

    def _load_cache(self):
        """Load cache entries from disk."""
        try:
            loaded_count = 0

            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    entry = CacheEntry(**data)

                    # Skip expired entries
                    if not entry.is_expired():
                        self.memory_cache[entry.key] = entry
                        loaded_count += 1
                    else:
                        # Remove expired file
                        cache_file.unlink()

                except Exception as e:
                    logger.warning(f"Failed to load cache file {cache_file}: {e}")
                    # Remove corrupted file
                    try:
                        cache_file.unlink()
                    except:
                        pass

            logger.info(f"Loaded {loaded_count} cache entries from disk")

        except Exception as e:
            logger.error(f"Failed to load cache: {e}")

    def _remove_entry(self, key: str):
        """Remove a cache entry from memory and disk."""
        try:
            if key in self.memory_cache:
                del self.memory_cache[key]

            # Remove from disk
            key_hash = self._generate_key_hash(key)
            file_path = self._get_cache_file_path(key_hash)
            if file_path.exists():
                file_path.unlink()

        except Exception as e:
            logger.warning(f"Failed to remove cache entry '{key}': {e}")

    def _evict_lru(self):
        """Evict the least recently used entry."""
        try:
            if not self.memory_cache:
                return

            # Find LRU entry
            lru_key = min(self.memory_cache.keys(),
                         key=lambda k: self.memory_cache[k].last_accessed)

            self._remove_entry(lru_key)
            self.stats["evictions"] += 1

            logger.debug(f"Evicted LRU cache entry: {lru_key}")

        except Exception as e:
            logger.warning(f"LRU eviction error: {e}")

# Global cache instances for different API types
WIKTIONARY_CACHE = PersistentCache(
    cache_dir="./cache/wiktionary",
    max_entries=500,
    default_ttl=24 * 3600,  # 24 hours
)

TRANSLATION_CACHE = PersistentCache(
    cache_dir="./cache/translation",
    max_entries=1000,
    default_ttl=7 * 24 * 3600,  # 7 days
)

# Convenience functions
def get_cached_response(cache: PersistentCache, key: str, fetch_func, *args, **kwargs):
    """
    Get a cached response or fetch and cache it.

    Args:
        cache: Cache instance to use
        key: Cache key
        fetch_func: Function to fetch data if not cached
        *args: Arguments for fetch function
        **kwargs: Keyword arguments for fetch function

    Returns:
        Cached or freshly fetched data
    """
    # Try cache first
    cached_data = cache.get(key)
    if cached_data is not None:
        logger.debug(f"Cache hit for key: {key}")
        return cached_data

    # Fetch fresh data
    logger.debug(f"Cache miss for key: {key}, fetching fresh data")
    try:
        data = fetch_func(*args, **kwargs)

        # Cache the result
        metadata = {
            "fetch_time": time.time(),
            "source": fetch_func.__name__
        }
        cache.set(key, data, metadata=metadata)

        return data

    except Exception as e:
        logger.warning(f"Failed to fetch data for cache key '{key}': {e}")
        # Return None or re-raise based on requirements
        raise


def warm_cache_for_language(language: str, top_words: int = 100, batch_size: int = 10) -> Dict[str, int]:
    """
    Pre-warm caches by fetching enrichment data for the most common words in a language.

    This significantly improves performance for deck generation by ensuring the most
    frequently used words are already cached.

    Args:
        language: Language name (e.g., "Hindi", "Spanish")
        top_words: Number of top frequency words to pre-warm (default: 100)
        batch_size: Number of words to process in each batch (default: 10)

    Returns:
        Dictionary with cache warming statistics
    """
    import os
    import pandas as pd
    from word_data_fetcher import enrich_word_data_batch

    logger.info(f"Starting cache warming for {language} with top {top_words} words")

    # Language code to filename mapping
    lang_code_map = {
        "Hindi": "Hindi (HI).xlsx",
        "Spanish": "Spanish (ES).xlsx",
        "French": "French (FR).xlsx",
        "German": "German (DE).xlsx",
        "Chinese": "Chinese (Simplified) (ZH-CN).xlsx",
        "Japanese": "Japanese (JA).xlsx",
        "Korean": "Korean (KO).xlsx",
        "Arabic": "Arabic (AR).xlsx",
        "Russian": "Russian (RU).xlsx",
        "Portuguese": "Portuguese (PT).xlsx",
        "Italian": "Italian (IT).xlsx",
        "Dutch": "Dutch (NL).xlsx",
        "Swedish": "Swedish (SV).xlsx",
        "Danish": "Danish (DA).xlsx",
        "Norwegian": "Norwegian (NO).xlsx",
        "Finnish": "Finnish (FI).xlsx",
        "Polish": "Polish (PL).xlsx",
        "Czech": "Czech (CS).xlsx",
        "Hungarian": "Hungarian (HU).xlsx",
        "Greek": "Greek (EL).xlsx",
        "Turkish": "Turkish (TR).xlsx",
        "Hebrew": "Hebrew (IW).xlsx",
        "Thai": "Thai (TH).xlsx",
        "Vietnamese": "Vietnamese (VI).xlsx",
        "Indonesian": "Indonesian (ID).xlsx"
    }

    filename = lang_code_map.get(language)
    if not filename:
        logger.warning(f"No frequency list available for language: {language}")
        return {"error": f"No frequency list for {language}"}

    freq_file_path = os.path.join("77 Languages Frequency Word Lists", filename)

    if not os.path.exists(freq_file_path):
        logger.warning(f"Frequency file not found: {freq_file_path}")
        return {"error": f"Frequency file not found: {freq_file_path}"}

    try:
        # Read frequency list
        df = pd.read_excel(freq_file_path)
        word_column = df.columns[0]  # First column contains the words

        # Get top words, clean them
        words = df[word_column].head(top_words).dropna().astype(str).str.strip().tolist()
        words = [w for w in words if w and len(w) > 0]

        if not words:
            logger.warning(f"No valid words found in frequency list for {language}")
            return {"error": f"No valid words in frequency list"}

        logger.info(f"Loaded {len(words)} words from {language} frequency list")

        # Warm cache in batches
        successful = 0
        failed = 0

        for i in range(0, len(words), batch_size):
            batch_words = words[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(words) + batch_size - 1) // batch_size

            logger.info(f"Warming cache batch {batch_num}/{total_batches} for {language}")

            try:
                # Use batch enrichment to warm caches
                results = enrich_word_data_batch(batch_words, language, batch_size=batch_size)

                # Count successes/failures
                for word, result in results.items():
                    if "Error" not in result:
                        successful += 1
                    else:
                        failed += 1

            except Exception as e:
                logger.error(f"Failed to warm cache batch {batch_num} for {language}: {e}")
                failed += len(batch_words)

        logger.info(f"Cache warming completed for {language}: {successful} successful, {failed} failed")

        return {
            "language": language,
            "words_attempted": len(words),
            "successful": successful,
            "failed": failed,
            "success_rate": successful / len(words) if words else 0
        }

    except Exception as e:
        logger.error(f"Cache warming failed for {language}: {e}")
        return {"error": str(e)}


def warm_cache_for_multiple_languages(languages: List[str], top_words: int = 100, batch_size: int = 10) -> Dict[str, Dict]:
    """
    Pre-warm caches for multiple languages.

    Args:
        languages: List of language names
        top_words: Number of top words per language
        batch_size: Batch size for processing

    Returns:
        Dictionary mapping language to warming results
    """
    results = {}

    for language in languages:
        logger.info(f"Starting cache warming for {language}")
        result = warm_cache_for_language(language, top_words, batch_size)
        results[language] = result

        # Small delay between languages to be respectful to APIs
        time.sleep(1)

def warm_cache_for_multiple_languages(languages: List[str], top_words: int = 100, batch_size: int = 10) -> Dict[str, Dict]:
    """
    Pre-warm caches for multiple languages.

    Args:
        languages: List of language names
        top_words: Number of top words per language
        batch_size: Batch size for processing

    Returns:
        Dictionary mapping language to warming results
    """
    results = {}

    for language in languages:
        logger.info(f"Starting cache warming for {language}")
        result = warm_cache_for_language(language, top_words, batch_size)
        results[language] = result

        # Small delay between languages to be respectful to APIs
        time.sleep(1)

    return results


# ============================================================================
# MEMORY MANAGEMENT UTILITIES
# ============================================================================

def get_memory_usage() -> Dict[str, float]:
    """
    Get current memory usage statistics.

    Returns:
        Dictionary with memory usage information in MB
    """
    try:
        import psutil  # type: ignore
        process = psutil.Process()
        memory_info = process.memory_info()

        return {
            "rss": memory_info.rss / 1024 / 1024,  # Resident Set Size in MB
            "vms": memory_info.vms / 1024 / 1024,  # Virtual Memory Size in MB
            "percent": process.memory_percent()
        }
    except ImportError:
        logger.warning("psutil not available for memory monitoring")
        return {"error": "psutil not installed"}
    except Exception as e:
        logger.warning(f"Memory monitoring failed: {e}")
        return {"error": str(e)}


def optimize_memory_for_large_datasets(max_memory_mb: float = 500) -> bool:
    """
    Optimize memory usage for large dataset processing.

    Args:
        max_memory_mb: Maximum allowed memory usage in MB

    Returns:
        True if optimization was performed, False otherwise
    """
    import gc

    try:
        memory_info = get_memory_usage()

        if "error" in memory_info:
            logger.warning("Cannot monitor memory usage, skipping optimization")
            return False

        current_memory = memory_info.get("rss", 0)

        if current_memory > max_memory_mb:
            logger.info(f"Memory usage ({current_memory:.1f}MB) exceeds limit ({max_memory_mb}MB), optimizing...")

            # Force garbage collection
            collected = gc.collect()
            logger.info(f"Garbage collection freed {collected} objects")

            # Clear any cached data that's not in use
            # Note: This is conservative - we don't want to clear valid caches

            # Check memory again
            memory_after = get_memory_usage()
            memory_after_mb = memory_after.get("rss", 0)

            logger.info(f"Memory after optimization: {memory_after_mb:.1f}MB (was {current_memory:.1f}MB)")

            return memory_after_mb < current_memory

        return False

    except Exception as e:
        logger.warning(f"Memory optimization failed: {e}")
        return False


def process_large_dataset_with_memory_management(
    items: List[Any],
    process_func,
    batch_size: int = 50,
    max_memory_mb: float = 500,
    progress_callback: Optional[callable] = None
) -> List[Any]:
    """
    Process large datasets with automatic memory management.

    Args:
        items: List of items to process
        process_func: Function to process each batch
        batch_size: Number of items per batch
        max_memory_mb: Memory limit before triggering optimization
        progress_callback: Optional callback for progress updates

    Returns:
        List of processed results
    """
    results = []
    total_items = len(items)

    for i in range(0, total_items, batch_size):
        batch = items[i:i + batch_size]
        batch_num = i // batch_size + 1
        total_batches = (total_items + batch_size - 1) // batch_size

        if progress_callback:
            progress_callback(batch_num, total_batches, len(batch))

        logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} items)")

        try:
            # Process batch
            batch_results = process_func(batch)
            results.extend(batch_results)

            # Check memory usage and optimize if needed
            optimized = optimize_memory_for_large_datasets(max_memory_mb)
            if optimized:
                logger.info("Memory optimization performed during batch processing")

        except Exception as e:
            logger.error(f"Failed to process batch {batch_num}: {e}")
            # Continue with next batch rather than failing completely
            continue

    logger.info(f"Large dataset processing completed: {len(results)}/{total_items} items processed")
    return results