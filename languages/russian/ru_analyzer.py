# languages/russian/ru_analyzer.py
"""
Russian Grammar Analyzer — Facade

Implements BaseGrammarAnalyzer for the Russian language.
Orchestrates domain components: config, prompt_builder, response_parser,
validator, fallbacks.

Lazy imports inside _call_ai() follow the required pattern to support test
mocking and avoid cross-test contamination (see CLAUDE.md — Analyzer import
patterns).

Class name: RuAnalyzer  (auto-discovered by analyzer_registry.py)
"""

import logging
import time
from typing import Any, Dict, List, Optional

from streamlit_app.language_analyzers.base_analyzer import (
    BaseGrammarAnalyzer,
    GrammarAnalysis,
    LanguageConfig,
)

from .domain.ru_config import RuConfig
from .domain.ru_prompt_builder import RuPromptBuilder
from .domain.ru_response_parser import RuResponseParser
from .domain.ru_fallbacks import RuFallbacks
from .domain.ru_validator import RuValidator

logger = logging.getLogger(__name__)


class RuAnalyzer(BaseGrammarAnalyzer):
    """
    Grammar analyzer for Russian (Русский язык).

    Russian — Indo-European, East Slavic branch.
    Key features: 6 cases, 3 genders (masc/fem/neut, plus common), aspect
    system (imperfective ↔ perfective pairs), reflexive verbs (-ся/-сь),
    4 participle types, gerunds (verbal adverbs), free word order driven
    by information structure.

    Script: Cyrillic (LTR).
    Complexity levels: beginner, intermediate, advanced.
    """

    VERSION = "1.0"
    LANGUAGE_CODE = "ru"
    LANGUAGE_NAME = "Russian"

    def __init__(self):
        # Initialise domain components
        self.ru_config = RuConfig()
        self.ru_fallbacks = RuFallbacks(self.ru_config)
        self.prompt_builder = RuPromptBuilder(self.ru_config)
        self.response_parser = RuResponseParser(self.ru_config, self.ru_fallbacks)
        self.validator = RuValidator(self.ru_config)

        config = LanguageConfig(
            code="ru",
            name="Russian",
            native_name="Русский",
            family="Indo-European",
            script_type="alphabetic",
            complexity_rating="high",
            key_features=[
                "case_system",
                "grammatical_gender",
                "verbal_aspect",
                "reflexive_verbs",
                "participial_system",
                "gerunds",
                "free_word_order",
                "pro_drop",
                "null_copula_present",
                "verbs_of_motion",
                "negative_concord",
            ],
            supported_complexity_levels=["beginner", "intermediate", "advanced"],
        )
        super().__init__(config)

    # ------------------------------------------------------------------
    # BaseGrammarAnalyzer abstract methods
    # ------------------------------------------------------------------

    def get_grammar_prompt(
        self, complexity: str, sentence: str, target_word: str
    ) -> str:
        return self.prompt_builder.build_single_prompt(
            sentence, target_word, complexity
        )

    def parse_grammar_response(
        self, ai_response: str, complexity: str, sentence: str
    ) -> Dict[str, Any]:
        return self.response_parser.parse_response(
            ai_response, complexity, sentence
        )

    def get_color_scheme(self, complexity: str) -> Dict[str, str]:
        return self.ru_config.get_color_scheme(complexity)

    def validate_analysis(
        self, parsed_data: Dict[str, Any], original_sentence: str
    ) -> float:
        result = self.validator.validate_result(parsed_data, original_sentence)
        return result.get("confidence", 0.0)

    # ------------------------------------------------------------------
    # Single-sentence analysis
    # ------------------------------------------------------------------

    def analyze_grammar(
        self,
        sentence: str,
        target_word: str,
        complexity: str,
        gemini_api_key: str,
    ) -> GrammarAnalysis:
        """Analyse grammar for a single Russian sentence."""
        try:
            start = time.time()
            prompt = self.prompt_builder.build_single_prompt(
                sentence, target_word, complexity
            )
            ai_response = self._call_ai(prompt, gemini_api_key)
            result = self.response_parser.parse_response(
                ai_response, complexity, sentence, target_word
            )
            validated = self.validator.validate_result(result, sentence)

            quality = self.validator.validate_explanation_quality(validated)
            base_conf = validated.get("confidence", 0.5)
            quality_score = quality.get("quality_score", 1.0)
            confidence = min(base_conf * quality_score, 1.0)
            validated["confidence"] = confidence

            html_output = self._generate_html_output(validated, sentence, complexity)
            elapsed = time.time() - start
            logger.info(
                f"Russian analysis done in {elapsed:.2f}s, confidence={confidence:.2f}"
            )
            return GrammarAnalysis(
                sentence=sentence,
                target_word=target_word or "",
                language_code=self.language_code,
                complexity_level=complexity,
                grammatical_elements=validated.get("elements", {}),
                explanations=validated.get("explanations", {}),
                word_explanations=self._format_word_explanations(
                    validated.get("word_explanations", [])
                ),
                color_scheme=self.get_color_scheme(complexity),
                html_output=html_output,
                confidence_score=confidence,
            )
        except Exception as exc:
            logger.error(f"Russian analysis failed: {exc}")
            fallback = self.ru_fallbacks.create_fallback(sentence, complexity)
            html_output = self._generate_html_output(fallback, sentence, complexity)
            return GrammarAnalysis(
                sentence=sentence,
                target_word=target_word or "",
                language_code=self.language_code,
                complexity_level=complexity,
                grammatical_elements=fallback.get("elements", {}),
                explanations=fallback.get("explanations", {}),
                word_explanations=self._format_word_explanations(
                    fallback.get("word_explanations", [])
                ),
                color_scheme=self.get_color_scheme(complexity),
                html_output=html_output,
                confidence_score=fallback.get("confidence", 0.3),
            )

    # ------------------------------------------------------------------
    # Batch analysis — matches Japanese ja_analyzer.py / Latvian lv_analyzer.py
    # pattern exactly. Returns List[GrammarAnalysis].
    # ------------------------------------------------------------------

    def batch_analyze_grammar(
        self,
        sentences: List[str],
        target_word,
        complexity: str,
        gemini_api_key: str = "",
    ) -> List[GrammarAnalysis]:
        """Analyse grammar for multiple Russian sentences in one AI call.

        ``target_word`` may be a single string (broadcast to every sentence)
        or a list of per-sentence targets.
        """
        logger.info(
            f"Batch analyse: {len(sentences)} sentences, complexity={complexity}"
        )
        try:
            prompt = self.prompt_builder.build_batch_prompt(
                sentences, target_word, complexity
            )
            ai_response = self._call_ai(prompt, gemini_api_key)
            results = self.response_parser.parse_batch_response(
                ai_response, sentences, complexity,
                target_word if isinstance(target_word, str) else "",
            )

            grammar_analyses = []
            for result, sentence in zip(results, sentences):
                validated = self.validator.validate_result(result, sentence)
                html_output = self._generate_html_output(
                    validated, sentence, complexity
                )
                tw = (
                    target_word if isinstance(target_word, str)
                    else (target_word[0] if target_word else "")
                )
                grammar_analyses.append(
                    GrammarAnalysis(
                        sentence=sentence,
                        target_word=tw or "",
                        language_code=self.language_code,
                        complexity_level=complexity,
                        grammatical_elements=validated.get("elements", {}),
                        explanations=validated.get("explanations", {}),
                        color_scheme=self.get_color_scheme(complexity),
                        html_output=html_output,
                        confidence_score=validated.get("confidence", 0.0),
                        word_explanations=self._format_word_explanations(
                            validated.get("word_explanations", [])
                        ),
                    )
                )
            return grammar_analyses

        except Exception as exc:
            logger.error(f"Batch analysis failed: {exc}")
            fallback_analyses = []
            for sentence in sentences:
                fallback = self.ru_fallbacks.create_fallback(sentence, complexity)
                html_output = self._generate_html_output(
                    fallback, sentence, complexity
                )
                tw = (
                    target_word if isinstance(target_word, str)
                    else (target_word[0] if target_word else "")
                )
                fallback_analyses.append(
                    GrammarAnalysis(
                        sentence=sentence,
                        target_word=tw or "",
                        language_code=self.language_code,
                        complexity_level=complexity,
                        grammatical_elements=fallback.get("elements", {}),
                        explanations=fallback.get("explanations", {}),
                        color_scheme=self.get_color_scheme(complexity),
                        html_output=html_output,
                        confidence_score=fallback.get("confidence", 0.3),
                        word_explanations=self._format_word_explanations(
                            fallback.get("word_explanations", [])
                        ),
                    )
                )
            return fallback_analyses

    # ------------------------------------------------------------------
    # AI call — lazy import to support test mocking (per CLAUDE.md)
    # ------------------------------------------------------------------

    def _call_ai(self, prompt: str, gemini_api_key: str = "") -> str:
        """Call Gemini AI for Russian grammar analysis. Lazy imports required.

        Implements the canonical primary→fallback model retry pattern with
        exponential backoff. Each attempt extracts the response text via
        ``_extract_response_text`` so a None/empty ``.text`` (caused by safety
        filter or max-tokens) is converted to a clean RuntimeError instead of
        an opaque ``AttributeError`` at the next ``.strip()`` call.
        """
        from streamlit_app.shared_utils import (
            get_gemini_api,
            get_gemini_fallback_model,
            get_gemini_model,
        )

        max_retries = 3
        base_delay = 1.0

        for attempt in range(max_retries):
            try:
                api = get_gemini_api()
                api.configure(api_key=gemini_api_key)

                try:
                    response = api.generate_content(
                        model=get_gemini_model(),
                        contents=prompt,
                        config={"max_output_tokens": 20000, "temperature": 0.1},
                    )
                    return self._extract_response_text(response)

                except Exception as primary_error:
                    logger.warning(
                        f"Primary model failed (attempt {attempt+1}): "
                        f"{str(primary_error)[:200]}"
                    )
                    try:
                        response = api.generate_content(
                            model=get_gemini_fallback_model(),
                            contents=prompt,
                            config={
                                "max_output_tokens": 20000,
                                "temperature": 0.1,
                            },
                        )
                        return self._extract_response_text(response)
                    except Exception as fallback_error:
                        logger.warning(
                            f"Fallback model also failed (attempt {attempt+1}): "
                            f"{str(fallback_error)[:200]}"
                        )
                        if attempt < max_retries - 1:
                            time.sleep(base_delay * (2 ** attempt))
                        else:
                            raise fallback_error

            except Exception as exc:
                logger.error(
                    f"All models failed on attempt {attempt+1}: {str(exc)[:200]}"
                )
                if attempt < max_retries - 1:
                    time.sleep(base_delay * (2 ** attempt))
                else:
                    return '{"error": "AI service unavailable", "sentence": "error"}'

        return '{"error": "AI service unavailable", "sentence": "error"}'

    @staticmethod
    def _extract_response_text(response) -> str:
        """Pull .text from a Gemini response, raising if it's missing.

        Gemini can return a 200 OK with ``response.text = None`` when the
        completion is blocked by a safety filter or hits the max-tokens cap.
        Letting ``.strip()`` raise ``AttributeError`` surfaces that as a
        confusing crash; raising a clean ``RuntimeError`` instead lets the
        retry/fallback layer above this method swap models.
        """
        text = getattr(response, "text", None)
        if not text or not str(text).strip():
            raise RuntimeError(
                "Gemini returned empty .text "
                "(likely safety filter or max-tokens hit)"
            )
        return str(text).strip()

    # ------------------------------------------------------------------
    # HTML output generation
    # ------------------------------------------------------------------

    def _format_word_explanations(self, raw: list) -> list:
        """Convert word_explanations to [word, role, color, meaning] list format.

        Per CLAUDE.md grammar-coloring invariant — pass through the original
        POS label and color from the analyzer; do NOT remap to a generic
        category.
        """
        result = []
        for item in raw:
            if isinstance(item, dict):
                result.append([
                    item.get("word", ""),
                    item.get("role", "other"),
                    item.get("color", "#CCCCCC"),
                    item.get("meaning", item.get("word", "")),
                ])
            elif isinstance(item, (list, tuple)) and len(item) >= 4:
                result.append(list(item))
        return result

    def _generate_html_output(
        self,
        parsed_data: Dict[str, Any],
        sentence: str,
        complexity: str,
    ) -> str:
        """Generate HTML with inline color styling for Anki display."""
        explanations = parsed_data.get("word_explanations", [])
        if not explanations:
            return f'<span style="color:#CCCCCC">{sentence}</span>'

        parts = []
        for item in explanations:
            if not isinstance(item, dict):
                continue
            word = item.get("word", "")
            color = item.get("color", "#CCCCCC")
            meaning = item.get("meaning", word)
            role = item.get("role", "other")
            tooltip = f"{role}: {meaning}"
            parts.append(
                f'<span style="color:{color}" title="{tooltip}">{word}</span>'
            )
        return " ".join(parts)

    def _map_grammatical_role_to_category(self, role: str) -> str:
        """Map a Russian role label to a broad category (for legacy callers)."""
        mapping = {
            "noun": "noun",
            "verb": "verb",
            "imperfective_verb": "verb",
            "perfective_verb": "verb",
            "infinitive": "verb",
            "imperative": "verb",
            "modal_verb": "verb",
            "auxiliary": "auxiliary",
            "copula": "auxiliary",
            "reflexive_verb": "verb",
            "adjective": "adjective",
            "short_adjective": "adjective",
            "comparative": "adjective",
            "superlative": "adjective",
            "adverb": "adverb",
            "pronoun": "pronoun",
            "personal_pronoun": "pronoun",
            "possessive_pronoun": "pronoun",
            "possessive_determiner": "pronoun",
            "reflexive_pronoun": "pronoun",
            "demonstrative": "pronoun",
            "relative_pronoun": "pronoun",
            "interrogative_pronoun": "pronoun",
            "indefinite_pronoun": "pronoun",
            "negative_pronoun": "pronoun",
            "preposition": "preposition",
            "conjunction": "conjunction",
            "coordinating_conjunction": "conjunction",
            "subordinating_conjunction": "conjunction",
            "particle": "particle",
            "aspectual_particle": "particle",
            "conditional_particle": "particle",
            "negation_particle": "particle",
            "numeral": "numeral",
            "interjection": "interjection",
            "participle": "participle",
            "present_active_participle": "participle",
            "past_active_participle": "participle",
            "present_passive_participle": "participle",
            "past_passive_participle": "participle",
            "gerund": "gerund",
            "verbal_noun": "noun",
            "other": "other",
        }
        return mapping.get(role, "other")

    # ------------------------------------------------------------------
    # Sentence generation prompt — Russian-specific
    # ------------------------------------------------------------------

    def get_sentence_generation_prompt(
        self,
        word: str,
        language: str,
        num_sentences: int,
        enriched_meaning: str = "",
        min_length: int = 3,
        max_length: int = 15,
        difficulty: str = "intermediate",
        topics: Optional[List[str]] = None,
    ) -> Optional[str]:
        """Russian-specific sentence generation prompt.

        Enforces character limits (75 chars for meanings, 60 for restrictions)
        and surfaces Russian-specific morphology (cases, aspect, reflexive
        verbs, governed cases on prepositions, animacy on masc-acc).
        """
        if topics:
            context_instruction = (
                f"- CRITICAL REQUIREMENT: ALL sentences MUST relate to these specific "
                f"topics: {', '.join(topics)}. Force the word usage into these contexts "
                f"even if it requires creative interpretation. Do NOT use generic contexts."
            )
        else:
            context_instruction = (
                "- Use diverse real-life contexts: home, travel, food, emotions, work, "
                "social life, daily actions, cultural experiences"
            )

        if enriched_meaning and enriched_meaning != "N/A":
            enriched_meaning_instruction = (
                f'Use this pre-reviewed meaning for "{word}": "{enriched_meaning[:200]}". '
                f"Generate a clean English meaning based on this."
            )
        else:
            enriched_meaning_instruction = (
                f'Provide a brief English meaning for "{word}".'
            )

        prompt = f"""You are a native-level expert linguist in Russian (Русский язык).

Your task: Generate a complete learning package for the Russian word "{word}" in ONE response.

===========================
STEP 1: WORD MEANING
===========================
{enriched_meaning_instruction}
Format: Return exactly one line like "house (a building where people live)" or "he (male pronoun, used as subject)"
IMPORTANT: Keep the entire meaning under 75 characters total.

===========================
WORD-SPECIFIC RESTRICTIONS
===========================
Based on the meaning above, identify any grammatical constraints for "{word}".
Examples: gender requirements (masculine/feminine/neuter), aspect (imperfective/perfective), case-government for prepositions, animacy, conjugation class.
If no restrictions apply, state "No specific grammatical restrictions."
IMPORTANT: Keep the entire restrictions summary under 60 characters total.

===========================
STEP 2: SENTENCES
===========================
Generate exactly {num_sentences} highly natural, idiomatic sentences in Russian for the word "{word}".

QUALITY RULES:
- Every sentence must sound like native Russian
- Grammar, syntax, spelling, and Russian-specific features must be correct
- The target word "{word}" MUST be used correctly according to restrictions
- Each sentence must be between {min_length} and {max_length} words long
- COUNT words precisely; if outside the range, regenerate internally
- Difficulty: {difficulty}

RUSSIAN-SPECIFIC REQUIREMENTS:
- Apply correct case marking — Russian has 6 cases: nominative, genitive, dative, accusative, instrumental, prepositional
- Use proper gender agreement (masc -∅/-й/-ь, fem -а/-я/-ь, neut -о/-е/-ё)
- For verbs, choose the correct ASPECT (imperfective for ongoing/habitual; perfective for completed/single-event); pair with the correct tense
- Apply correct verb conjugation by person (1st/2nd/3rd) and number (singular/plural); past tense agrees in gender
- Use correct preposition + case combinations (в/на + acc for motion, + prep for location; с + gen/inst; у + gen; к + dat; о/об + prep)
- Apply animacy where it matters (masc-acc and pl-acc: animate = gen-shaped, inanimate = nom-shaped)
- Use reflexive verbs (-ся / -сь) where natural
- Cyrillic only — no Latin transliteration in the sentences

VARIETY REQUIREMENTS:
- Use different verb tenses and aspects when applicable
- Include different pronoun types (personal, possessive, demonstrative, reflexive)
- Use prepositional phrases with different cases
- Use both simple and complex sentence structures
{context_instruction}

===========================
STEP 3: ENGLISH TRANSLATIONS
===========================
For EACH sentence above, provide a natural, fluent English translation.

===========================
STEP 4: IPA TRANSCRIPTION
===========================
For EACH sentence above, provide IPA phonetic transcription using standard IPA symbols for Russian (include stress marks where unambiguous).

===========================
STEP 5: IMAGE KEYWORDS
===========================
For EACH sentence above, generate exactly 3 specific keywords for image search.
- Keywords should be concrete and specific
- Keywords in English only

===========================
OUTPUT FORMAT - FOLLOW EXACTLY
===========================
Return your response in this exact text format:

MEANING: [brief English meaning]

RESTRICTIONS: [grammatical restrictions]

SENTENCES:
1. [sentence 1 in Russian]
2. [sentence 2 in Russian]

TRANSLATIONS:
1. [natural English translation for sentence 1]
2. [natural English translation for sentence 2]

IPA:
1. [IPA transcription for sentence 1]
2. [IPA transcription for sentence 2]

KEYWORDS:
1. [keyword1, keyword2, keyword3]
2. [keyword1, keyword2, keyword3]

IMPORTANT:
- Return ONLY the formatted text, no extra explanation
- Sentences must be in Russian (Cyrillic) only
- Ensure exactly {num_sentences} sentences, translations, IPA transcriptions, and keywords
- Respect character limits for meaning and restrictions"""
        return prompt
