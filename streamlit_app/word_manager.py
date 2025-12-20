"""
Word Manager Module

Handles word-related database operations including queries, progress tracking,
and word management functions.
"""

import sqlite3
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# Setup logging
logger = logging.getLogger(__name__)

# Database path
DB_PATH = Path(__file__).parent / "language_learning.db"


# ============================================================================
# WORD QUERIES
# ============================================================================

def get_words_paginated(language: str, page: int = 1, per_page: int = 50) -> Tuple[List[Dict], int]:
    """
    Get paginated words for a language.

    Args:
        language: Language name
        page: Page number (1-based)
        per_page: Words per page

    Returns:
        Tuple of (words_list, total_pages)
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM words WHERE language = ?", (language,))
        total_words = cursor.fetchone()[0]
        total_pages = (total_words + per_page - 1) // per_page

        # Get paginated results
        offset = (page - 1) * per_page
        cursor.execute(
            """SELECT word, rank, completed, times_generated, last_generated
               FROM words WHERE language = ?
               ORDER BY rank LIMIT ? OFFSET ?""",
            (language, per_page, offset)
        )

        words = []
        for row in cursor.fetchall():
            words.append({
                "word": row[0],
                "rank": row[1],
                "completed": row[2],
                "times_generated": row[3],
                "last_generated": row[4]
            })

        return words, total_pages

    except Exception as e:
        logger.error(f"Error getting paginated words: {e}")
        return [], 0
    finally:
        conn.close()


def search_words(language: str, query: str, limit: int = 20) -> List[Dict]:
    """
    Search for words in a language.

    Args:
        language: Language name
        query: Search query
        limit: Maximum results

    Returns:
        List of matching words
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(
            """SELECT word, rank, completed, times_generated, last_generated
               FROM words WHERE language = ? AND word LIKE ?
               ORDER BY rank LIMIT ?""",
            (language, f"%{query}%", limit)
        )

        words = []
        for row in cursor.fetchall():
            words.append({
                "word": row[0],
                "rank": row[1],
                "completed": row[2],
                "times_generated": row[3],
                "last_generated": row[4]
            })

        return words

    except Exception as e:
        logger.error(f"Error searching words: {e}")
        return []
    finally:
        conn.close()


def get_completed_words(language: str) -> List[str]:
    """
    Get list of completed words for a language.

    Args:
        language: Language name

    Returns:
        List of completed words
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT word FROM words WHERE language = ? AND completed = 1 ORDER BY rank",
            (language,)
        )
        return [row[0] for row in cursor.fetchall()]

    except Exception as e:
        logger.error(f"Error getting completed words: {e}")
        return []
    finally:
        conn.close()


# ============================================================================
# PROGRESS TRACKING
# ============================================================================

def mark_word_completed(language: str, word: str, completed: bool = True):
    """
    Mark a word as completed or not.

    Args:
        language: Language name
        word: Word to mark
        completed: Completion status
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(
            "UPDATE words SET completed = ? WHERE language = ? AND word = ? COLLATE NOCASE",
            (1 if completed else 0, language, word)
        )
        conn.commit()

    except Exception as e:
        logger.error(f"Error marking word completed: {e}")
    finally:
        conn.close()


def mark_words_completed(language: str, words: List[str], completed: bool = True):
    """
    Mark multiple words as completed.

    Args:
        language: Language name
        words: List of words to mark
        completed: Completion status
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Create placeholders for the IN clause
        placeholders = ','.join('?' * len(words))
        cursor.execute(
            f"UPDATE words SET completed = ? WHERE language = ? AND word COLLATE NOCASE IN ({placeholders})",
            [1 if completed else 0, language] + words
        )
        conn.commit()

    except Exception as e:
        logger.error(f"Error marking words completed: {e}")
    finally:
        conn.close()


def increment_word_count(language: str, word: str):
    """
    Increment the times_generated count for a word.

    Args:
        language: Language name
        word: Word to increment
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(
            """UPDATE words SET times_generated = times_generated + 1,
                                last_generated = CURRENT_TIMESTAMP
               WHERE language = ? AND word = ? COLLATE NOCASE""",
            (language, word)
        )
        conn.commit()

    except Exception as e:
        logger.error(f"Error incrementing word count: {e}")
    finally:
        conn.close()


def get_word_rank(language: str, word: str) -> Optional[int]:
    """
    Get the frequency rank of a word.

    Args:
        language: Language name
        word: Word to look up

    Returns:
        Rank (1-based), or None if word not found
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT rank FROM words WHERE language = ? AND word = ? COLLATE NOCASE",
            (language, word)
        )
        result = cursor.fetchone()
        return result[0] if result else None

    except Exception as e:
        logger.error(f"Error getting word rank: {e}")
        return None
    finally:
        conn.close()