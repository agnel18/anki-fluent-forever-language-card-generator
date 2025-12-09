"""
SQLite Database Manager for Language Learning App
Handles word lists, progress tracking, and statistics
"""

import sqlite3
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import pandas as pd

logger = logging.getLogger(__name__)

# Database location
DB_PATH = Path(__file__).parent.parent / "user_data.db"

# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def init_database():
    """Initialize SQLite database with schema."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Words table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                language TEXT NOT NULL,
                word TEXT NOT NULL,
                rank INTEGER NOT NULL,
                times_generated INTEGER DEFAULT 0,
                last_generated TIMESTAMP,
                completed BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(language, word)
            )
        """)
        
        # Fast lookup indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_language_rank ON words(language, rank)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_language_word ON words(language, word)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_completed ON words(language, completed)")
        
        # Generation history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS generation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                language TEXT,
                words_generated INTEGER,
                sentences_generated INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        logger.info(f"Database initialized at {DB_PATH}")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        return False
    finally:
        conn.close()


def import_excel_to_db(excel_dir: Path = None):
    """
    One-time import: Load all Excel files into SQLite.
    Only runs if database is empty.
    Uses most-common-words-multilingual source data.
    """
    if excel_dir is None:
        # Use the official most-common-words-multilingual source
        excel_dir = Path("D:/Language Learning/most-common-words-multilingual-main/most-common-words-multilingual-main/data/xlsx")
    
    if not excel_dir.exists():
        logger.warning(f"Excel directory not found: {excel_dir}")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if database already has words
        cursor.execute("SELECT COUNT(*) FROM words")
        count = cursor.fetchone()[0]
        
        if count > 0:
            logger.info(f"Database already populated ({count} words)")
            return True
        
        logger.info("Starting Excel → SQLite import...")
        total_words = 0
        
        # Process all Excel files
        for excel_file in sorted(excel_dir.glob("*.xlsx")):
            try:
                # Extract language name from filename (keep full name including Simplified/Traditional)
                filename = excel_file.stem
                # Format: "Spanish (ES)" → "Spanish", "Chinese (Simplified) (ZH-CN)" → "Chinese (Simplified)"
                # Extract everything before the last occurrence of " ("
                if filename.count(" (") > 1:
                    # Multiple parentheses: keep text before the last one (e.g., "Chinese (Simplified)" from "Chinese (Simplified) (ZH-CN)")
                    parts = filename.rsplit(" (", 1)
                    language = parts[0]
                else:
                    # Single parentheses: remove it (e.g., "Spanish" from "Spanish (ES)")
                    language = filename.split(" (")[0]
                
                logger.info(f"Importing {language}...")
                
                # Read Excel
                df = pd.read_excel(excel_file, sheet_name=0, header=None)
                words = df.iloc[:, 0].tolist()
                
                # Clean words
                words = [str(w).strip() for w in words if w and str(w).strip()]
                
                # Skip header row (all files have one)
                if words:
                    words = words[1:]
                
                # Insert into database
                for rank, word in enumerate(words, start=1):
                    try:
                        cursor.execute(
                            """INSERT OR IGNORE INTO words (language, word, rank) 
                               VALUES (?, ?, ?)""",
                            (language, word, rank)
                        )
                    except Exception as e:
                        logger.error(f"Error inserting '{word}' ({language}): {e}")
                        continue
                
                total_words += len(words)
                logger.info(f"  ✓ {language}: {len(words)} words")
                
            except Exception as e:
                logger.error(f"Error processing {excel_file}: {e}")
                continue
        
        conn.commit()
        logger.info(f"✅ Import complete: {total_words} words from {len(list(excel_dir.glob('*.xlsx')))} languages")
        return True
        
    except Exception as e:
        logger.error(f"Import error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


# ============================================================================
# WORD QUERIES
# ============================================================================

def get_languages() -> Dict[str, int]:
    """Get all languages and word counts."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT language, COUNT(*) as word_count 
            FROM words 
            GROUP BY language 
            ORDER BY language
        """)
        
        result = {row[0]: row[1] for row in cursor.fetchall()}
        return result
        
    except Exception as e:
        logger.error(f"Error getting languages: {e}")
        return {}
    finally:
        conn.close()


