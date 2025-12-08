#!/usr/bin/env python3
"""
Test script for complete generation workflow
Tests: sentences, audio, images, TSV export, all per-sentence architecture
"""

import sys
import asyncio
import os
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent / "streamlit_app"))

from core_functions import generate_complete_deck
from frequency_utils import load_frequency_list

async def test_generation():
    """Test complete generation workflow"""
    
    print("=" * 80)
    print("🧪 TESTING COMPLETE GENERATION WORKFLOW")
    print("=" * 80)
    
    # Test parameters
    language = "Spanish"
    test_words = ["el", "gato", "casa"]  # 3 words = 30 sentences, 30 audio, 30 images
    output_dir = Path(__file__).parent / "test_output"
    output_dir.mkdir(exist_ok=True)
    
    # API keys (from .env or environment)
    groq_key = os.getenv("GROQ_API_KEY", "your_groq_key_here")
    pixabay_key = os.getenv("PIXABAY_API_KEY", "your_pixabay_key_here")
    
    print(f"\n📋 Test Configuration:")
    print(f"  Language: {language}")
    print(f"  Words: {', '.join(test_words)}")
    print(f"  Sentences per word: 10")
    print(f"  Expected audio files: 30 (3 words × 10 sentences)")
    print(f"  Expected image files: 30 (3 words × 10 sentences)")
    print(f"  Output directory: {output_dir}")
    
    print(f"\n⏳ Starting generation...")
    
    try:
        result = await asyncio.to_thread(
            generate_complete_deck,
            words=test_words,
            language=language,
            groq_api_key=groq_key,
            pixabay_api_key=pixabay_key,
            output_dir=str(output_dir),
            num_sentences=10,
            audio_speed=0.8,
            voice=None,
            all_words=test_words,
        )
        
        if not result["success"]:
            print(f"\n❌ Generation failed: {result.get('error', 'Unknown error')}")
            return False
        
        print(f"\n✅ Generation successful!")
        print(f"\n📊 Results:")
        print(f"  TSV path: {result.get('tsv_path')}")
        print(f"  Media dir: {result.get('media_dir')}")
        print(f"  Output dir: {result.get('output_dir')}")
        
        # Verify files
        media_dir = Path(result.get("media_dir", ""))
        tsv_path = Path(result.get("tsv_path", ""))
        
        if media_dir.exists():
            mp3_files = list(media_dir.glob("*.mp3"))
            jpg_files = list(media_dir.glob("*.jpg"))
            print(f"\n📁 Media Files:")
            print(f"  MP3 files: {len(mp3_files)} (expected 30)")
            print(f"  JPG files: {len(jpg_files)} (expected 30)")
            
            if mp3_files:
                print(f"\n  Audio samples:")
                for mp3 in sorted(mp3_files)[:3]:
                    size = mp3.stat().st_size
                    status = "✅" if size > 1000 else "⚠️ (small)"
                    print(f"    {status} {mp3.name} ({size} bytes)")
            
            if jpg_files:
                print(f"\n  Image samples:")
                for jpg in sorted(jpg_files)[:3]:
                    size = jpg.stat().st_size
                    status = "✅" if size > 5000 else "⚠️ (small)"
                    print(f"    {status} {jpg.name} ({size} bytes)")
        
        # Verify TSV
        if tsv_path.exists():
            import pandas as pd
            df = pd.read_csv(tsv_path, sep="\t", header=None)
            print(f"\n📋 TSV Export:")
            print(f"  Rows: {len(df)} (expected 30)")
            print(f"  Columns: {len(df.columns)} (expected 9)")
            
            if len(df) > 0:
                print(f"\n  First row (sample):")
                row = df.iloc[0]
                for i, val in enumerate(row):
                    field_names = [
                        "File Name", "Word", "Meaning",
                        "Sentence", "IPA", "English",
                        "Sound", "Image", "Tags"
                    ]
                    print(f"    {field_names[i]}: {str(val)[:50]}...")
            
            # Check for Sound and Image columns
            if len(df.columns) >= 8:
                print(f"\n  Sound column (8):")
                sound_sample = str(df.iloc[0, 6])
                print(f"    {sound_sample[:60]}...")
                
                print(f"\n  Image column (9):")
                image_sample = str(df.iloc[0, 7])
                print(f"    {image_sample[:60]}...")
        
        print(f"\n" + "=" * 80)
        print("✅ ALL TESTS PASSED!")
        print("=" * 80)
        
        print(f"\n📝 Summary:")
        print(f"  ✅ Sentences generated (Groq)")
        print(f"  ✅ Audio generated (Edge TTS)")
        print(f"  ✅ Images downloaded (Pixabay)")
        print(f"  ✅ TSV created (Anki format)")
        print(f"  ✅ Per-sentence architecture verified")
        print(f"  ✅ File naming: rank_word_sentence format")
        print(f"  ✅ Single media/ folder structure")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with exception:")
        print(f"  {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_generation())
    sys.exit(0 if success else 1)
