"""
End-to-End Pipeline Integration Test

Tests the FULL generation pipeline for languages with grammar analyzers by mocking
the Gemini API with realistic, linguistically accurate responses. Exercises:

  Content generation → Parsing → Grammar analysis → Audio → Images → Card assembly

Produces a detailed human-readable report (console + file).

Usage:
    python -m pytest tests/test_end_to_end_pipeline.py -v -s
    python -m pytest tests/test_end_to_end_pipeline.py -v -s -k "japanese"
"""

import json
import logging
import os
import sys
import textwrap
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch, PropertyMock
import tempfile

import pytest

# ---------------------------------------------------------------------------
# Path setup (mirrors tests/conftest.py)
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "streamlit_app"))

os.environ.setdefault("STREAMLIT_SERVER_HEADLESS", "true")
os.environ.setdefault("STREAMLIT_BROWSER_GATHER_USAGE_STATS", "false")

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Report directory
# ---------------------------------------------------------------------------
REPORT_DIR = PROJECT_ROOT / "tests" / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# MOCK DATA PER LANGUAGE
# ============================================================================
# Each entry supplies:
#   word            – a top-100 frequency word
#   language_name   – full name expected by the pipeline
#   language_code   – ISO code used by the analyzer registry
#   topic           – one topic from constants.py curated list
#   mock_content_response  – exact text Gemini would return for content generation
#   mock_grammar_responses – list of JSON dicts (one per sentence) the analyzer's
#                            _call_ai would return for grammar analysis

