import pytest

class TestArabicValidator:
    """Test Arabic validator component"""

    def test_initialization(self, arabic_validator, arabic_config):
        """Test validator initializes correctly"""
        assert arabic_validator.config == arabic_config

    def test_valid_result_validation(self, arabic_validator):
        """Test validation of valid analysis result"""
        result = {
            'word_explanations': [
                ['القطة', 'noun (اسم)', '#4ECDC4', 'Subject noun with definite article'],
                ['سوداء', 'adjective (صفة)', '#FFD700', 'Predicate adjective']
            ],
            'explanations': {
                'overall_structure': 'Simple nominal sentence structure',
                'key_features': 'Definite article and adjective agreement'
            }
        }

        sentence = "القطة سوداء"
        validated = arabic_validator.validate_result(result, sentence)

        assert 'validation_metadata' in validated
        assert 'confidence_score' in validated
        assert validated['confidence_score'] > 0.5  # Should have decent confidence

    def test_invalid_result_validation(self, arabic_validator):
        """Test validation of invalid analysis result"""
        result = {
            'word_explanations': [],  # Empty explanations
            'explanations': {}  # Empty explanations
        }

        validated = arabic_validator.validate_result(result, "test sentence")

        assert validated['confidence_score'] < 0.5  # Should have low confidence
        assert 'validation_metadata' in validated

    def test_arabic_linguistic_validation(self, arabic_validator):
        """Test Arabic-specific linguistic validation"""
        # Test with definite article
        result_with_al = {
            'word_explanations': [
                ['القطة', 'noun (اسم)', '#4ECDC4', 'Subject noun with definite article']
            ],
            'explanations': {
                'overall_structure': 'Simple sentence',
                'key_features': 'Definite article usage'
            }
        }

        validated = arabic_validator.validate_result(result_with_al, "القطة")
        # Should not penalize for having definite article analysis
        assert validated['confidence_score'] > 0.3

    def test_word_alignment_validation(self, arabic_validator):
        """Test word-to-sentence alignment validation"""
        # Create result with proper word alignment
        result = {
            'word_explanations': [
                ['القطة', 'noun', '#4ECDC4', 'test'],
                ['سوداء', 'adjective', '#FFD700', 'test']
            ],
            'explanations': {
                'overall_structure': 'test',
                'key_features': 'test'
            }
        }

        validated = arabic_validator.validate_result(result, "القطة سوداء")
        # Should have reasonable confidence for proper alignment
        assert validated['confidence_score'] > 0.4

    def test_content_quality_validation(self, arabic_validator):
        """Test content quality validation"""
        # Test with good explanations
        good_result = {
            'word_explanations': [
                ['القطة', 'noun (اسم)', '#4ECDC4', 'Subject noun with definite article']
            ],
            'explanations': {
                'overall_structure': 'Complete sentence structure analysis',
                'key_features': 'Important grammatical features explained'
            }
        }

        good_validation = arabic_validator.validate_result(good_result, "القطة")

        # Test with poor explanations
        poor_result = {
            'word_explanations': [
                ['القطة', 'noun', '#4ECDC4', 'word']  # Too short
            ],
            'explanations': {
                'overall_structure': 'ok',  # Too short
                'key_features': 'test'
            }
        }

        poor_validation = arabic_validator.validate_result(poor_result, "القطة")

        # Good result should have higher confidence
        assert good_validation['confidence_score'] > poor_validation['confidence_score']

    def test_structural_validation(self, arabic_validator):
        """Test basic structural validation"""
        # Valid structure
        valid_result = {
            'word_explanations': [['word', 'role', '#FFAA00', 'meaning']],
            'explanations': {'overall_structure': 'test', 'key_features': 'test'}
        }

        assert arabic_validator._validate_structure(
            valid_result['word_explanations'], "test", []
        ) == 1.0

        # Invalid structure
        invalid_result = {
            'word_explanations': [['word']],  # Missing elements
            'explanations': {'overall_structure': 'test'}
        }

        score = arabic_validator._validate_structure(
            invalid_result['word_explanations'], "test", []
        )
        assert score < 1.0

    def test_linguistic_score_calculation(self, arabic_validator):
        """Test linguistic accuracy score calculation"""
        # Test with definite article (should get bonus)
        result_with_al = {
            'word_explanations': [
                ['القطة', 'noun', '#4ECDC4', 'Subject with definite article ال']
            ],
            'explanations': {'overall_structure': 'test', 'key_features': 'test'}
        }

        score = arabic_validator.calculate_linguistic_score(
            result_with_al['word_explanations'], "القطة"
        )
        assert score >= 1.0  # Should get bonus for recognizing definite article

    def test_validation_metadata(self, arabic_validator):
        """Test that validation metadata is properly added"""
        result = {
            'word_explanations': [['test', 'noun', '#FFAA00', 'test']],
            'explanations': {'overall_structure': 'test', 'key_features': 'test'}
        }

        validated = arabic_validator.validate_result(result, "test")

        metadata = validated['validation_metadata']
        assert 'word_count' in metadata
        assert 'sentence_length' in metadata
        assert 'confidence_score' in metadata
        assert 'validation_issues' in metadata
        assert 'is_rtl_validated' in metadata
        assert metadata['is_rtl_validated'] == True