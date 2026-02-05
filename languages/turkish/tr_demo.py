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

from languages.turkish import TurkishAnalyzer


def demonstrate_turkish_analyzer():
    """Demonstrate Turkish analyzer with sample sentences."""

    print("🇹🇷 Turkish Language Analyzer Demonstration")
    print("=" * 50)

    # Initialize analyzer
    try:
        analyzer = TurkishAnalyzer()
        print("✓ Turkish analyzer initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize analyzer: {e}")
        return

    # Validate setup
    validation = analyzer.validate_setup()
    if validation['overall_valid']:
        print("✓ Analyzer setup validation passed")
    else:
        print("✗ Setup validation failed:")
        for error in validation['config_errors'] + validation['infrastructure_errors']:
            print(f"  - {error}")
        return

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
                result = analyzer.analyze(sentence, complexity=complexity)

                if result.success and result.analysis:
                    # Show formatted result
                    formatted = analyzer.format_analysis_result(result, 'simple')
                    print(formatted)

                    # Show validation summary
                    if result.metadata and 'validation_summary' in result.metadata:
                        summary = result.metadata['validation_summary']
                        error_rate = summary.get('error_rate', 0)
                        if error_rate > 0:
                            print(f"⚠️  Validation issues: {summary.get('errors', 0)} errors")
                        else:
                            print("✓ Analysis validated successfully")

                else:
                    print(f"✗ Analysis failed: {result.error_message}")

            except Exception as e:
                print(f"✗ Error during analysis: {e}")

    # Show analyzer capabilities
    print("\n🔧 Analyzer Capabilities")
    print("-" * 30)
    print(f"Supported complexities: {analyzer.get_supported_complexities()}")
    print(f"Grammatical categories (beginner): {analyzer.get_grammatical_categories('beginner')}")
    print(f"Case markers: {analyzer.get_case_markers()}")
    print(f"Vowel harmony rules: Back={analyzer.get_vowel_harmony_rules()['back_vowels']}, Front={analyzer.get_vowel_harmony_rules()['front_vowels']}")
    print(f"Word order: {analyzer.get_word_order_info()}")


if __name__ == "__main__":
    demonstrate_turkish_analyzer()