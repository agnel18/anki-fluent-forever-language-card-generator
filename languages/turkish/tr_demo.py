"""
Turkish Analyzer Demonstration
=============================

Demonstrates the Turkish language analyzer with sample sentences.
Shows morphological analysis, vowel harmony, and case system handling.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from languages.turkish import TrAnalyzer


def demonstrate_turkish_analyzer():
    """Demonstrate Turkish analyzer with sample sentences."""

    print("🇹🇷 Turkish Language Analyzer Demonstration")
    print("=" * 50)

    # Initialize analyzer
    try:
        analyzer = TrAnalyzer()
        print("✓ Turkish analyzer initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize analyzer: {e}")
        return

    api_key = None
    try:
        import os
        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
    except Exception:
        api_key = None

    # Sample sentences for different complexity levels
    samples = {
        'beginner': [
            "Merhaba dünya!",
            "Ben kitap okuyorum.",
            "Ali eve gitti."
        ],
        'intermediate': [
            "Kitabı Ali'ye verdim.",
            "Evimde yemek yiyorum.",
            "Annemin mektubunu okudum."
        ],
        'advanced': [
            "Annemin gönderdiği mektupları okuyordum.",
            "Yarın gideceğimiz yer hazır mı?",
            "Arkadaşımın bana verdiği kitabı okuyorum."
        ]
    }

    # Demonstrate analysis for each complexity level
    for complexity, sentences in samples.items():
        print(f"\n📚 {complexity.title()} Level Analysis")
        print("-" * 30)

        for sentence in sentences:
            print(f"\nSentence: {sentence}")
            try:
                if not api_key:
                    print("⚠️  GEMINI_API_KEY not set; skipping analysis")
                    continue

                target_word = sentence.split()[0] if sentence.split() else ""
                result = analyzer.analyze_grammar(sentence, target_word, complexity, api_key)

                if result and getattr(result, 'word_explanations', None):
                    print(f"✓ Word explanations: {len(result.word_explanations)}")
                else:
                    print("✗ Analysis returned no word explanations")

            except Exception as e:
                print(f"✗ Error during analysis: {e}")

    # Show analyzer capabilities
    print("\n🔧 Analyzer Capabilities")
    print("-" * 30)
    print(f"Supported complexities: {analyzer.config.supported_complexity_levels}")


if __name__ == "__main__":
    demonstrate_turkish_analyzer()