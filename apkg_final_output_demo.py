import os
import json
from languages.french.fr_analyzer import FrAnalyzer
from streamlit_app.sentence_generator import generate_word_meaning_sentences_and_keywords

# Set up API key
os.environ['GEMINI_API_KEY'] = 'AIzaSyBGe5U5f3Xy19w8OhV3XzcJa1lfYFHPUcE'
api_key = 'AIzaSyBGe5U5f3Xy19w8OhV3XzcJa1lfYFHPUcE'

print('=' * 100)
print('FINAL APKG OUTPUT FORMAT - FRENCH LANGUAGE LEARNING CARDS')
print('=' * 100)
print()

# Generate content for a French word
word = 'manger'
print(f'🎯 GENERATING APKG CONTENT FOR WORD: {word.upper()}')
print('-' * 60)

try:
    # Generate sentences and content
    result = generate_word_meaning_sentences_and_keywords(
        word=word,
        language='French',
        num_sentences=2,
        difficulty='intermediate',
        gemini_api_key=api_key
    )

    # Analyze grammar for each sentence
    analyzer = FrAnalyzer()
    sentences = result.get('sentences', [])

    print(f'📖 WORD MEANING: {result.get("meaning", "N/A")}')
    print(f'⚠️  GRAMMATICAL RESTRICTIONS: {result.get("restrictions", "N/A")}')
    print()

    # Show final APKG card format for each sentence
    for i, sentence in enumerate(sentences[:2], 1):  # Show first 2 sentences
        print(f'🃏 CARD {i} - FINAL APKG FORMAT')
        print('=' * 40)

        # Perform grammar analysis
        analysis = analyzer.analyze_grammar(
            sentence=sentence,
            target_word=word,
            complexity='intermediate',
            gemini_api_key=api_key
        )

        # Format word explanations as HTML (exactly as it appears in APKG)
        word_explanations_html = ""
        explanations = analysis.word_explanations
        if explanations and len(explanations) > 0:
            explanation_items = []
            for exp in explanations:
                if len(exp) >= 4:
                    exp_word, pos, color, explanation = exp[0], exp[1], exp[2], exp[3]
                    explanation_items.append(f'<div class="explanation-item"><span class="word-highlight" style="color: {color};"><strong>{exp_word}</strong></span> ({pos}): {explanation}</div>')
            if explanation_items:
                word_explanations_html = '<div class="word-explanations"><strong>Grammar Explanations:</strong><br>' + ''.join(explanation_items) + '</div>'

        # Create the final APKG card data structure
        card_data = {
            "file_name": f"{word}_{i:02d}",
            "word": word,
            "meaning": result.get("meaning", ""),
            "sentence": sentence,
            "ipa": "",  # Would contain IPA transliteration
            "english": "",  # Would contain English translation
            "audio": "[sound:manger_01.mp3]",  # Would contain actual audio file reference
            "image": '<img src="manger_01.jpg">',  # Would contain actual image file reference
            "image_keywords": result.get("keywords", [""])[i-1] if i-1 < len(result.get("keywords", [])) else "",
            "colored_sentence": analysis.html_output,
            "word_explanations": word_explanations_html,
            "grammar_summary": f"Sentence structure analysis for '{word}' in French",
            "tags": ""
        }

        print('📋 FINAL APKG CARD FIELDS:')
        print(f'   File Name: {card_data["file_name"]}')
        print(f'   What is the Word?: {card_data["word"]}')
        print(f'   Meaning of the Word: {card_data["meaning"]}')
        print(f'   Sentence: {card_data["sentence"]}')
        print(f'   IPA Transliteration: {card_data["ipa"]}')
        print(f'   English Translation: {card_data["english"]}')
        print(f'   Sound: {card_data["audio"]}')
        print(f'   Image: {card_data["image"]}')
        print(f'   Image Keywords: {card_data["image_keywords"]}')
        print(f'   Colored Sentence: {card_data["colored_sentence"][:100]}...')
        print(f'   Word Explanations: {card_data["word_explanations"][:100]}...')
        print(f'   Grammar Summary: {card_data["grammar_summary"]}')
        print(f'   Tags: {card_data["tags"]}')
        print()

        print('🎴 ANKI CARD TEMPLATES (What users see):')
        print()

        # Card 1: Listening
        print('   🗣️  CARD 1 - LISTENING:')
        print('   Front: 🎧 Listen and understand')
        print('           [Audio playback button]')
        print('   Back:  [Colored sentence with grammar highlighting]')
        print('           [Image]')
        print('           [English translation]')
        print('           Word: manger (to eat/consume food)')
        print('           [IPA pronunciation]')
        print('           [Detailed grammar explanations for each word]')
        print('           [Grammar summary]')
        print('           Keywords: [image keywords]')
        print()

        # Card 2: Production
        print('   ✍️  CARD 2 - PRODUCTION:')
        print('   Front: 💬 Say this in French:')
        print('           [English translation prompt]')
        print('   Back:  [Colored sentence with grammar highlighting]')
        print('           [Audio playback]')
        print('           [Image]')
        print('           [IPA pronunciation]')
        print('           Word: manger (to eat/consume food)')
        print('           [Detailed grammar explanations for each word]')
        print('           [Grammar summary]')
        print('           Keywords: [image keywords]')
        print()

        # Card 3: Reading
        print('   📖 CARD 3 - READING:')
        print('   Front: 📖 Read and understand:')
        print('           [Colored sentence with grammar highlighting]')
        print('   Back:  [Audio playback]')
        print('           [Image]')
        print('           [English translation]')
        print('           [IPA pronunciation]')
        print('           Word: manger (to eat/consume food)')
        print('           [Detailed grammar explanations for each word]')
        print('           [Grammar summary]')
        print('           Keywords: [image keywords]')
        print()

        print('=' * 100)
        print()

except Exception as e:
    print(f'❌ ERROR: {e}')
    print()
    print('📝 SAMPLE FALLBACK FORMAT (when API fails):')
    print()

    fallback_card = {
        "file_name": f"{word}_01",
        "word": word,
        "meaning": word,
        "sentence": f"This is a sample sentence with {word}.",
        "ipa": "",
        "english": f"This is a sample sentence with {word}.",
        "audio": "",
        "image": "",
        "image_keywords": f"{word}, language, learning",
        "colored_sentence": f"This is a sample sentence with <span style='color: #FF6B6B'>{word}</span>.",
        "word_explanations": '<div class="word-explanations"><strong>Grammar Explanations:</strong><br><div class="explanation-item"><span class="word-highlight" style="color: #FF6B6B;"><strong>manger</strong></span> (noun): Target word: manger</div></div>',
        "grammar_summary": "Basic sentence structure in French",
        "tags": ""
    }

    print('📋 FALLBACK APKG CARD FIELDS:')
    for key, value in fallback_card.items():
        print(f'   {key}: {str(value)[:80]}{"..." if len(str(value)) > 80 else ""}')