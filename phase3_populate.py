"""
Phase 3: Populate DB with 500 Hindi words.
"""

import pandas as pd
from word_data_fetcher import fetch_word_data
from db_setup import insert_word
import time

# Load Hindi frequency list
df = pd.read_excel("77 Languages Frequency Word Lists/Hindi (HI).xlsx")

# Get top 500 words
top_words = df.iloc[:500, 0].tolist()

print(f"Starting Phase 3: Populating DB with {len(top_words)} Hindi words...")

success_count = 0
for i, word in enumerate(top_words, 1):
    if i % 50 == 0:
        print(f"Processed {i}/{len(top_words)} words...")
    data = fetch_word_data(word, "hi")
    if data.get("source") != "N/A":
        success_count += 1
    insert_word(word, "hi", data)
    time.sleep(0.05)  # Small delay

print(f"\nPopulation complete!")
print(f"Successful fetches: {success_count}/{len(top_words)} ({success_count/len(top_words)*100:.1f}%)")
print("DB populated. Ready for manual review in Phase 3.3.")