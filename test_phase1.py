"""
Test script for Phase 1: Test fetching on 10 Hindi words from frequency list.
"""

import pandas as pd
from word_data_fetcher import fetch_word_data
from db_setup import insert_word
import json

# Load Hindi frequency list
df = pd.read_excel("77 Languages Frequency Word Lists/Hindi (HI).xlsx")

# Get top 10 words (assuming first column is words)
top_words = df.iloc[:10, 0].tolist()  # Adjust column if needed

print("Testing top 10 Hindi words and inserting into DB:")
for word in top_words:
    print(f"\nFetching data for: {word}")
    data = fetch_word_data(word, "hi")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    
    # Insert into DB
    insert_word(word, "hi", data)
    print(f"Inserted {word} into DB.")

print("\nTest complete. Check word_enrichment.db for data.")