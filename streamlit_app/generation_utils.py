# Generation utilities module
# Extracted from core_functions.py for better separation of concerns

import logging
import pandas as pd
from typing import List, Dict

logger = logging.getLogger(__name__)

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
def estimate_api_costs(num_words: int, num_sentences: int = 10) -> dict:
    """
    Estimate API usage for cost calculator (Optimized 2-Pass Architecture).

    Token usage per word:
    - PASS 1 (raw generation): ~200 tokens
    - PASS 2 (batch validation + enrichment): ~200 tokens
    - Total: ~400 tokens per word

    With 100k free tokens:
    - ~250 words/month (10 sentences each = 2,500 sentences)

    Args:
        num_words: Number of words to process
        num_sentences: Sentences per word

    Returns:
        Dict with estimates
    """
    total_sentences = num_words * num_sentences
    avg_chars_per_sentence = 90

    return {
        "total_sentences": total_sentences,
        "total_images": total_sentences,
        "pixabay_requests": total_sentences,  # One per sentence
        "groq_tokens_est": int(num_words * 400),  # 2-pass architecture: ~400 tokens/word
        "edge_tts_chars": int(total_sentences * avg_chars_per_sentence),
    }

def parse_csv_upload(file_content: bytes) -> list[dict]:
    """
    Parse uploaded CSV file.

    Args:
        file_content: CSV file bytes

    Returns:
        List of dicts with 'word' and 'meaning' keys
    """
    try:
        df = pd.read_csv(file_content)
        # Expect columns: word, meaning (flexible naming)
        cols = df.columns.str.lower()
        word_col = [c for c in cols if "word" in c][0] if any("word" in c for c in cols) else cols[0]
        meaning_col = [c for c in cols if "meaning" in c or "translation" in c][0] if any("meaning" in c or "translation" in c for c in cols) else cols[1] if len(cols) > 1 else "meaning"

        result = []
        for _, row in df.iterrows():
            result.append({
                "word": str(row[word_col]).strip(),
                "meaning": str(row[meaning_col]).strip(),
            })

        return result
    except Exception as e:
        logger.error(f"CSV parse error: {e}")
        return []