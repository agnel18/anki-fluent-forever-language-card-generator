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
        language: Language name (e.g., "Spanish", "Mandarin Chinese")
        limit: Maximum number of words to load
        
    Returns:
        List of words in frequency order
    """
    # Mapping from UI names to file names
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
    
    # Get the filename-friendly name
    search_name = language_mapping.get(language, language)
    
    lists_dir = Path(__file__).parent.parent / "109 Languages Frequency Word Lists"
    
    if not lists_dir.exists():
        return []
    
    # Find matching file by looking for the search_name in filename
    matching_files = []
    for file in lists_dir.glob("*.xlsx"):
        if search_name in file.stem:
            matching_files.append(file)
    
    if not matching_files:
        # Fallback: just try the original language name
        for file in lists_dir.glob("*.xlsx"):
            if language in file.stem:
                matching_files.append(file)
    
    if not matching_files:
        # Last resort: return empty list
        print(f"Warning: No word list found for {language} or {search_name}")
        return []
    
    file_path = matching_files[0]
    
    try:
        df = pd.read_excel(file_path, sheet_name=0, header=None)
        words = df.iloc[:, 0].tolist()  # Get first column
        
        # Clean words
        words = [str(w).strip() for w in words if w and str(w).strip()]
        
        if limit:
            words = words[:limit]
        
        return words
    except Exception as e:
        print(f"Error loading {language} frequency list from {file_path}: {e}")
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
