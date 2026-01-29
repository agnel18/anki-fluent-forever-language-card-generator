# Arabic Tests Configuration
# Pytest configuration and fixtures for Arabic analyzer tests

import pytest
import json
import os
from pathlib import Path

@pytest.fixture(scope="session")
def test_data_dir():
    """Path to test data directory"""
    return Path(__file__).parent / "fixtures"

@pytest.fixture(scope="session")
def sample_arabic_sentences(test_data_dir):
    """Load sample Arabic sentences for testing"""
    sentences_file = test_data_dir / "sample_sentences.json"
    if sentences_file.exists():
        with open(sentences_file, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        # Default sample sentences
        return {
            "beginner": {
                "simple": [
                    "القطة سوداء",
                    "أنا أدرس العربية",
                    "الطالب يقرأ الكتاب"
                ],
                "with_target": [
                    {"sentence": "القطة نائمة", "target": "قطة"},
                    {"sentence": "أنا أحب القهوة", "target": "أحب"},
                    {"sentence": "المعلم يكتب الدرس", "target": "يكتب"}
                ]
            },
            "intermediate": {
                "complex": [
                    "الطالب الذي يدرس بجد سيحصل على درجة عالية",
                    "بعد أن أكمل واجبه ذهب إلى الملعب",
                    "رغم المطر استمر اللاعبون في اللعب"
                ]
            },
            "advanced": {
                "complex": [
                    "الخوارزمية التي تم تحسينها للأداء الآن تعالج البيانات بكفاءة أكبر من الإصدارات السابقة مع الحفاظ على التوافق مع الإصدارات السابقة",
                    "على الرغم من توصيات اللجنة قررت الإدارة المضي قدما في عملية الاندماج",
                    "الظاهرة رغم ندرتها تحدث تحت ظروف ميكانيكية كمية محددة"
                ]
            }
        }

@pytest.fixture(scope="session")
def expected_arabic_outputs(test_data_dir):
    """Load expected outputs for Arabic validation"""
    outputs_file = test_data_dir / "expected_outputs.json"
    if outputs_file.exists():
        with open(outputs_file, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        # Default expected outputs
        return {
            "basic_analysis": {
                "sentence": "القطة سوداء",
                "expected_roles": ["definite_article", "noun", "adjective"],
                "min_confidence": 0.7,
                "required_explanations": ["overall_structure", "key_features"]
            }
        }

@pytest.fixture(scope="session")
def mock_arabic_responses(test_data_dir):
    """Load mock AI responses for Arabic testing"""
    responses_file = test_data_dir / "mock_responses.json"
    if responses_file.exists():
        with open(responses_file, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        # Default mock responses
        return {
            "valid_response": {
                "words": [
                    {"word": "القطة", "grammatical_role": "noun", "meaning": "Subject noun with definite article"},
                    {"word": "سوداء", "grammatical_role": "adjective", "meaning": "Predicate adjective describing the subject"}
                ],
                "explanations": {
                    "overall_structure": "Simple nominal sentence with subject-predicate structure",
                    "key_features": "Definite article assimilation, adjective agreement"
                }
            },
            "malformed_response": "This is not JSON",
            "incomplete_response": {
                "words": [
                    {"word": "القطة", "grammatical_role": "noun"}
                ]
            }
        }

@pytest.fixture
def arabic_config():
    """Create Arabic config instance for testing"""
    from ..domain.ar_config import ArConfig
    return ArConfig()

@pytest.fixture
def arabic_analyzer(arabic_config):
    """Create Arabic analyzer instance for testing"""
    from ..ar_analyzer import ArAnalyzer
    return ArAnalyzer(config=arabic_config)

@pytest.fixture
def arabic_prompt_builder(arabic_config):
    """Create Arabic prompt builder for testing"""
    from ..domain.ar_prompt_builder import ArPromptBuilder
    return ArPromptBuilder(arabic_config)

@pytest.fixture
def arabic_response_parser(arabic_config):
    """Create Arabic response parser for testing"""
    from ..domain.ar_response_parser import ArResponseParser
    return ArResponseParser(arabic_config)

@pytest.fixture
def arabic_validator(arabic_config):
    """Create Arabic validator for testing"""
    from ..domain.ar_validator import ArValidator
    return ArValidator(arabic_config)