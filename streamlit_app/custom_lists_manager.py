# custom_lists_manager.py - Manage user-uploaded custom word lists

import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import json

logger = logging.getLogger(__name__)

# Database path
DB_PATH = Path(__file__).parent / "language_learning.db"


def save_custom_word_list(user_id: str, list_name: str, words: List[str],
                         language: str = None) -> bool:
    """Save a custom word list for a user."""
    if not words:
        return False

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        words_json = json.dumps(words)
        word_count = len(words)

        cursor.execute("""
            INSERT OR REPLACE INTO custom_word_lists
            (user_id, list_name, language, words, word_count, last_used)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, list_name, language, words_json, word_count, datetime.now()))

        # Create progress entries for each word
        list_id = cursor.lastrowid

        for word in words:
            cursor.execute("""
                INSERT OR IGNORE INTO custom_word_progress
                (user_id, list_id, word)
                VALUES (?, ?, ?)
            """, (user_id, list_id, word))

        conn.commit()
        logger.info(f"Saved custom list '{list_name}' for user {user_id} with {word_count} words")
        return True

    except Exception as e:
        logger.error(f"Error saving custom word list: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def get_user_custom_lists(user_id: str) -> List[Dict]:
    """Get all custom word lists for a user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id, list_name, language, word_count, created_at, last_used, is_favorite
            FROM custom_word_lists
            WHERE user_id = ?
            ORDER BY last_used DESC, created_at DESC
        """, (user_id,))

        lists = []
        for row in cursor.fetchall():
            lists.append({
                "id": row[0],
                "name": row[1],
                "language": row[2],
                "word_count": row[3],
                "created_at": row[4],
                "last_used": row[5],
                "is_favorite": bool(row[6])
            })

        return lists

    except Exception as e:
        logger.error(f"Error getting custom lists: {e}")
        return []
    finally:
        conn.close()


def get_custom_list_words(user_id: str, list_id: int) -> Tuple[List[str], Dict]:
    """Get words from a custom list with progress information."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Get list info
        cursor.execute("""
            SELECT words FROM custom_word_lists
            WHERE user_id = ? AND id = ?
        """, (user_id, list_id))

        row = cursor.fetchone()
        if not row:
            return [], {}

        try:
            words = json.loads(row[0])
        except (json.JSONDecodeError, TypeError):
            return [], {}

        # Get progress for each word
        cursor.execute("""
            SELECT word, completed, times_generated, last_generated
            FROM custom_word_progress
            WHERE user_id = ? AND list_id = ?
        """, (user_id, list_id))

        progress = {}
        for row in cursor.fetchall():
            progress[row[0]] = {
                "completed": bool(row[1]),
                "times_generated": row[2] or 0,
                "last_generated": row[3]
            }

        # Update last_used timestamp
        cursor.execute("""
            UPDATE custom_word_lists
            SET last_used = ?
            WHERE user_id = ? AND id = ?
        """, (datetime.now(), user_id, list_id))

        conn.commit()

        return words, progress

    except Exception as e:
        logger.error(f"Error getting custom list words: {e}")
        return [], {}
    finally:
        conn.close()


def mark_custom_word_completed(user_id: str, list_id: int, word: str, completed: bool = True) -> bool:
    """Mark a word as completed in a custom list."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE custom_word_progress
            SET completed = ?, last_generated = ?
            WHERE user_id = ? AND list_id = ? AND word = ?
        """, (1 if completed else 0, datetime.now(), user_id, list_id, word))

        conn.commit()
        return True

    except Exception as e:
        logger.error(f"Error marking custom word completed: {e}")
        return False
    finally:
        conn.close()


def increment_custom_word_count(user_id: str, list_id: int, word: str) -> bool:
    """Increment the generation count for a word in a custom list."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE custom_word_progress
            SET times_generated = times_generated + 1, last_generated = ?
            WHERE user_id = ? AND list_id = ? AND word = ?
        """, (datetime.now(), user_id, list_id, word))

        conn.commit()
        return True

    except Exception as e:
        logger.error(f"Error incrementing custom word count: {e}")
        return False
    finally:
        conn.close()


def delete_custom_list(user_id: str, list_id: int) -> bool:
    """Delete a custom word list and all its progress data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Delete progress entries first (foreign key constraint)
        cursor.execute("""
            DELETE FROM custom_word_progress
            WHERE user_id = ? AND list_id = ?
        """, (user_id, list_id))

        # Delete the list
        cursor.execute("""
            DELETE FROM custom_word_lists
            WHERE user_id = ? AND id = ?
        """, (user_id, list_id))

        conn.commit()
        logger.info(f"Deleted custom list {list_id} for user {user_id}")
        return True

    except Exception as e:
        logger.error(f"Error deleting custom list: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def toggle_favorite_list(user_id: str, list_id: int) -> bool:
    """Toggle favorite status of a custom list."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE custom_word_lists
            SET is_favorite = NOT is_favorite
            WHERE user_id = ? AND id = ?
        """, (user_id, list_id))

        conn.commit()
        return True

    except Exception as e:
        logger.error(f"Error toggling favorite status: {e}")
        return False
    finally:
        conn.close()


def get_custom_list_stats(user_id: str, list_id: int) -> Dict:
    """Get statistics for a custom word list."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT COUNT(*) as total_words,
                   SUM(completed) as completed_words,
                   SUM(times_generated) as total_generations
            FROM custom_word_progress
            WHERE user_id = ? AND list_id = ?
        """, (user_id, list_id))

        row = cursor.fetchone()
        total_words = row[0] or 0
        completed_words = row[1] or 0
        total_generations = row[2] or 0

        return {
            "total_words": total_words,
            "completed_words": completed_words,
            "remaining_words": total_words - completed_words,
            "completion_percentage": (completed_words / total_words * 100) if total_words > 0 else 0,
            "total_generations": total_generations
        }

    except Exception as e:
        logger.error(f"Error getting custom list stats: {e}")
        return {}
    finally:
        conn.close()