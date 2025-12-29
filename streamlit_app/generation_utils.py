# Generation utilities module
# Extracted from core_functions.py for better separation of concerns

import logging
import pandas as pd
import re
from typing import List, Dict
from groq import Groq

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


def generate_image_keywords(sentence: str, translation: str, target_word: str, groq_api_key: str) -> str:
    """
    Generate AI-powered keywords for image search based on sentence content.

    Args:
        sentence: The sentence text
        translation: English translation
        target_word: The target word being learned
        groq_api_key: Groq API key

    Returns:
        Comma-separated keywords string
    """
    if not groq_api_key:
        logger.warning("Groq API key not available, using fallback keywords")
        return f"{target_word}, language, learning"

    try:
        client = Groq(api_key=groq_api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": f"Generate 3-5 relevant keywords for an image that represents the sentence: '{sentence}' with translation: '{translation}'. The sentence is about the word '{target_word}'. Return only a comma-separated list of keywords, no explanations or formatting."}],
            max_tokens=100
        )
        raw_response = response.choices[0].message.content.strip()
        
        # Extract just the keywords from the response
        # Remove any introductory text and formatting
        lines = raw_response.split('\n')
        keywords_list = []
        
        for line in lines:
            line = line.strip()
            # Skip empty lines and explanatory text
            if not line or line.startswith(('Here are', 'These keywords', 'The keywords', 'Keywords:')):
                continue
            # Remove numbering like "1. " or "- "
            line = re.sub(r'^\d+\.\s*', '', line)
            line = re.sub(r'^-\s*', '', line)
            # Clean up the line
            line = line.strip()
            if line and not line.startswith(('These', 'The', 'Keywords')):
                keywords_list.append(line)
        
        # If we found numbered/listed keywords, join them
        if keywords_list:
            keywords = ', '.join(keywords_list[:5])  # Limit to 5 keywords
        else:
            # Fallback: try to extract comma-separated keywords
            keywords = re.sub(r'[^\w\s,]', '', raw_response)  # Remove special chars
            keywords = re.sub(r'\s+', ' ', keywords)  # Normalize spaces
            keywords = keywords.strip()
        
        # Ensure we have something useful
        if not keywords or len(keywords.split(',')) < 2:
            keywords = f"{target_word}, language, learning"
            
        return keywords
    except Exception as e:
        logger.error(f"Error generating image keywords: {e}")
        return f"{target_word}, language, learning"