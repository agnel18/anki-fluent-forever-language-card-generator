# Generation utilities module
# Extracted from core_functions.py for better separation of concerns

import logging
import pandas as pd
import re
import time
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
            messages=[{"role": "user", "content": f"Generate exactly 3 diverse and specific keywords for an image that represents the sentence: '{sentence}' with translation: '{translation}'. The sentence is about the word '{target_word}'. Make the keywords unique and visual - avoid generic terms like 'language' or 'learning'. Focus on concrete objects, actions, or scenes. Return only a comma-separated list of 3 keywords, no explanations or formatting."}],
            max_tokens=100
        )
        raw_response = response.choices[0].message.content.strip()
        
        # Rate limiting: wait 2 seconds between API calls to respect per-minute limits
        time.sleep(2)
        
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
            keywords = ', '.join(keywords_list[:3])  # Limit to 3 keywords
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


def batch_generate_image_keywords(
    sentences_data: List[Dict[str, str]],
    groq_api_key: str
) -> List[str]:
    """
    Generate AI-powered keywords for image search for MULTIPLE sentences in ONE API call.
    Much more efficient than individual calls - saves API quota and reduces latency.

    Args:
        sentences_data: List of dicts with keys 'sentence', 'english_translation', 'target_word'
        groq_api_key: Groq API key

    Returns:
        List of comma-separated keywords strings, one per sentence
    """
    if not groq_api_key:
        logger.warning("Groq API key not available, using fallback keywords")
        return [f"{data['target_word']}, language, learning" for data in sentences_data]

    if not sentences_data:
        return []

    try:
        client = Groq(api_key=groq_api_key)

        # Build a single prompt for all sentences
        prompt_parts = []
        for i, data in enumerate(sentences_data, 1):
            prompt_parts.append(f"Sentence {i}: '{data['sentence']}' (translation: '{data['english_translation']}', target word: '{data['target_word']}')")

        prompt = f"""Generate exactly 3 diverse and specific keywords for an image that represents each sentence. Make the keywords unique and visual - avoid generic terms like 'language' or 'learning'. Focus on concrete objects, actions, or scenes.

{"".join(prompt_parts)}

Return the results in this exact format:
Sentence 1: keyword1, keyword2, keyword3
Sentence 2: keyword1, keyword2, keyword3
..."""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200  # Enough for all sentences
        )

        raw_response = response.choices[0].message.content.strip()

        # Rate limiting: wait 2 seconds between API calls to respect per-minute limits
        time.sleep(2)

        # Parse the response
        results = []
        lines = raw_response.split('\n')

        for line in lines:
            line = line.strip()
            if line.startswith('Sentence ') and ':' in line:
                # Extract keywords after the colon
                keywords_part = line.split(':', 1)[1].strip()
                # Clean up any extra formatting
                keywords_part = re.sub(r'[^\w\s,]', '', keywords_part)
                keywords_part = re.sub(r'\s+', ' ', keywords_part).strip()

                if keywords_part and len(keywords_part.split(',')) >= 2:
                    results.append(keywords_part)
                else:
                    # Fallback for this sentence
                    sentence_idx = len(results)
                    if sentence_idx < len(sentences_data):
                        target_word = sentences_data[sentence_idx]['target_word']
                        results.append(f"{target_word}, language, learning")

        # Ensure we have results for all sentences
        while len(results) < len(sentences_data):
            target_word = sentences_data[len(results)]['target_word']
            results.append(f"{target_word}, language, learning")

        return results[:len(sentences_data)]  # Don't return more than requested

    except Exception as e:
        logger.error(f"Error in batch image keyword generation: {e}")
        return [f"{data['target_word']}, language, learning" for data in sentences_data]