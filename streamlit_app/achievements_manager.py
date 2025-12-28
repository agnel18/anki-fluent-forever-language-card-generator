# achievements_manager.py - Achievement system for user milestones

import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Database path
DB_PATH = Path(__file__).parent / "language_learning.db"


@dataclass
class Achievement:
    """Achievement definition."""
    type: str
    key: str
    title: str
    description: str
    icon: str
    target_value: int
    category: str = "general"


# Predefined achievements
ACHIEVEMENTS = [
    # Usage Streaks
    Achievement("streak", "first_day", "First Steps", "Use the app for the first time", "🎯", 1, "usage"),
    Achievement("streak", "week_warrior", "Week Warrior", "Use the app for 7 consecutive days", "🔥", 7, "usage"),
    Achievement("streak", "month_master", "Month Master", "Use the app for 30 consecutive days", "👑", 30, "usage"),

    # Deck Generation
    Achievement("decks", "first_deck", "Deck Creator", "Generate your first Anki deck", "📚", 1, "creation"),
    Achievement("decks", "deck_collector", "Deck Collector", "Generate 10 decks", "📚📚", 10, "creation"),
    Achievement("decks", "deck_master", "Deck Master", "Generate 50 decks", "🎓", 50, "creation"),
    Achievement("decks", "deck_legend", "Deck Legend", "Generate 100 decks", "🏆", 100, "creation"),

    # Words Generated
    Achievement("words", "word_smith", "Word Smith", "Generate decks with 100 words", "✍️", 100, "creation"),
    Achievement("words", "word_weaver", "Word Weaver", "Generate decks with 500 words", "🕸️", 500, "creation"),
    Achievement("words", "word_wizard", "Word Wizard", "Generate decks with 1000 words", "🧙", 1000, "creation"),

    # Languages
    Achievement("languages", "polyglot_start", "Polyglot Start", "Use 3 different languages", "🌍", 3, "languages"),
    Achievement("languages", "polyglot", "Polyglot", "Use 5 different languages", "🌎", 5, "languages"),
    Achievement("languages", "linguist", "Linguist", "Use 10 different languages", "🌏", 10, "languages"),

    # Custom Lists
    Achievement("custom_lists", "list_maker", "List Maker", "Create your first custom word list", "📝", 1, "custom"),
    Achievement("custom_lists", "list_collector", "List Collector", "Create 5 custom word lists", "📋", 5, "custom"),
    Achievement("custom_lists", "list_master", "List Master", "Create 10 custom word lists", "📋📋", 10, "custom"),
]


def initialize_achievements(user_id: str):
    """Initialize all achievements for a new user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        for achievement in ACHIEVEMENTS:
            cursor.execute("""
                INSERT OR IGNORE INTO achievements
                (user_id, achievement_type, achievement_key, title, description, icon, target_value)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, achievement.type, achievement.key, achievement.title,
                  achievement.description, achievement.icon, achievement.target_value))

        conn.commit()
        logger.info(f"Initialized {len(ACHIEVEMENTS)} achievements for user {user_id}")

    except Exception as e:
        logger.error(f"Error initializing achievements: {e}")
        conn.rollback()
    finally:
        conn.close()


