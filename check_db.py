import sqlite3
import os
from pathlib import Path

# Check database
db_path = Path("user_data.db")
if db_path.exists():
    print(f"Database exists: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check tables
    cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Tables: {tables}")

    if 'words' in tables:
        # Check word count
        cursor.execute('SELECT COUNT(*) FROM words')
        total_words = cursor.fetchone()[0]
        print(f"Total words: {total_words}")

        # Check languages
        cursor.execute('SELECT language, COUNT(*) FROM words GROUP BY language ORDER BY language')
        languages = dict(cursor.fetchall())
        print(f"Languages: {languages}")
        print(f"Number of languages: {len(languages)}")

    conn.close()
else:
    print("Database does not exist")

# Check Excel directory
excel_dir = Path("109 Languages Frequency Word Lists")
if excel_dir.exists():
    excel_files = list(excel_dir.glob("*.xlsx"))
    print(f"\nExcel directory exists with {len(excel_files)} .xlsx files")
    if excel_files:
        print("First 5 files:", [f.name for f in excel_files[:5]])
else:
    print("\nExcel directory does not exist")