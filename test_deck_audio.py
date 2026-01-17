#!/usr/bin/env python3
"""
Test audio generation in the exact same context as deck generation
"""

import sys
import os
from pathlib import Path

# Add streamlit_app to path
sys.path.insert(0, str(Path(__file__).parent / 'streamlit_app'))

from audio_generator import generate_audio

def test_deck_audio_context():
    """Test audio generation with exact same parameters as deck generation"""

    # Exact parameters from Hindi deck generation
    sentences = [
        {'sentence': 'मैं आपको नमस्ते कहता हूँ।'},
        {'sentence': 'नमस्ते कहकर वह चला गया।'},
        {'sentence': 'मैं आपका धन्यवाद देता हूँ।'},
        {'sentence': 'उसने मुझे धन्यवाद दिया।'}
    ]

    # Extract sentence texts
    sentence_texts = [s['sentence'] for s in sentences]

    voice = "hi-IN-SwaraNeural"
    media_dir = "test_output/media"
    word = "test_word"
    audio_speed = 0.8
    deck_unique_id = "20260114_162455_328"

    # Create media directory
    Path(media_dir).mkdir(parents=True, exist_ok=True)

    print(f"Testing audio generation with:")
    print(f"  Sentences: {len(sentence_texts)}")
    print(f"  Voice: {voice}")
    print(f"  Media dir: {media_dir}")
    print(f"  Word: {word}")
    print(f"  Audio speed: {audio_speed}")
    print(f"  Unique ID: {deck_unique_id}")

    try:
        # Call exactly like in deck generation
        audio_filenames = generate_audio(
            sentence_texts,
            voice,
            media_dir,
            batch_name=word,
            rate=audio_speed,
            unique_id=deck_unique_id
        )

        print(f"Audio generation returned: {audio_filenames}")

        # Check files
        for filename in audio_filenames:
            if filename:
                filepath = Path(media_dir) / filename
                if filepath.exists():
                    size = filepath.stat().st_size
                    print(f"  ✅ {filename}: {size} bytes")
                    if size == 0:
                        print(f"     ❌ File is empty!")
                else:
                    print(f"  ❌ {filename}: File not found")
            else:
                print("  ❌ Empty filename")

    except Exception as e:
        print(f"❌ Audio generation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_deck_audio_context()