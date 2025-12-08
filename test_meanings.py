#!/usr/bin/env python3
"""Test word meaning generation"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "streamlit_app"))

# Load .env file
from dotenv import load_dotenv
import os

env_file = Path(__file__).parent / ".env"
load_dotenv(env_file)

from core_functions import generate_word_meaning

groq_key = os.getenv("GROQ_API_KEY", "")
if not groq_key:
    print("❌ GROQ_API_KEY not set")
    sys.exit(1)

# Test words
test_words = [
    ("el", "Spanish"),
    ("gato", "Spanish"),
    ("casa", "Spanish"),
    ("bonjour", "French"),
    ("perro", "Spanish"),
]

print("=" * 80)
print("🧪 TESTING WORD MEANING GENERATION")
print("=" * 80)

for word, language in test_words:
    try:
        meaning = generate_word_meaning(word, language, groq_key)
        print(f"✅ {language:10} | {word:15} → {meaning}")
    except Exception as e:
        print(f"❌ {language:10} | {word:15} → ERROR: {e}")

print("\n" + "=" * 80)
