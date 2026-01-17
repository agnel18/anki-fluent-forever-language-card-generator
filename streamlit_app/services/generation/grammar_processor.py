"""
Grammar Processor Service

Handles grammar analysis and sentence coloring using language analyzers.
Extracted from sentence_generator.py for better separation of concerns.
"""

import json
import logging
from typing import Dict, Any, List, Optional

# Import the new grammar analyzer system
try:
    from language_analyzers.analyzer_registry import get_analyzer
    logger = logging.getLogger(__name__)
    logger.info("Successfully imported analyzer registry")
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"Failed to import analyzer registry: {e}. Grammar analysis will be unavailable.")
    get_analyzer = None

logger = logging.getLogger(__name__)


class GrammarProcessor:
    """
    Service for processing grammar analysis and sentence coloring.
    """

    def analyze_grammar_and_color(
        self,
        sentence: str,
        word: str,
        language: str,
        groq_api_key: str,
        language_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze grammar and provide colored sentence with explanations.

        Args:
            sentence: The sentence to analyze
            word: Target word in the sentence
            language: Language name
            groq_api_key: API key for fallback analysis
            language_code: ISO language code (optional)

        Returns:
            Dict with colored_sentence, word_explanations, and grammar_summary
        """
        # Try to get language-specific analyzer
        analyzer = None
        if language_code:
            analyzer = get_analyzer(language_code) if get_analyzer else None

        if analyzer:
            # Use the language-specific analyzer
            logger.info(f"Using {language_code} analyzer for grammar analysis")
            try:
                # Determine complexity level (default to intermediate)
                complexity = "intermediate"

                # Analyze grammar using the language-specific analyzer
                analysis_result = analyzer.analyze_grammar(
                    sentence=sentence,
                    target_word=word,
                    complexity=complexity,
                    groq_api_key=groq_api_key
                )

                # Convert analyzer result to expected format
                colored_sentence = analysis_result.html_output
                word_explanations = self._convert_analyzer_output_to_explanations(analysis_result, language_code)
                grammar_summary = self._create_grammar_summary(analysis_result, language_code)

                result = {
                    "colored_sentence": colored_sentence,
                    "word_explanations": word_explanations,
                    "grammar_summary": grammar_summary
                }

                # API usage tracking
                try:
                    import streamlit as st
                    if "groq_api_calls" not in st.session_state:
                        st.session_state.groq_api_calls = 0
                    if "groq_tokens_used" not in st.session_state:
                        st.session_state.groq_tokens_used = 0
                    st.session_state.groq_api_calls += 1
                    st.session_state.groq_tokens_used += 150
                except Exception:
                    pass

                logger.info(f"Grammar analysis completed using {language_code} analyzer")
                return result

            except Exception as e:
                logger.warning(f"Language-specific analyzer failed for {language_code}: {e}, falling back to generic analysis")

        # Fallback to generic analysis
        logger.info(f"Using generic grammar analysis for {language}")
        return self._analyze_grammar_generic(sentence, word, language, groq_api_key)

    def _convert_analyzer_output_to_explanations(self, analysis_result, language_code: str) -> List[List[Any]]:
        """Convert analyzer output to word explanations format."""
        word_explanations = []

        # First, try to use word_explanations directly if available (preferred for detailed analysis)
        if hasattr(analysis_result, 'word_explanations') and analysis_result.word_explanations:
            logger.info(f"Using word_explanations directly from analyzer result ({len(analysis_result.word_explanations)} items)")
            for exp in analysis_result.word_explanations:
                if len(exp) >= 4:
                    word, pos, color, explanation = exp[0], exp[1], exp[2], exp[3]
                    # Map POS to category for consistency
                    category = self._map_pos_to_category(pos)
                    word_explanations.append([word, category, color, explanation])
            return word_explanations

        # Fallback: combine grammatical elements and explanations
        elements = analysis_result.grammatical_elements
        explanations = analysis_result.explanations

        for element_type, element_list in elements.items():
            for element in element_list:
                word = element.get('word', '')
                if word:
                    # Find corresponding explanation
                    explanation = explanations.get(element_type, f"{element_type} in {language_code} grammar")
                    color = analysis_result.color_scheme.get(element_type, '#CCCCCC')

                    word_explanations.append([word, element_type, color, explanation])

        logger.info(f"Generated {len(word_explanations)} word explanations")
        return word_explanations

    def _map_pos_to_category(self, pos: str) -> str:
        """Map part-of-speech tags to grammatical categories."""
        pos_lower = pos.lower()

        # Map various POS tags to categories
        if any(keyword in pos_lower for keyword in ['pronoun', 'personal', 'demonstrative', 'possessive', 'reflexive']):
            return 'pronoun'
        elif any(keyword in pos_lower for keyword in ['verb', 'auxiliary', 'modal', 'linking']):
            return 'verb'
        elif any(keyword in pos_lower for keyword in ['noun', 'proper noun']):
            return 'noun'
        elif any(keyword in pos_lower for keyword in ['adjective', 'determiner']):
            return 'adjective'
        elif any(keyword in pos_lower for keyword in ['adverb']):
            return 'adverb'
        elif any(keyword in pos_lower for keyword in ['preposition', 'postposition', 'case marker']):
            return 'postposition'
        elif any(keyword in pos_lower for keyword in ['conjunction', 'subordinating', 'coordinating']):
            return 'conjunction'
        elif any(keyword in pos_lower for keyword in ['interjection', 'interrogative']):
            return 'interjection'
        elif any(keyword in pos_lower for keyword in ['numeral', 'number']):
            return 'numeral'
        else:
            return 'other'

    def _create_grammar_summary(self, analysis_result, language_code: str) -> str:
        """Create grammar summary from analysis result."""
        # Try to get meaningful summary from explanations
        if hasattr(analysis_result, 'explanations') and analysis_result.explanations:
            # Look for overall structure or key features
            overall = analysis_result.explanations.get('overall_structure', '')
            key_features = analysis_result.explanations.get('key_features', '')

            if overall and key_features:
                return f"{overall} {key_features}"
            elif overall:
                return overall
            elif key_features:
                return key_features

        # Try to build summary from word explanations
        if hasattr(analysis_result, 'word_explanations') and analysis_result.word_explanations:
            categories = {}
            for exp in analysis_result.word_explanations:
                if len(exp) >= 2:
                    category = self._map_pos_to_category(exp[1])
                    categories[category] = categories.get(category, 0) + 1

            if categories:
                category_summary = ", ".join([f"{count} {cat}{'s' if count > 1 else ''}" for cat, count in categories.items()])
                return f"Sentence contains {category_summary}"

        # Fallback to generic summary
        return f"Grammar analysis for {language_code.upper()}"

    def _analyze_grammar_generic(
        self,
        sentence: str,
        word: str,
        language: str,
        groq_api_key: str,
    ) -> Dict[str, Any]:
        """
        Generic grammar analysis fallback when no language-specific analyzer is available.
        """
        from groq import Groq

        client = Groq(api_key=groq_api_key)

        # Color mapping for different POS categories
        color_map = {
            "noun": "#FF6B6B",        # Red - things/objects
            "verb": "#4ECDC4",        # Teal - actions
            "adjective": "#45B7D1",   # Blue - descriptions
            "adverb": "#96CEB4",      # Green - how/when/where
            "pronoun": "#FFEAA7",     # Yellow - replacements
            "preposition": "#DDA0DD", # Plum - relationships
            "conjunction": "#98D8C8", # Mint - connections
            "article": "#F7DC6F",     # Light yellow - determiners
            "interjection": "#FF9999", # Light red - exclamations
            "other": "#CCCCCC"        # Gray - other parts
        }

        prompt = f"""You are a linguistics expert specializing in {language} grammar analysis for language learners.

TASK: Analyze this {language} sentence and provide grammatical coloring information.

SENTENCE: "{sentence}"
TARGET WORD: "{word}"

INSTRUCTIONS:
1. Break down the sentence into individual words/tokens
2. For each word, identify its part of speech (POS) category
3. Assign an appropriate color based on POS
4. Provide a brief explanation for each word's grammatical role

COLOR CATEGORIES (use these exact names):
- noun (red): people, places, things, ideas
- verb (teal): actions, states, occurrences
- adjective (blue): descriptions of nouns
- adverb (green): modify verbs, adjectives, other adverbs
- pronoun (yellow): replace nouns (he, she, it, they, etc.)
- preposition (plum): show relationships (in, on, at, with, etc.)
- conjunction (mint): connect clauses (and, but, or, because, etc.)
- article (light yellow): determiners (the, a, an)
- interjection (light red): exclamations (oh, wow, hey)
- other (gray): numbers, punctuation, unclassified words

OUTPUT FORMAT: Return ONLY a valid JSON object with this exact structure:
{{
  "colored_sentence": "<span style='color: #COLOR1'>word1</span> <span style='color: #COLOR2'>word2</span> ...",
  "word_explanations": [
    ["word1", "pos_category", "#COLOR1", "brief explanation of grammatical role"],
    ["word2", "pos_category", "#COLOR2", "brief explanation of grammatical role"],
    ...
  ],
  "grammar_summary": "Brief summary of the sentence's grammatical structure"
}}

IMPORTANT:
- Return ONLY valid JSON, no extra text
- Use the exact color codes from the categories above
- Ensure the colored_sentence contains the original sentence with proper HTML span tags
- Each word_explanations entry must have exactly 4 elements: [word, pos, color, explanation]"""

        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,  # Lower temperature for consistent analysis
                max_tokens=1500,
            )

            response_text = response.choices[0].message.content.strip()

            # Parse JSON response
            try:
                result = json.loads(response_text)
                # Validate required fields
                if not all(key in result for key in ['colored_sentence', 'word_explanations', 'grammar_summary']):
                    raise ValueError("Missing required fields in response")

                # API usage tracking
                try:
                    import streamlit as st
                    if "groq_api_calls" not in st.session_state:
                        st.session_state.groq_api_calls = 0
                    if "groq_tokens_used" not in st.session_state:
                        st.session_state.groq_tokens_used = 0
                    st.session_state.groq_api_calls += 1
                    st.session_state.groq_tokens_used += 100
                except Exception:
                    pass

                logger.info("Generic grammar analysis completed")
                return result

            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Failed to parse generic grammar analysis response: {e}")
                # Return fallback
                return self._create_generic_fallback(sentence, word, language)

        except Exception as e:
            logger.error(f"Error in generic grammar analysis: {e}")
            return self._create_generic_fallback(sentence, word, language)

    def _create_generic_fallback(self, sentence: str, word: str, language: str) -> Dict[str, Any]:
        """Create fallback grammar analysis when AI fails."""
        # Simple word-by-word coloring
        words = sentence.split()
        colored_parts = []
        explanations = []

        for w in words:
            if w.lower() == word.lower():
                # Highlight target word
                colored_parts.append(f"<span style='color: #FF6B6B'>{w}</span>")
                explanations.append([w, "target_word", "#FF6B6B", f"Target word: {word}"])
            else:
                # Generic coloring
                colored_parts.append(f"<span style='color: #CCCCCC'>{w}</span>")
                explanations.append([w, "other", "#CCCCCC", "Other word in sentence"])

        return {
            "colored_sentence": " ".join(colored_parts),
            "word_explanations": explanations,
            "grammar_summary": f"Basic analysis of {language} sentence structure"
        }

    def batch_analyze_grammar_and_color(
        self,
        sentences: List[str],
        target_words: List[str],
        language: str,
        groq_api_key: str,
        language_code: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Analyze multiple sentences in batches of 8 for optimal efficiency.
        Processes sentences in chunks of 8 to minimize API calls while staying within model limits.

        Args:
            sentences: List of sentences to analyze
            target_words: Corresponding target words
            language: Language name
            groq_api_key: API key
            language_code: ISO language code

        Returns:
            List of analysis results
        """
        if not sentences:
            return []

        # Try to get language-specific analyzer for batch processing
        analyzer = None
        if language_code:
            analyzer = get_analyzer(language_code) if get_analyzer else None

        if analyzer and hasattr(analyzer, 'batch_analyze_grammar'):
            # Use 8-sentence batch processing for efficiency
            logger.info(f"Using 8-sentence batch processing with {language_code} analyzer for {len(sentences)} sentences")

            try:
                # Process sentences in chunks of 8
                BATCH_SIZE = 8
                all_results = []

                for batch_start in range(0, len(sentences), BATCH_SIZE):
                    batch_end = min(batch_start + BATCH_SIZE, len(sentences))
                    batch_sentences = sentences[batch_start:batch_end]
                    batch_target_words = target_words[batch_start:batch_end] if target_words else [sentences[batch_start].split()[0]] * len(batch_sentences)

                    logger.info(f"Processing batch {batch_start//BATCH_SIZE + 1}: sentences {batch_start + 1}-{batch_end}")

                    # Determine complexity level (default to intermediate)
                    complexity = "intermediate"

                    # Use same target word for all sentences in batch (common case)
                    target_word = batch_target_words[0] if batch_target_words else batch_sentences[0].split()[0]

                    # Batch analyze this chunk of 8 sentences at once
                    batch_results = analyzer.batch_analyze_grammar(
                        sentences=batch_sentences,
                        target_word=target_word,
                        complexity=complexity,
                        groq_api_key=groq_api_key
                    )

                    # Convert to expected format
                    for i, analysis_result in enumerate(batch_results):
                        try:
                            colored_sentence = analysis_result.html_output
                            word_explanations = self._convert_analyzer_output_to_explanations(analysis_result, language_code)
                            grammar_summary = self._create_grammar_summary(analysis_result, language_code)

                            result = {
                                "colored_sentence": colored_sentence,
                                "word_explanations": word_explanations,
                                "grammar_summary": grammar_summary
                            }
                            all_results.append(result)

                        except Exception as e:
                            logger.error(f"Failed to convert batch result {batch_start + i + 1}: {e}")
                            all_results.append(self._create_generic_fallback(sentences[batch_start + i], batch_target_words[i] if i < len(batch_target_words) else target_word, language))

                # API usage tracking (count each batch as one call)
                num_batches = (len(sentences) + BATCH_SIZE - 1) // BATCH_SIZE
                try:
                    import streamlit as st
                    if "groq_api_calls" not in st.session_state:
                        st.session_state.groq_api_calls = 0
                    if "groq_tokens_used" not in st.session_state:
                        st.session_state.groq_tokens_used = 0
                    st.session_state.groq_api_calls += num_batches
                    st.session_state.groq_tokens_used += (150 * len(sentences))  # Estimate tokens
                except Exception:
                    pass

                logger.info(f"Batch grammar analysis completed for {len(sentences)} sentences in {num_batches} API calls using {language_code} analyzer")
                return all_results

            except Exception as e:
                logger.warning(f"Batch processing failed for {language_code}: {e}, falling back to individual processing")

        # Fallback to individual processing
        logger.info(f"Falling back to individual processing for {len(sentences)} sentences")
        results = []
        for sentence, target_word in zip(sentences, target_words):
            try:
                result = self.analyze_grammar_and_color(
                    sentence=sentence,
                    word=target_word,
                    language=language,
                    groq_api_key=groq_api_key,
                    language_code=language_code
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to analyze sentence '{sentence}': {e}")
                results.append(self._create_generic_fallback(sentence, target_word, language))

        return results


# Global instance for backward compatibility
_grammar_processor = None

def get_grammar_processor() -> GrammarProcessor:
    """Get global grammar processor instance."""
    global _grammar_processor
    if _grammar_processor is None:
        _grammar_processor = GrammarProcessor()
    return _grammar_processor