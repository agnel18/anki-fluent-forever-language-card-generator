"""Test script for Streamlit app components"""
import sys
from pathlib import Path

# Test 1: YAML Configuration
print("=" * 60)
print("TEST 1: YAML Configuration")
print("=" * 60)

try:
    import yaml
    yaml_path = Path("languages.yaml")
    with open(yaml_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    assert "top_5" in config, "Missing top_5"
    assert "all_languages" in config, "Missing all_languages"
    assert "ui_strings" in config, "Missing ui_strings"
    
    top_5_count = len(config["top_5"])
    all_lang_count = len(config["all_languages"])
    ui_lang_count = len(config["ui_strings"])
    
    assert top_5_count == 5, f"Expected 5 top languages, got {top_5_count}"
    assert all_lang_count >= 50, f"Expected 50+ languages, got {all_lang_count}"
    
    top_5_langs = [lang["name"] for lang in config["top_5"]]
    ui_langs = list(config["ui_strings"].keys())
    
    print("✅ YAML Config Valid")
    print(f"   Top 5: {', '.join(top_5_langs)}")
    print(f"   Total Languages: {all_lang_count}")
    print(f"   UI Languages: {', '.join(ui_langs)}")
    
except Exception as e:
    print(f"❌ YAML Config Error: {e}")
    sys.exit(1)

# Test 2: Core Functions Import
print("\n" + "=" * 60)
print("TEST 2: Core Functions Import")
print("=" * 60)

try:
    from core_functions import (
        generate_sentences,
        generate_audio,
        generate_images_pixabay,
        create_anki_tsv,
        create_zip_export,
        estimate_api_costs,
        get_available_voices,
        parse_csv_upload,
    )
    print("✅ All core functions imported successfully")
    
except Exception as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)

# Test 3: API Cost Estimator
print("\n" + "=" * 60)
print("TEST 3: API Cost Estimator")
print("=" * 60)

try:
    costs = estimate_api_costs(num_words=5, num_sentences=10)
    
    assert "total_sentences" in costs
    assert "total_images" in costs
    assert "pixabay_requests" in costs
    assert "groq_tokens_est" in costs
    
    assert costs["total_sentences"] == 50
    assert costs["total_images"] == 50
    assert costs["pixabay_requests"] == 50
    
    print("✅ Cost Estimator Works")
    print(f"   5 words × 10 sentences = {costs['total_sentences']} total")
    print(f"   Pixabay requests: {costs['pixabay_requests']}")
    print(f"   Groq tokens (est.): {costs['groq_tokens_est']:,}")
    
except Exception as e:
    print(f"❌ Cost Estimator Error: {e}")
    sys.exit(1)

# Test 4: Voice Availability
print("\n" + "=" * 60)
print("TEST 4: Voice Availability")
print("=" * 60)

try:
    test_languages = ["en", "es", "fr", "zh", "ar", "hi"]
    
    for lang_code in test_languages:
        voices = get_available_voices(lang_code)
        assert len(voices) > 0, f"No voices for {lang_code}"
        print(f"✅ {lang_code.upper()}: {voices[0]}")
    
except Exception as e:
    print(f"❌ Voice Availability Error: {e}")
    sys.exit(1)

# Test 5: Streamlit Import
print("\n" + "=" * 60)
print("TEST 5: Streamlit Import")
print("=" * 60)

try:
    import streamlit as st
    print(f"✅ Streamlit imported (v{st.__version__})")
    
except Exception as e:
    print(f"❌ Streamlit Error: {e}")
    sys.exit(1)

# Summary
print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED")
print("=" * 60)
print("\nThe Streamlit app is ready to deploy!")
print("\nLocal run:")
print("  streamlit run app.py")
print("\nStreamlit Cloud:")
print("  1. Push to GitHub")
print("  2. Go to streamlit.io/cloud")
print("  3. Deploy from repo")
