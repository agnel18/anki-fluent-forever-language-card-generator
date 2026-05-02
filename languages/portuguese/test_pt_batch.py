"""Batch processing tests for Portuguese analyzer."""

import json
import time
from unittest.mock import patch

import pytest

from languages.portuguese.pt_analyzer import PtAnalyzer
from streamlit_app.language_analyzers.base_analyzer import GrammarAnalysis


MOCK_BATCH_RESPONSE = json.dumps(
    [
        {
            "sentence": "Eu falo português.",
            "overall_structure": "Subject-Verb-Object",
            "sentence_structure": "Subject-Verb-Object",
            "word_explanations": [
                {
                    "word": "Eu",
                    "grammatical_role": "personal_pronoun",
                    "color": "#9370DB",
                    "meaning": "I (1st person singular nominative)",
                },
                {
                    "word": "falo",
                    "grammatical_role": "verb",
                    "color": "#44FF44",
                    "meaning": "speak (1st person singular present)",
                },
                {
                    "word": "português",
                    "grammatical_role": "noun",
                    "color": "#FFAA00",
                    "meaning": "Portuguese (language, noun)",
                },
            ],
            "confidence": 0.92,
        },
        {
            "sentence": "Nós falamos na escola.",
            "overall_structure": "Subject-Verb-Locative",
            "sentence_structure": "Subject-Verb-Locative",
            "word_explanations": [
                {
                    "word": "Nós",
                    "grammatical_role": "personal_pronoun",
                    "color": "#9370DB",
                    "meaning": "we (1st person plural)",
                },
                {
                    "word": "falamos",
                    "grammatical_role": "verb",
                    "color": "#44FF44",
                    "meaning": "speak (1st person plural present)",
                },
                {
                    "word": "na",
                    "grammatical_role": "contraction",
                    "color": "#FF7F50",
                    "meaning": "in the (em + a)",
                    "contraction_parts": ["em", "a"],
                },
                {
                    "word": "escola",
                    "grammatical_role": "noun",
                    "color": "#FFAA00",
                    "meaning": "school (feminine singular)",
                },
            ],
            "confidence": 0.91,
        },
    ],
    ensure_ascii=False,
)


class TestPtAnalyzerBatchProcessing:
    @pytest.fixture
    def analyzer(self):
        return PtAnalyzer()

    def test_batch_analyze_grammar_method_exists(self, analyzer):
        assert hasattr(analyzer, "batch_analyze_grammar")
        assert callable(getattr(analyzer, "batch_analyze_grammar"))

    def test_batch_processing_structure(self, analyzer):
        sentences = ["Eu falo português.", "Nós falamos na escola."]
        with patch.object(PtAnalyzer, "_call_ai", return_value=MOCK_BATCH_RESPONSE):
            results = analyzer.batch_analyze_grammar(
                sentences, "falar", "intermediate", "fake-key"
            )

        assert len(results) == len(sentences)
        for result in results:
            assert isinstance(result, GrammarAnalysis)
            assert result.language_code == "pt"
            assert len(result.word_explanations) > 0

    def test_batch_fallback_on_error(self, analyzer):
        sentences = ["Eu falo português.", "Nós falamos na escola."]
        with patch.object(PtAnalyzer, "_call_ai", side_effect=Exception("API down")):
            results = analyzer.batch_analyze_grammar(
                sentences, "falar", "intermediate", "fake-key"
            )

        assert len(results) == len(sentences)
        for result in results:
            assert isinstance(result, GrammarAnalysis)
            assert len(result.word_explanations) > 0

    def test_batch_efficiency(self, analyzer):
        sentences = [
            "Eu falo português.",
            "Nós falamos na escola.",
            "Ela fala três línguas.",
            "Eles falaram ontem.",
            "Você fala muito rápido.",
        ]

        batch_payload = json.dumps(
            [json.loads(MOCK_BATCH_RESPONSE)[0] for _ in sentences], ensure_ascii=False
        )

        start_time = time.time()
        with patch.object(PtAnalyzer, "_call_ai", return_value=batch_payload):
            results = analyzer.batch_analyze_grammar(
                sentences, "falar", "intermediate", "fake-key"
            )
        elapsed = time.time() - start_time

        assert len(results) == len(sentences)
        assert elapsed < 1.5
