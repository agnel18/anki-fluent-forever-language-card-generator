# Batch Processor Service for Sentence Generation
# Handles batch processing of sentences for grammar analysis

import logging
import json
import time
from typing import List, Dict, Any, Optional, Tuple

from .api_client import APIClient
from .data_transformer import DataTransformer

logger = logging.getLogger(__name__)


class BatchProcessor:
    """
    Service for handling batch processing of sentences.
    Provides unified batch processing for both analyzer-specific and generic languages.
    """

    def __init__(self, api_client: APIClient):
        self.api_client = api_client

    def process_batch(self, sentences: List[str], word: str, language: str,
                     language_code: str, analyzer=None, complexity_level: str = "beginner",
                     native_language: str = "English") -> List[Dict[str, Any]]:
        """
        Process a batch of sentences for grammar analysis using 8-sentence chunks.
        This ensures efficient batch processing with maximum 8 sentences per API call.

        Args:
            sentences: List of sentences to analyze
            word: Target word being learned
            language: Full language name
            language_code: ISO language code
            analyzer: Language-specific analyzer (optional)
            complexity_level: Learning complexity level
            native_language: User's native language for explanations

        Returns:
            List of processed sentence results with grammar analysis
        """
        if not sentences:
            return []

        logger.info(f"Processing batch of {len(sentences)} sentences for {language} using 8-sentence chunks")

        # Process sentences in chunks of 8 to optimize API usage
        chunk_size = 8
        all_results = []

        for i in range(0, len(sentences), chunk_size):
            chunk = sentences[i:i + chunk_size]
            logger.info(f"Processing chunk {i//chunk_size + 1} with {len(chunk)} sentences")

            try:
                # Process this chunk as a batch
                chunk_results, failed_indices = self._process_chunk(
                    sentences=chunk,
                    word=word,
                    language=language,
                    language_code=language_code,
                    analyzer=analyzer,
                    complexity_level=complexity_level,
                    native_language=native_language
                )

                # If some sentences failed, retry only those individually
                if failed_indices:
                    logger.warning(f"Chunk {i//chunk_size + 1} had {len(failed_indices)} failed sentences, retrying individually")
                    failed_sentences = [chunk[idx] for idx in failed_indices]
                    retry_results = self._process_sentences_individually(
                        sentences=failed_sentences,
                        word=word,
                        language=language,
                        language_code=language_code,
                        analyzer=analyzer,
                        complexity_level=complexity_level,
                        native_language=native_language
                    )

                    # Merge retry results back into chunk results
                    for failed_idx, retry_result in zip(failed_indices, retry_results):
                        chunk_results[failed_idx] = retry_result

                all_results.extend(chunk_results)

            except Exception as e:
                logger.error(f"Chunk processing failed for chunk {i//chunk_size + 1}: {e}")
                # Fallback: Process entire chunk individually
                logger.info(f"Falling back to individual processing for entire chunk {i//chunk_size + 1}")
                chunk_fallback_results = self._process_sentences_individually(
                    sentences=chunk,
                    word=word,
                    language=language,
                    language_code=language_code,
                    analyzer=analyzer,
                    complexity_level=complexity_level,
                    native_language=native_language
                )
                all_results.extend(chunk_fallback_results)

        logger.info(f"Successfully processed {len(all_results)} sentences in total")
        return all_results

    def _process_chunk(self, sentences: List[str], word: str, language: str,
                      language_code: str, analyzer=None, complexity_level: str = "beginner",
                      native_language: str = "English") -> Tuple[List[Dict[str, Any]], List[int]]:
        """
        Process a chunk of up to 8 sentences as a single batch API call.
        Returns processed results and indices of failed sentences for partial fallback.
        """
        # Create batch prompt for this chunk
        prompt = self._create_batch_prompt(
            sentences=sentences,
            word=word,
            language=language,
            language_code=language_code,
            analyzer=analyzer,
            complexity_level=complexity_level,
            native_language=native_language
        )

        try:
            # Make single batch API call for this chunk
            response_text = self.api_client.call_completion(
                prompt=prompt,
                temperature=0.3,
                max_tokens=4000
            )

            # Parse batch response
            processed_results = self._parse_batch_response(
                response_text=response_text,
                sentences=sentences,
                analyzer=analyzer,
                language=language,
                complexity_level=complexity_level,
                language_code=language_code,
                native_language=native_language
            )

            # Check for failed results (empty word_explanations or error indicators)
            failed_indices = []
            for i, result in enumerate(processed_results):
                if not result.get("word_explanations") or len(result.get("word_explanations", [])) == 0:
                    failed_indices.append(i)

            return processed_results, failed_indices

        except Exception as e:
            logger.error(f"Chunk processing failed: {e}")
            # If batch fails completely, mark all as failed
            failed_indices = list(range(len(sentences)))
            return [], failed_indices

    def _create_batch_prompt(self, sentences: List[str], word: str, language: str,
                           language_code: str, analyzer, complexity_level: str,
                           native_language: str) -> str:
        """Create the appropriate batch prompt based on analyzer availability."""
        # Common sentences text for all prompts
        sentences_text = "\n".join(f"{i+1}. {sentence}" for i, sentence in enumerate(sentences))
        
        if analyzer and hasattr(analyzer, 'get_batch_grammar_prompt'):
            # Use analyzer's batch prompt method
            logger.info(f"Using analyzer's batch prompt for {language_code}")
            return analyzer.get_batch_grammar_prompt(complexity_level, sentences, word, native_language)
        elif analyzer:
            # Fallback to default batch prompt for analyzers
            logger.info(f"Using fallback batch prompt for {language_code}")

            return f"""Analyze the grammar of these {language} sentences and provide detailed analysis for each one.

Target word: "{word}"
Language: {language_code}
Complexity level: {complexity_level}
Analysis should be in {native_language}

Sentences to analyze:
{sentences_text}

Return your analysis in this exact JSON format:
{{
  "batch_results": [
    {{
      "sentence_index": 1,
      "sentence": "{sentences[0] if sentences else ''}",
      "words": [
        {{
          "word": "example",
          "grammatical_role": "noun",
          "category": "nouns",
          "explanation": "Explanation in {native_language}"
        }}
      ],
      "word_combinations": [],
      "explanations": {{
        "sentence_structure": "Brief grammatical summary in {native_language}",
        "complexity_notes": "Notes about {complexity_level} level structures used"
      }}
    }}
  ]
}}

IMPORTANT:
- Analyze ALL {len(sentences)} sentences in this single response
- Each sentence must have complete word-by-word grammatical analysis
- Use language-specific grammatical categories appropriate for {language_code}
- Provide explanations in {native_language}
- Return ONLY the JSON object, no additional text or markdown formatting
"""
        else:
            # Generic batch analysis for languages without specific analyzers
            # Generate dynamic examples for actual sentence count
            generic_examples = []
            for i, sentence in enumerate(sentences[:2]):  # Show examples for first 2 sentences
                generic_examples.append(f"""  {{
    "sentence_index": {i+1},
    "colored_sentence": "<span style='color: #FF6B6B'>Subject</span> <span style='color: #4ECDC4'>verb</span> <span style='color: #45B7D1'>object</span>",
    "word_explanations": [
      ["word1", "noun", "#FF6B6B", "explanation in {native_language}"],
      ["word2", "verb", "#4ECDC4", "explanation in {native_language}"]
    ],
    "grammar_summary": "Brief explanation of sentence grammar structure in {native_language}"
  }}""")

            examples_text = ",\n".join(generic_examples)

            return f"""Analyze the grammar of these {language} sentences and provide color-coded HTML output.

Sentences:
{sentences_text}

For EACH sentence, return analysis in this exact JSON format:

[
{examples_text}
]

Color codes to use:
- #FF6B6B: nouns (red)
- #4ECDC4: verbs (teal)
- #45B7D1: adjectives/adverbs (blue)
- #96CEB4: prepositions/conjunctions (green)
- #FFEAA7: pronouns/articles (yellow)
- #CCCCCC: other (gray)

Provide explanations in {native_language}. Return ONLY the JSON array, no additional text."""

    def _parse_batch_response(self, response_text: str, sentences: List[str], analyzer,
                            language: str, complexity_level: str, language_code: str,
                            native_language: str) -> List[Dict[str, Any]]:
        """Parse the batch response and convert to expected format."""
        try:
            if analyzer and hasattr(analyzer, 'parse_batch_grammar_response'):
                # Use analyzer's batch parsing method
                parsed_results = analyzer.parse_batch_grammar_response(response_text, sentences, complexity_level, native_language)

                # Generate HTML for each result using the analyzer's _generate_html_output method
                results_with_html = []
                for i, parsed_data in enumerate(parsed_results):
                    sentence = parsed_data.get("sentence", sentences[i] if i < len(sentences) else "")

                    # Generate colored sentence HTML
                    if hasattr(analyzer, '_generate_html_output'):
                        colored_sentence = analyzer._generate_html_output(parsed_data, sentence, complexity_level)
                        print(f"DEBUG BATCH: Generated colored_sentence for sentence {i+1}: {colored_sentence[:100]}...")
                    else:
                        # Fallback if analyzer doesn't have HTML generation
                        colored_sentence = sentence

                    # Ensure word_explanations are in the expected format
                    word_explanations = parsed_data.get("word_explanations", [])

                    # Get grammar summary
                    grammar_summary = parsed_data.get("explanations", {}).get("sentence_structure",
                        f"This sentence uses {language_code} grammatical structures appropriate for {complexity_level} learners.")

                    results_with_html.append({
                        "colored_sentence": colored_sentence,
                        "word_explanations": word_explanations,
                        "grammar_summary": grammar_summary,
                    })

                return results_with_html

            # Extract JSON from response
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            if analyzer:
                # Parse analyzer-specific batch response
                batch_data = json.loads(response_text)
                if "batch_results" not in batch_data:
                    raise ValueError("Missing batch_results in analyzer response")

                results = []
                for item in batch_data["batch_results"][:len(sentences)]:
                    # Convert analyzer format to expected format
                    word_explanations = []
                    if "words" in item:
                        for word_data in item["words"]:
                            grammatical_role = word_data.get("grammatical_role", "")
                            category = analyzer._map_grammatical_role_to_category(grammatical_role) if analyzer and hasattr(analyzer, '_map_grammatical_role_to_category') else "other"
                            color = DataTransformer.get_color_for_category(category, language)
                            word_explanations.append([
                                word_data.get("word", ""),
                                word_data.get("grammatical_role", ""),
                                color,
                                word_data.get("explanation", "")
                            ])

                    # Add word combinations if present
                    if "word_combinations" in item:
                        for combo in item["word_combinations"]:
                            word = combo.get("word", "")
                            if word:
                                color = DataTransformer.get_color_for_category("other", language)
                                word_explanations.append([
                                    word,
                                    combo.get("grammatical_structure", ""),
                                    color,
                                    combo.get("combined_meaning", "")
                                ])

                    # Generate colored sentence from word explanations
                    sentence = item.get("sentence", "")
                    logger.error(f"DEBUG BATCH: analyzer = {type(analyzer)}, hasattr = {hasattr(analyzer, '_generate_html_output')}")
                    # Use analyzer's HTML generation method instead of simple batch processor method
                    if analyzer and hasattr(analyzer, '_generate_html_output'):
                        # Create parsed_data format expected by analyzer's _generate_html_output
                        parsed_data_for_html = {
                            'word_explanations': word_explanations,
                            'sentence': sentence
                        }
                        print(f"DEBUG BATCH: Calling analyzer._generate_html_output for sentence: {sentence[:50]}...")
                        colored_sentence = analyzer._generate_html_output(parsed_data_for_html, sentence, complexity_level)
                        print(f"DEBUG BATCH: Got colored_sentence: {colored_sentence[:100]}...")
                    else:
                        # Fallback to simple method if analyzer doesn't have the method
                        colored_sentence = self._generate_colored_sentence_from_explanations(sentence, word_explanations)

                    grammar_summary = item.get("explanations", {}).get("sentence_structure",
                        f"This sentence uses {language_code} grammatical structures appropriate for {complexity_level} learners.")

                    results.append({
                        "colored_sentence": colored_sentence,
                        "word_explanations": word_explanations,
                        "grammar_summary": grammar_summary,
                    })

                return results

            else:
                # Parse generic batch response
                results = json.loads(response_text)
                if not isinstance(results, list):
                    raise ValueError("Expected JSON array for generic batch response")

                processed_results = []
                for i, result in enumerate(results[:len(sentences)]):
                    if isinstance(result, dict):
                        processed_results.append({
                            "colored_sentence": result.get("colored_sentence", sentences[i]),
                            "word_explanations": result.get("word_explanations", []),
                            "grammar_summary": result.get("grammar_summary", ""),
                        })
                    else:
                        processed_results.append({
                            "colored_sentence": sentences[i],
                            "word_explanations": [],
                            "grammar_summary": "Analysis failed",
                        })

                return processed_results

        except Exception as e:
            logger.error(f"Failed to parse batch response: {e}")
            # Return fallback results
            return [{
                "colored_sentence": sentence,
                "word_explanations": [],
                "grammar_summary": "Batch parsing failed"
            } for sentence in sentences]

    def _process_sentences_individually(self, sentences: List[str], word: str, language: str,
                                      language_code: str, analyzer, complexity_level: str,
                                      native_language: str) -> List[Dict[str, Any]]:
        """Fallback function to process sentences individually when batch processing fails.
        Implements exponential backoff for rate limiting and partial fallbacks."""
        processed_results = []
        base_delay = 1  # Start with 1 second
        max_delay = 30  # Maximum 30 seconds
        max_retries = 3  # Maximum retries per sentence

        for i, sentence in enumerate(sentences):
            retry_count = 0
            current_delay = base_delay

            while retry_count <= max_retries:
                try:
                    if analyzer:
                        # Use analyzer's individual processing
                        prompt = analyzer.get_grammar_prompt(complexity_level, sentence, word, native_language)
                        response_text = self.api_client.call_completion(prompt, temperature=0.3, max_tokens=2000)

                        parsed_data = analyzer.parse_grammar_response(response_text, complexity_level, sentence)
                        colored_sentence = analyzer._generate_html_output(parsed_data, sentence, complexity_level)

                        # Convert to word_explanations format
                        if "word_explanations" in parsed_data and parsed_data["word_explanations"]:
                            word_explanations = parsed_data["word_explanations"]
                        else:
                            word_explanations = self._convert_analyzer_output_to_explanations(parsed_data, language)

                        grammar_summary = parsed_data.get('explanations', {}).get('sentence_structure',
                            f"This sentence uses {language_code} grammatical structures appropriate for {complexity_level} learners.")
                    else:
                        # Generic individual processing
                        prompt = f"""Analyze the grammar of this {language} sentence and provide color-coded HTML output.

Sentence: {sentence}

Return analysis in this exact JSON format:
{{
  "colored_sentence": "<span style='color: #FF6B6B'>Subject</span> <span style='color: #4ECDC4'>verb</span> <span style='color: #45B7D1'>object</span>",
  "word_explanations": [
    ["word1", "noun", "#FF6B6B", "explanation in {native_language}"],
    ["word2", "verb", "#4ECDC4", "explanation in {native_language}"]
  ],
  "grammar_summary": "Brief explanation of sentence grammar structure in {native_language}"
}}

Color codes: nouns=#FF6B6B, verbs=#4ECDC4, adjectives/adverbs=#45B7D1, prepositions/conjunctions=#96CEB4, pronouns/articles=#FFEAA7, other=#CCCCCC
Return ONLY the JSON object."""

                        response_text = self.api_client.call_completion(prompt, temperature=0.3, max_tokens=2000)

                        # Extract and parse JSON
                        if "```json" in response_text:
                            response_text = response_text.split("```json")[1].split("```")[0].strip()
                        elif "```" in response_text:
                            response_text = response_text.split("```")[1].split("```")[0].strip()

                        result = json.loads(response_text)
                        colored_sentence = result.get("colored_sentence", sentence)
                        word_explanations = result.get("word_explanations", [])
                        grammar_summary = result.get("grammar_summary", "")

                    processed_results.append({
                        "colored_sentence": colored_sentence,
                        "word_explanations": word_explanations,
                        "grammar_summary": grammar_summary,
                    })

                    # Success - break out of retry loop
                    break

                except Exception as e:
                    retry_count += 1
                    if retry_count <= max_retries:
                        logger.warning(f"Individual processing failed for sentence {i+1} (attempt {retry_count}/{max_retries + 1}): {e}")
                        logger.info(f"Retrying in {current_delay} seconds...")
                        time.sleep(current_delay)
                        current_delay = min(current_delay * 2, max_delay)  # Exponential backoff
                    else:
                        logger.error(f"Individual processing failed permanently for sentence {i+1}: {e}")
                        processed_results.append({
                            "colored_sentence": sentence,
                            "word_explanations": [],
                            "grammar_summary": f"Analysis failed for {language_code} sentence after {max_retries + 1} attempts",
                        })

        return processed_results

    def _convert_analyzer_output_to_explanations(self, grammar_result: Dict[str, Any], language: str) -> List[List[Any]]:
        """Convert analyzer output to word_explanations format."""
        # This is a simplified version - the full implementation is in sentence_generator.py
        explanations = []

        # Handle different analyzer formats
        if 'elements' in grammar_result:
            elements = grammar_result.get('elements', {})
            element_explanations = grammar_result.get('explanations', {})

            for element_type, word_list in elements.items():
                if element_type == 'word_combinations':
                    for combo_data in word_list:
                        word = combo_data.get('word', '')
                        meaning = combo_data.get('combined_meaning', '')
                        structure = combo_data.get('grammatical_structure', '')

                        if word and len(word) > 1:
                            color = DataTransformer.get_color_for_category("other", language)
                            explanations.append([word, structure, color, meaning])

        return explanations

    def _generate_colored_sentence_from_explanations(self, sentence: str, word_explanations: List[List[Any]]) -> str:
        """Generate a colored HTML sentence from word explanations."""
        if not word_explanations:
            return sentence

        # Simple approach: color words that appear in explanations
        colored_parts = []
        remaining_text = sentence

        for word, pos, color, explanation in word_explanations:
            if word in remaining_text:
                parts = remaining_text.split(word, 1)
                if parts[0]:
                    colored_parts.append(parts[0])
                colored_parts.append(f"<span style='color: {color}' title='{explanation}'>{word}</span>")
                remaining_text = parts[1] if len(parts) > 1 else ""
            else:
                colored_parts.append(f"<span style='color: {color}' title='{explanation}'>{word}</span>")

        if remaining_text:
            colored_parts.append(remaining_text)

        return "".join(colored_parts)