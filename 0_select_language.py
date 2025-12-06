#!/usr/bin/env python3
"""
Language Selection Setup Script
Allows users to choose their target language from 109 supported languages
"""

import os
import pandas as pd
from pathlib import Path

def get_available_languages():
    """Get list of all available language frequency word lists"""
    languages_dir = Path(__file__).parent / "109 Languages Frequency Word Lists"
    
    if not languages_dir.exists():
        print("❌ Error: '109 Languages Frequency Word Lists' folder not found!")
        return []
    
    # Get all .xlsx files except temporary ones
    language_files = sorted([f for f in languages_dir.glob("*.xlsx") if not f.name.startswith("~")])
    
    return language_files

def parse_language_name(filename):
    """Extract language name and code from filename"""
    # Format: "Language Name (CODE).xlsx"
    name = filename.stem  # Remove .xlsx
    if "(" in name and ")" in name:
        lang_name = name[:name.rfind("(")].strip()
        lang_code = name[name.rfind("(")+1:name.rfind(")")].strip()
        return lang_name, lang_code
    return name, None

def select_language():
    """Interactive language selection"""
    languages = get_available_languages()
    
    if not languages:
        print("❌ No language files found!")
        return None
    
    print("\n" + "="*60)
    print("🌍 FLUENT FOREVER - LANGUAGE SELECTION")
    print("="*60)
    print(f"\n✅ Found {len(languages)} languages available\n")
    
    # Display languages in columns
    for i, lang_file in enumerate(languages, 1):
        lang_name, lang_code = parse_language_name(lang_file)
        print(f"{i:3d}. {lang_name:30s} ({lang_code})")
        
        # Add spacing every 30 languages
        if i % 30 == 0:
            print()
    
    print("\n" + "-"*60)
    while True:
        try:
            choice = input(f"\nEnter language number (1-{len(languages)}): ").strip()
            choice_idx = int(choice) - 1
            
            if 0 <= choice_idx < len(languages):
                selected_file = languages[choice_idx]
                lang_name, lang_code = parse_language_name(selected_file)
                print(f"\n✅ Selected: {lang_name} ({lang_code})")
                return selected_file, lang_name, lang_code
            else:
                print(f"❌ Please enter a number between 1 and {len(languages)}")
        except ValueError:
            print("❌ Invalid input. Please enter a number.")

def create_language_config(lang_file, lang_name, lang_code):
    """Create configuration for selected language"""
    config_file = Path(__file__).parent / "language_config.txt"
    
    config = {
        "language_name": lang_name,
        "language_code": lang_code,
        "frequency_file": str(lang_file),
        "output_dir": f"FluentForever_{lang_name.replace(' ', '_')}_Perfect",
    }
    
    # Write config
    with open(config_file, "w", encoding="utf-8") as f:
        for key, value in config.items():
            f.write(f"{key}={value}\n")
    
    print(f"\n✅ Configuration saved to: language_config.txt")
    return config

def main():
    print("\nInitializing Fluent Forever Language Card Generator...\n")
    
    # Select language
    result = select_language()
    if not result:
        print("\n❌ Language selection cancelled.")
        return
    
    lang_file, lang_name, lang_code = result
    
    # Verify frequency file
    print(f"\n📊 Loading frequency word list...")
    try:
        df = pd.read_excel(lang_file)
        print(f"✅ Loaded {len(df)} words from {lang_name} frequency list")
        print(f"   Columns: {list(df.columns)}")
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return
    
    # Create configuration
    config = create_language_config(lang_file, lang_name, lang_code)
    
    print("\n" + "="*60)
    print("📝 CONFIGURATION SUMMARY")
    print("="*60)
    print(f"Language:      {config['language_name']}")
    print(f"Language Code: {config['language_code']}")
    print(f"Frequency File: {config['frequency_file']}")
    print(f"Output Dir:    {config['output_dir']}")
    print("="*60)
    
    print("\n✅ Setup complete! You can now run the scripts:")
    print("   1. python 1_generate_sentences.py")
    print("   2. python 2_download_audio.py")
    print("   3. python 3_download_images.py")
    print("   4. python 4_create_anki_tsv.py")
    print()

if __name__ == "__main__":
    main()
