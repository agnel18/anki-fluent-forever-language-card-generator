# languages/{language}/domain/{lang_code}_prompt_builder.py
"""
{Language} Prompt Builder - Domain Component

GOLD STANDARD PROMPT BUILDING:
This component demonstrates how to create effective AI prompts for grammar analysis.
It provides complexity-aware prompt generation with language-specific customization.

RESPONSIBILITIES:
1. Build AI prompts for different complexity levels
2. Include language-specific grammatical information
3. Format prompts for optimal AI responses
4. Cache prompts for performance

PROMPT FEATURES:
- Complexity-aware: Different instructions for different levels
- Language-specific: {Language}-appropriate examples and terminology
- Structured output: Explicit JSON format requirements
- Target word highlighting: Special handling for focus words

INTEGRATION:
- Called by main analyzer for AI interaction
- Uses configuration for language-specific data
- Supports batch processing for efficiency
"""
# type: ignore  # Template file with placeholders - ignore type checking

import hashlib
from string import Template
from typing import Dict, Any, List


class LanguagePromptBuilder:
    """
    Builds AI prompts for {Language} grammatical analysis.

    GOLD STANDARD PROMPT BUILDING APPROACH:
    - Complexity-based prompt customization
    - Language-specific terminology and examples
    - Structured JSON output requirements
    - Performance optimization through caching
    """

    def __init__(self, config):
        """
        Initialize with configuration.

        TEMPLATE INITIALIZATION:
        1. Store config reference for access to templates and settings
        2. Pre-compile templates for performance
        3. Validate template availability
        4. Set up error handling for template rendering
        """
        self.config = config
        self.prompt_cache = {}

        # Template strings (customize for your language)
        self.single_template = Template(self._get_single_template())
        self.batch_template = Template(self._get_batch_template())

    def _get_single_template(self) -> str:
        """Get the single sentence analysis template"""
        return '''
Analyze this {Language} sentence for grammatical structure:

Sentence: {{sentence}}
Target word: {{target_word}}
Complexity level: {{complexity}}

Provide a detailed grammatical analysis with the following JSON structure:
{{
  "word_explanations": [
    [
      "word1",
      "grammatical_role",
      "#color_code",
      "explanation_of_role"
    ],
    [
      "word2",
      "grammatical_role",
      "#color_code",
      "explanation_of_role"
    ]
  ],
  "elements": {{
    "noun": [{{"word": "example", "grammatical_role": "noun"}}],
    "verb": [{{"word": "example", "grammatical_role": "verb"}}]
  }},
  "explanations": {{
    "overall_structure": "Brief explanation of sentence structure",
    "key_features": "Notable grammatical features in this sentence"
  }},
  "confidence": 0.95
}}

Grammatical roles to use ({{complexity}} level):
{{grammatical_roles}}

Important:
- Analyze each word's grammatical role precisely
- Use only valid grammatical roles from the list above
- Provide clear, educational explanations
- Maintain consistent color coding
- Return only valid JSON
'''

    def _get_batch_template(self) -> str:
        """Get the batch analysis template"""
        return '''
Analyze these {Language} sentences for grammatical structure:

Sentences: {{sentences}}
Target word: {{target_word}}
Complexity level: {{complexity}}

Return a JSON object with exactly this structure:
{{
  "batch_results": [
    {{
      "sentence": "first sentence",
      "word_explanations": [
        ["word1", "role", "#color", "explanation"],
        ["word2", "role", "#color", "explanation"]
      ],
      "elements": {{"noun": [], "verb": []}},
      "explanations": {{
        "overall_structure": "structure explanation",
        "key_features": "key features"
      }},
      "confidence": 0.95
    }}
  ]
}}

Grammatical roles: {{grammatical_roles}}
'''

    def build_single_prompt(self, sentence: str, target_word: str, complexity: str) -> str:
        """Build prompt for single sentence analysis."""
        try:
            cache_key = self._generate_cache_key(sentence, target_word, complexity)
            if cache_key in self.prompt_cache:
                return self.prompt_cache[cache_key]

            grammatical_roles = self._format_grammatical_roles(complexity)

            context = {
                'sentence': sentence,
                'target_word': target_word,
                'complexity': complexity,
                'Language': self.config.language_config.name,
                'grammatical_roles': grammatical_roles
            }

            prompt = self.single_template.substitute(**context)

            # Cache the prompt
            self.prompt_cache[cache_key] = prompt
            return prompt

        except Exception as e:
            # Fallback prompt
            return f'''Analyze this {self.config.language_config.name} sentence grammatically:

Sentence: {sentence}
Target word: {target_word}
Complexity: {complexity}

Return JSON with word_explanations, elements, explanations, and confidence.'''

    def build_batch_prompt(self, sentences: List[str], target_word: str, complexity: str) -> str:
        """Build prompt for batch analysis."""
        try:
            grammatical_roles = self._format_grammatical_roles(complexity)

            context = {
                'sentences': '\n'.join(f"- {s}" for s in sentences),
                'target_word': target_word,
                'complexity': complexity,
                'Language': self.config.language_config.name,
                'grammatical_roles': grammatical_roles
            }

            prompt = self.batch_template.substitute(**context)
            return prompt

        except Exception as e:
            # Fallback prompt
            sentences_text = '\n'.join(sentences)
            return f'''Analyze these {self.config.language_config.name} sentences:

Sentences: {sentences_text}
Target word: {target_word}
Complexity: {complexity}

Return JSON with batch_results array.'''

    def _format_grammatical_roles(self, complexity: str) -> str:
        """Format grammatical roles for prompt inclusion"""
        roles = self.config.get_grammatical_roles(complexity)

        # Format as bullet points for clarity
        formatted_roles = []
        for role_key, role_description in roles.items():
            formatted_roles.append(f"- {role_key}: {role_description}")

        return "\n".join(formatted_roles)

    def get_complexity_specific_instructions(self, complexity: str) -> str:
        """Get complexity-specific analysis instructions"""
        instructions = {
            'beginner': """
Focus on basic parts of speech and sentence structure.
Identify: nouns, verbs, adjectives, adverbs, pronouns, prepositions, conjunctions.
Keep explanations simple and clear.""",

            'intermediate': """
Include grammatical relationships and modifiers.
Identify: all basic roles plus auxiliary verbs, particles, case markers.
Explain how words relate to each other in the sentence.""",

            'advanced': """
Provide comprehensive grammatical analysis.
Identify: all grammatical categories including complex forms, aspect, mood.
Explain morphological features, agreement patterns, and discourse functions."""
        }

        return instructions.get(complexity, instructions['intermediate'])

    def _generate_cache_key(self, sentence: str, target_word: str, complexity: str) -> str:
        """Generate cache key for prompt"""
        key_string = f"{sentence}|{target_word or ''}|{complexity}"
        return hashlib.md5(key_string.encode()).hexdigest()

    def clear_cache(self):
        """Clear prompt cache"""
        self.prompt_cache.clear()