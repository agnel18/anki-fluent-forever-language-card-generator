"""Test TSV and ZIP export"""
import os
import sys
import tempfile
from pathlib import Path
import zipfile

def test_export_functions():
    """Test TSV and ZIP creation"""
    
    print("Testing TSV and ZIP Export...")
    
    try:
        from core_functions import create_anki_tsv, create_zip_export
        
        # Mock data
        mock_words_data = [
            {
                "word": "hello",
                "meaning": "greeting",
                "sentences": [
                    {
                        "sentence": "Hello, how are you?",
                        "english_translation": "Hello, how are you?",
                        "context": "greeting",
                    },
                    {
                        "sentence": "Say hello to everyone.",
                        "english_translation": "Say hello to everyone.",
                        "context": "social",
                    },
                ],
                "audio_files": ["hello_01.mp3", "hello_02.mp3"],
                "image_files": ["hello_01.jpg", "hello_02.jpg"],
            }
        ]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create mock audio and image files
            audio_dir = tmpdir_path / "audio"
            image_dir = tmpdir_path / "images"
            audio_dir.mkdir()
            image_dir.mkdir()
            
            for audio_file in mock_words_data[0]["audio_files"]:
                (audio_dir / audio_file).write_bytes(b"mock audio content")
            
            for image_file in mock_words_data[0]["image_files"]:
                (image_dir / image_file).write_bytes(b"mock image content")
            
            # Test TSV creation
            tsv_path = tmpdir_path / "test.tsv"
            print(f"  Creating TSV: {tsv_path}")
            
            if not create_anki_tsv(mock_words_data, str(tsv_path)):
                print("  ❌ TSV creation failed")
                return False
            
            if not tsv_path.exists():
                print("  ❌ TSV file not created")
                return False
            
            tsv_size = tsv_path.stat().st_size
            print(f"  ✅ TSV created ({tsv_size} bytes)")
            
            # Test ZIP creation
            zip_path = tmpdir_path / "test_deck.zip"
            print(f"  Creating ZIP: {zip_path}")
            
            if not create_zip_export(
                str(tsv_path),
                str(audio_dir),
                str(image_dir),
                str(zip_path),
            ):
                print("  ❌ ZIP creation failed")
                return False
            
            # Verify ZIP contents
            if not zipfile.is_zipfile(zip_path):
                print("  ❌ Invalid ZIP file created")
                return False
            
            with zipfile.ZipFile(zip_path, "r") as zf:
                files = zf.namelist()
                print(f"  ✅ ZIP created with {len(files)} files:")
                for file in files[:5]:  # Show first 5
                    print(f"     - {file}")
                if len(files) > 5:
                    print(f"     ... and {len(files) - 5} more")
            
            return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_export_functions()
    sys.exit(0 if success else 1)
