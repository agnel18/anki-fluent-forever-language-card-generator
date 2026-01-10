"""
Database Setup for Word Enrichment

Creates SQLite DB with words table.
"""

import sqlite3
import os

DB_PATH = "word_enrichment.db"

def create_db():
    """Create the database and tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create words table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT NOT NULL,
            lang_code TEXT NOT NULL,
            enriched_data TEXT NOT NULL,  -- JSON string
            validated BOOLEAN DEFAULT FALSE,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(word, lang_code)
        )
    """)

    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_word_lang ON words(word, lang_code)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_lang ON words(lang_code)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_validated ON words(validated)")

    conn.commit()
    conn.close()
    print(f"Database created at {DB_PATH}")

def insert_word(word: str, lang_code: str, enriched_data: dict):
    """Insert or update a word entry."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    import json
    data_json = json.dumps(enriched_data, ensure_ascii=False)

    cursor.execute("""
        INSERT OR REPLACE INTO words (word, lang_code, enriched_data, last_updated)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
    """, (word, lang_code, data_json))

    conn.commit()
    conn.close()

def get_word(word: str, lang_code: str) -> dict:
    """Retrieve word data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT enriched_data FROM words WHERE word = ? AND lang_code = ?", (word, lang_code))
    row = cursor.fetchone()
    conn.close()

    if row:
        import json
        return json.loads(row[0])
    return None

if __name__ == "__main__":
    create_db()
    print("DB setup complete.")