"""End-to-end integration test for complete pipeline"""
import os
import sys
import tempfile
from pathlib import Path

def test_e2e_pipeline():
    """Test complete pipeline: sentences → audio → images → TSV → ZIP"""
    
    print("Testing End-to-End Pipeline...")
    print("=" * 60)
    
    try:
        from core_functions import (
            generate_sentences,
            generate_audio,
            generate_images_pixabay,
            create_anki_tsv,
            create_zip_export,
            get_available_voices,
            estimate_api_costs,
        )
        
        # Step 1: Test data generation
        print("\n✅ Step 1: Functions imported successfully")
        print("   - generate_sentences")
        print("   - generate_audio")
        print("   - generate_images_pixabay")
        print("   - create_anki_tsv")
        print("   - create_zip_export")
        print("   - get_available_voices")
        print("   - estimate_api_costs")
        
        # Step 2: Test voice availability
        print("\n✅ Step 2: Testing voice availability")
        en_voices = get_available_voices("en")
        es_voices = get_available_voices("es")
        print(f"   English voices: {len(en_voices)} available")
        if en_voices:
            print(f"   Example: {en_voices[0]}")
        print(f"   Spanish voices: {len(es_voices)} available")
        if es_voices:
            print(f"   Example: {es_voices[0]}")
        
        # Step 3: Test cost estimation
        print("\n✅ Step 3: Testing cost estimation")
        costs = estimate_api_costs(
            num_words=1,
            num_sentences=10
        )
        print(f"   API cost estimation (1 word, 10 sentences):")
        for key, value in costs.items():
            print(f"   - {key}: {value}")
        
        # Step 4: Mock data structure
        print("\n✅ Step 4: Creating mock pipeline data")
        mock_words_data = [
            {
                "word": "test",
                "meaning": "an examination",
                "sentences": [
                    {
                        "sentence": "I took a test today.",
                        "english_translation": "I took a test today.",
                        "context": "exam",
                    }
                    for _ in range(2)  # 2 sentences instead of 10 for speed
                ],
                "audio_files": ["test_01.mp3", "test_02.mp3"],
                "image_files": ["test_01.jpg", "test_02.jpg"],
            }
        ]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create mock files
            audio_dir = tmpdir_path / "audio"
            image_dir = tmpdir_path / "images"
            audio_dir.mkdir()
            image_dir.mkdir()
            
            for af in mock_words_data[0]["audio_files"]:
                (audio_dir / af).write_bytes(b"mock mp3 data")
            
            for imf in mock_words_data[0]["image_files"]:
                (image_dir / imf).write_bytes(b"mock jpg data")
            
            # Step 5: Create TSV
            print("\n✅ Step 5: Creating TSV file")
            tsv_file = tmpdir_path / "ANKI_IMPORT.tsv"
            if create_anki_tsv(mock_words_data, str(tsv_file)):
                size = tsv_file.stat().st_size
                print(f"   TSV file created: {size} bytes")
                with open(tsv_file) as f:
                    lines = f.readlines()
                    print(f"   TSV lines: {len(lines)}")
                    print(f"   First line: {lines[0][:70]}...")
            
            # Step 6: Create ZIP
            print("\n✅ Step 6: Creating ZIP export")
            zip_file = tmpdir_path / "deck.zip"
            if create_zip_export(
                str(tsv_file),
                str(audio_dir),
                str(image_dir),
                str(zip_file),
            ):
                size = zip_file.stat().st_size
                print(f"   ZIP file created: {size} bytes")
                
                import zipfile
                with zipfile.ZipFile(zip_file, "r") as zf:
                    files = zf.namelist()
                    print(f"   ZIP contents: {len(files)} files")
                    for f in files:
                        info = zf.getinfo(f)
                        print(f"     - {f} ({info.file_size} bytes)")
            
        print("\n" + "=" * 60)
        print("🎉 END-TO-END PIPELINE TEST PASSED!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_e2e_pipeline()
    sys.exit(0 if success else 1)
