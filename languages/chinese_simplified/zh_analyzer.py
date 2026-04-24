"""
Chinese Simplified Grammar Analyzer - Main Facade

Following Chinese Traditional Clean Architecture gold standard:
- Clean facade pattern for domain component integration
- Single entry point for all Chinese Simplified analysis
- Error handling and fallback coordination
- Type safety and validation throughout

RESPONSIBILITIES:
1. Coordinate all domain components for analysis
2. Provide unified API for single and batch analysis
3. Handle configuration loading and initialization
4. Manage error recovery and fallback mechanisms
5. Ensure consistent Chinese Simplified linguistic accuracy

INTEGRATION:
- Main entry point for Chinese Simplified analysis
- Used by infrastructure layer (API endpoints, CLI)
- Coordinates with all domain components
- Maintains separation of concerns
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from streamlit_app.language_analyzers.base_analyzer import BaseGrammarAnalyzer, LanguageConfig, GrammarAnalysis

from .domain.zh_config import ZhConfig
from .domain.zh_prompt_builder import ZhPromptBuilder
from .domain.zh_response_parser import ZhResponseParser
from .domain.zh_validator import ZhValidator
from .domain.zh_patterns import ZhPatterns
from .domain.zh_fallbacks import ZhFallbacks

logger = logging.getLogger(__name__)


@dataclass
class AnalysisRequest:
    """Request for grammatical analysis."""
    sentence: str
    target_word: Optional[str] = None
    complexity: str = "intermediate"
    analysis_type: str = "single"  # "single" or "batch"


@dataclass
class AnalysisResult:
    """Result of grammatical analysis."""
    success: bool
    sentence: str
    words: List[Dict[str, Any]]
    overall_structure: str
    key_features: str
    confidence: float
    validation_issues: List[str]
    validation_suggestions: List[str]
    error_message: Optional[str] = None
    fallback_used: bool = False


@dataclass
class BatchAnalysisResult:
    """Result of batch grammatical analysis."""
    success: bool
    results: List[AnalysisResult]
    total_sentences: int
    average_confidence: float
    error_message: Optional[str] = None
    fallback_used: bool = False


class ZhAnalyzer(BaseGrammarAnalyzer):
    """
    Main analyzer facade for Chinese Simplified grammar analysis.

    Following Chinese Traditional Clean Architecture gold standard.
    """

    VERSION = "1.0"
    LANGUAGE_CODE = "zh"
    LANGUAGE_NAME = "Chinese Simplified"

    def __init__(self):
        """
        Initialize analyzer with all domain components.
        """
        # Create language config
        language_config = LanguageConfig(
            code="zh",
            name="Chinese (Simplified)",
            native_name="简体中文",
            family="Sino-Tibetan",
            script_type="logographic",
            complexity_rating="intermediate",
            key_features=["tonal_language", "character_based", "analytic_syntax"],
            supported_complexity_levels=["beginner", "intermediate", "advanced"]
        )

        # Initialize domain components first
        self.zh_config = ZhConfig()
        self.prompt_builder = ZhPromptBuilder(self.zh_config)
        self.response_parser = ZhResponseParser(self.zh_config)
        self.validator = ZhValidator(self.zh_config)
        self.patterns = ZhPatterns(self.zh_config)
        self.fallbacks = ZhFallbacks(self.zh_config)

        # Call parent constructor
        super().__init__(language_config)

        logger.info("ZhAnalyzer initialized with all domain components")

    # ===================================================================
    # CORE ANALYSIS METHODS (mirroring Traditional gold standard)
    # ===================================================================

    def analyze_grammar(self, sentence: str, target_word: str, complexity: str, gemini_api_key: str) -> GrammarAnalysis:
        """Analyze grammar for a single sentence (gold-standard pipeline)."""
        if not sentence or not sentence.strip():
            logger.warning("Empty sentence provided to analyze_grammar")
            return GrammarAnalysis(word_explanations=[], confidence=0.0,
                                   explanation_quality={'quality_score': 0.0, 'issues': ['Empty sentence']},
                                   processing_time=0.0)

        if not target_word or not target_word.strip():
            logger.warning("Empty target_word provided to analyze_grammar")
            return GrammarAnalysis(word_explanations=[], confidence=0.0,
                                   explanation_quality={'quality_score': 0.0, 'issues': ['Empty target word']},
                                   processing_time=0.0)

        if not gemini_api_key or not gemini_api_key.strip():
            logger.warning("Empty API key provided to analyze_grammar")
            return GrammarAnalysis(word_explanations=[], confidence=0.0,
                                   explanation_quality={'quality_score': 0.0, 'issues': ['Invalid API key']},
                                   processing_time=0.0)

        try:
            prompt = self.get_grammar_prompt(complexity, sentence, target_word)
            ai_response = self._call_ai(prompt, gemini_api_key)
            result = self.response_parser.parse_response(ai_response, complexity, sentence, target_word)
            validated_result = self.validator.validate_result(result, sentence)

            # Quality validation (gold standard)
            quality_validation = self.validator.validate_explanation_quality(validated_result)
            validated_result['explanation_quality'] = quality_validation

            base_confidence = validated_result.get('confidence', 0.5)
            quality_score = quality_validation.get('quality_score', 1.0)
            adjusted_confidence = min(base_confidence * quality_score, 1.0)
            validated_result['confidence'] = adjusted_confidence

            if quality_validation.get('issues'):
                logger.info(f"Explanation quality issues for '{sentence}': {quality_validation['issues']}")

            html_output = self._generate_html_output(validated_result, sentence, complexity)

            return GrammarAnalysis(
                sentence=sentence,
                target_word=target_word or "",
                language_code=self.language_code,
                complexity_level=complexity,
                grammatical_elements=validated_result.get('elements', {}),
                explanations=validated_result.get('explanations', {}),
                color_scheme=self.get_color_scheme(complexity),
                html_output=html_output,
                confidence_score=validated_result.get('confidence', 0.0),
                word_explanations=validated_result.get('word_explanations', [])
            )
        except Exception as e:
            logger.error(f"Analysis failed for '{sentence}': {e}")
            # Fixed: use self.fallbacks (matches __init__ and Japanese pattern)
            fallback_result = self.fallbacks.create_fallback(sentence, complexity)
            html_output = self._generate_html_output(fallback_result, sentence, complexity)
            return GrammarAnalysis(
                sentence=sentence,
                target_word=target_word or "",
                language_code=self.language_code,
                complexity_level=complexity,
                grammatical_elements=fallback_result.get('elements', {}),
                explanations=fallback_result.get('explanations', {}),
                color_scheme=self.get_color_scheme(complexity),
                html_output=html_output,
                confidence_score=fallback_result.get('confidence', 0.3),
                word_explanations=fallback_result.get('word_explanations', [])
            )

    def batch_analyze_grammar(self, sentences: List[str], target_words: List[str] = None, complexity: str = "intermediate", gemini_api_key: str = None, target_word: str = "") -> List[Dict[str, Any]]:
        """Batch grammar analysis for Chinese Simplified — matches Japanese pattern exactly."""
        # Normalize: accept both target_words list and legacy target_word kwarg
        if target_words is None:
            target_words = [target_word] * len(sentences) if target_word else [""] * len(sentences)
        logger.info(f"Batch analyze: {len(sentences)} sentences for Chinese Simplified")
        try:
            # Build one batch prompt (Chinese-specific)
            prompt = self.prompt_builder.build_batch_analysis_prompt(sentences, target_words[0] if target_words else "", complexity)
            
            # AI call (lazy import already inside _call_ai)
            ai_response = self._call_ai(prompt, gemini_api_key)
            
            # Parse batch response
            results = self.response_parser.parse_batch_response(ai_response, sentences, complexity, target_words[0] if target_words else "")

            grammar_results = []
            for result, sentence, target_word in zip(results, sentences, target_words):
                validated_result = self.validator.validate_result(result, sentence)
                html_output = self._generate_html_output(validated_result, sentence, complexity)

                grammar_results.append({
                    "colored_sentence": html_output,
                    "word_explanations": validated_result.get('word_explanations', []),
                    "grammar_summary": validated_result.get('grammar_summary', f"Grammar analysis for ZH ({complexity})"),
                    "validation_score": validated_result.get('confidence', 0.0)
                })
            return grammar_results

        except Exception as e:
            logger.error(f"Batch analysis failed: {e}")
            # Safe fallback structure expected by E2E test
            fallback_results = []
            for sentence in sentences:
                fallback_result = self.fallbacks.create_fallback(sentence, complexity) if hasattr(self, 'fallbacks') else {}
                html_output = self._generate_html_output(fallback_result, sentence, complexity)
                fallback_results.append({
                    "colored_sentence": html_output or f"<span>{sentence}</span>",
                    "word_explanations": fallback_result.get('word_explanations', []),
                    "grammar_summary": fallback_result.get('grammar_summary', f"Grammar analysis for ZH ({complexity})"),
                    "validation_score": 0.3
                })
            return fallback_results

    def _call_ai(self, prompt: str, gemini_api_key: str) -> str:
        """Call Google Gemini AI (robust version with max tokens)."""
        logger.info(f"DEBUG: _call_ai called with prompt: {prompt[:200]}...")
        try:
            from streamlit_app.shared_utils import get_gemini_model, get_gemini_fallback_model, get_gemini_api
            api = get_gemini_api()
            api.configure(api_key=gemini_api_key)
            try:
                response = api.generate_content(
                    model=get_gemini_model(),
                    contents=prompt,
                    config={'max_output_tokens': 20000}
                )
                ai_response = response.text.strip()
            except Exception as primary_error:
                logger.warning(f"Primary model failed: {primary_error}")
                response = api.generate_content(
                    model=get_gemini_fallback_model(),
                    contents=prompt,
                    config={'max_output_tokens': 20000}
                )
                ai_response = response.text.strip()
            logger.info(f"AI response received: {ai_response[:500]}...")
            return ai_response
        except Exception as e:
            logger.error(f"AI call failed: {e}")
            return '{"sentence": "error", "words": []}'

    def get_grammar_prompt(self, complexity: str, sentence: str, target_word: str) -> str:
        """Delegate to prompt builder (Simplified-specific)."""
        return self.prompt_builder.build_single_analysis_prompt(sentence, target_word, complexity)

    def get_color_scheme(self, complexity: str) -> Dict[str, str]:
        """Return color scheme."""
        return self.zh_config.get_color_scheme(complexity)
    
    def parse_grammar_response(self, ai_response: str, complexity: str, 
                               sentence: str, target_word: str = "") -> Dict[str, Any]:
        """Parse the raw AI response into structured grammar data.
        Required by BaseGrammarAnalyzer – delegates to domain parser.
        """
        return self.response_parser.parse_response(
            ai_response, complexity, sentence, target_word
        )

    def validate_analysis(self, parsed_data: Dict[str, Any], original_sentence: str) -> float:
        """Validate analysis quality and return confidence score (MUST return float)."""
        result = self.validator.validate_result(parsed_data, original_sentence)
        return result.get('confidence', 0.0)  

    def _generate_html_output(self, parsed_data: Dict[str, Any], sentence: str, complexity: str) -> str:
        """Generate colored HTML for Chinese Simplified sentences."""
        # Safe guard against non-dict (ValidationResult dataclass or similar)
        if not isinstance(parsed_data, dict):
            parsed_data = getattr(parsed_data, '__dict__', {}) if hasattr(parsed_data, '__dict__') else {}

        explanations = parsed_data.get('word_explanations', [])
        color_scheme = self.get_color_scheme(complexity)

        if not explanations:
            return sentence  # fallback — at least show the sentence

        # Chinese-specific coloring (character-based, no spaces)
        html_parts = []
        covered = 0

        for exp in explanations:
            if len(exp) < 3:
                continue
            word = exp[0]
            role = exp[1]
            category = self._map_grammatical_role_to_category(role)
            color = color_scheme.get(category, color_scheme.get('other', '#AAAAAA'))

            idx = sentence.find(word, covered)
            if idx == -1:
                idx = sentence.find(word)

            if idx != -1:
                if idx > covered:
                    uncovered = sentence[covered:idx]
                    html_parts.append(f'<span style="color: {color_scheme.get("other", "#AAAAAA")}; font-weight: bold;">{uncovered}</span>')
                html_parts.append(f'<span style="color: {color}; font-weight: bold;">{word}</span>')
                covered = idx + len(word)
            else:
                html_parts.append(f'<span style="color: {color}; font-weight: bold;">{word}</span>')

        if covered < len(sentence):
            remaining = sentence[covered:]
            html_parts.append(f'<span style="color: {color_scheme.get("other", "#AAAAAA")}; font-weight: bold;">{remaining}</span>')

        return ''.join(html_parts)
    
    def _map_grammatical_role_to_category(self, role: str) -> str:
        """Map specific grammatical roles to color categories (required by _generate_html_output)."""
        hierarchy = getattr(self.zh_config, 'grammatical_roles', {}).get('role_hierarchy', {})
        return hierarchy.get(role, role)

    # ===================================================================
    # ADDITIONAL METHODS (kept for full compatibility)
    # ===================================================================

    def get_sentence_generation_prompt(self, word, language, num_sentences, enriched_meaning="", min_length=3, max_length=15, difficulty="intermediate", topics=None):
        """Delegate to Chinese prompt builder (required by agent spec)."""
        return self.prompt_builder.get_sentence_generation_prompt(
            word, language, num_sentences, enriched_meaning, min_length, max_length, difficulty, topics
        )

    def get_component_status(self) -> Dict[str, Any]:
        """Get status of all domain components."""
        return {
            "config_loaded": bool(self.zh_config.grammatical_roles),
            "patterns_available": self.patterns.get_pattern_info() if hasattr(self.patterns, 'get_pattern_info') else True,
            "complexity_levels": ["beginner", "intermediate", "advanced"],
            "grammatical_roles_count": len(self.zh_config.grammatical_roles),
            "color_schemes": {level: len(self.get_color_scheme(level)) for level in ["beginner", "intermediate", "advanced"]}
        }