"""
Phase 3.3: Manual Review and Cleaning Script

Exports DB data to CSV for manual review, then imports cleaned data back.
"""

import sqlite3
import pandas as pd
import json
import os
from datetime import datetime

DB_PATH = "word_enrichment.db"

def export_for_review():
    """Export DB data to CSV for manual review."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM words WHERE lang_code = 'hi'", conn)
    conn.close()

    # Parse JSON enriched_data column
    def parse_enriched_data(json_str):
        try:
            data = json.loads(json_str)
            return pd.Series({
                'meaning': data.get('meaning', 'N/A'),
                'usages': '; '.join(data.get('usages', ['N/A'])),
                'variations': '; '.join(data.get('variations', ['N/A'])),
                'source': data.get('source', 'N/A')
            })
        except:
            return pd.Series({
                'meaning': 'N/A',
                'usages': 'N/A',
                'variations': 'N/A',
                'source': 'N/A'
            })

    # Expand enriched_data into columns
    expanded = df['enriched_data'].apply(parse_enriched_data)
    df = pd.concat([df[['id', 'word', 'lang_code', 'validated']], expanded], axis=1)

    # Create export filename with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"hindi_words_review_{timestamp}.csv"

    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"Exported {len(df)} words to {filename}")
    print(f"Validated words: {df['validated'].sum()}/{len(df)}")
    print(f"Words with data: {len(df[df['meaning'] != 'N/A'])}/{len(df)}")

    return filename

def import_cleaned_data(csv_file):
    """Import cleaned CSV data back to DB."""
    if not os.path.exists(csv_file):
        print(f"File {csv_file} not found")
        return

    df = pd.read_csv(csv_file, encoding='utf-8-sig')

    # Convert back to JSON format
    def create_enriched_data(row):
        return json.dumps({
            'meaning': row['meaning'] if pd.notna(row['meaning']) else 'N/A',
            'usages': [u.strip() for u in str(row['usages']).split(';') if u.strip() and u.strip() != 'N/A'] if pd.notna(row['usages']) else ['N/A'],
            'variations': [v.strip() for v in str(row['variations']).split(';') if v.strip() and v.strip() != 'N/A'] if pd.notna(row['variations']) else ['N/A'],
            'source': row['source'] if pd.notna(row['source']) else 'N/A'
        }, ensure_ascii=False)

    df['enriched_data'] = df.apply(create_enriched_data, axis=1)

    # Update DB
    conn = sqlite3.connect(DB_PATH)
    for _, row in df.iterrows():
        conn.execute("""
            UPDATE words
            SET enriched_data = ?, validated = ?, last_updated = ?
            WHERE id = ?
        """, (row['enriched_data'], bool(row['validated']), datetime.now().isoformat(), row['id']))

    conn.commit()
    conn.close()

    print(f"Imported cleaned data from {csv_file}")
    print(f"Updated {len(df)} words")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "import":
        if len(sys.argv) > 2:
            import_cleaned_data(sys.argv[2])
        else:
            print("Usage: python phase3_review.py import <csv_file>")
    else:
        export_for_review()