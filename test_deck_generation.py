#!/usr/bin/env python3
"""
Test script to verify deck generation works with refactored code
"""
import sys
import os
sys.path.append('streamlit_app')

from core_functions import generate_complete_deck

def test_deck_generation():
    """Test deck generation with new refactored code"""
    # Test deck generation with a small set
    test_words = ['hello', 'world', 'test']
    language = 'English'
    groq_key = os.getenv('GROQ_API_KEY', 'test_key')
    pixabay_key = os.getenv('PIXABAY_API_KEY', 'test_key')

    print('Testing deck generation with new refactored code...')
    print(f'Words: {test_words}')
    print(f'Language: {language}')
    print(f'API Keys: Groq={"SET" if groq_key != "test_key" else "NOT SET"}, Pixabay={"SET" if pixabay_key != "test_key" else "NOT SET"}')

    result = generate_complete_deck(
        words=test_words,
        language=language,
        groq_api_key=groq_key,
        pixabay_api_key=pixabay_key,
        output_dir='test_output',
        num_sentences=2,  # Small number for quick test
        progress_callback=lambda p, m, s: print(f'{p:.1%}: {m}'),
    )

    print(f'\nDeck generation result: {result}')

    if result.get('success'):
        print('✅ Deck generation successful!')
        output_dir = result.get('output_dir')
        print(f'Output directory: {output_dir}')

        tsv_path = result.get('tsv_path')
        if tsv_path and os.path.exists(tsv_path):
            print(f'✅ TSV file created: {tsv_path}')

            # Check file size and content
            file_size = os.path.getsize(tsv_path)
            print(f'File size: {file_size} bytes')

            # Read first few lines to verify content
            with open(tsv_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:5]  # First 5 lines
                print(f'First {len(lines)} lines of TSV:')
                for i, line in enumerate(lines, 1):
                    print(f'  {i}: {line.strip()[:100]}...' if len(line) > 100 else f'  {i}: {line.strip()}')

        else:
            print('❌ TSV file not found')

        media_dir = result.get('media_dir')
        if media_dir and os.path.exists(media_dir):
            media_files = os.listdir(media_dir)
            print(f'✅ Media directory created with {len(media_files)} files')
        else:
            print('❌ Media directory not found')

    else:
        print(f'❌ Deck generation failed: {result.get("error")}')

    return result

if __name__ == '__main__':
    test_deck_generation()