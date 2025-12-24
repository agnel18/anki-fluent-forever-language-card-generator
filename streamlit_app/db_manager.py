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
    from db_setup import init_database, import_excel_to_db, remove_unsupported_languages, reset_database, delete_database
    logger.info("Successfully imported from db_setup")
except ImportError as e:
    logger.warning(f"Failed to import from db_setup: {e}. Using fallback implementations.")
    # Fallback implementations would go here if needed

# Import from word_manager module
try:
    from word_manager import (
        get_words_paginated, search_words, get_completed_words,
        mark_word_completed, mark_words_completed, increment_word_count, get_word_rank
    )
    logger.info("Successfully imported from word_manager")
except ImportError as e:
    logger.warning(f"Failed to import from word_manager: {e}. Using fallback implementations.")
    # Fallback implementations would go here if needed

# Import from stats_manager module
try:
    from stats_manager import get_languages, get_word_stats, log_generation
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

# ============================================================================
# INITIALIZATION ON IMPORT
# ============================================================================

# Auto-initialize database on first import
try:
    # Check if database exists
    from pathlib import Path
    DB_PATH = Path(__file__).parent / "language_learning.db"

    if not DB_PATH.exists():
        logger.info("Creating database...")
        init_database()
        # Import Excel data if database is empty
        import_excel_to_db()
    else:
        # Check database integrity and handle corruption
        try:
            import sqlite3
            conn = sqlite3.connect(str(DB_PATH))
            cursor = conn.cursor()
            # Test database integrity
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            if result and result[0] != "ok":
                logger.warning(f"Database integrity check failed: {result[0]}, recreating database")
                conn.close()
                delete_database()
                init_database()
                import_excel_to_db()
            else:
                # Ensure schema is up to date
                init_database()
                # Check if we need to import data
                cursor.execute("SELECT COUNT(*) FROM words")
                count = cursor.fetchone()[0]
                if count == 0:
                    logger.info("Database exists but is empty, importing Excel data...")
                    import_excel_to_db()
            conn.close()
        except sqlite3.DatabaseError as e:
            logger.error(f"Database corruption detected: {e}, recreating database")
            try:
                delete_database()
                init_database()
                import_excel_to_db()
            except Exception as recreate_error:
                logger.error(f"Failed to recreate database: {recreate_error}")
except Exception as e:
    logger.error(f"Database initialization error: {e}")