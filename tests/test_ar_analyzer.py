#!/usr/bin/env python3
"""
Test suite for Arabic Grammar Analyzer (ar_analyzer.py)

This test suite validates the Arabic analyzer's ability to correctly identify
grammatical roles, handle root-based morphology, case markings (iʿrāb),
definite article assimilation, and Arabic-specific linguistic features.
"""

import pytest
import json
from unittest.mock import Mock, patch

from streamlit_app.language_analyzers.analyzers.ar_analyzer import ArAnalyzer


class TestArAnalyzer:
    """Test cases for Arabic grammar analyzer"""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance for testing"""
        return ArAnalyzer()

    def test_initialization(self, analyzer):
        """Test analyzer initialization"""
        assert analyzer.language_code == "ar"
        assert analyzer.language_name == "Arabic"
        assert analyzer.version == "1.0"
        assert hasattr(analyzer, '_initialize_patterns')

    def test_grammatical_roles_structure(self, analyzer):
        """Test grammatical roles are properly defined"""
        roles = analyzer.GRAMMATICAL_ROLES

        # Check all complexity levels exist
        assert 'beginner' in roles
        assert 'intermediate' in roles
        assert 'advanced' in roles

        # Check beginner has basic roles
        beginner_roles = roles['beginner']
        assert 'noun' in beginner_roles
        assert 'verb' in beginner_roles
        assert 'particle' in beginner_roles

        # Check intermediate has more specific roles
        intermediate_roles = roles['intermediate']
        assert 'preposition' in intermediate_roles
        assert 'conjunction' in intermediate_roles
        assert 'definite_article' in intermediate_roles

        # Check advanced has most specific roles
        advanced_roles = roles['advanced']
        assert 'nominative' in advanced_roles
        assert 'accusative' in advanced_roles
        assert 'genitive' in advanced_roles
        assert 'perfect_verb' in advanced_roles

    def test_pattern_initialization(self, analyzer):
        """Test that patterns are properly initialized"""
        # Check case endings
        assert hasattr(analyzer, 'case_endings')
        assert 'nominative' in analyzer.case_endings
        assert 'accusative' in analyzer.case_endings
        assert 'genitive' in analyzer.case_endings

        # Check definite article patterns
        assert hasattr(analyzer, 'definite_article_patterns')
        assert 'original' in analyzer.definite_article_patterns
        assert 'assimilated_ta' in analyzer.definite_article_patterns

        # Check particle patterns
        assert hasattr(analyzer, 'particle_patterns')
        assert 'prepositions' in analyzer.particle_patterns
        assert 'conjunctions' in analyzer.particle_patterns

        # Check verb form patterns
        assert hasattr(analyzer, 'verb_form_patterns')
        assert 'form1_perfect' in analyzer.verb_form_patterns
        assert 'form2' in analyzer.verb_form_patterns

    def test_color_scheme_beginner(self, analyzer):
        """Test color scheme for beginner level"""
        colors = analyzer.get_color_scheme("beginner")

        assert colors['nouns'] == "#FFAA00"  # Orange
        assert colors['verbs'] == "#44FF44"  # Green
        assert colors['particles'] == "#FF4444"  # Red

    def test_color_scheme_intermediate(self, analyzer):
        """Test color scheme for intermediate level"""
        colors = analyzer.get_color_scheme("intermediate")

        assert 'adjectives' in colors
        assert 'articles' in colors
        assert 'pronouns' in colors
        assert colors['articles'] == "#FFD700"  # Gold

    def test_color_scheme_advanced(self, analyzer):
        """Test color scheme for advanced level"""
        colors = analyzer.get_color_scheme("advanced")

        assert 'cases' in colors
        assert 'participles' in colors
        assert colors['cases'] == "#228B22"  # Forest Green

    def test_map_grammatical_role_to_category(self, analyzer):
        """Test role mapping function"""
        # Test basic mappings
        assert analyzer._map_grammatical_role_to_category("noun") == "nouns"
        assert analyzer._map_grammatical_role_to_category("verb") == "verbs"
        assert analyzer._map_grammatical_role_to_category("preposition") == "particles"
        assert analyzer._map_grammatical_role_to_category("definite_article") == "articles"

        # Test case markings
        assert analyzer._map_grammatical_role_to_category("nominative") == "cases"
        assert analyzer._map_grammatical_role_to_category("accusative") == "cases"
        assert analyzer._map_grammatical_role_to_category("genitive") == "cases"

        # Test verb types
        assert analyzer._map_grammatical_role_to_category("perfect_verb") == "verbs"
        assert analyzer._map_grammatical_role_to_category("imperfect_verb") == "verbs"

    def test_validate_analysis_high_confidence(self, analyzer):
        """Test validation with high confidence analysis"""
        parsed_data = {
            'elements': {
                'nouns': [{'word': 'الكتاب'}],
                'verbs': [{'word': 'يقرأ'}],
                'particles': [{'word': 'في'}]
            },
            'explanations': {
                'sentence_structure': 'VSO with prepositional phrase',
                'complexity_notes': 'Present tense reading description'
            },
            'word_explanations': [
                ['الكتاب', 'noun', '#FFAA00', 'the book'],
                ['يقرأ', 'verb', '#44FF44', 'reads/is reading'],
                ['في', 'particle', '#FF4444', 'in']
            ]
        }

        sentence = "يقرأ الكتاب في الصف"
        confidence = analyzer.validate_analysis(parsed_data, sentence)

        # Should be high confidence due to complete analysis
        assert confidence >= 0.6

    def test_validate_analysis_low_confidence(self, analyzer):
        """Test validation with incomplete analysis"""
        parsed_data = {
            'elements': {},
            'explanations': {},
            'word_explanations': []
        }

        sentence = "الطالب يقرأ الكتاب"
        confidence = analyzer.validate_analysis(parsed_data, sentence)

        # Should be lower confidence due to missing elements
        assert confidence < 0.85

    def test_arabic_script_validation(self, analyzer):
        """Test Arabic script validation"""
        # Test with Arabic text
        arabic_sentence = "الطالب يقرأ الكتاب"
        confidence = analyzer.validate_analysis({
            'word_explanations': [['الطالب', 'noun', '#FFAA00', 'the student']]
        }, arabic_sentence)

        # Should get Arabic script bonus
        assert confidence > 0.5

    def test_reorder_explanations_for_rtl(self, analyzer):
        """Test RTL reordering of explanations"""
        word_explanations = [
            ['الكتاب', 'noun', '#FFAA00', 'the book'],
            ['يقرأ', 'verb', '#44FF44', 'reads'],
            ['الطالب', 'noun', '#FFAA00', 'the student']
        ]

        sentence = "الطالب يقرأ الكتاب"
        reordered = analyzer._reorder_explanations_for_rtl(sentence, word_explanations)

        # Should be reversed for RTL: الكتاب, يقرأ, الطالب
        expected_order = ['الطالب', 'يقرأ', 'الكتاب']
        actual_order = [exp[0] for exp in reordered]
        assert actual_order == expected_order

    def test_get_grammar_prompt_beginner(self, analyzer):
        """Test beginner level prompt generation"""
        sentence = "الطالب يقرأ"
        target_word = "يقرأ"
        prompt = analyzer.get_grammar_prompt("beginner", sentence, target_word)

        assert "الطالب يقرأ" in prompt
        assert "يقرأ" in prompt
        assert "right to left" in prompt
        assert "RTL order" in prompt
        assert "noun" in prompt
        assert "verb" in prompt

    def test_get_grammar_prompt_intermediate(self, analyzer):
        """Test intermediate level prompt generation"""
        sentence = "أقرأ الكتاب في المكتبة"
        target_word = "أقرأ"
        prompt = analyzer.get_grammar_prompt("intermediate", sentence, target_word)

        assert "أقرأ الكتاب في المكتبة" in prompt
        assert "أقرأ" in prompt
        assert "Definite article" in prompt
        assert "preposition" in prompt

    def test_get_grammar_prompt_advanced(self, analyzer):
        """Test advanced level prompt generation"""
        sentence = "كتبَ الطالبُ الكتابَ"
        target_word = "كتب"
        prompt = analyzer.get_grammar_prompt("advanced", sentence, target_word)

        assert "كتبَ الطالبُ الكتابَ" in prompt
        assert "كتب" in prompt
        assert "Case markings" in prompt
        assert "iʿrāb" in prompt

    def test_batch_prompt_generation(self, analyzer):
        """Test batch prompt generation"""
        sentences = [
            "الطالب يقرأ",
            "المعلم يكتب",
            "الكتاب مفيد"
        ]
        target_word = "يقرأ"
        prompt = analyzer.get_batch_grammar_prompt("intermediate", sentences, target_word)

        assert "الطالب يقرأ" in prompt
        assert "المعلم يكتب" in prompt
        assert "الكتاب مفيد" in prompt
        assert "يقرأ" in prompt
        assert "Arabic" in prompt

    def test_prompt_language_parameter(self, analyzer):
        """Test prompt generation with different native languages"""
        sentence = "الطالب يقرأ"
        target_word = "يقرأ"

        # Test English
        prompt_en = analyzer.get_grammar_prompt("beginner", sentence, target_word, "English")
        assert "English" in prompt_en

        # Test Arabic
        prompt_ar = analyzer.get_grammar_prompt("beginner", sentence, target_word, "Arabic")
        assert "Arabic" in prompt_ar

    # Tricky Arabic words test data
    TRICKY_WORDS_AR = [
        {
            "word": "كان",
            "conjugated_form": "كان",
            "test_sentence": "كان الطالب مجتهداً",
            "complexity": "intermediate",
            "expected_challenges": ["past_tense_verb", "sentence_word_order"]
        },
        {
            "word": "في",
            "conjugated_form": "في",
            "test_sentence": "الكتاب في الدرج",
            "complexity": "intermediate",
            "expected_challenges": ["preposition_usage", "definite_article"]
        },
        {
            "word": "ما",
            "conjugated_form": "ما",
            "test_sentence": "ما قرأت الكتاب",
            "complexity": "intermediate",
            "expected_challenges": ["negation_particle", "verb_negation"]
        },
        {
            "word": "من",
            "conjugated_form": "من",
            "test_sentence": "جاء الطالب من المدرسة",
            "complexity": "intermediate",
            "expected_challenges": ["preposition_from", "motion_verbs"]
        },
        {
            "word": "إلى",
            "conjugated_form": "إلى",
            "test_sentence": "ذهب الطالب إلى المدرسة",
            "complexity": "intermediate",
            "expected_challenges": ["preposition_to", "direction_indication"]
        },
        {
            "word": "أن",
            "conjugated_form": "أن",
            "test_sentence": "أريد أن أقرأ",
            "complexity": "advanced",
            "expected_challenges": ["subjunctive_particle", "complement_clause"]
        },
        {
            "word": "كتب",
            "conjugated_form": "كتبَ",
            "test_sentence": "كتبَ الطالبُ الكتابَ",
            "complexity": "advanced",
            "expected_challenges": ["case_markings", "past_tense_perfect"]
        },
        {
            "word": "الكتاب",
            "conjugated_form": "الكتاب",
            "test_sentence": "قرأت الكتاب أمس",
            "complexity": "intermediate",
            "expected_challenges": ["definite_article", "noun_with_article"]
        },
        {
            "word": "يكتب",
            "conjugated_form": "يكتب",
            "test_sentence": "الطالب يكتب الدرس",
            "complexity": "intermediate",
            "expected_challenges": ["imperfect_verb", "present_continuous"]
        },
        {
            "word": "كاتب",
            "conjugated_form": "كاتب",
            "test_sentence": "الكاتب مشهور",
            "complexity": "advanced",
            "expected_challenges": ["active_participle", "root_based_formation"]
        }
    ]

    @pytest.mark.parametrize("word_data", TRICKY_WORDS_AR)
    def test_tricky_arabic_words_basic(self, analyzer, word_data):
        """Test basic functionality with tricky Arabic words"""
        sentence = word_data["test_sentence"]
        target_word = word_data["conjugated_form"]
        complexity = word_data["complexity"]

        # Mock AI response for testing
        mock_response = {
            "words": [
                {
                    "word": target_word,
                    "individual_meaning": f"translation of {target_word}",
                    "grammatical_role": "verb" if "verb" in word_data["expected_challenges"][0] else "particle"
                }
            ]
        }

        with patch.object(analyzer, '_call_ai_model', return_value=json.dumps(mock_response)):
            result = analyzer.analyze_grammar(sentence, target_word, complexity, "fake_key")

            assert result.target_word == target_word
            assert result.language_code == "ar"
            assert result.complexity_level == complexity
            assert len(result.grammatical_elements) > 0

    @pytest.mark.parametrize("word_data", TRICKY_WORDS_AR)
    def test_tricky_arabic_words_parsing_simulation(self, analyzer, word_data):
        """Test parsing simulation with tricky Arabic words using mock AI responses"""
        sentence = word_data["test_sentence"]
        target_word = word_data["conjugated_form"]
        complexity = word_data["complexity"]

        # Create mock AI response that simulates real parsing
        mock_words = []
        for word in sentence.split():
            # Determine grammatical role based on Arabic patterns
            if word.startswith("ال"):
                role = "noun"  # Definite article + noun
            elif word.startswith("ي") and len(word) > 3:
                role = "verb"  # Imperfect verb prefix
            elif word in ["كان", "كانت", "كانوا", "كانت", "كنا", "كنتم", "كنتن", "كانوا"]:  # Past tense verb
                role = "verb"
            elif word in ["في", "من", "إلى", "على", "مع"]:
                role = "preposition"
            elif word in ["و", "ف", "أو"]:
                role = "conjunction"
            elif word in ["ما", "لا", "لم", "لن"]:
                role = "negation"
            else:
                role = "noun"  # Default

            mock_words.append({
                "word": word,
                "individual_meaning": f"meaning of {word}",
                "grammatical_role": role
            })

        mock_response = {"words": mock_words}

        with patch.object(analyzer, '_call_ai_model', return_value=json.dumps(mock_response)):
            result = analyzer.analyze_grammar(sentence, target_word, complexity, "fake_key")

            # Verify the analysis completed successfully
            assert result.target_word == target_word
            assert result.language_code == "ar"
            assert len(result.grammatical_elements) > 0
            # Check that at least one element contains words
            has_words = any(len(word_list) > 0 for word_list in result.grammatical_elements.values())
            assert has_words, "No words found in grammatical elements"

    def test_parse_grammar_response_json(self, analyzer):
        """Test parsing JSON response"""
        ai_response = '''```json
{
  "words": [
    {
      "word": "الكتاب",
      "individual_meaning": "the book",
      "grammatical_role": "noun"
    },
    {
      "word": "يقرأ",
      "individual_meaning": "reads",
      "grammatical_role": "verb"
    }
  ]
}
```'''

        sentence = "يقرأ الكتاب"
        result = analyzer.parse_grammar_response(ai_response, "beginner", sentence)

        assert 'elements' in result
        assert 'word_explanations' in result
        assert len(result['word_explanations']) == 2

    def test_parse_grammar_response_fallback(self, analyzer):
        """Test fallback parsing when JSON fails"""
        ai_response = "Some unstructured text response"

        sentence = "الطالب يقرأ"
        result = analyzer.parse_grammar_response(ai_response, "beginner", sentence)

        # Should return fallback structure
        assert 'elements' in result
        assert 'word_explanations' in result

    def test_transform_to_standard_format(self, analyzer):
        """Test transformation to standard format"""
        parsed_data = {
            "words": [
                {
                    "word": "الكتاب",
                    "individual_meaning": "the book",
                    "grammatical_role": "noun"
                },
                {
                    "word": "يقرأ",
                    "individual_meaning": "reads",
                    "grammatical_role": "verb"
                }
            ]
        }

        result = analyzer._transform_to_standard_format(parsed_data, "beginner")

        assert 'elements' in result
        assert 'noun' in result['elements']
        assert 'verb' in result['elements']
        assert len(result['word_explanations']) == 2

    def test_rtl_reordering(self, analyzer):
        """Test RTL-specific reordering"""
        word_explanations = [
            ['الكتاب', 'noun', '#FFAA00', 'the book'],
            ['يقرأ', 'verb', '#44FF44', 'reads'],
            ['الطالب', 'noun', '#FFAA00', 'the student']
        ]

        sentence = "الطالب يقرأ الكتاب"
        reordered = analyzer._reorder_explanations_for_rtl(sentence, word_explanations)

        # Should be in reverse order for RTL
        assert reordered == list(reversed(word_explanations))

    def test_arabic_unicode_validation(self, analyzer):
        """Test Arabic Unicode character validation"""
        # Test valid Arabic text
        arabic_text = "السلام عليكم"
        confidence = analyzer.validate_analysis({
            'word_explanations': [['السلام', 'noun', '#FFAA00', 'peace']]
        }, arabic_text)

        assert confidence > 0.0

    def test_mixed_script_handling(self, analyzer):
        """Test handling of mixed script content"""
        mixed_text = "Hello الكتاب world"
        confidence = analyzer.validate_analysis({
            'word_explanations': [['Hello', 'noun', '#FFAA00', 'hello']]
        }, mixed_text)

        # Should still work but with lower Arabic bonus
        assert confidence >= 0.0