def get_words_paginated(language: str, page: int = 1, page_size: int = 20) -> Tuple[List[str], int]:
    """
    Get words paginated by rank.
    
    Args:
        language: Language name
        page: Page number (1-indexed)
        page_size: Words per page
        
    Returns:
        (list of words, total count)
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM words WHERE language = ?", (language,))
        total = cursor.fetchone()[0]
        
        # Get paginated words
        offset = (page - 1) * page_size
        cursor.execute(
            """SELECT word FROM words 
               WHERE language = ? 
               ORDER BY rank ASC 
               LIMIT ? OFFSET ?""",
            (language, page_size, offset)
        )
        
        words = [row[0] for row in cursor.fetchall()]
        return words, total
        
    except Exception as e:
        logger.error(f"Error getting paginated words: {e}")
        return [], 0
    finally:
        conn.close()


def search_words(language: str, query: str, limit: int = 50) -> List[str]:
    """
    Fast search using SQLite LIKE.
    
    Args:
        language: Language name
        query: Search term
        limit: Max results
        
    Returns:
        List of matching words
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        search_pattern = f"%{query.lower()}%"
        cursor.execute(
            """SELECT word FROM words 
               WHERE language = ? AND LOWER(word) LIKE ? 
               ORDER BY rank ASC 
               LIMIT ?""",
            (language, search_pattern, limit)
        )
        
        return [row[0] for row in cursor.fetchall()]
        
    except Exception as e:
        logger.error(f"Error searching words: {e}")
        return []
    finally:
        conn.close()


def get_completed_words(language: str) -> List[str]:
    """Get list of completed words for a language."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT word FROM words WHERE language = ? AND completed = 1 ORDER BY word",
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

def mark_word_completed(language: str, word: str) -> bool:
    """Mark a word as completed."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "UPDATE words SET completed = 1, last_generated = ? WHERE language = ? AND word = ?",
            (datetime.now().isoformat(), language, word)
        )
        conn.commit()
        return cursor.rowcount > 0
        
    except Exception as e:
        logger.error(f"Error marking word completed: {e}")
        return False
    finally:
        conn.close()


def mark_words_completed(language: str, words: List[str]) -> int:
    """Mark multiple words as completed. Returns count of updated words."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        now = datetime.now().isoformat()
        for word in words:
            cursor.execute(
                "UPDATE words SET completed = 1, last_generated = ? WHERE language = ? AND word = ?",
                (now, language, word)
            )
        
        conn.commit()
        return cursor.rowcount
        
    except Exception as e:
        logger.error(f"Error marking words completed: {e}")
        return 0
    finally:
        conn.close()


def increment_word_count(language: str, word: str) -> bool:
    """Increment times_generated for a word."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """UPDATE words 
               SET times_generated = times_generated + 1, 
                   last_generated = ? 
               WHERE language = ? AND word = ?""",
            (datetime.now().isoformat(), language, word)
        )
        conn.commit()
        return cursor.rowcount > 0
        
    except Exception as e:
        logger.error(f"Error incrementing word count: {e}")
        return False
    finally:
        conn.close()


def get_word_stats(language: str) -> Dict:
    """Get statistics for a language."""
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
    """Log a deck generation to history."""
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


def get_word_rank(language: str, word: str) -> int:
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


# ============================================================================
# DATABASE RESET & CLEANUP
# ============================================================================

def reset_database():
    """Reset all progress (for testing)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("UPDATE words SET completed = 0, times_generated = 0, last_generated = NULL")
        conn.commit()
        logger.info("Database reset")
        return True
        
    except Exception as e:
        logger.error(f"Error resetting database: {e}")
        return False
    finally:
        conn.close()


def delete_database():
    """Delete the database file (complete reset)."""
    try:
        if DB_PATH.exists():
            DB_PATH.unlink()
            logger.info("Database deleted")
            return True
        return False
        
    except Exception as e:
        logger.error(f"Error deleting database: {e}")
        return False


# ============================================================================
# INITIALIZATION ON IMPORT
# ============================================================================

# Auto-initialize on first import
if not DB_PATH.exists():
    logger.info("Creating database...")
    init_database()
    import_excel_to_db()
else:
    # Ensure schema is up to date
    init_database()
