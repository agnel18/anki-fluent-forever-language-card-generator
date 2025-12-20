# Database setup module
# Extracted from db_manager.py for better separation of concerns

import sqlite3
import logging
from pathlib import Path
from typing import List
import pandas as pd

logger = logging.getLogger(__name__)

# Database location
DB_PATH = Path(__file__).parent / "language_learning.db"

def init_database():
    """Initialize SQLite database with schema."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Optimize for memory and performance
        cursor.execute("PRAGMA cache_size = -1024")  # 1MB cache
        cursor.execute("PRAGMA synchronous = NORMAL")  # Balance performance/safety
        cursor.execute("PRAGMA journal_mode = WAL")  # Better concurrency
        cursor.execute("PRAGMA temp_store = MEMORY")  # Temp tables in memory

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
        # Use the local frequency word lists
        excel_dir = Path(__file__).parent.parent / "77 Languages Frequency Word Lists"

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

def remove_unsupported_languages(unsupported_languages: List[str]):
    """
    Remove data for unsupported languages from the database.

    Args:
        unsupported_languages: List of language names to remove
    """
    if not unsupported_languages:
        logger.info("No languages to remove")
        return True

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Get count before removal
        cursor.execute("SELECT COUNT(*) FROM words WHERE language IN ({})".format(','.join('?' * len(unsupported_languages))), unsupported_languages)
        count_before = cursor.fetchone()[0]

        # Remove words for unsupported languages
        cursor.execute("DELETE FROM words WHERE language IN ({})".format(','.join('?' * len(unsupported_languages))), unsupported_languages)

        # Remove related generation history
        cursor.execute("DELETE FROM generation_history WHERE language IN ({})".format(','.join('?' * len(unsupported_languages))), unsupported_languages)

        conn.commit()
        logger.info(f"✅ Removed {count_before} words for {len(unsupported_languages)} unsupported languages")
        return True

    except Exception as e:
        logger.error(f"Error removing unsupported languages: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def reset_database():
    """Reset database by dropping all tables and recreating schema."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Drop existing tables
        cursor.execute("DROP TABLE IF EXISTS words")
        cursor.execute("DROP TABLE IF EXISTS generation_history")

        conn.commit()
        logger.info("Database tables dropped")

        # Reinitialize
        conn.close()
        return init_database()

    except Exception as e:
        logger.error(f"Database reset error: {e}")
        return False
    finally:
        conn.close()

def delete_database():
    """Delete the database file entirely."""
    try:
        if DB_PATH.exists():
            DB_PATH.unlink()
            logger.info(f"Database file deleted: {DB_PATH}")
            return True
        else:
            logger.info("Database file not found")
            return True
    except Exception as e:
        logger.error(f"Error deleting database: {e}")
        return False