"""Test Edge TTS audio generation"""
import os
import sys
import tempfile
from pathlib import Path

def test_edge_tts():
    """Test Edge TTS audio generation"""
    
    print("Testing Edge TTS Audio Generation...")
    
    try:
        from core_functions import generate_audio
        
        test_sentences = [
            "Hello, how are you today?",
            "The weather is beautiful.",
        ]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            print(f"  Generating audio files to: {tmpdir}")
            
            audio_files = generate_audio(
                sentences=test_sentences,
                voice="en-US-AvaNeural",
                output_dir=tmpdir,
                batch_name="test",
                rate=0.8,
            )
            
            if not audio_files:
                print("  ❌ No audio files generated")
                return False
            
            print(f"  ✅ Generated {len(audio_files)} audio files:")
            
            for audio_file in audio_files:
                file_path = Path(tmpdir) / audio_file
                if file_path.exists():
                    file_size = file_path.stat().st_size
                    print(f"     ✅ {audio_file} ({file_size} bytes)")
                else:
                    print(f"     ❌ {audio_file} not found")
                    return False
            
            return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_edge_tts()
    sys.exit(0 if success else 1)
