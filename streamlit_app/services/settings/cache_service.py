"""
Cache Manager Service
Handles cache operations and statistics display.
"""

import streamlit as st
from typing import Dict, Any


class CacheService:
    """Service for cache management operations."""

    def __init__(self):
        """Initialize the cache service."""
        self._cache_manager = None

    def _get_cache_manager(self):
        """Get or initialize the cache manager."""
        if self._cache_manager is None:
            try:
                from cache_manager import get_cache_manager
                self._cache_manager = get_cache_manager()
            except Exception as e:
                st.error(f"Cache manager unavailable: {e}")
                return None
        return self._cache_manager

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        cache_manager = self._get_cache_manager()
        if cache_manager:
            return cache_manager.get_stats()
        return {
            'memory_entries': 0,
            'max_memory_entries': 0,
            'disk_entries': 0,
            'hits': 0,
            'misses': 0,
            'cache_dir': 'N/A'
        }

    def clear_all_cache(self) -> int:
        """
        Clear all cached entries.

        Returns:
            Number of entries cleared
        """
        cache_manager = self._get_cache_manager()
        if cache_manager:
            return cache_manager.clear_all()
        return 0

    def clear_expired_cache(self) -> None:
        """Clear expired cache entries."""
        cache_manager = self._get_cache_manager()
        if cache_manager:
            cache_manager.cleanup()

    def clear_namespace_cache(self, namespace: str) -> int:
        """
        Clear cache entries for a specific namespace.

        Args:
            namespace: Cache namespace to clear

        Returns:
            Number of entries cleared
        """
        cache_manager = self._get_cache_manager()
        if cache_manager:
            return cache_manager.clear_namespace(namespace)
        return 0

    def clear_gemini_cache(self) -> int:
        """
        Clear all Gemini-related cache entries.

        Returns:
            Number of entries cleared
        """
        total_cleared = 0
        total_cleared += self.clear_namespace_cache("gemini_meaning")
        total_cleared += self.clear_namespace_cache("gemini_sentences_pass1")
        total_cleared += self.clear_namespace_cache("gemini_sentences_pass2")
        return total_cleared

    def clear_image_cache(self) -> int:
        """
        Clear image search cache entries.

        Returns:
            Number of entries cleared
        """
        return self.clear_namespace_cache("google_image_search")

    def is_cache_available(self) -> bool:
        """
        Check if cache functionality is available.

        Returns:
            True if cache is available, False otherwise
        """
        return self._get_cache_manager() is not None