#!/usr/bin/env python3
"""
Phase 11: Test improved batch processing
"""

import os
import sys
sys.path.append('.')

from hindi_failure_batching_qa import process_batch
from streamlit_app.language_analyzers.analyzers.hi_analyzer import HiAnalyzer

def test_improved_batch():
    """Test the improved batch processing with enhanced prompts"""
    test_words = ['आना', 'टका', 'होना', 'मैं', 'का']
    analyzer = HiAnalyzer()
    api_key = os.getenv('GROQ_API_KEY')

    print('🧪 PHASE 11: Testing Improved Batch Processing')
    print('=' * 50)
    print(f'Testing {len(test_words)} words: {test_words}')

    try:
        result = process_batch(test_words, analyzer, api_key, is_failure_batch=False)

        print(f'\n📊 Results:')
        print(f'  ✅ Successful: {result["success_count"]}/{result["total_count"]} ({result["success_rate"]:.1%})')
        print(f'  ❌ Failed: {result["fail_count"]}')

        if result['successful']:
            print('\n✅ Successful words:')
            for item in result['successful']:
                print(f'  - {item["word"]} → {item["grammatical_role"]} (confidence: {item["confidence_score"]})')

        if result['failed']:
            print('\n❌ Failed words:')
            for item in result['failed']:
                print(f'  - {item["word"]} → confidence: {item["confidence_score"]}')

        return result

    except Exception as e:
        print(f'❌ Error: {e}')
        return None

if __name__ == "__main__":
    test_improved_batch()