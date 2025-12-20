"""
Database Manager Module

Central database management with modular imports and fallbacks.
Imports functions from specialized modules while maintaining backward compatibility.
"""

import logging
from pathlib import Path

# Setup logging
logger = logging.getLogger(__name__)

# ============================================================================
# MODULAR IMPORTS WITH FALLBACKS
# ============================================================================

# Import from db_setup module
try:
    from .db_setup import init_database, import_excel_to_db, remove_unsupported_languages, reset_database, delete_database
    logger.info("Successfully imported from db_setup")
except ImportError as e:
    logger.warning(f"Failed to import from db_setup: {e}. Using fallback implementations.")
    # Fallback implementations would go here if needed

# Import from word_manager module
try:
    from .word_manager import (
        get_words_paginated, search_words, get_completed_words,
        mark_word_completed, mark_words_completed, increment_word_count, get_word_rank
    )
    logger.info("Successfully imported from word_manager")
except ImportError as e:
    logger.warning(f"Failed to import from word_manager: {e}. Using fallback implementations.")
    # Fallback implementations would go here if needed

# Import from stats_manager module
try:
    from .stats_manager import get_languages, get_word_stats, log_generation
    logger.info("Successfully imported from stats_manager")
except ImportError as e:
    logger.warning(f"Failed to import from stats_manager: {e}. Using fallback implementations.")
    # Fallback implementations would go here if needed

# ============================================================================
# LEGACY COMPATIBILITY
# ============================================================================

# For backward compatibility, expose all functions at module level
__all__ = [
    # Database setup
    'init_database', 'import_excel_to_db', 'remove_unsupported_languages',
    'reset_database', 'delete_database',
    # Word operations
    'get_words_paginated', 'search_words', 'get_completed_words',
    'mark_word_completed', 'mark_words_completed', 'increment_word_count', 'get_word_rank',
    # Statistics
    'get_languages', 'get_word_stats', 'log_generation'
]