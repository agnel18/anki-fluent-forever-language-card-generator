import os
import json
from languages.french.fr_analyzer import FrAnalyzer
from streamlit_app.sentence_generator import generate_word_meaning_sentences_and_keywords

# Set up API key
os.environ['GEMINI_API_KEY'] = 'AIzaSyBGe5U5f3Xy19w8OhV3XzcJa1lfYFHPUcE'
api_key = 'AIzaSyBGe5U5f3Xy19w8OhV3XzcJa1lfYFHPUcE'

print('=' * 80)
print('FRENCH LANGUAGE LEARNING - SENTENCE GENERATION & GRAMMAR ANALYSIS REPORT')
print('=' * 80)
print()

# Test words for French
test_words = ['manger', 'parler', 'écouter', 'comprendre']

for word in test_words:
    print(f'🔤 WORD: {word.upper()}')
    print('-' * 50)

    try:
        # Generate sentences for the word
        result = generate_word_meaning_sentences_and_keywords(
            word=word,
            language='French',
            num_sentences=3,
            difficulty='intermediate',
            gemini_api_key=api_key
        )

        print(f'📖 MEANING: {result.get("meaning", "N/A")}')
        print(f'⚠️  RESTRICTIONS: {result.get("restrictions", "N/A")}')
        print()

        # Analyze each generated sentence
        analyzer = FrAnalyzer()
        sentences = result.get('sentences', [])

        for i, sentence in enumerate(sentences, 1):
            print(f'📝 SENTENCE {i}: "{sentence}"')

            try:
                # Perform grammar analysis
                analysis = analyzer.analyze_grammar(
                    sentence=sentence,
                    target_word=word,
                    complexity='intermediate',
                    gemini_api_key=api_key
                )

                print(f'   ✅ CONFIDENCE: {analysis.confidence_score:.2f}')
                print(f'   🎨 HTML OUTPUT: {analysis.html_output}')
                print(f'   📊 GRAMMATICAL ELEMENTS: {len(analysis.grammatical_elements)} categories')

                # Show word explanations
                print(f'   🔍 WORD EXPLANATIONS ({len(analysis.word_explanations)}):')
                for j, exp in enumerate(analysis.word_explanations, 1):
                    word_text, category, color, explanation = exp
                    print(f'      {j}. "{word_text}" ({category}) - {explanation[:100]}...')

                # Show grammatical elements breakdown
                print(f'   📚 GRAMMAR BREAKDOWN:')
                for category, elements in analysis.grammatical_elements.items():
                    print(f'      • {category.upper()}: {len(elements)} elements')
                    for element in elements[:2]:  # Show first 2 elements
                        if isinstance(element, dict):
                            word = element.get('word', element.get('text', 'N/A'))
                            role = element.get('role', element.get('type', 'N/A'))
                            print(f'         - {word}: {role}')

            except Exception as e:
                print(f'   ❌ ANALYSIS ERROR: {e}')

            print()

        # Show keywords if available
        keywords = result.get('keywords', [])
        if keywords:
            print(f'🔑 KEYWORDS: {keywords}')

        print()
        print('=' * 80)
        print()

    except Exception as e:
        print(f'❌ GENERATION ERROR: {e}')
        print()
        continue