"""
Frequency list management and utilities.
Handles loading word lists and batch size recommendations.
"""

import os
from pathlib import Path
from typing import List, Dict, Tuple
import pandas as pd

# Batch size presets with time/complexity estimates
BATCH_PRESETS = {
    100: {
        "label": "🟢 Quick Start",
        "time_estimate": "10 minutes",
        "description": "Perfect for first-timers",
        "emoji": "🟢",
        "recommended": True
    },
    200: {
        "label": "🟡 Medium",
        "time_estimate": "20 minutes",
        "description": "Good balance of size and speed",
        "emoji": "🟡",
        "recommended": False
    },
    500: {
        "label": "🟠 Comprehensive",
        "time_estimate": "45-60 minutes",
        "description": "Most common choice",
        "emoji": "🟠",
        "recommended": False
    },
    1000: {
        "label": "🔴 Long Session",
        "time_estimate": "90+ minutes",
        "description": "Consider splitting into 2-3 batches",
        "emoji": "🔴",
        "recommended": False
    },
    3000: {
        "label": "⚫ Not Recommended",
        "time_estimate": "4+ hours",
        "description": "Split into 3 batches of 1000",
        "emoji": "⚫",
        "recommended": False,
        "disabled": True
    },
    5000: {
        "label": "⚫ Not Recommended",
        "time_estimate": "6+ hours",
        "description": "Split into 5 batches of 1000",
        "emoji": "⚫",
        "recommended": False,
        "disabled": True
    }
}

def get_available_frequency_lists() -> Dict[str, int]:
    """
    Get available frequency word lists.
    Returns dict of {language: max_words_available}
    """
    lists_dir = Path(__file__).parent.parent / "109 Languages Frequency Word Lists"
    
    available_lists = {}
    
    if lists_dir.exists():
        for file in lists_dir.glob("*.xlsx"):
            language_code = file.stem.split(" (")[1].rstrip(")")
            language_name = file.stem.split(" (")[0]
            
            # Try to count words in the file
            try:
                df = pd.read_excel(file, sheet_name=0, header=None)
                word_count = len(df)
                available_lists[language_name] = word_count
            except:
                available_lists[language_name] = 5000  # Default estimate
    
    return available_lists


def load_frequency_list(language: str, limit: int = None) -> List[str]:
    """
    Load frequency word list for a language.
    
    Args:
        language: Language name (e.g., "Spanish", "Hindi")
        limit: Maximum number of words to load
        
    Returns:
        List of words in frequency order
    """
    lists_dir = Path(__file__).parent.parent / "109 Languages Frequency Word Lists"
    
    # Find matching language file
    matching_files = list(lists_dir.glob(f"{language}*"))
    
    if not matching_files:
        return []
    
    file_path = matching_files[0]
    
    try:
        df = pd.read_excel(file_path, sheet_name=0, header=None)
        words = df[0].tolist()  # Assume first column is words
        
        if limit:
            words = words[:limit]
        
        return [str(w).strip() for w in words if w]
    except Exception as e:
        print(f"Error loading {language} frequency list: {e}")
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
    if total_words <= 100:
        return [total_words], "✅ One batch - quick and easy!"
    elif total_words <= 500:
        return [total_words], "✅ One batch - manageable"
    elif total_words <= 1000:
        return [total_words], "⚠️ Large batch - may take 90+ minutes"
    else:
        # Split into 1000-word chunks
        num_batches = (total_words + 999) // 1000
        batches = [1000] * num_batches
        if total_words % 1000 != 0:
            batches[-1] = total_words % 1000
        
        return batches, f"📊 Recommended: Split into {num_batches} batches of ~1000 words each"


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
