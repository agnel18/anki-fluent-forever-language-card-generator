import pytest
import re
from unittest.mock import MagicMock
from languages.turkish.tr_analyzer import TrAnalyzer

class MockDeckExporter:
    """Mock deck exporter for testing purposes"""

    def extract_apkg_fields(self, result):
        """Mock APKG field extraction"""
        return {
            'sentence': getattr(result, 'sentence', 'Test sentence'),
            'word_explanations': getattr(result, 'word_explanations', []),
            'html_output': getattr(result, 'html_output', '<span>Test</span>'),
            'confidence_score': getattr(result, 'confidence_score', 0.8)
        }

class TestTrApkgExportFields:
    """Test APKG export field values for quality and compliance for Turkish"""

    @pytest.fixture
    def analyzer(self):
        return TrAnalyzer()

    @pytest.fixture
    def deck_exporter(self):
        return MockDeckExporter()

    def test_final_grammar_analysis_apkg_test(self, analyzer, deck_exporter):
        """FINAL TEST: Take 1 of the 3 generated sentences and check word-by-word analysis in APKG output"""
        # This test depends on the sentence generation test having run first
        # In practice, you might need to run the sentence generation test separately
        # or mock the generated sentences

        # For this test, we'll use sample Turkish sentences
        simulated_sentences = [
            "Evde güzel bir yemek pişiriyorum ve ailemle birlikte yiyoruz.",
            "Okula gitmek için hızlı bir şekilde hazırlanıp dışarı çıktım.",
            "Kitap okumak çok güzel bir hobidir ve zaman geçiririm."
        ]
        test_word = "güzel"  # beautiful
        test_sentence = simulated_sentences[0]  # Take first sentence

        print(f"\n🔍 Grammar Analysis Test Details:")
        print(f"- Selected Sentence: '{test_sentence}'")
        print(f"- Target Word: '{test_word}'")
        print(f"- Complexity: intermediate")

        # Perform grammar analysis on the selected sentence
        result = analyzer.analyze_grammar(test_sentence, test_word, "intermediate", "mock_key")

        assert result is not None, f"Grammar analysis returned None for sentence: {test_sentence}"
        assert hasattr(result, 'word_explanations'), "Missing word explanations"
        assert hasattr(result, 'html_output'), "Missing HTML output"

        # Check word-by-word analysis
        word_explanations = result.word_explanations
        assert len(word_explanations) > 0, "No word explanations generated"

        print(f"- Word Explanations Generated: {len(word_explanations)}")
        print(f"\nWord-by-word breakdown:")

        # Verify each word has proper analysis (word, role, color, meaning)
        for word_exp in word_explanations:
            assert len(word_exp) >= 4, f"Incomplete word explanation: {word_exp}"
            word, role, color, meaning = word_exp[:4]

            # Validate word is present in sentence
            word_present = word.lower() in test_sentence.lower()
            assert word_present, f"Word '{word}' not found in sentence: {test_sentence}"

            # Validate role is not empty
            role_valid = bool(role.strip())
            assert role_valid, f"Empty grammatical role for word '{word}'"

            # Validate color is a valid hex color
            color_valid = color.startswith('#') and len(color) == 7
            assert color_valid, f"Invalid color format: {color}"

            # Validate meaning is within character limits
            meaning_length = len(meaning)
            meaning_valid = meaning_length <= 75 and len(meaning.strip()) > 0
            assert meaning_valid, f"Word explanation invalid: '{meaning}' ({meaning_length} chars)"

            print(f"- {word}: {role}, {color}, '{meaning}' ({meaning_length} chars) ✓")

        # Check HTML output has proper coloring and marking
        html_output = result.html_output
        assert '<span' in html_output, "HTML output missing span elements for coloring"
        assert 'style=' in html_output, "HTML output missing style attributes"

        # Verify target word is properly highlighted
        target_highlighted = test_word.lower() in html_output.lower()
        assert target_highlighted, f"Target word '{test_word}' not highlighted in HTML"

        print(f"\nHTML Output Validation:")
        print(f"- Contains span elements: ✓")
        print(f"- Contains style attributes: ✓")
        print(f"- Target word highlighted: {'✓' if target_highlighted else '❌'}")
        print(f"- HTML Preview: {html_output[:100]}...")

        # Check for proper color application (at least one color from scheme)
        color_scheme = analyzer.get_color_scheme("intermediate")
        colors_used = set()
        for color in color_scheme.values():
            if color in html_output:
                colors_used.add(color)
        color_scheme_valid = len(colors_used) > 0
        assert color_scheme_valid, f"No colors from scheme applied in HTML: {color_scheme}"

        print(f"- Colors from scheme applied: {'✓' if color_scheme_valid else '❌'} ({len(colors_used)} colors used)")

        # Simulate APKG export and verify final output
        apkg_fields = deck_exporter.extract_apkg_fields(result)

        # Verify APKG fields contain the analyzed data
        assert 'sentence' in apkg_fields, "APKG missing sentence field"
        assert 'word_explanations' in apkg_fields, "APKG missing word_explanations field"
        assert 'html_output' in apkg_fields, "APKG missing html_output field"

        # Verify the sentence in APKG matches the analyzed sentence
        sentence_match = apkg_fields['sentence'] == test_sentence
        assert sentence_match, "APKG sentence doesn't match analyzed sentence"

        print(f"\nAPKG Export Validation:")
        print(f"- Sentence field present: ✓")
        print(f"- Word explanations field present: ✓")
        print(f"- HTML output field present: ✓")
        print(f"- Sentence matches analyzed: {'✓' if sentence_match else '❌'}")

        # Verify HTML in APKG has proper formatting
        apkg_html = apkg_fields.get('html_output', '')
        html_formatting_valid = '<span' in apkg_html and 'style=' in apkg_html
        assert html_formatting_valid, "APKG HTML missing proper formatting"

        print(f"- APKG HTML properly formatted: {'✓' if html_formatting_valid else '❌'}")

        print(f"\n✅ Grammar Analysis APKG Test PASSED")
        print(f"- Confidence Score: {getattr(result, 'confidence_score', 'N/A')}")
        print(f"- All validations passed: ✓")

        # Check for proper color application (at least one color from scheme)
        color_scheme = analyzer.get_color_scheme("intermediate")
        colors_used = set()
        for color in color_scheme.values():
            if color in html_output:
                colors_used.add(color)
        assert len(colors_used) > 0, f"No colors from scheme applied in HTML: {color_scheme}"

        # Simulate APKG export and verify final output
        apkg_fields = deck_exporter.extract_apkg_fields(result)

        # Verify APKG fields contain the analyzed data
        assert 'sentence' in apkg_fields, "APKG missing sentence field"
        assert 'word_explanations' in apkg_fields, "APKG missing word_explanations field"
        assert 'html_output' in apkg_fields, "APKG missing html_output field"

        # Verify the sentence in APKG matches the analyzed sentence
        assert apkg_fields['sentence'] == test_sentence, "APKG sentence doesn't match analyzed sentence"

        # Verify HTML in APKG has proper formatting
        apkg_html = apkg_fields['html_output']
        assert '<span' in apkg_html, "APKG HTML missing span elements"
        assert len(apkg_html) > len(test_sentence), "APKG HTML not properly formatted with colors"

    def test_bright_poppy_colors_applied(self, analyzer):
        """Test that bright poppy colors are correctly applied to grammatical roles"""
        result = analyzer.analyze_grammar("Test sentence", "test", "intermediate", "mock_key")

        # Check that HTML contains bright poppy color codes
        bright_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F', '#BB8FCE']
        html_output = result.html_output

        # Verify at least one bright color is used
        color_found = any(color in html_output for color in bright_colors)
        assert color_found, f"No bright poppy colors found in HTML: {html_output}"

    def test_parsing_logic_accuracy(self, analyzer):
        """Test that parsing logic correctly extracts and structures data"""
        result = analyzer.analyze_grammar("Türkçe bir cümle örneği test için", "cümle", "intermediate", "mock_key")

        # Verify word_explanations structure
        assert hasattr(result, 'word_explanations')
        assert isinstance(result.word_explanations, list)
        assert len(result.word_explanations) > 0

        # Check each word explanation has required fields
        for word_exp in result.word_explanations:
            assert len(word_exp) >= 4, f"Word explanation incomplete: {word_exp}"
            word, role, color, meaning = word_exp[:4]
            assert isinstance(word, str) and word.strip()
            assert isinstance(role, str) and role.strip()
            assert isinstance(color, str) and color.startswith('#')
            assert isinstance(meaning, str) and len(meaning.strip()) > 0

    def test_html_output_structure(self, analyzer):
        """Test that HTML output has proper structure and formatting"""
        result = analyzer.analyze_grammar("Test sentence", "test", "intermediate", "mock_key")
        html_output = result.html_output

        # Check for required HTML elements
        assert '<span' in html_output, "HTML should contain span elements for coloring"
        assert 'style=' in html_output, "HTML should contain style attributes"
        assert '</span>' in html_output, "HTML should have closing span tags"

        # Verify no malformed HTML
        span_count = html_output.count('<span')
        close_count = html_output.count('</span>')
        assert span_count == close_count, f"Mismatched span tags: {span_count} open, {close_count} close"

    def test_sentence_coloring_consistency(self, analyzer):
        """Test that sentence coloring is consistent and properly applied"""
        result = analyzer.analyze_grammar("Kedi masa üzerinde oturuyor", "kedi", "intermediate", "mock_key")
        html_output = result.html_output

        # Extract colors used in the sentence
        color_pattern = r'color:#([A-Fa-f0-9]{6})'
        colors_used = re.findall(color_pattern, html_output)

        # Verify colors are from the defined color scheme
        color_scheme = analyzer.get_color_scheme("intermediate")
        valid_colors = set(color_scheme.values())

        for color in colors_used:
            full_color = f"#{color}"
            assert full_color in valid_colors, f"Color {full_color} not in color scheme: {valid_colors}"

    def test_word_explanations_quality(self, analyzer):
        """Test that word explanations meet quality standards for APKG export"""
        result = analyzer.analyze_grammar("Öğrenci kitabı okuyarak öğreniyor", "okuyarak", "intermediate", "mock_key")

        explanations = result.word_explanations

        for word_exp in explanations:
            word, role, color, meaning = word_exp[:4]

            # Check character limits for APKG compatibility
            assert len(meaning) <= 75, f"Word explanation too long: {len(meaning)} chars > 75 limit"

            # Verify no repetitive role information (prevention-at-source)
            role_lower = role.lower()
            meaning_lower = meaning.lower()
            assert role_lower not in meaning_lower, f"Role '{role}' repeated in meaning: {meaning}"

            # Check for educational value
            assert len(meaning.split()) >= 3, f"Explanation too brief: {meaning}"

    def test_gold_standard_comparison(self, analyzer):
        """Test that results compare favorably against gold standard analyzers"""
        # Load gold standard results (Chinese Simplified as reference)
        gold_standard_result = self._load_gold_standard_result("zh", "intermediate")

        # Run analysis on same sentence
        result = analyzer.analyze_grammar(
            gold_standard_result['sentence'],
            gold_standard_result['target_word'],
            "intermediate",
            "mock_key"
        )

        # Compare key metrics
        assert len(result.word_explanations) >= len(gold_standard_result['word_explanations']), \
            "Fewer word explanations than gold standard"

        # Check confidence score meets minimum threshold
        assert result.confidence_score >= gold_standard_result['min_confidence'], \
            f"Confidence {result.confidence_score} below gold standard {gold_standard_result['min_confidence']}"

        # Verify HTML output quality
        assert len(result.html_output) >= len(gold_standard_result['html_output']) * 0.8, \
            "HTML output significantly shorter than gold standard"

    def test_apkg_field_values_final_format(self, analyzer, deck_exporter):
        """Test that final APKG field values are properly formatted"""
        result = analyzer.analyze_grammar("Sample sentence for testing", "sample", "intermediate", "mock_key")

        # Simulate APKG field extraction
        fields = deck_exporter.extract_apkg_fields(result)

        # Verify required fields exist
        required_fields = ['sentence', 'word_explanations', 'html_output', 'confidence_score']
        for field in required_fields:
            assert field in fields, f"Missing required APKG field: {field}"
            assert fields[field] is not None, f"APKG field {field} is None"

        # Check field value types and formats
        assert isinstance(fields['sentence'], str)
        assert isinstance(fields['word_explanations'], (list, str))
        assert isinstance(fields['html_output'], str)
        assert isinstance(fields['confidence_score'], (int, float))

        # Verify HTML field contains proper coloring
        assert '<span' in fields['html_output'], "APKG HTML field missing span elements"

    def _load_gold_standard_result(self, language_code: str, complexity: str) -> dict:
        """Load gold standard result for comparison"""
        # Implementation would load from test fixtures
        # This is a placeholder for the actual implementation
        return {
            'sentence': 'Test sentence',
            'target_word': 'test',
            'word_explanations': [['test', 'noun', '#FF6B6B', 'A sample word']],
            'html_output': '<span style="color:#FF6B6B">Test</span> sentence',
            'min_confidence': 0.7
        }