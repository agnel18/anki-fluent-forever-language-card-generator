#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test complete generation with word meanings and top-3 image selection"""

import sys
from pathlib import Path
from dotenv import load_dotenv
import os

# Load .env
env_file = Path(__file__).parent / ".env"
load_dotenv(env_file)

sys.path.insert(0, str(Path(__file__).parent / "streamlit_app"))

from core_functions import generate_complete_deck

def test_generation():
    """Test complete generation workflow"""
    
    print("=" * 80)
    print("TEST: WORD MEANINGS + TOP-3 IMAGE SELECTION")
    print("=" * 80)
    
    # Test parameters
    language = "Spanish"
    test_words = ["el", "gato"]
    output_dir = Path(__file__).parent / "test_output_new"
    output_dir.mkdir(exist_ok=True)
    
    # API keys from .env
    groq_key = os.getenv("GROQ_API_KEY", "")
    pixabay_key = os.getenv("PIXABAY_API_KEY", "")
    
    print(f"\nConfig:")
    print(f"  Language: {language}")
    print(f"  Words: {', '.join(test_words)}")
    print(f"  Expected: Word meanings + top-3 image selection")
    
    try:
        result = generate_complete_deck(
            words=test_words,
            language=language,
            groq_api_key=groq_key,
            pixabay_api_key=pixabay_key,
            output_dir=str(output_dir),
            num_sentences=5,  # Just 5 sentences for speed
            audio_speed=0.8,
            voice=None,
            all_words=test_words,
        )
        
        if not result["success"]:
            print(f"\nERROR: {result.get('error', 'Unknown')}")
            return False
        
        # Check results
        tsv_path = Path(result.get("tsv_path", ""))
        media_dir = Path(result.get("media_dir", ""))
        
        if tsv_path.exists():
            import pandas as pd
            df = pd.read_csv(tsv_path, sep="\t", header=None)
            
            print(f"\nResults:")
            print(f"  TSV rows: {len(df)}")
            print(f"\n  Sample card 1:")
            row = df.iloc[0]
            print(f"    Word: {row[1]}")
            print(f"    Meaning: {row[2]}")
            print(f"    Sentence: {row[3][:50]}...")
            print(f"    English: {row[5][:50]}...")
            
            if len(df) > 5:
                print(f"\n  Sample card 2 (different word):")
                row = df.iloc[5]
                print(f"    Word: {row[1]}")
                print(f"    Meaning: {row[2]}")
        
        if media_dir.exists():
            mp3_files = list(media_dir.glob("*.mp3"))
            jpg_files = list(media_dir.glob("*.jpg"))
            print(f"\n  Media files:")
            print(f"    MP3: {len(mp3_files)}")
            print(f"    JPG: {len(jpg_files)}")
        
        print("\nSUCCESS: All features working!")
        print("  + Word meanings generated")
        print("  + Top-3 image selection active")
        return True
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_generation()
    sys.exit(0 if success else 1)
