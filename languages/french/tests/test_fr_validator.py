"""French validator tests."""

import sys
from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from languages.french.domain.fr_config import FrConfig
from languages.french.domain.fr_validator import FrValidator


def test_validator_creation():
    config = FrConfig()
    validator = FrValidator(config)
    assert validator is not None


def test_confidence_calculation():
    config = FrConfig()
    validator = FrValidator(config)

    # Mock result
    result = {
        "word_explanations": [["test", "noun", "blue", "a test"]],
        "html_output": "<div>test</div>",
        "confidence_score": 0.8
    }

    confidence = validator._calculate_confidence(result, "test sentence")
    assert isinstance(confidence, float)
    assert 0.0 <= confidence <= 1.0