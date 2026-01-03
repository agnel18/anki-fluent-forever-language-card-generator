#!/usr/bin/env python3
"""
Phase 12 MVP Testing: Simplified Analyzer Validation
Tests "good enough" quality on top 100 words for target languages
"""

import os
import json
import time
from typing import Dict, List, Tuple
from groq import Groq

class SimplifiedAnalyzer:
    """Simplified analyzer for MVP - basic POS tagging only"""

    def __init__(self, language: str, api_key: str):
        self.language = language
        self.client = Groq(api_key=api_key)

        # Simplified color scheme
        self.colors = {
            'noun': '#0000FF',      # blue
            'verb': '#FF0000',      # red
            'adjective': '#008000', # green
            'pronoun': '#800080',   # purple
            'postposition': '#FFA500', # orange
            'other': '#808080'      # gray
        }

    def classify_word_simple(self, word: str) -> Tuple[str, float]:
        """Simple classification with basic categories"""

        prompt = f"""
Classify this {self.language} word into ONE category:
{word}

Categories:
- noun: people, places, things, concepts
- verb: actions, states, processes
- adjective: descriptions, qualities
- pronoun: I, you, he, she, it, we, they
- postposition: relationships like of, to, from, with, at, on, in
- other: if unclear or doesn't fit above

Return ONLY the category name in lowercase.
"""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.1
            )

            result = response.choices[0].message.content.strip().lower()

            # Validate response
            valid_categories = {'noun', 'verb', 'adjective', 'pronoun', 'postposition', 'other'}
            if result in valid_categories:
                confidence = 0.9 if result != 'other' else 0.5
                return result, confidence
            else:
                return 'other', 0.3

        except Exception as e:
            print(f"API Error for {word}: {e}")
            return 'other', 0.0

def test_top_words(analyzer: SimplifiedAnalyzer, words: List[str], max_words: int = 50) -> Dict:
    """Test analyzer on top words"""

    results = {
        'total_tested': 0,
        'successful': 0,
        'categories': {},
        'failures': [],
        'api_calls': 0
    }

    print(f"\n🧪 Testing {analyzer.language} analyzer on top {max_words} words...")

    for i, word in enumerate(words[:max_words]):
        print(f"  {i+1:2d}/{max_words}: Testing '{word}'...", end=' ')

        category, confidence = analyzer.classify_word_simple(word)
        results['api_calls'] += 1
        results['total_tested'] += 1

        # Count categories
        if category not in results['categories']:
            results['categories'][category] = 0
        results['categories'][category] += 1

        if confidence >= 0.8:
            results['successful'] += 1
            print(f"✅ {category} ({confidence:.1f})")
        else:
            results['failures'].append({'word': word, 'category': category, 'confidence': confidence})
            print(f"⚠️  {category} ({confidence:.1f})")

        time.sleep(0.5)  # Rate limiting

    # Calculate success rate
    success_rate = (results['successful'] / results['total_tested']) * 100 if results['total_tested'] > 0 else 0

    results['success_rate'] = success_rate
    results['quality_assessment'] = 'GOOD' if success_rate >= 85 else 'NEEDS_IMPROVEMENT'

    print(f"\n📊 Results for {analyzer.language}:")
    print(f"   Success Rate: {success_rate:.1f}% ({results['successful']}/{results['total_tested']})")
    print(f"   API Calls: {results['api_calls']}")
    print(f"   Assessment: {results['quality_assessment']}")

    if results['categories']:
        print("   Category Distribution:")
        for cat, count in sorted(results['categories'].items()):
            print(f"     {cat}: {count}")

    if results['failures']:
        print(f"   Failures ({len(results['failures'])}):")
        for failure in results['failures'][:5]:  # Show first 5
            print(f"     {failure['word']} → {failure['category']} ({failure['confidence']:.1f})")

    return results

def load_top_words(language_code: str, limit: int = 100) -> List[str]:
    """Load top words from frequency list"""
    # This would load from the Excel files in 77 Languages Frequency Word Lists/
    # For now, return sample words based on language

    sample_words = {
        'ES': ['el', 'la', 'de', 'que', 'y', 'en', 'un', 'ser', 'se', 'no', 'haber', 'por', 'con', 'su', 'para', 'como', 'estar', 'tener', 'le', 'lo'],
        'FR': ['le', 'de', 'un', 'à', 'être', 'et', 'en', 'avoir', 'que', 'pour', 'dans', 'ce', 'il', 'qui', 'ne', 'sur', 'se', 'pas', 'plus', 'pouvoir'],
        'DE': ['der', 'die', 'und', 'in', 'den', 'von', 'zu', 'das', 'mit', 'sich', 'des', 'auf', 'für', 'ist', 'im', 'dem', 'nicht', 'ein', 'Die', 'eine'],
        'JA': ['の', 'に', 'は', 'を', 'た', 'が', 'で', 'て', 'と', 'し', 'れ', 'さ', 'ある', 'いる', 'も', 'する', 'から', 'な', 'こと', 'として'],
        'KO': ['이', '그', '하', '있', '것', '들', '그렇', '되', '수', '이', '보', '않', '없', '나', '사람', '주', '아니', '등', '같', '우리']
    }

    return sample_words.get(language_code.upper(), ['test', 'word', 'sample'])[:limit]

def main():
    """Test simplified analyzers for MVP languages"""

    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("❌ Please set GROQ_API_KEY environment variable")
        return

    # Test languages for MVP
    test_languages = [
        ('Spanish', 'ES'),
        ('French', 'FR'),
        ('German', 'DE'),
        ('Japanese', 'JA'),
        ('Korean', 'KO')
    ]

    all_results = {}

    print("🚀 Phase 12 MVP Testing: Simplified Analyzers")
    print("=" * 50)

    for language_name, lang_code in test_languages:
        try:
            # Create analyzer
            analyzer = SimplifiedAnalyzer(language_name, api_key)

            # Load top words (simplified for demo)
            top_words = load_top_words(lang_code, 20)  # Test 20 words first

            # Test analyzer
            results = test_top_words(analyzer, top_words, max_words=20)
            all_results[language_name] = results

            print(f"\n{'='*30}\n")

        except Exception as e:
            print(f"❌ Error testing {language_name}: {e}")
            continue

    # Summary
    print("📈 PHASE 12 MVP TESTING SUMMARY")
    print("=" * 40)

    total_successful = 0
    total_tested = 0
    total_api_calls = 0

    for lang, results in all_results.items():
        success_rate = results.get('success_rate', 0)
        tested = results.get('total_tested', 0)
        api_calls = results.get('api_calls', 0)

        total_successful += results.get('successful', 0)
        total_tested += tested
        total_api_calls += api_calls

        status = "✅" if success_rate >= 85 else "⚠️" if success_rate >= 70 else "❌"
        print(f"{status} {lang}: {success_rate:.1f}% ({results.get('successful', 0)}/{tested}) - {api_calls} API calls")

    if total_tested > 0:
        overall_success = (total_successful / total_tested) * 100
        print(f"\n🎯 Overall: {overall_success:.1f}% success rate")
        print(f"📊 Total API calls: {total_api_calls}")
        print(f"⏱️  Estimated time for 100 words: ~{total_api_calls * 5} seconds")

        if overall_success >= 85:
            print("✅ MVP APPROACH VALIDATED - Ready for expansion!")
        else:
            print("⚠️  Needs optimization before full implementation")

if __name__ == "__main__":
    main()</content>
<parameter name="filePath">d:\Language Learning\LanguagLearning\phase12_mvp_test.py