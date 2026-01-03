#!/usr/bin/env python3
"""Test script for Phase 5.5: Guaranteed Color Consistency Architecture"""

from streamlit_app.language_analyzers.family_base_analyzers.indo_european_analyzer import IndoEuropeanAnalyzer
from streamlit_app.language_analyzers.base_analyzer import LanguageConfig

def test_color_extraction():
    """Test the color extraction method"""
    config = LanguageConfig(
        code='hi',
        name='Hindi',
        native_name='हिंदी',
        family='Indo-European',
        script_type='abugida',
        complexity_rating='medium',
        key_features=['postpositions', 'gender_agreement', 'case_marking', 'verb_conjugation', 'aspect_tense', 'honorifics'],
        supported_complexity_levels=['beginner', 'intermediate', 'advanced']
    )

    analyzer = IndoEuropeanAnalyzer(config)

    # Test HTML with colored words
    test_html = '<div class="word-explanations"><strong>Grammar Explanations:</strong><br><div class="explanation-item"><span class="word-highlight" style="color: #FF4444;"><strong>मैं</strong></span> (pronoun): I (first person singular pronoun)</div><div class="explanation-item"><span class="word-highlight" style="color: #44FF44;"><strong>खाना</strong></span> (noun): food/meal</div></div>'

    colors = analyzer._extract_colors_from_grammar_explanations(test_html)
    print('Extracted colors:', colors)

    # Expected: {'मैं': '#FF4444', 'खाना': '#44FF44'}
    expected = {'मैं': '#FF4444', 'खाना': '#44FF44'}
    if colors == expected:
        print('✅ Color extraction test PASSED')
    else:
        print('❌ Color extraction test FAILED')
        print(f'Expected: {expected}')
        print(f'Got: {colors}')

def test_html_generation():
    """Test HTML generation with guaranteed color consistency"""
    config = LanguageConfig(
        code='hi',
        name='Hindi',
        native_name='हिंदी',
        family='Indo-European',
        script_type='abugida',
        complexity_rating='medium',
        key_features=['postpositions', 'gender_agreement', 'case_marking', 'verb_conjugation', 'aspect_tense', 'honorifics'],
        supported_complexity_levels=['beginner', 'intermediate', 'advanced']
    )

    analyzer = IndoEuropeanAnalyzer(config)

    # Mock parsed data with word_explanations (authoritative color source)
    parsed_data = {
        'word_explanations': [
            ['मैं', 'pronoun', '#FF4444', 'I (first person singular pronoun)'],
            ['खाना', 'noun', '#44FF44', 'food/meal'],
            ['खाता', 'verb', '#FFAA00', 'eat (masculine)']
        ],
        'sentence': 'मैं खाना खाता हूँ'
    }

    html_output = analyzer._generate_html_output(parsed_data, parsed_data['sentence'], 'beginner')
    print('Generated HTML:', html_output)

    # Check that colors from word_explanations are used
    if '#FF4444' in html_output and '#44FF44' in html_output and '#FFAA00' in html_output:
        print('✅ HTML generation test PASSED - Colors from word_explanations used')
    else:
        print('❌ HTML generation test FAILED - Colors not properly applied')

if __name__ == '__main__':
    print('Testing Phase 5.5: Guaranteed Color Consistency Architecture')
    print('=' * 60)

    test_color_extraction()
    print()
    test_html_generation()

    print()
    print('Phase 5.5 testing complete!')