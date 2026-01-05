"""
Response Parser Service
Handles parsing and validation of API responses for sentence generation.
"""

import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class ResponseParser:
    """
    Service for parsing API responses and converting them to expected formats.
    Handles both batch and individual response parsing with validation.
    """

    @staticmethod
    def parse_8sentence_batch_response(
        response_text: str,
        batch_sentences: List[str],
        analyzer,
        complexity_level: str,
        language_code: str
    ) -> List[Dict[str, Any]]:
        """
        Parse the batch response from the 8-sentence analysis and convert to individual sentence results.
        Includes automatic fallback to individual processing if batch parsing fails.
        """
        try:
            # Extract JSON from response
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            batch_data = json.loads(response_text)

            if not isinstance(batch_data, dict) or "batch_analysis" not in batch_data:
                raise ValueError("Invalid batch response format")

            batch_results = batch_data["batch_analysis"]

            if not isinstance(batch_results, list) or len(batch_results) != len(batch_sentences):
                raise ValueError(f"Expected {len(batch_sentences)} results, got {len(batch_results) if isinstance(batch_results, list) else 'non-list'}")

            processed_results = []

            for i, sentence_result in enumerate(batch_results):
                if not isinstance(sentence_result, dict):
                    raise ValueError(f"Invalid sentence result format at index {i}")

                sentence_index = sentence_result.get("sentence_index", i + 1)
                grammatical_analysis = sentence_result.get("grammatical_analysis", {})

                # Convert batch format to analyzer-compatible format for parse_grammar_response
                # Create a mock JSON response that the analyzer can parse
                mock_response = json.dumps({
                    "words": grammatical_analysis.get("words", []),
                    "word_combinations": grammatical_analysis.get("word_combinations", []),
                    "explanations": {
                        "sentence_structure": grammatical_analysis.get("sentence_structure", ""),
                        "complexity_notes": grammatical_analysis.get("complexity_notes", "")
                    }
                })

                # Use analyzer's parse_grammar_response method to get proper format
                sentence = batch_sentences[i]
                parsed_data = analyzer.parse_grammar_response(mock_response, complexity_level, sentence)

                # Generate HTML output using analyzer
                colored_sentence = analyzer._generate_html_output(parsed_data, sentence, complexity_level)

                # Get word_explanations from parsed_data (now properly formatted)
                word_explanations = parsed_data.get("word_explanations", [])

                # Create grammar summary
                grammar_summary = grammatical_analysis.get("sentence_structure",
                    f"This sentence uses {language_code} grammatical structures appropriate for {complexity_level} learners.")

                processed_results.append({
                    "colored_sentence": colored_sentence,
                    "word_explanations": word_explanations,
                    "grammar_summary": grammar_summary,
                })

            logger.info(f"Successfully parsed batch response for {len(processed_results)} sentences")
            return processed_results

        except Exception as e:
            logger.error(f"Failed to parse batch response: {e}")
            logger.info("Batch parsing failed, individual processing will be used as fallback")
            raise  # Re-raise to trigger fallback in calling function

    @staticmethod
    def convert_analyzer_output_to_explanations(grammar_result: Dict[str, Any], language: str) -> List[List[Any]]:
        """
        Convert analyzer output to word_explanations format [word, pos, color, explanation].
        Handles both traditional word-based and new character-based analysis formats.
        """
        from services.sentence_generation.data_transformer import DataTransformer

        explanations = []

        # Check if this is character-based analysis (Chinese analyzer)
        if 'characters' in grammar_result:
            # Character-based analysis (Chinese)
            characters = grammar_result.get('characters', [])
            word_combinations = grammar_result.get('word_combinations', [])

            # Add individual character explanations
            for char_data in characters:
                char = char_data.get('character', '')
                meaning = char_data.get('individual_meaning', '')
                role = char_data.get('grammatical_role', '')
                pronunciation = char_data.get('pronunciation', '')

                if char:
                    # Map grammatical role to color category
                    color_category = DataTransformer.map_grammatical_role_to_color_category(role)
                    color = DataTransformer.get_color_for_category(color_category, language)

                    explanation = f"{meaning}"
                    if pronunciation and pronunciation != 'unknown':
                        explanation += f" ({pronunciation})"
                    if role:
                        explanation += f" - {role}"

                    explanations.append([char, role, color, explanation])

            # Add word combination explanations
            for combo_data in word_combinations:
                word = combo_data.get('word', '')
                meaning = combo_data.get('combined_meaning', '')
                structure = combo_data.get('grammatical_structure', '')

                if word and len(word) > 1:  # Only for actual combinations
                    color_category = DataTransformer.map_grammatical_role_to_color_category(structure)
                    color = DataTransformer.get_color_for_category(color_category, language)

                    explanation = f"{meaning} - {structure}"
                    explanations.append([word, structure, color, explanation])

        elif 'elements' in grammar_result:
            # New analyzer format with elements and explanations
            elements = grammar_result.get('elements', {})
            element_explanations = grammar_result.get('explanations', {})

            # Process each grammatical element category
            for element_type, word_list in elements.items():
                if element_type == 'word_combinations':
                    # Handle word combinations specially
                    for combo_data in word_list:
                        word = combo_data.get('word', '')
                        meaning = combo_data.get('combined_meaning', '')
                        structure = combo_data.get('grammatical_structure', '')

                        if word:
                            color_category = DataTransformer.map_grammatical_role_to_color_category(element_type)
                            color = DataTransformer.get_color_for_category(color_category, language)

                            explanation = f"{meaning}"
                            if structure:
                                explanation += f" - {structure}"

                            explanations.append([word, element_type, color, explanation])
                else:
                    # Handle individual words
                    for word_data in word_list:
                        word = word_data.get('word', '')
                        meaning = word_data.get('individual_meaning', '')
                        pronunciation = word_data.get('pronunciation', '')
                        role = word_data.get('grammatical_role', element_type)

                        if word:
                            color_category = DataTransformer.map_grammatical_role_to_color_category(role)
                            color = DataTransformer.get_color_for_category(color_category, language)

                            explanation = f"{meaning}"
                            if pronunciation and pronunciation != 'unknown':
                                explanation += f" ({pronunciation})"
                            if role and role != element_type:
                                explanation += f" - {role}"

                            explanations.append([word, role, color, explanation])

            # If no elements but we have explanations, add a general explanation
            if not explanations and element_explanations:
                for exp_type, exp_text in element_explanations.items():
                    color = DataTransformer.get_color_for_category(exp_type, language)
                    explanations.append(['', exp_type, color, exp_text])

        else:
            # Traditional word-based analysis
            word_explanations = grammar_result.get('word_explanations', [])
            explanations.extend(word_explanations)

        return explanations