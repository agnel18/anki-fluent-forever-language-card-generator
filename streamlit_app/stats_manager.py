"""
Stats Manager Module

Handles statistics and analytics database operations including language lists,
word statistics, and generation history logging.
"""

import sqlite3
import logging
from pathlib import Path
from typing import List, Dict

# Setup logging
logger = logging.getLogger(__name__)

# Database path
DB_PATH = Path(__file__).parent / "language_learning.db"


# ============================================================================
# LANGUAGE MANAGEMENT
# ============================================================================

def get_languages() -> List[str]:
    """
    Get list of available languages.

    Returns:
        List of language names
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT DISTINCT language FROM words ORDER BY language")
        return [row[0] for row in cursor.fetchall()]

    except Exception as e:
        logger.error(f"Error getting languages: {e}")
        return []
    finally:
        conn.close()


# ============================================================================
# STATISTICS
# ============================================================================

def get_word_stats(language: str) -> Dict:
    """
    Get statistics for a language.

    Args:
        language: Language name

    Returns:
        Dictionary with stats
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Total words
        cursor.execute("SELECT COUNT(*) FROM words WHERE language = ?", (language,))
        total = cursor.fetchone()[0]

        # Completed words
        cursor.execute("SELECT COUNT(*) FROM words WHERE language = ? AND completed = 1", (language,))
        completed = cursor.fetchone()[0]

        # Times generated
        cursor.execute("SELECT SUM(times_generated) FROM words WHERE language = ?", (language,))
        times_gen = cursor.fetchone()[0] or 0

        return {
            "total": total,
            "completed": completed,
            "remaining": total - completed,
            "times_generated": times_gen,
            "completion_percent": (completed / total * 100) if total > 0 else 0
        }

    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return {}
    finally:
        conn.close()


# ============================================================================
# GENERATION HISTORY
# ============================================================================

def log_generation(session_id: str, language: str, words_count: int, sentences_count: int):
    """
    Log a deck generation to history.

    Args:
        session_id: Session identifier
        language: Language name
        words_count: Number of words generated
        sentences_count: Number of sentences generated
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(
            """INSERT INTO generation_history (session_id, language, words_generated, sentences_generated)
               VALUES (?, ?, ?, ?)""",
            (session_id, language, words_count, sentences_count)
        )
        conn.commit()

    except Exception as e:
        logger.error(f"Error logging generation: {e}")
    finally:
        conn.close()