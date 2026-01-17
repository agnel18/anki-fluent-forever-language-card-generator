#!/usr/bin/env python3
"""
Test audio generation with the same parameters as deck generation
"""

import sys
import os
from pathlib import Path

# Add streamlit_app to path
sys.path.insert(0, str(Path(__file__).parent / 'streamlit_app'))

from audio_generator import generate_audio

def test_audio_generation():
    """Test audio generation with Hindi sentences"""

    # Test data from Hindi deck generation
    sentences = [
        "मैं आपको नमस्ते कहता हूँ।",
        "नमस्ते कहकर वह चला गया।",
        "मैं आपका धन्यवाद देता हूँ।",
        "उसने मुझे धन्यवाद दिया।"
    ]

    voice = "hi-IN-SwaraNeural"
    output_dir = "test_audio_output"
    batch_name = "test_word"
    rate = 0.8
    unique_id = "20260114_162455_328"

    print(f"Testing audio generation with {len(sentences)} sentences")
    print(f"Voice: {voice}")
    print(f"Output dir: {output_dir}")
    print(f"Rate: {rate}")
    print(f"Unique ID: {unique_id}")

    # Create output directory
    Path(output_dir).mkdir(exist_ok=True)

    try:
        # Call generate_audio
        result = generate_audio(
            sentences=sentences,
            voice=voice,
            output_dir=output_dir,
            batch_name=batch_name,
            rate=rate,
            unique_id=unique_id
        )

        print(f"Audio generation returned: {result}")

        # Check files
        for filename in result:
            if filename:
                filepath = Path(output_dir) / filename
                if filepath.exists():
                    size = filepath.stat().st_size
                    print(f"✅ {filename}: {size} bytes")
                    if size == 0:
                        print(f"  ❌ File is empty!")
                else:
                    print(f"❌ {filename}: File not found")
            else:
                print("❌ Empty filename in result")

    except Exception as e:
        print(f"❌ Audio generation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_audio_generation()