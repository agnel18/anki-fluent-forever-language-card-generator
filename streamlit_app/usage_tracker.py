# usage_tracker.py - Track app usage for streaks and analytics

import sqlite3
import logging
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
import json

logger = logging.getLogger(__name__)

# Database path
DB_PATH = Path(__file__).parent / "language_learning.db"


def log_app_usage(user_id: str, decks_generated: int = 0, words_generated: int = 0,
                  languages_used: List[str] = None, session_duration: int = 0):
    """Log daily app usage for streak tracking."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        today = date.today()
        languages_json = json.dumps(languages_used or [])

        cursor.execute("""
            INSERT OR REPLACE INTO app_usage
            (user_id, date, decks_generated, words_generated, languages_used, session_duration)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, today, decks_generated, words_generated, languages_json, session_duration))

        conn.commit()
        logger.debug(f"Logged app usage for user {user_id}: {decks_generated} decks, {words_generated} words")

    except Exception as e:
        logger.error(f"Error logging app usage: {e}")
    finally:
        conn.close()


def get_usage_streak(user_id: str) -> int:
    """Calculate current usage streak (consecutive days with app usage)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Get all usage dates for the user in the last 60 days, ordered by date desc
        cursor.execute("""
            SELECT date FROM app_usage
            WHERE user_id = ?
            ORDER BY date DESC
            LIMIT 60
        """, (user_id,))

        dates = [row[0] for row in cursor.fetchall()]

        if not dates:
            return 0

        # Convert to date objects
        usage_dates = set()
        for date_str in dates:
            try:
                usage_dates.add(datetime.strptime(date_str, '%Y-%m-%d').date())
            except ValueError:
                continue

        if not usage_dates:
            return 0

        # Calculate streak
        today = date.today()
        streak = 0

        # Check if used today
        if today in usage_dates:
            streak = 1
            # Count consecutive days backward from yesterday
            check_date = today - timedelta(days=1)
            while check_date in usage_dates:
                streak += 1
                check_date -= timedelta(days=1)
        else:
            # Check if used yesterday (for continuing streak)
            yesterday = today - timedelta(days=1)
            if yesterday in usage_dates:
                streak = 1
                # Count consecutive days backward from day before yesterday
                check_date = yesterday - timedelta(days=1)
                while check_date in usage_dates:
                    streak += 1
                    check_date -= timedelta(days=1)

        return streak

    except Exception as e:
        logger.error(f"Error calculating usage streak: {e}")
        return 0
    finally:
        conn.close()


def get_usage_stats(user_id: str) -> Dict:
    """Get comprehensive usage statistics."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Total stats
        cursor.execute("""
            SELECT
                COUNT(DISTINCT date) as total_days_used,
                SUM(decks_generated) as total_decks,
                SUM(words_generated) as total_words,
                SUM(session_duration) as total_duration
            FROM app_usage
            WHERE user_id = ?
        """, (user_id,))

        row = cursor.fetchone()
        total_days_used = row[0] or 0
        total_decks = row[1] or 0
        total_words = row[2] or 0
        total_duration = row[3] or 0

        # Languages used
        cursor.execute("""
            SELECT languages_used FROM app_usage
            WHERE user_id = ? AND languages_used IS NOT NULL
        """, (user_id,))

        all_languages = set()
        for row in cursor.fetchall():
            try:
                languages = json.loads(row[0])
                all_languages.update(languages)
            except (json.JSONDecodeError, TypeError):
                continue

        # Weekly stats (last 7 days)
        week_ago = date.today() - timedelta(days=7)
        cursor.execute("""
            SELECT
                COUNT(DISTINCT date) as weekly_days,
                SUM(decks_generated) as weekly_decks,
                SUM(words_generated) as weekly_words
            FROM app_usage
            WHERE user_id = ? AND date >= ?
        """, (user_id, week_ago))

        weekly_row = cursor.fetchone()
        weekly_days = weekly_row[0] or 0
        weekly_decks = weekly_row[1] or 0
        weekly_words = weekly_row[2] or 0

        return {
            "total_days_used": total_days_used,
            "total_decks_generated": total_decks,
            "total_words_generated": total_words,
            "total_session_duration": total_duration,
            "unique_languages_used": len(all_languages),
            "current_streak": get_usage_streak(user_id),
            "weekly_days": weekly_days,
            "weekly_decks": weekly_decks,
            "weekly_words": weekly_words,
            "languages_list": sorted(list(all_languages))
        }

    except Exception as e:
        logger.error(f"Error getting usage stats: {e}")
        return {}
    finally:
        conn.close()


def get_recent_activity(user_id: str, days: int = 30) -> List[Dict]:
    """Get recent app activity for the specified number of days."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        start_date = date.today() - timedelta(days=days)

        cursor.execute("""
            SELECT date, decks_generated, words_generated, languages_used, session_duration
            FROM app_usage
            WHERE user_id = ? AND date >= ?
            ORDER BY date DESC
        """, (user_id, start_date))

        activity = []
        for row in cursor.fetchall():
            try:
                languages = json.loads(row[3]) if row[3] else []
            except (json.JSONDecodeError, TypeError):
                languages = []

            activity.append({
                "date": row[0],
                "decks_generated": row[1] or 0,
                "words_generated": row[2] or 0,
                "languages_used": languages,
                "session_duration": row[4] or 0
            })

        return activity

    except Exception as e:
        logger.error(f"Error getting recent activity: {e}")
        return []
    finally:
        conn.close()