JAPANESE_MOCK_DATA: Dict[str, Any] = {
    "word": "食べる",
    "language_name": "Japanese",
    "language_code": "ja",
    "topic": "Food & Cooking",
    "num_sentences": 4,
    "min_length": 8,
    "max_length": 13,
    "difficulty": "beginner",
    # --- Mock Gemini response for content generation (sentence_generator) ---
    "mock_content_response": textwrap.dedent("""\
        MEANING: to eat (to consume food by putting it in the mouth)

        RESTRICTIONS: No specific grammatical restrictions.

        SENTENCES:
        1. 私は毎朝パンとたまごを食べます。
        2. 子供たちは学校で昼ごはんを食べます。
        3. あなたは何を食べたいですか。
        4. 母は台所でりんごを食べています。

        TRANSLATIONS:
        1. I eat bread and eggs every morning.
        2. The children eat lunch at school.
        3. What do you want to eat?
        4. My mother is eating an apple in the kitchen.

        IPA:
        1. わたし は まいあさ パン と たまご を たべます
        2. こどもたち は がっこう で ひるごはん を たべます
        3. あなた は なに を たべたい です か
        4. はは は だいどころ で りんご を たべています

        KEYWORDS:
        1. bread on plate, fried eggs, breakfast table
        2. children in cafeteria, school lunch tray, eating together
        3. restaurant menu, food choices, question mark
        4. woman in kitchen, red apple, eating fruit"""),

    # --- Mock Gemini responses for grammar analysis (one JSON per sentence) ---
    # The Japanese analyzer calls _call_ai once per batch; the batch prompt asks
    # for a JSON array. We supply the full array as a single string response.
    "mock_grammar_batch_response": json.dumps([
        {
            "sentence": "私は毎朝パンとたまごを食べます。",
            "words": [
                {"word": "私", "reading": "わたし", "grammatical_role": "pronoun", "conjugation_form": None, "politeness": None, "individual_meaning": "I (first person pronoun)"},
                {"word": "は", "reading": "は", "grammatical_role": "particle", "conjugation_form": None, "politeness": None, "individual_meaning": "topic marker particle"},
                {"word": "毎朝", "reading": "まいあさ", "grammatical_role": "adverb", "conjugation_form": None, "politeness": None, "individual_meaning": "every morning"},
                {"word": "パン", "reading": "パン", "grammatical_role": "noun", "conjugation_form": None, "politeness": None, "individual_meaning": "bread"},
                {"word": "と", "reading": "と", "grammatical_role": "particle", "conjugation_form": None, "politeness": None, "individual_meaning": "and (listing particle)"},
                {"word": "たまご", "reading": "たまご", "grammatical_role": "noun", "conjugation_form": None, "politeness": None, "individual_meaning": "egg"},
                {"word": "を", "reading": "を", "grammatical_role": "particle", "conjugation_form": None, "politeness": None, "individual_meaning": "object marker particle"},
                {"word": "食べます", "reading": "たべます", "grammatical_role": "verb", "conjugation_form": "masu", "politeness": "polite", "individual_meaning": "eat (polite present)"}
            ],
            "explanations": {
                "overall_structure": "SOV sentence: Subject は Time Object を Verb (polite).",
                "key_features": "Uses topic particle は, object particle を, listing particle と, polite -ます form.",
                "complexity_notes": "Beginner-friendly polite sentence with basic particles."
            }
        },
        {
            "sentence": "子供たちは学校で昼ごはんを食べます。",
            "words": [
                {"word": "子供たち", "reading": "こどもたち", "grammatical_role": "noun", "conjugation_form": None, "politeness": None, "individual_meaning": "children (plural)"},
                {"word": "は", "reading": "は", "grammatical_role": "particle", "conjugation_form": None, "politeness": None, "individual_meaning": "topic marker particle"},
                {"word": "学校", "reading": "がっこう", "grammatical_role": "noun", "conjugation_form": None, "politeness": None, "individual_meaning": "school"},
                {"word": "で", "reading": "で", "grammatical_role": "particle", "conjugation_form": None, "politeness": None, "individual_meaning": "location of action particle"},
                {"word": "昼ごはん", "reading": "ひるごはん", "grammatical_role": "noun", "conjugation_form": None, "politeness": None, "individual_meaning": "lunch"},
                {"word": "を", "reading": "を", "grammatical_role": "particle", "conjugation_form": None, "politeness": None, "individual_meaning": "object marker particle"},
                {"word": "食べます", "reading": "たべます", "grammatical_role": "verb", "conjugation_form": "masu", "politeness": "polite", "individual_meaning": "eat (polite present)"}
            ],
            "explanations": {
                "overall_structure": "SOV sentence: Subject は Location で Object を Verb.",
                "key_features": "Uses location particle で to mark where action takes place, topic particle は, object particle を.",
                "complexity_notes": "Beginner pattern with location marker で."
            }
        },
        {
            "sentence": "あなたは何を食べたいですか。",
            "words": [
                {"word": "あなた", "reading": "あなた", "grammatical_role": "pronoun", "conjugation_form": None, "politeness": None, "individual_meaning": "you (second person pronoun)"},
                {"word": "は", "reading": "は", "grammatical_role": "particle", "conjugation_form": None, "politeness": None, "individual_meaning": "topic marker particle"},
                {"word": "何", "reading": "なに", "grammatical_role": "pronoun", "conjugation_form": None, "politeness": None, "individual_meaning": "what (interrogative)"},
                {"word": "を", "reading": "を", "grammatical_role": "particle", "conjugation_form": None, "politeness": None, "individual_meaning": "object marker particle"},
                {"word": "食べたい", "reading": "たべたい", "grammatical_role": "verb", "conjugation_form": "tai", "politeness": "plain", "individual_meaning": "want to eat (desire form)"},
                {"word": "です", "reading": "です", "grammatical_role": "copula", "conjugation_form": "masu", "politeness": "polite", "individual_meaning": "is/am/are (polite copula)"},
                {"word": "か", "reading": "か", "grammatical_role": "particle", "conjugation_form": None, "politeness": None, "individual_meaning": "question marker particle"}
            ],
            "explanations": {
                "overall_structure": "Interrogative SOV: Subject は WH-word を Verb-たい です か?",
                "key_features": "Uses -たい desire form, question particle か, polite copula です.",
                "complexity_notes": "Beginner question pattern with -たい (want to) form."
            }
        },
        {
            "sentence": "母は台所でりんごを食べています。",
            "words": [
                {"word": "母", "reading": "はは", "grammatical_role": "noun", "conjugation_form": None, "politeness": None, "individual_meaning": "mother (humble form)"},
                {"word": "は", "reading": "は", "grammatical_role": "particle", "conjugation_form": None, "politeness": None, "individual_meaning": "topic marker particle"},
                {"word": "台所", "reading": "だいどころ", "grammatical_role": "noun", "conjugation_form": None, "politeness": None, "individual_meaning": "kitchen"},
                {"word": "で", "reading": "で", "grammatical_role": "particle", "conjugation_form": None, "politeness": None, "individual_meaning": "location of action particle"},
                {"word": "りんご", "reading": "りんご", "grammatical_role": "noun", "conjugation_form": None, "politeness": None, "individual_meaning": "apple"},
                {"word": "を", "reading": "を", "grammatical_role": "particle", "conjugation_form": None, "politeness": None, "individual_meaning": "object marker particle"},
                {"word": "食べています", "reading": "たべています", "grammatical_role": "verb", "conjugation_form": "te_iru", "politeness": "polite", "individual_meaning": "is eating (progressive, polite)"}
            ],
            "explanations": {
                "overall_structure": "SOV progressive: Subject は Location で Object を Verb-ている.",
                "key_features": "Uses て-いる progressive form for ongoing action, location particle で.",
                "complexity_notes": "Beginner level — て-いる progressive is common early grammar."
            }
        }
    ], ensure_ascii=False),
}


