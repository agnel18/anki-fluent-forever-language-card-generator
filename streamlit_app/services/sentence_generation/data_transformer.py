"""
Data Transformer Service
Handles data format conversions and transformations for sentence generation.
"""

import logging
from typing import List, Dict, Any

from streamlit_app.language_analyzers.analyzer_registry import get_analyzer

logger = logging.getLogger(__name__)


class DataTransformer:
    """
    Service for transforming data between different formats used in sentence generation.
    Handles grammatical role mapping, color assignment, and prompt creation.
    """

    # Language name to ISO code mapping for analyzer registry
    LANGUAGE_NAME_TO_CODE = {
        "English": "en",
        "Spanish": "es",
        "French": "fr",
        "German": "de",
        "Italian": "it",
        "Portuguese": "pt",
        "Russian": "ru",
        "Japanese": "ja",
        "Korean": "ko",
        "Chinese (Simplified)": "zh",
        "Chinese (Traditional)": "zh-tw",
        "Arabic": "ar",
        "Hindi": "hi",
        "Bengali": "bn",
        "Telugu": "te",
        "Tamil": "ta",
        "Dutch": "nl",
        "Swedish": "sv",
        "Norwegian": "no",
        "Danish": "da",
        "Finnish": "fi",
        "Polish": "pl",
        "Czech": "cs",
        "Slovak": "sk",
        "Hungarian": "hu",
        "Romanian": "ro",
        "Bulgarian": "bg",
        "Croatian": "hr",
        "Serbian": "sr",
        "Slovenian": "sl",
        "Ukrainian": "uk",
        "Greek": "el",
        "Turkish": "tr",
        "Hebrew": "he",
        "Persian": "fa",
        "Urdu": "ur",
        "Thai": "th",
        "Vietnamese": "vi",
        "Indonesian": "id",
        "Malay": "ms",
        "Swahili": "sw",
        "Amharic": "am",
        "Yoruba": "yo",
        "Hausa": "ha",
        "Igbo": "ig",
        "Zulu": "zu",
        "Xhosa": "xh",
        "Afrikaans": "af",
        "Albanian": "sq",
        "Armenian": "hy",
        "Azerbaijani": "az",
        "Basque": "eu",
        "Belarusian": "be",
        "Bosnian": "bs",
        "Catalan": "ca",
        "Corsican": "co",
        "Esperanto": "eo",
        "Estonian": "et",
        "Filipino": "fil",
        "Frisian": "fy",
        "Galician": "gl",
        "Georgian": "ka",
        "Gujarati": "gu",
        "Haitian Creole": "ht",
        "Hawaiian": "haw",
        "Icelandic": "is",
        "Irish": "ga",
        "Javanese": "jw",
        "Kannada": "kn",
        "Kazakh": "kk",
        "Khmer": "km",
        "Kurdish": "ku",
        "Kyrgyz": "ky",
        "Lao": "lo",
        "Latin": "la",
        "Latvian": "lv",
        "Lithuanian": "lt",
        "Luxembourgish": "lb",
        "Macedonian": "mk",
        "Malagasy": "mg",
        "Malayalam": "ml",
        "Maltese": "mt",
        "Maori": "mi",
        "Marathi": "mr",
        "Mongolian": "mn",
        "Myanmar (Burmese)": "my",
        "Nepali": "ne",
        "Norwegian (Bokmål)": "no",
        "Norwegian (Nynorsk)": "nn",
        "Odia (Oriya)": "or",
        "Pashto": "ps",
        "Punjabi": "pa",
        "Samoan": "sm",
        "Scots Gaelic": "gd",
        "Sesotho": "st",
        "Shona": "sn",
        "Sindhi": "sd",
        "Sinhala (Sinhalese)": "si",
        "Somali": "so",
        "Sundanese": "su",
        "Tajik": "tg",
        "Tatar": "tt",
        "Telugu": "te",
        "Tigrinya": "ti",
        "Tsonga": "ts",
        "Turkmen": "tk",
        "Uighur": "ug",
        "Uyghur": "ug",
        "Uzbek": "uz",
        "Welsh": "cy",
        "Xhosa": "xh",
        "Yiddish": "yi",
        "Yoruba": "yo",
        "Zulu": "zu"
    }

    @staticmethod
    def map_grammatical_role_to_color_category(role: str) -> str:
        """Map grammatical role to color category"""
        role_lower = role.lower()

        if any(kw in role_lower for kw in ['pronoun', 'demonstrative']):
            return 'pronouns'
        elif any(kw in role_lower for kw in ['verb', 'linking', 'action']):
            return 'verbs'
        elif any(kw in role_lower for kw in ['particle', 'marker']):
            return 'particles'
        elif any(kw in role_lower for kw in ['noun', 'object', 'subject']):
            return 'nouns'
        elif any(kw in role_lower for kw in ['adjective', 'description']):
            return 'adjectives'
        elif any(kw in role_lower for kw in ['adverb', 'manner']):
            return 'adverbs'
        else:
            return 'other'

    @staticmethod
    def get_color_for_category(category: str, language: str) -> str:
        """Get color for grammatical category based on language"""
        # Use the analyzer's color scheme if available
        normalized_language = language.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('（', '').replace('）', '')
        analyzer = get_analyzer(DataTransformer.LANGUAGE_NAME_TO_CODE.get(normalized_language))
        if analyzer:
            color_scheme = analyzer.get_color_scheme('beginner')  # Default to beginner
            return color_scheme.get(category, '#CCCCCC')

        # Fallback colors
        fallback_colors = {
            'pronouns': '#FF4444',
            'verbs': '#44FF44',
            'particles': '#4444FF',
            'nouns': '#FFAA00',
            'adjectives': '#FF44FF',
            'adverbs': '#44FFFF',
            'other': '#888888'
        }
        return fallback_colors.get(category, '#CCCCCC')

    @staticmethod
    def create_8sentence_batch_prompt(
        analyzer,
        sentences: List[str],
        word: str,
        complexity_level: str,
        language_code: str,
        native_language: str = "English"
    ) -> str:
        """
        Create a batch prompt for analyzing 8 sentences together in one API call.
        This reduces API calls by 87% compared to individual sentence processing.
        """
        # Get the base prompt structure from the analyzer
        base_prompt = analyzer.get_grammar_prompt(complexity_level, sentences[0], word)

        # Extract the core analysis instructions from the base prompt
        # Remove sentence-specific parts and adapt for batch processing
        batch_instructions = f"""
Analyze ALL {len(sentences)} sentences below as a batch. For each sentence, provide complete grammatical analysis including word-by-word breakdown, grammatical roles, and color coding.

Target word: "{word}"
Language: {language_code}
Complexity level: {complexity_level}
Analysis should be in {native_language}

Sentences to analyze:
"""

        # Add numbered sentences
        for i, sentence in enumerate(sentences, 1):
            batch_instructions += f"{i}. {sentence}\n"

        # Add batch output format requirements
        batch_instructions += f"""

Return your analysis in this exact JSON format:
{{
  "batch_analysis": [
    {{
      "sentence_index": 1,
      "sentence": "{sentences[0] if sentences else ''}",
      "grammatical_analysis": {{
        "words": [
          {{
            "word": "example",
            "grammatical_role": "noun",
            "category": "noun",
            "explanation": "Explanation in {native_language}"
          }}
        ],
        "sentence_structure": "Brief grammatical summary in {native_language}",
        "complexity_notes": "Notes about {complexity_level} level structures used"
      }}
    }},
    {{
      "sentence_index": 2,
      "sentence": "{sentences[1] if len(sentences) > 1 else ''}",
      "grammatical_analysis": {{
        "words": [
          {{
            "word": "example",
            "grammatical_role": "verb",
            "category": "verb",
            "explanation": "Explanation in {native_language}"
          }}
        ],
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

        return batch_instructions