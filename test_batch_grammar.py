#!/usr/bin/env python3
"""
Test batch grammar processing with Hindi analyzer
"""

import sys
import os

# Add streamlit_app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'streamlit_app'))

from services.generation.grammar_processor import get_grammar_processor

# Test batch grammar processing with Hindi analyzer
processor = get_grammar_processor()

test_sentences = [
    'राम ने किताब पढ़ी।',
    'मैं खाना खाता हूं।',
    'वह स्कूल जाता है।'
]

target_words = ['राम', 'खाना', 'स्कूल']

print('Testing batch grammar analysis with Hindi analyzer...')
try:
    results = processor.batch_analyze_grammar_and_color(
        sentences=test_sentences,
        target_words=target_words,
        language='Hindi',
        groq_api_key='dummy_key',  # This will fail but we can check if the prompt generation works
        language_code='hi'
    )
    print('✅ Batch grammar analysis completed successfully!')
    for i, result in enumerate(results):
        colored = result.get("colored_sentence", "N/A")
        print(f'Sentence {i+1}: {colored[:100]}...')

except Exception as e:
    print(f'❌ Batch grammar analysis failed: {e}')
    import traceback
    traceback.print_exc()