# ============================================================================
# Mapping: add more languages here to extend coverage
# ============================================================================
LANGUAGE_MOCK_DATA = {
    "japanese": JAPANESE_MOCK_DATA,
    # Future: "french": FRENCH_MOCK_DATA, "spanish": SPANISH_MOCK_DATA, etc.
}


# ============================================================================
# HELPERS
# ============================================================================

class PipelineReport:
    """Accumulates test results and renders a human-readable report."""

    def __init__(self, language_name: str, word: str, difficulty: str, topic: str):
        self.language_name = language_name
        self.word = word
        self.difficulty = difficulty
        self.topic = topic
        self.started_at = datetime.now()
        self.stages: List[Dict[str, Any]] = []
        self.sentences_data: List[Dict[str, Any]] = []
        self.audio_files: List[str] = []
        self.image_files: List[str] = []
        self.meaning = ""
        self.errors: List[str] = []

    def add_stage(self, name: str, passed: bool, detail: str = ""):
        self.stages.append({"name": name, "passed": passed, "detail": detail})

    def render(self) -> str:
        elapsed = (datetime.now() - self.started_at).total_seconds()
        sep = "=" * 80
        thin = "-" * 80

        lines = [
            sep,
            f"  END-TO-END PIPELINE REPORT — {self.language_name.upper()}",
            sep,
            f"  Word          : {self.word}",
            f"  Language       : {self.language_name}",
            f"  Difficulty     : {self.difficulty}",
            f"  Topic          : {self.topic}",
            f"  Generated at   : {self.started_at:%Y-%m-%d %H:%M:%S}",
            f"  Elapsed        : {elapsed:.2f}s",
            sep,
            "",
            "STAGE RESULTS",
            thin,
        ]

        all_passed = True
        for s in self.stages:
            icon = "PASS" if s["passed"] else "FAIL"
            all_passed = all_passed and s["passed"]
            lines.append(f"  [{icon}] {s['name']}")
            if s["detail"]:
                for d in s["detail"].split("\n"):
                    lines.append(f"         {d}")

        lines += ["", thin, f"  OVERALL: {'ALL STAGES PASSED' if all_passed else 'SOME STAGES FAILED'}", thin, ""]

        # Content generation
        lines += ["CONTENT GENERATION OUTPUT", thin]
        lines.append(f"  Meaning: {self.meaning}")
        lines.append("")

        for i, sd in enumerate(self.sentences_data, 1):
            lines.append(f"  --- Sentence {i} ---")
            lines.append(f"  Original   : {sd.get('sentence', 'N/A')}")
            lines.append(f"  Translation: {sd.get('english_translation', 'N/A')}")
            lines.append(f"  IPA/Reading: {sd.get('ipa', 'N/A')}")
            lines.append(f"  Keywords   : {sd.get('image_keywords', 'N/A')}")
            lines.append("")

            # Grammar analysis
            colored = sd.get("colored_sentence", "")
            explanations = sd.get("word_explanations", [])
            summary = sd.get("grammar_summary", "")

            lines.append(f"  Colored HTML : {colored[:200]}{'…' if len(colored) > 200 else ''}")
            lines.append(f"  Grammar Summ : {summary}")
            lines.append(f"  Word Explanations ({len(explanations)} words):")
            for exp in explanations:
                if len(exp) >= 4:
                    lines.append(f"    {exp[0]:12s}  {exp[1]:14s}  {exp[2]:8s}  {exp[3]}")
                else:
                    lines.append(f"    {exp}")
            lines.append("")

        # Audio / Images
        lines += ["AUDIO FILES", thin]
        for a in self.audio_files:
            lines.append(f"  {a}")
        if not self.audio_files:
            lines.append("  (none — mock returned empty list)")

        lines += ["", "IMAGE FILES", thin]
        for img in self.image_files:
            lines.append(f"  {img}")
        if not self.image_files:
            lines.append("  (none — mock returned empty list)")

        # Errors
        if self.errors:
            lines += ["", "ERRORS", thin]
            for e in self.errors:
                lines.append(f"  !! {e}")

        lines += ["", sep, "  END OF REPORT", sep, ""]
        return "\n".join(lines)


