#!/usr/bin/env python3
"""
Test script to generate a Hindi deck and evaluate quality.
"""

import sys
import os
from pathlib import Path

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value
# Add the streamlit_app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'streamlit_app'))

from core_functions import generate_complete_deck
import json

import os

def test_hindi_deck_generation():
    """Generate a Hindi deck and evaluate quality."""

    # Check for API keys
    groq_api_key = os.getenv('GROQ_API_KEY')
    pixabay_api_key = os.getenv('PIXABAY_API_KEY')

    if not groq_api_key:
        print("❌ GROQ_API_KEY environment variable not set")
        return

    if not pixabay_api_key:
        print("❌ PIXABAY_API_KEY environment variable not set")
        return

    # Test parameters
    language = "Hindi"  # Must match the case in _voice_for_language
    words = ["नमस्ते", "धन्यवाद", "पानी", "खाना", "घर"]  # Hello, Thank you, Water, Food, Home
    num_sentences = 2
    output_dir = "test_output"

    print(f"Generating deck for {language} with {len(words)} words...")
    print(f"Output directory: {output_dir}")

    try:
        # Generate complete deck
        result = generate_complete_deck(
            words=words,
            language=language,
            groq_api_key=groq_api_key,
            pixabay_api_key=pixabay_api_key,
            output_dir=output_dir,
            num_sentences=num_sentences,
            difficulty="intermediate"
        )

        print(f"Generation result: {result}")

        if not result.get('success', False):
            print(f"❌ Generation failed: {result.get('error', 'Unknown error')}")
            return

        # Check for TSV file
        tsv_path = result.get('tsv_path')
        if tsv_path and os.path.exists(tsv_path):
            print(f"✅ TSV file created: {tsv_path}")
            # Read and analyze TSV content
            analyze_tsv_quality(tsv_path)
        else:
            print("❌ No TSV file generated")

        # Check for media files
        media_dir = result.get('media_dir')
        if media_dir and os.path.exists(media_dir):
            audio_files = [f for f in os.listdir(media_dir) if f.endswith('.mp3')]
            image_files = [f for f in os.listdir(media_dir) if f.endswith(('.jpg', '.png'))]
            print(f"✅ Media directory: {media_dir}")
            print(f"  Audio files: {len(audio_files)}")
            print(f"  Image files: {len(image_files)}")
        else:
            print("❌ No media directory")

    except Exception as e:
        print(f"❌ Generation failed: {e}")
        import traceback
        traceback.print_exc()

def analyze_tsv_quality(tsv_path):
    """Analyze the quality of generated TSV content."""
    try:
        import pandas as pd

        df = pd.read_csv(tsv_path, sep='\t')
        print(f"\n=== TSV ANALYSIS ===")
        print(f"Total rows: {len(df)}")
        print(f"Columns: {list(df.columns)}")

        # Analyze content quality
        total_sentences = 0
        valid_sentences = 0
        has_ipa = 0
        has_audio = 0
        has_images = 0

        for idx, row in df.iterrows():
            sentence = row.get('Sentence', '')
            ipa = row.get('IPA', '')
            audio = row.get('Audio', '')
            images = row.get('Images', '')

            total_sentences += 1

            if sentence and len(sentence) > 10:
                valid_sentences += 1
            if ipa and str(ipa).lower() not in ['n/a', 'none', '']:
                has_ipa += 1
            if audio and str(audio).lower() not in ['n/a', 'none', '']:
                has_audio += 1
            if images and str(images).lower() not in ['n/a', 'none', '']:
                has_images += 1

        # Calculate percentages
        validity_rate = (valid_sentences / total_sentences * 100) if total_sentences > 0 else 0
        ipa_rate = (has_ipa / total_sentences * 100) if total_sentences > 0 else 0
        audio_rate = (has_audio / total_sentences * 100) if total_sentences > 0 else 0
        image_rate = (has_images / total_sentences * 100) if total_sentences > 0 else 0

        print(f"Valid sentences (>10 chars): {valid_sentences}/{total_sentences} ({validity_rate:.1f}%)")
        print(f"Sentences with IPA: {has_ipa}/{total_sentences} ({ipa_rate:.1f}%)")
        print(f"Sentences with audio: {has_audio}/{total_sentences} ({audio_rate:.1f}%)")
        print(f"Sentences with images: {has_images}/{total_sentences} ({image_rate:.1f}%)")

        # Overall quality score
        quality_score = (validity_rate + ipa_rate + audio_rate + image_rate) / 4
        print(f"\nOverall Quality Score: {quality_score:.1f}/100")

        if quality_score >= 80:
            print("✅ Excellent quality!")
        elif quality_score >= 60:
            print("⚠️ Good quality, some improvements needed")
        else:
            print("❌ Poor quality, significant issues")

        # Show sample content
        print("\n=== SAMPLE CONTENT ===")
        for i in range(min(3, len(df))):
            row = df.iloc[i]
            print(f"Word {i+1}: {row.get('Word', 'N/A')}")
            print(f"  Sentence: {row.get('Sentence', 'N/A')}")
            print(f"  IPA: {row.get('IPA', 'N/A')}")
            print(f"  Audio: {row.get('Audio', 'N/A')}")
            print(f"  Images: {row.get('Images', 'N/A')}")
            print()

    except Exception as e:
        print(f"❌ TSV analysis failed: {e}")

if __name__ == "__main__":
    test_hindi_deck_generation()