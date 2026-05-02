
"""Batch processing tests for Latvian analyzer."""

import json
import time
from unittest.mock import patch

import pytest

from languages.latvian.lv_analyzer import LvAnalyzer
from streamlit_app.language_analyzers.base_analyzer import GrammarAnalysis


MOCK_BATCH_RESPONSE = json.dumps(
    [
        {
            "sentence": "Es runāju latviski.",
            "overall_structure": "Subject-Verb-Adverb",
            "sentence_structure": "Subject-Verb-Adverb",
            "word_explanations": [
                {
                    "word": "Es",
                    "role": "personal_pronoun",
                    "color": "#9370DB",
                    "meaning": "I (1st person singular)",
                },
                {
                    "word": "runāju",
                    "role": "verb",
                    "color": "#4ECDC4",
                    "meaning": "speak",
                },
            ],
            "confidence": 0.9,
        },
        {
            "sentence": "Mēs runājam skolā.",
            "overall_structure": "Subject-Verb-Locative",
            "sentence_structure": "Subject-Verb-Locative",
            "word_explanations": [
                {
                    "word": "Mēs",
                    "role": "personal_pronoun",
                    "color": "#9370DB",
                    "meaning": "we",
                },
                {
                    "word": "runājam",
                    "role": "verb",
                    "color": "#4ECDC4",
                    "meaning": "speak",
                },
            ],
            "confidence": 0.88,
        },
    ],
    ensure_ascii=False,
)


class TestLvAnalyzerBatchProcessing:
    @pytest.fixture
    def analyzer(self):
        return LvAnalyzer()

    def test_batch_analyze_grammar_method_exists(self, analyzer):
        assert hasattr(analyzer, "batch_analyze_grammar")
        assert callable(getattr(analyzer, "batch_analyze_grammar"))

    def test_batch_processing_structure(self, analyzer):
        sentences = ["Es runāju latviski.", "Mēs runājam skolā."]
        with patch.object(LvAnalyzer, "_call_ai", return_value=MOCK_BATCH_RESPONSE):
            results = analyzer.batch_analyze_grammar(
                sentences, "runāt", "intermediate", "fake-key"
            )

        assert len(results) == len(sentences)
        for result in results:
            assert isinstance(result, GrammarAnalysis)
            assert result.language_code == "lv"
            assert len(result.word_explanations) > 0

    def test_batch_fallback_on_error(self, analyzer):
        sentences = ["Es runāju latviski.", "Mēs runājam skolā."]
        with patch.object(LvAnalyzer, "_call_ai", side_effect=Exception("API down")):
            results = analyzer.batch_analyze_grammar(
                sentences, "runāt", "intermediate", "fake-key"
            )

        assert len(results) == len(sentences)
        for result in results:
            assert isinstance(result, GrammarAnalysis)
            assert len(result.word_explanations) > 0

    def test_batch_efficiency(self, analyzer):
        sentences = [
            "Es runāju latviski.",
            "Mēs runājam skolā.",
            "Viņi runā par ēdienu.",
            "Tu runā pārāk ātri.",
            "Viņa runāja vakar.",
        ]

        # Reuse deterministic mocked response to keep this a speed test.
        batch_payload = json.dumps(
            [json.loads(MOCK_BATCH_RESPONSE)[0] for _ in sentences], ensure_ascii=False
        )

        start_time = time.time()
        with patch.object(LvAnalyzer, "_call_ai", return_value=batch_payload):
            results = analyzer.batch_analyze_grammar(
                sentences, "runāt", "intermediate", "fake-key"
            )
        elapsed = time.time() - start_time

        assert len(results) == len(sentences)
        assert elapsed < 1.5