def _build_mock_session_state(difficulty: str = "beginner") -> dict:
    """Return a dict that behaves like st.session_state for test purposes."""
    return {
        "google_api_key": "AIzaFAKE_TEST_KEY_1234567890",
        "google_tts_api_key": "AIzaFAKE_TTS_KEY_1234567890",
        "pixabay_api_key": "FAKE_PIXABAY_KEY_12345",
        "difficulty": difficulty,
        "enable_topics": True,
        "selected_topics": ["Food & Cooking"],
        "native_language": "English",
        "audio_speed": 0.8,
        "gemini_api_calls": 0,
        "gemini_tokens_used": 0,
    }


# ============================================================================
# MAIN TEST
# ============================================================================

@pytest.mark.parametrize("lang_key", list(LANGUAGE_MOCK_DATA.keys()))
def test_end_to_end_pipeline(lang_key: str, tmp_path: Path):
    """
    Full end-to-end pipeline test for a language.

    Mocks Gemini API at the lowest level (genai.generate_content) so that the
    full parsing → validation → grammar analysis → card assembly chain is exercised.
    Audio and image generation are mocked to return fake file paths.
    """
    data = LANGUAGE_MOCK_DATA[lang_key]
    word = data["word"]
    language_name = data["language_name"]
    language_code = data["language_code"]
    difficulty = data["difficulty"]
    topic = data["topic"]
    num_sentences = data["num_sentences"]
    min_length = data["min_length"]
    max_length = data["max_length"]

    report = PipelineReport(language_name, word, difficulty, topic)

    # ---- Session state mock --------------------------------------------------
    mock_state = _build_mock_session_state(difficulty)

    # We need a dict-like object that also supports attribute access for
    # st.session_state.get() and st.session_state.xxx patterns.
    class MockSessionState(dict):
        def __getattr__(self, name):
            try:
                return self[name]
            except KeyError:
                raise AttributeError(name)
        def __setattr__(self, name, value):
            self[name] = value

    session_state = MockSessionState(mock_state)

    # ---- Build mock Gemini responses -----------------------------------------
    # The pipeline makes two distinct API calls to Gemini:
    #   1. Content generation  (content_generator → genai.generate_content)
    #   2. Grammar analysis    (ja_analyzer._call_ai → genai.generate_content)
    #
    # We use a side-effect function that returns the right response based on
    # whether the call is for content or grammar.

    content_response_text = data["mock_content_response"]
    grammar_response_text = data["mock_grammar_batch_response"]

    call_counter = {"content": 0, "grammar": 0}

    def mock_generate_content(*args, **kwargs):
        """Route mock responses based on prompt content."""
        mock_resp = MagicMock()

        # Inspect the prompt/contents to decide which response to return
        contents = kwargs.get("contents", "")
        if not contents and args:
            # positional: model, contents, ...
            contents = args[1] if len(args) > 1 else ""

        contents_str = str(contents).lower()

        # Grammar analysis prompts contain "grammatical_role" or "grammatical role"
        # or "json" + "words" pattern
        if "grammatical_role" in contents_str or ("json" in contents_str and "words" in contents_str and "sentence" in contents_str):
            mock_resp.text = grammar_response_text
            call_counter["grammar"] += 1
        else:
            # Content generation
            mock_resp.text = content_response_text
            call_counter["content"] += 1

        return mock_resp

    # ---- Mock audio & image generation ---------------------------------------
    def mock_generate_audio(sentences_list, voice, output_dir, **kwargs):
        """Return fake audio file paths."""
        return [f"audio_{i}.mp3" for i in range(len(sentences_list))]

    def mock_generate_images(queries, media_dir, **kwargs):
        """Return fake image file paths and used URLs set."""
        return [f"image_{i}.jpg" for i in range(len(queries))], set()

    # ---- Run the pipeline under mocks ----------------------------------------
    output_dir = str(tmp_path / "output")
    os.makedirs(output_dir, exist_ok=True)

    # Patch points:
    #  1. st.session_state      → our MockSessionState
    #  2. genai.generate_content → mock_generate_content (via the client wrapper)
    #  3. generate_audio         → mock_generate_audio
    #  4. generate_images_pixabay → mock_generate_images
    #  5. genai.configure        → no-op
    #  6. genai.types            → mock with GenerateContentConfig

    mock_genai = MagicMock()
    mock_genai.generate_content = mock_generate_content
    mock_genai.configure = MagicMock()  # no-op
    mock_genai.genai = MagicMock()
    mock_genai.genai.types.GenerateContentConfig = dict  # simple dict for config

    with patch("streamlit.session_state", session_state), \
         patch("streamlit_app.services.generation.content_generator.get_gemini_api", return_value=mock_genai), \
         patch("streamlit_app.shared_utils.get_gemini_api", return_value=mock_genai), \
         patch("streamlit_app.core_functions.generate_audio", mock_generate_audio), \
         patch("streamlit_app.core_functions.generate_images_pixabay", mock_generate_images):

        # ---- STAGE 1: Analyzer Discovery -----------------------------------
        from streamlit_app.language_analyzers.analyzer_registry import AnalyzerRegistry
        registry = AnalyzerRegistry()
        registry._discover_analyzers()
        analyzer = registry.get_analyzer(language_code)
        analyzer_found = analyzer is not None

        report.add_stage(
            "1. Analyzer Discovery",
            analyzer_found,
            f"Analyzer for '{language_code}': {type(analyzer).__name__ if analyzer else 'NOT FOUND'}"
        )

        # ---- STAGE 2: Content Generation -----------------------------------
        from streamlit_app.services.generation.content_generator import ContentGenerator
        cg = ContentGenerator()

        content_result = cg.generate_word_meaning_sentences_and_keywords(
            word=word,
            language=language_name,
            num_sentences=num_sentences,
            gemini_api_key=session_state["google_api_key"],
            min_length=min_length,
            max_length=max_length,
            difficulty=difficulty,
            topics=[topic],
        )

        sentences_parsed = len(content_result.get("sentences", []))
        translations_parsed = len(content_result.get("translations", []))
        ipa_parsed = len(content_result.get("ipa", []))
        keywords_parsed = len(content_result.get("keywords", []))
        meaning = content_result.get("meaning", "")

        content_ok = (
            sentences_parsed == num_sentences
            and translations_parsed == num_sentences
            and meaning != ""
        )

        report.meaning = meaning
        report.add_stage(
            "2. Content Generation + Parsing",
            content_ok,
            f"Meaning: {meaning}\n"
            f"Sentences: {sentences_parsed}/{num_sentences}, "
            f"Translations: {translations_parsed}/{num_sentences}, "
            f"IPA: {ipa_parsed}/{num_sentences}, "
            f"Keywords: {keywords_parsed}/{num_sentences}"
        )

        # ---- Build sentence dicts (mimics sentence_generator.py) -----------
        sentences_list = []
        for i, s in enumerate(content_result.get("sentences", [])):
            sentences_list.append({
                "sentence": s,
                "english_translation": content_result["translations"][i] if i < len(content_result.get("translations", [])) else "",
                "ipa": content_result["ipa"][i] if i < len(content_result.get("ipa", [])) else "",
                "image_keywords": content_result["keywords"][i] if i < len(content_result.get("keywords", [])) else "",
                "context": "general",
                "role_of_word": "target",
                "word": word,
                "meaning": meaning,
            })

        # ---- STAGE 3: Grammar Analysis (batch) -----------------------------
        # Patch _call_ai on the analyzer so it returns our mock grammar JSON
        # instead of actually calling Gemini
        from streamlit_app.services.generation.grammar_processor import GrammarProcessor
        gp = GrammarProcessor()

        grammar_results = gp.batch_analyze_grammar_and_color(
            sentences=[s["sentence"] for s in sentences_list],
            target_words=[word] * len(sentences_list),
            language=language_name,
            gemini_api_key=session_state["google_api_key"],
            language_code=language_code,
        )

        # Merge grammar results into sentence dicts
        grammar_ok = True
        grammar_details = []
        for i, result in enumerate(grammar_results):
            sentences_list[i]["colored_sentence"] = result.get("colored_sentence", "")
            sentences_list[i]["word_explanations"] = result.get("word_explanations", [])
            sentences_list[i]["grammar_summary"] = result.get("grammar_summary", "")

            has_colored = bool(result.get("colored_sentence"))
            has_explanations = len(result.get("word_explanations", [])) > 0
            has_summary = bool(result.get("grammar_summary"))

            sentence_ok = has_colored and has_explanations and has_summary
            grammar_ok = grammar_ok and sentence_ok
            grammar_details.append(
                f"Sentence {i+1}: colored={'YES' if has_colored else 'NO'}, "
                f"explanations={len(result.get('word_explanations', []))}, "
                f"summary={'YES' if has_summary else 'NO'}"
            )

        report.add_stage(
            "3. Grammar Analysis (Batch)",
            grammar_ok,
            "\n".join(grammar_details)
        )
        report.sentences_data = sentences_list

        # ---- STAGE 4: Audio Generation (mocked) ---------------------------
        audio_files = mock_generate_audio(
            [s["sentence"] for s in sentences_list],
            "ja-JP-NanamiNeural",
            str(tmp_path / "media"),
        )
        report.audio_files = audio_files
        report.add_stage(
            "4. Audio Generation (mocked)",
            len(audio_files) == num_sentences,
            f"Generated {len(audio_files)} audio file paths"
        )

        # ---- STAGE 5: Image Generation (mocked) ---------------------------
        image_files, _ = mock_generate_images(
            [s.get("image_keywords", "") for s in sentences_list],
            str(tmp_path / "media"),
        )
        report.image_files = image_files
        report.add_stage(
            "5. Image Generation (mocked)",
            len(image_files) == num_sentences,
            f"Generated {len(image_files)} image file paths"
        )

        # ---- STAGE 6: Card Assembly Verification ---------------------------
        card_assembly_ok = True
        assembly_issues = []
        for i, s in enumerate(sentences_list):
            required = ["sentence", "english_translation", "ipa", "image_keywords",
                        "colored_sentence", "word_explanations", "grammar_summary"]
            for field in required:
                if field not in s or not s[field]:
                    card_assembly_ok = False
                    assembly_issues.append(f"Sentence {i+1} missing '{field}'")

        report.add_stage(
            "6. Card Assembly Verification",
            card_assembly_ok,
            "\n".join(assembly_issues) if assembly_issues else "All required fields present for all sentences"
        )

        # ---- STAGE 7: Difficulty Setting Verification ----------------------
        # Verify that difficulty='beginner' was respected (not overridden to 'intermediate')
        difficulty_ok = session_state.get("difficulty") == difficulty
        report.add_stage(
            "7. Difficulty Setting Respected",
            difficulty_ok,
            f"Session state difficulty: {session_state.get('difficulty')}, expected: {difficulty}"
        )

    # ---- Render & save report ------------------------------------------------
    report_text = report.render()
    print("\n" + report_text)

    report_file = REPORT_DIR / f"pipeline_report_{lang_key}.txt"
    report_file.write_text(report_text, encoding="utf-8")
    logger.info(f"Report saved to {report_file}")

    # ---- Assertions ----------------------------------------------------------
    assert analyzer_found, f"Analyzer for {language_code} was NOT discovered"
    assert content_ok, f"Content generation failed: {sentences_parsed}/{num_sentences} sentences"
    assert grammar_ok, "Grammar analysis missing colored_sentence, word_explanations, or grammar_summary"
    assert card_assembly_ok, f"Card assembly issues: {assembly_issues}"
    assert difficulty_ok, f"Difficulty was overridden: got {session_state.get('difficulty')}, expected {difficulty}"


# ============================================================================
# STANDALONE RUNNER (for running outside pytest)
# ============================================================================
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--tb=short"])
