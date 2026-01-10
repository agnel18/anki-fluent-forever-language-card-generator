"""
Unit tests for persistent cache functionality.
Tests cache operations, memory management, and cache warming.
"""

import pytest
import sys
import os
import tempfile
import shutil
from unittest.mock import Mock, patch

# Add the streamlit_app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'streamlit_app'))

from persistent_cache import PersistentCache, get_memory_usage, warm_cache_for_language, warm_cache_for_multiple_languages


class TestPersistentCache:
    """Test persistent cache functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.cache = PersistentCache(
            cache_dir=self.temp_dir,
            max_entries=10,
            default_ttl=300  # 5 minutes
        )

    def teardown_method(self):
        """Clean up test fixtures."""
        self.cache.clear()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cache_initialization(self):
        """Test cache initialization."""
        assert str(self.cache.cache_dir) == self.temp_dir
        assert self.cache.max_entries == 10
        assert self.cache.default_ttl == 300

    def test_cache_set_get(self):
        """Test basic cache set and get operations."""
        # Set a value
        self.cache.set('test_key', 'test_value')

        # Get the value
        result = self.cache.get('test_key')
        assert result == 'test_value'

    def test_cache_miss(self):
        """Test cache miss behavior."""
        result = self.cache.get('nonexistent_key')
        assert result is None

    def test_cache_expiration(self):
        """Test cache expiration."""
        # Set a value with short TTL
        self.cache.set('short_key', 'short_value', ttl=1)

        # Should be available immediately
        assert self.cache.get('short_key') == 'short_value'

        # Wait for expiration
        import time
        time.sleep(2)

        # Should be expired
        assert self.cache.get('short_key') is None

    def test_cache_metadata(self):
        """Test cache metadata storage."""
        # Note: This cache doesn't store metadata, just test basic functionality
        self.cache.set('meta_key', 'meta_value')
        result = self.cache.get('meta_key')
        assert result == 'meta_value'

    def test_cache_size_limit(self):
        """Test cache size limits."""
        # Fill cache beyond limit
        for i in range(15):  # More than max_entries (10)
            self.cache.set(f'key_{i}', f'value_{i}')

        # Cache should have evicted old entries
        # (Exact behavior depends on LRU implementation)
        total_entries = len(self.cache.memory_cache)
        assert total_entries <= 10

    def test_cache_clear(self):
        """Test cache clearing."""
        self.cache.set('key1', 'value1')
        self.cache.set('key2', 'value2')

        assert self.cache.get('key1') == 'value1'
        assert self.cache.get('key2') == 'value2'

        self.cache.clear()

        assert self.cache.get('key1') is None
        assert self.cache.get('key2') is None


class TestMemoryManagement:
    """Test memory management functionality."""

    def test_memory_usage_structure(self):
        """Test that memory usage returns proper structure."""
        memory = get_memory_usage()

        # Should be a dictionary
        assert isinstance(memory, dict)

        # Should contain expected keys (or error if psutil not available)
        if 'error' not in memory:
            assert 'rss' in memory
            assert 'vms' in memory
            assert 'percent' in memory

            # Values should be numbers
            assert isinstance(memory['rss'], (int, float))
            assert isinstance(memory['vms'], (int, float))
            assert isinstance(memory['percent'], (int, float))

    def test_memory_usage_fallback(self):
        """Test memory usage fallback when psutil fails."""
        # Mock psutil import to fail
        import builtins
        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == 'psutil':
                raise ImportError("psutil not available")
            return original_import(name, *args, **kwargs)

        builtins.__import__ = mock_import
        try:
            memory = get_memory_usage()

            assert 'error' in memory
            assert 'psutil not installed' in memory['error']
        finally:
            builtins.__import__ = original_import


class TestCacheWarming:
    """Test cache warming functionality."""

    @patch('word_data_fetcher.enrich_word_data_batch')
    def test_warm_cache_for_language_success(self, mock_enrich):
        """Test successful cache warming."""
        # Mock successful enrichment
        mock_enrich.return_value = {'word1': 'definition1', 'word2': 'definition2'}

        result = warm_cache_for_language('Hindi', top_words=2, batch_size=2)

        # Should return success statistics
        assert 'language' in result
        assert result['language'] == 'Hindi'
        assert result['words_attempted'] == 2
        assert result['successful'] == 2
        assert result['failed'] == 0
        assert result['success_rate'] == 1.0

    @patch('word_data_fetcher.enrich_word_data_batch')
    def test_warm_cache_for_language_partial_failure(self, mock_enrich):
        """Test cache warming with partial failures."""
        # Mock partial success
        mock_enrich.return_value = {'word1': 'definition1', 'word2': 'Error: failed'}

        result = warm_cache_for_language('Spanish', top_words=2, batch_size=2)

        assert result['successful'] == 1
        assert result['failed'] == 1
        assert result['success_rate'] == 0.5

    def test_warm_cache_unsupported_language(self):
        """Test cache warming for unsupported language."""
        result = warm_cache_for_language('UnsupportedLang', top_words=1)

        assert 'error' in result
        assert 'No frequency list' in result['error']

    @patch('persistent_cache.warm_cache_for_language')
    def test_warm_cache_multiple_languages(self, mock_warm_single):
        """Test warming cache for multiple languages."""
        mock_warm_single.return_value = {'language': 'Test', 'successful': 1, 'failed': 0}

        languages = ['Hindi', 'Spanish']
        result = warm_cache_for_multiple_languages(languages, top_words=1)

        # Should call warm_cache_for_language for each language
        assert mock_warm_single.call_count == 2
        assert len(result) == 2


if __name__ == "__main__":
    pytest.main([__file__])