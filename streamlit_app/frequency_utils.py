"""
Frequency list management and utilities.
Handles loading word lists (via SQLite) and batch size recommendations.
"""

import os
from pathlib import Path
from typing import List, Dict, Tuple
import pandas as pd

# Lazy imports to avoid circular dependencies
# from db_manager import get_words_paginated, search_words, get_languages

# Batch size presets with time/complexity estimates
BATCH_PRESETS = {
    5: {
        "label": "🟢 Quick Start",
        "time_estimate": "5-10 minutes",
        "description": "Perfect for first-timers (50 sentences)",
        "emoji": "🟢",
        "recommended": True
    },
    10: {
        "label": "🟡 Small",
        "time_estimate": "10-15 minutes",
        "description": "Good for testing (100 sentences)",
        "emoji": "🟡",
        "recommended": False
    },
    20: {
        "label": "🟠 Medium",
        "time_estimate": "20-30 minutes",
        "description": "Balanced batch (200 sentences)",
        "emoji": "🟠",
        "recommended": False
    },
    40: {
        "label": "🔴 Large",
        "time_estimate": "40-60 minutes",
        "description": "Bigger commitment (400 sentences)",
        "emoji": "🔴",
        "recommended": False
    },
    50: {
        "label": "⚫ Very Large",
        "time_estimate": "50-80 minutes",
        "description": "Full session (500 sentences)",
        "emoji": "⚫",
        "recommended": False
    }
}

def get_available_frequency_lists() -> Dict[str, int]:
    """
    Get available frequency word lists from SQLite database.
    Returns dict of {language: word_count}
    """
    from db_manager import get_languages
    from stats_manager import get_word_stats

    languages = get_languages()
    return {lang: get_word_stats(lang).get("total", 0) for lang in languages}


def load_frequency_list(language: str, limit: int = None) -> List[str]:
    """
    Load frequency word list for a language from SQLite.
    
    Args:
        language: Language name (e.g., "Spanish", "Mandarin Chinese")
        limit: Maximum number of words to load
        
    Returns:
        List of words in frequency order
    """
    from db_manager import get_words_paginated
    
    # Mapping from UI names to database names
    language_mapping = {
        "Mandarin Chinese": "Chinese (Simplified)",
        "Cantonese": "Chinese (Traditional)",
        "Moroccan Arabic": "Arabic",
        "English": "English",
        "Spanish": "Spanish",
        "French": "French",
        "German": "German",
        "Italian": "Italian",
        "Portuguese": "Portuguese",
        "Russian": "Russian",
        "Chinese (Simplified)": "Chinese (Simplified)",
        "Chinese (Traditional)": "Chinese (Traditional)",
    }
    
    db_language = language_mapping.get(language, language)
    
    try:
        # Get all words from database
        words, total = get_words_paginated(db_language, page=1, per_page=1000)
        
        if limit:
            words = words[:limit]
        
        return words if words else []
        
    except Exception as e:
        print(f"Error loading {language} frequency list from database: {e}")
        return []

def get_batch_info(batch_size: int) -> Dict:
    """Get information about a batch size."""
    return BATCH_PRESETS.get(batch_size, {})


def format_batch_option(batch_size: int) -> str:
    """Format batch size for UI display."""
    info = BATCH_PRESETS.get(batch_size, {})
    return f"{info.get('emoji', '•')} {batch_size} words ({info.get('time_estimate', 'N/A')})"


def recommend_batch_strategy(total_words: int) -> Tuple[List[int], str]:
    """
    Recommend how to split a large word list into batches.
    
    Args:
        total_words: Total number of words to generate
        
    Returns:
        (list of batch sizes, recommendation message)
    """
    if total_words <= 5:
        return [total_words], "✅ Quick batch - less than 5 minutes!"
    elif total_words <= 10:
        return [total_words], "✅ Small batch - very manageable"
    elif total_words <= 20:
        return [total_words], "✅ Medium batch - 20-30 minutes"
    elif total_words <= 50:
        return [total_words], "⚠️ Large batch - 50-80 minutes"
    else:
        # Split into 50-word chunks
        num_batches = (total_words + 49) // 50
        batches = [50] * num_batches
        if total_words % 50 != 0:
            batches[-1] = total_words % 50
        
        return batches, f"📊 Recommended: Split into {num_batches} batches of ~50 words each"


def get_csv_template() -> str:
    """
    Generate CSV template for custom word uploads.
    
    Returns:
        CSV string
    """
    return """Word
hello
book
water
house
person
love
computer
language
learn
study
create
amazing
beautiful
wonderful
incredible"""


def validate_word_list(words: List[str]) -> Tuple[bool, str]:
    """
    Validate uploaded word list.
    
    Args:
        words: List of words
        
    Returns:
        (is_valid, error_message)
    """
    if not words:
        return False, "❌ No words found in file"
    
    if len(words) > 5000:
        return False, "❌ Too many words (max 5000). Please split into batches."
    
    if len(words) < 1:
        return False, "❌ Too few words (min 1)"
    
    # Check for duplicates
    unique_words = set(words)
    if len(unique_words) < len(words) * 0.9:
        duplicates = len(words) - len(unique_words)
        return True, f"⚠️ Warning: {duplicates} duplicate words will be removed"
    
    return True, f"✅ Valid list: {len(unique_words)} unique words"


def parse_uploaded_word_file(uploaded_file) -> Tuple[List[str], str]:
    """
    Parse CSV or XLSX file uploaded by user.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        (list of words, status message)
    """
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file)
        else:
            return [], "❌ Only CSV and XLSX files are supported"
        
        # Get first column (assumes word list)
        if df.empty:
            return [], "❌ File is empty"
        
        words = df.iloc[:, 0].tolist()
        words = [str(w).strip() for w in words if w and str(w).strip()]
        
        if not words:
            return [], "❌ No words found in file"
        
        return words, f"✅ Loaded {len(words)} words"
        
    except Exception as e:
        return [], f"❌ Error reading file: {str(e)}"


def get_words_with_ranks(language: str, page: int = 1, page_size: int = 25) -> Tuple[pd.DataFrame, int]:
    """
    Get paginated words with their frequency ranks for display.
    
    Args:
        language: Language name
        page: Page number (1-indexed)
        page_size: Number of words per page
        
    Returns:
        (DataFrame with columns ['Rank', 'Word', 'Completed'], total_word_count)
    """
    from db_manager import get_words_paginated, get_completed_words
    
    words, total_count = get_words_paginated(language, page=page, per_page=page_size)
    completed = get_completed_words(language)
    
    # Build dataframe with rank and completion status
    start_rank = (page - 1) * page_size + 1
    data = []
    
    for idx, word_dict in enumerate(words, start=start_rank):
        word = word_dict['word']
        data.append({
            'Rank': idx,
            'Word': word,
            'Completed': '✓' if word in completed else ''
        })
    
    df = pd.DataFrame(data)
    return df, total_count