def update_achievement_progress(user_id: str, achievement_type: str, current_value: int):
    """Update progress for all achievements of a specific type."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Get all achievements of this type
        cursor.execute("""
            SELECT achievement_key, target_value, is_unlocked
            FROM achievements
            WHERE user_id = ? AND achievement_type = ?
        """, (user_id, achievement_type))

        achievements = cursor.fetchall()

        for key, target_value, is_unlocked in achievements:
            if not is_unlocked and current_value >= target_value:
                # Unlock achievement
                cursor.execute("""
                    UPDATE achievements
                    SET progress_value = ?, is_unlocked = 1, unlocked_at = ?
                    WHERE user_id = ? AND achievement_type = ? AND achievement_key = ?
                """, (current_value, datetime.now(), user_id, achievement_type, key))

                logger.info(f"User {user_id} unlocked achievement: {key}")

        # Update progress for all achievements of this type
        cursor.execute("""
            UPDATE achievements
            SET progress_value = ?
            WHERE user_id = ? AND achievement_type = ? AND progress_value < ?
        """, (current_value, user_id, achievement_type, current_value))

        conn.commit()

    except Exception as e:
        logger.error(f"Error updating achievement progress: {e}")
        conn.rollback()
    finally:
        conn.close()


def get_user_achievements(user_id: str) -> List[Dict]:
    """Get all achievements for a user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT achievement_type, achievement_key, title, description, icon,
                   progress_value, target_value, is_unlocked, unlocked_at
            FROM achievements
            WHERE user_id = ?
            ORDER BY is_unlocked DESC, achievement_type, target_value
        """, (user_id,))

        achievements = []
        for row in cursor.fetchall():
            achievements.append({
                "type": row[0],
                "key": row[1],
                "title": row[2],
                "description": row[3],
                "icon": row[4],
                "progress": row[5] or 0,
                "target": row[6],
                "unlocked": bool(row[7]),
                "unlocked_at": row[8],
                "progress_percentage": min(100, ((row[5] or 0) / row[6]) * 100) if row[6] > 0 else 0
            })

        return achievements

    except Exception as e:
        logger.error(f"Error getting user achievements: {e}")
        return []
    finally:
        conn.close()


def get_unlocked_achievements(user_id: str) -> List[Dict]:
    """Get only unlocked achievements for a user."""
    achievements = get_user_achievements(user_id)
    return [a for a in achievements if a["unlocked"]]


def get_recent_unlocks(user_id: str, days: int = 7) -> List[Dict]:
    """Get achievements unlocked in the last N days."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=days)

        cursor.execute("""
            SELECT title, description, icon, unlocked_at
            FROM achievements
            WHERE user_id = ? AND is_unlocked = 1 AND unlocked_at >= ?
            ORDER BY unlocked_at DESC
        """, (user_id, cutoff_date))

        recent = []
        for row in cursor.fetchall():
            recent.append({
                "title": row[0],
                "description": row[1],
                "icon": row[2],
                "unlocked_at": row[3]
            })

        return recent

    except Exception as e:
        logger.error(f"Error getting recent unlocks: {e}")
        return []
    finally:
        conn.close()


def check_and_update_achievements(user_id: str):
    """Check all achievement conditions and update progress."""
    try:
        # Import here to avoid circular imports
        from usage_tracker import get_usage_streak, get_usage_stats
        from custom_lists_manager import get_user_custom_lists

        # Check usage streak achievements
        current_streak = get_usage_streak(user_id)
        update_achievement_progress(user_id, "streak", current_streak)

        # Check deck generation achievements
        usage_stats = get_usage_stats(user_id)
        total_decks = usage_stats.get("total_decks_generated", 0)
        update_achievement_progress(user_id, "decks", total_decks)

        # Check words generated achievements
        total_words = usage_stats.get("total_words_generated", 0)
        update_achievement_progress(user_id, "words", total_words)

        # Check languages used achievements
        languages_used = usage_stats.get("unique_languages_used", 0)
        update_achievement_progress(user_id, "languages", languages_used)

        # Check custom lists achievements
        custom_lists = get_user_custom_lists(user_id)
        total_lists = len(custom_lists)
        update_achievement_progress(user_id, "custom_lists", total_lists)

    except Exception as e:
        logger.error(f"Error checking achievements: {e}")


def get_achievement_stats(user_id: str) -> Dict:
    """Get achievement statistics for a user."""
    achievements = get_user_achievements(user_id)

    total_achievements = len(achievements)
    unlocked_count = sum(1 for a in achievements if a["unlocked"])

    # Group by category
    categories = {}
    for achievement in achievements:
        category = achievement["type"]
        if category not in categories:
            categories[category] = {"total": 0, "unlocked": 0}
        categories[category]["total"] += 1
        if achievement["unlocked"]:
            categories[category]["unlocked"] += 1

    return {
        "total_achievements": total_achievements,
        "unlocked_count": unlocked_count,
        "completion_percentage": (unlocked_count / total_achievements * 100) if total_achievements > 0 else 0,
        "categories": categories
    }