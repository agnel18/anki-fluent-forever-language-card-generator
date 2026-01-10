"""
Phase 2 Pilot: Batch fetch and populate DB with 100 Hindi words.
"""

import pandas as pd
from word_data_fetcher import fetch_word_data
from db_setup import insert_word
import time

# Load Hindi frequency list
df = pd.read_excel("77 Languages Frequency Word Lists/Hindi (HI).xlsx")

# Get top 100 words
top_words = df.iloc[:100, 0].tolist()

print(f"Starting Phase 2 pilot: Fetching and inserting {len(top_words)} Hindi words...")

success_count = 0
total_count = len(top_words)

for i, word in enumerate(top_words, 1):
    print(f"Fetching {i}/{total_count}: {word}")
    data = fetch_word_data(word, "hi")
    
    if data.get("source") != "N/A":
        success_count += 1
    
    insert_word(word, "hi", data)
    
    # Small delay to avoid overwhelming
    time.sleep(0.1)

success_rate = (success_count / total_count) * 100
print(f"\nPilot complete!")
print(f"Successful fetches: {success_count}/{total_count} ({success_rate:.1f}%)")
print("Check word_enrichment.db for populated data.")

if success_rate >= 90:
    print("✅ Success criteria met!")
else:
    print("⚠️ Below 90% - need to expand mock data or implement real APIs.")