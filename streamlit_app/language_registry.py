# Language Registry
# Central source of truth for language mappings and configurations

import logging
from typing import Dict, Optional, Set, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class LanguageConfig:
    """Configuration for a language including all necessary mappings."""
    iso_code: str  # ISO 639-1 code (e.g., 'zh', 'hi', 'es')
    full_name: str  # Full language name (e.g., 'Chinese', 'Hindi', 'Spanish')
    epitran_code: Optional[str]  # Epitran language code (e.g., 'cmn-Latn', 'hin-Deva')
    phonemizer_code: Optional[str]  # Phonemizer language code
    family: str  # Language family (e.g., 'Sino-Tibetan', 'Indo-European')
    script_type: str  # Script type (e.g., 'logographic', 'alphabetic', 'abugida')
    complexity: str  # Learning complexity ('low', 'medium', 'high')

class LanguageRegistry:
    """
    Central registry for all language configurations and mappings.

    Provides consistent mappings between:
    - ISO codes ↔ full names
    - IPA system codes
    - Language metadata
    """

    def __init__(self):
        self._languages: Dict[str, LanguageConfig] = {}
        self._iso_to_full: Dict[str, str] = {}
        self._full_to_iso: Dict[str, str] = {}
        self._load_language_configs()

    def _load_language_configs(self):
        """Load all language configurations."""
        # Core languages with full configurations (your original 14 - UNCHANGED)
        self._add_language(LanguageConfig(
            iso_code='zh',
            full_name='Chinese',
            epitran_code='cmn-Latn',  # Mandarin Chinese
            phonemizer_code='zh',
            family='Sino-Tibetan',
            script_type='logographic',
            complexity='high'
        ), variant_names=['Chinese (Simplified)', 'Chinese Simplified', '简体中文'])

        self._add_language(LanguageConfig(
            iso_code='zh-tw',
            full_name='Chinese Traditional',
            epitran_code='cmn-Latn',  # Same as simplified for IPA
            phonemizer_code='zh',
            family='Sino-Tibetan',
            script_type='logographic',
            complexity='high'
        ), variant_names=['Chinese (Traditional)', 'Chinese Traditional', '繁体中文'])

        self._add_language(LanguageConfig(
            iso_code='hi',
            full_name='Hindi',
            epitran_code='hin-Deva',
            phonemizer_code='hi',
            family='Indo-European',
            script_type='abugida',
            complexity='medium'
        ))

        self._add_language(LanguageConfig(
            iso_code='es',
            full_name='Spanish',
            epitran_code='spa-Latn',
            phonemizer_code='es',
            family='Indo-European',
            script_type='alphabetic',
            complexity='low'
        ))

        self._add_language(LanguageConfig(
            iso_code='ar',
            full_name='Arabic',
            epitran_code='ara-Arab',
            phonemizer_code='ar',
            family='Afro-Asiatic',
            script_type='abjad',
            complexity='high'
        ))

        self._add_language(LanguageConfig(
            iso_code='en',
            full_name='English',
            epitran_code='eng-Latn',
            phonemizer_code='en',
            family='Indo-European',
            script_type='alphabetic',
            complexity='low'
        ))

        self._add_language(LanguageConfig(
            iso_code='ja',
            full_name='Japanese',
            epitran_code='jpn-Hira',
            phonemizer_code='ja',
            family='Japonic',
            script_type='mixed',
            complexity='high'
        ))

        self._add_language(LanguageConfig(
            iso_code='ko',
            full_name='Korean',
            epitran_code='kor-Hang',
            phonemizer_code='ko',
            family='Koreanic',
            script_type='alphabetic',
            complexity='medium'
        ))

        self._add_language(LanguageConfig(
            iso_code='fr',
            full_name='French',
            epitran_code='fra-Latn',
            phonemizer_code='fr',
            family='Indo-European',
            script_type='alphabetic',
            complexity='low'
        ))

        self._add_language(LanguageConfig(
            iso_code='de',
            full_name='German',
            epitran_code='deu-Latn',
            phonemizer_code='de',
            family='Indo-European',
            script_type='alphabetic',
            complexity='low'
        ))

        self._add_language(LanguageConfig(
            iso_code='it',
            full_name='Italian',
            epitran_code='ita-Latn',
            phonemizer_code='it',
            family='Indo-European',
            script_type='alphabetic',
            complexity='low'
        ))

        self._add_language(LanguageConfig(
            iso_code='pt',
            full_name='Portuguese',
            epitran_code='por-Latn',
            phonemizer_code='pt',
            family='Indo-European',
            script_type='alphabetic',
            complexity='low'
        ))

        self._add_language(LanguageConfig(
            iso_code='ru',
            full_name='Russian',
            epitran_code='rus-Cyrl',
            phonemizer_code='ru',
            family='Indo-European',
            script_type='alphabetic',
            complexity='medium'
        ))

        self._add_language(LanguageConfig(
            iso_code='tr',
            full_name='Turkish',
            epitran_code='tur-Latn',
            phonemizer_code='tr',
            family='Turkic',
            script_type='alphabetic',
            complexity='medium'
        ))

        # ====================================================================
        # ALL REMAINING LANGUAGES (63 more) - added in exactly the same style
        # ====================================================================
        self._add_language(LanguageConfig(
            iso_code='af', full_name='Afrikaans', epitran_code=None, phonemizer_code='af',
            family='Indo-European', script_type='alphabetic', complexity='low'
        ))
        self._add_language(LanguageConfig(
            iso_code='sq', full_name='Albanian', epitran_code=None, phonemizer_code='sq',
            family='Indo-European', script_type='alphabetic', complexity='medium'
        ))
        self._add_language(LanguageConfig(
            iso_code='am', full_name='Amharic', epitran_code=None, phonemizer_code='am',
            family='Afro-Asiatic', script_type='abugida', complexity='high'
        ))
        self._add_language(LanguageConfig(
            iso_code='hy', full_name='Armenian', epitran_code=None, phonemizer_code='hy',
            family='Indo-European', script_type='alphabetic', complexity='medium'
        ))
        self._add_language(LanguageConfig(
            iso_code='az', full_name='Azerbaijani', epitran_code=None, phonemizer_code='az',
            family='Turkic', script_type='alphabetic', complexity='medium'
        ))
        self._add_language(LanguageConfig(
            iso_code='eu', full_name='Basque', epitran_code=None, phonemizer_code='eu',
            family='Isolate', script_type='alphabetic', complexity='medium'
        ))
        self._add_language(LanguageConfig(
            iso_code='be', full_name='Belarusian', epitran_code=None, phonemizer_code='be',
            family='Indo-European', script_type='alphabetic', complexity='medium'
        ))
        self._add_language(LanguageConfig(
            iso_code='bn', full_name='Bengali', epitran_code=None, phonemizer_code='bn',
            family='Indo-European', script_type='abugida', complexity='medium'
        ))
        self._add_language(LanguageConfig(
            iso_code='bs', full_name='Bosnian', epitran_code=None, phonemizer_code='bs',
            family='Indo-European', script_type='alphabetic', complexity='medium'
        ))
        self._add_language(LanguageConfig(
            iso_code='bg', full_name='Bulgarian', epitran_code=None, phonemizer_code='bg',
            family='Indo-European', script_type='alphabetic', complexity='medium'
        ))
        self._add_language(LanguageConfig(
            iso_code='my', full_name='Burmese', epitran_code=None, phonemizer_code='my',
            family='Sino-Tibetan', script_type='abugida', complexity='high'
        ))
        self._add_language(LanguageConfig(
            iso_code='ca', full_name='Catalan', epitran_code=None, phonemizer_code='ca',
            family='Indo-European', script_type='alphabetic', complexity='low'
        ))
        self._add_language(LanguageConfig(
            iso_code='hr', full_name='Croatian', epitran_code=None, phonemizer_code='hr',
            family='Indo-European', script_type='alphabetic', complexity='medium'
        ))
        self._add_language(LanguageConfig(
            iso_code='cs', full_name='Czech', epitran_code=None, phonemizer_code='cs',
            family='Indo-European', script_type='alphabetic', complexity='medium'
        ))
        self._add_language(LanguageConfig(
            iso_code='da', full_name='Danish', epitran_code=None, phonemizer_code='da',
            family='Indo-European', script_type='alphabetic', complexity='low'
        ))
        self._add_language(LanguageConfig(
            iso_code='nl', full_name='Dutch', epitran_code=None, phonemizer_code='nl',
            family='Indo-European', script_type='alphabetic', complexity='low'
        ))
        self._add_language(LanguageConfig(
            iso_code='et', full_name='Estonian', epitran_code=None, phonemizer_code='et',
            family='Uralic', script_type='alphabetic', complexity='medium'
        ))
        self._add_language(LanguageConfig(
            iso_code='fi', full_name='Finnish', epitran_code=None, phonemizer_code='fi',
            family='Uralic', script_type='alphabetic', complexity='medium'
        ))
        self._add_language(LanguageConfig(
            iso_code='gl', full_name='Galician', epitran_code=None, phonemizer_code='gl',
            family='Indo-European', script_type='alphabetic', complexity='low'
        ))
        self._add_language(LanguageConfig(
            iso_code='ka', full_name='Georgian', epitran_code=None, phonemizer_code='ka',
            family='Kartvelian', script_type='alphabetic', complexity='high'
        ))
        self._add_language(LanguageConfig(
            iso_code='el', full_name='Greek', epitran_code=None, phonemizer_code='el',
            family='Indo-European', script_type='alphabetic', complexity='medium'
        ))
        self._add_language(LanguageConfig(
            iso_code='gu', full_name='Gujarati', epitran_code=None, phonemizer_code='gu',
            family='Indo-European', script_type='abugida', complexity='medium'
        ))
        self._add_language(LanguageConfig(
            iso_code='he', full_name='Hebrew', epitran_code=None, phonemizer_code='he',
            family='Afro-Asiatic', script_type='abjad', complexity='high'
        ))
        self._add_language(LanguageConfig(
            iso_code='hu', full_name='Hungarian', epitran_code=None, phonemizer_code='hu',
            family='Uralic', script_type='alphabetic', complexity='medium'
        ))
        self._add_language(LanguageConfig(
            iso_code='is', full_name='Icelandic', epitran_code=None, phonemizer_code='is',
            family='Indo-European', script_type='alphabetic', complexity='medium'
        ))
        self._add_language(LanguageConfig(
            iso_code='id', full_name='Indonesian', epitran_code=None, phonemizer_code='id',
            family='Austronesian', script_type='alphabetic', complexity='low'
        ))
        self._add_language(LanguageConfig(
            iso_code='ga', full_name='Irish', epitran_code=None, phonemizer_code='ga',
            family='Indo-European', script_type='alphabetic', complexity='medium'
        ))
        self._add_language(LanguageConfig(
            iso_code='jv', full_name='Javanese', epitran_code=None, phonemizer_code='jv',
            family='Austronesian', script_type='alphabetic', complexity='medium'
        ))
        self._add_language(LanguageConfig(
            iso_code='kn', full_name='Kannada', epitran_code=None, phonemizer_code='kn',
            family='Dravidian', script_type='abugida', complexity='medium'
        ))
        self._add_language(LanguageConfig(
            iso_code='kk', full_name='Kazakh', epitran_code=None, phonemizer_code='kk',
            family='Turkic', script_type='alphabetic', complexity='medium'
        ))
        self._add_language(LanguageConfig(
            iso_code='km', full_name='Khmer', epitran_code=None, phonemizer_code='km',
            family='Austroasiatic', script_type='abugida', complexity='high'
        ))
        self._add_language(LanguageConfig(
            iso_code='lo', full_name='Lao', epitran_code=None, phonemizer_code='lo',
            family='Tai-Kadai', script_type='abugida', complexity='high'
        ))
        self._add_language(LanguageConfig(
            iso_code='lv', full_name='Latvian', epitran_code=None, phonemizer_code='lv',
            family='Indo-European', script_type='alphabetic', complexity='medium'
        ))
        self._add_language(LanguageConfig(
            iso_code='lt', full_name='Lithuanian', epitran_code=None, phonemizer_code='lt',
            family='Indo-European', script_type='alphabetic', complexity='medium'
        ))
        self._add_language(LanguageConfig(
            iso_code='mk', full_name='Macedonian', epitran_code=None, phonemizer_code='mk',
            family='Indo-European', script_type='alphabetic', complexity='medium'
        ))
        self._add_language(LanguageConfig(
            iso_code='ms', full_name='Malay', epitran_code=None, phonemizer_code='ms',
            family='Austronesian', script_type='alphabetic', complexity='low'
        ))
        self._add_language(LanguageConfig(
            iso_code='ml', full_name='Malayalam', epitran_code='mal-Mlym', phonemizer_code='ml',
            family='Dravidian', script_type='abugida', complexity='medium'
        ))
        self._add_language(LanguageConfig(
            iso_code='mt', full_name='Maltese', epitran_code=None, phonemizer_code='mt',
            family='Afro-Asiatic', script_type='alphabetic', complexity='medium'
        ))
        self._add_language(LanguageConfig(
            iso_code='mr', full_name='Marathi', epitran_code=None, phonemizer_code='mr',
            family='Indo-European', script_type='abugida', complexity='medium'
        ))
        self._add_language(LanguageConfig(
            iso_code='mn', full_name='Mongolian', epitran_code=None, phonemizer_code='mn',
            family='Mongolic', script_type='alphabetic', complexity='medium'
        ))
        self._add_language(LanguageConfig(
            iso_code='ne', full_name='Nepali', epitran_code=None, phonemizer_code='ne',
            family='Indo-European', script_type='abugida', complexity='medium'
        ))
        self._add_language(LanguageConfig(
            iso_code='nb', full_name='Norwegian', epitran_code=None, phonemizer_code='nb',
            family='Indo-European', script_type='alphabetic', complexity='low'
        ))
        self._add_language(LanguageConfig(
            iso_code='ps', full_name='Pashto', epitran_code=None, phonemizer_code='ps',
            family='Indo-European', script_type='abugida', complexity='high'
        ))
        self._add_language(LanguageConfig(
            iso_code='fa', full_name='Persian', epitran_code=None, phonemizer_code='fa',
            family='Indo-European', script_type='abjad', complexity='high'
        ))
        self._add_language(LanguageConfig(
            iso_code='pl', full_name='Polish', epitran_code=None, phonemizer_code='pl',
            family='Indo-European', script_type='alphabetic', complexity='medium'
        ))
        self._add_language(LanguageConfig(
            iso_code='ro', full_name='Romanian', epitran_code=None, phonemizer_code='ro',
            family='Indo-European', script_type='alphabetic', complexity='medium'
        ))
        self._add_language(LanguageConfig(
            iso_code='sr', full_name='Serbian', epitran_code=None, phonemizer_code='sr',
            family='Indo-European', script_type='alphabetic', complexity='medium'
        ))
        self._add_language(LanguageConfig(
            iso_code='si', full_name='Sinhala', epitran_code=None, phonemizer_code='si',
            family='Indo-European', script_type='abugida', complexity='high'
        ))
        self._add_language(LanguageConfig(
            iso_code='sk', full_name='Slovak', epitran_code=None, phonemizer_code='sk',
            family='Indo-European', script_type='alphabetic', complexity='medium'
        ))
        self._add_language(LanguageConfig(
            iso_code='sl', full_name='Slovenian', epitran_code=None, phonemizer_code='sl',
            family='Indo-European', script_type='alphabetic', complexity='medium'
        ))
        self._add_language(LanguageConfig(
            iso_code='so', full_name='Somali', epitran_code=None, phonemizer_code='so',
            family='Afro-Asiatic', script_type='alphabetic', complexity='medium'
        ))
        self._add_language(LanguageConfig(
            iso_code='su', full_name='Sundanese', epitran_code=None, phonemizer_code='su',
            family='Austronesian', script_type='alphabetic', complexity='low'
        ))
        self._add_language(LanguageConfig(
            iso_code='sw', full_name='Swahili', epitran_code=None, phonemizer_code='sw',
            family='Niger-Congo', script_type='alphabetic', complexity='low'
        ))
        self._add_language(LanguageConfig(
            iso_code='sv', full_name='Swedish', epitran_code=None, phonemizer_code='sv',
            family='Indo-European', script_type='alphabetic', complexity='low'
        ))
        self._add_language(LanguageConfig(
            iso_code='ta', full_name='Tamil', epitran_code=None, phonemizer_code='ta',
            family='Dravidian', script_type='abugida', complexity='medium'
        ))
        self._add_language(LanguageConfig(
            iso_code='te', full_name='Telugu', epitran_code=None, phonemizer_code='te',
            family='Dravidian', script_type='abugida', complexity='medium'
        ))
        self._add_language(LanguageConfig(
            iso_code='th', full_name='Thai', epitran_code=None, phonemizer_code='th',
            family='Tai-Kadai', script_type='abugida', complexity='high'
        ))
        self._add_language(LanguageConfig(
            iso_code='uk', full_name='Ukrainian', epitran_code=None, phonemizer_code='uk',
            family='Indo-European', script_type='alphabetic', complexity='medium'
        ))
        self._add_language(LanguageConfig(
            iso_code='ur', full_name='Urdu', epitran_code=None, phonemizer_code='ur',
            family='Indo-European', script_type='abugida', complexity='medium'
        ))
        self._add_language(LanguageConfig(
            iso_code='uz', full_name='Uzbek', epitran_code=None, phonemizer_code='uz',
            family='Turkic', script_type='alphabetic', complexity='medium'
        ))
        self._add_language(LanguageConfig(
            iso_code='vi', full_name='Vietnamese', epitran_code=None, phonemizer_code='vi',
            family='Austroasiatic', script_type='alphabetic', complexity='medium'
        ))
        self._add_language(LanguageConfig(
            iso_code='cy', full_name='Welsh', epitran_code=None, phonemizer_code='cy',
            family='Indo-European', script_type='alphabetic', complexity='medium'
        ))
        self._add_language(LanguageConfig(
            iso_code='zu', full_name='Zulu', epitran_code=None, phonemizer_code='zu',
            family='Niger-Congo', script_type='alphabetic', complexity='medium'
        ))

        logger.info(f"Loaded {len(self._languages)} language configurations")

    def _add_language(self, config: LanguageConfig, variant_names: List[str] = None):
        """Add a language configuration to the registry."""
        self._languages[config.iso_code] = config
        self._iso_to_full[config.iso_code] = config.full_name
        self._full_to_iso[config.full_name] = config.iso_code

        # Add variant names if provided
        if variant_names:
            for variant in variant_names:
                self._full_to_iso[variant] = config.iso_code

    def get_config(self, identifier: str) -> Optional[LanguageConfig]:
        """
        Get language configuration by ISO code or full name.

        Args:
            identifier: ISO code (e.g., 'zh') or full name (e.g., 'Chinese')

        Returns:
            LanguageConfig or None if not found
        """
        # Try as ISO code first
        if identifier in self._languages:
            return self._languages[identifier]

        # Try as full name
        iso_code = self._full_to_iso.get(identifier)
        if iso_code:
            return self._languages.get(iso_code)

        return None

    def get_iso_code(self, full_name: str) -> Optional[str]:
        """Get ISO code from full language name."""
        return self._full_to_iso.get(full_name)

    def get_full_name(self, iso_code: str) -> Optional[str]:
        """Get full language name from ISO code."""
        return self._iso_to_full.get(iso_code)

    def get_epitran_code(self, identifier: str) -> Optional[str]:
        """Get Epitran language code for IPA generation."""
        config = self.get_config(identifier)
        return config.epitran_code if config else None

    def get_phonemizer_code(self, identifier: str) -> Optional[str]:
        """Get Phonemizer language code for IPA generation."""
        config = self.get_config(identifier)
        return config.phonemizer_code if config else None

    def is_logographic(self, identifier: str) -> bool:
        """Check if language uses logographic script."""
        config = self.get_config(identifier)
        return config.script_type == 'logographic' if config else False

    def get_supported_languages(self) -> Set[str]:
        """Get set of all supported ISO codes."""
        return set(self._languages.keys())

    def normalize_language_input(self, language_input: str) -> str:
        """
        Normalize language input to standard format.

        Handles various input formats and returns consistent ISO code.

        Args:
            language_input: Language identifier (ISO code, full name, or variant)

        Returns:
            Normalized ISO code, or original input if not recognized
        """
        # Handle common variations
        normalized = language_input.lower().strip()

        # Direct mappings for common variations
        variations = {
            'chinese simplified': 'zh',
            'chinese traditional': 'zh-tw',
            'mandarin chinese': 'zh',
            'mandarin': 'zh',
            'spanish': 'es',
            'hindi': 'hi',
            'arabic': 'ar',
            'english': 'en',
            'japanese': 'ja',
            'korean': 'ko',
            'french': 'fr',
            'german': 'de',
            'italian': 'it',
            'portuguese': 'pt',
            'russian': 'ru',
        }

        if normalized in variations:
            return variations[normalized]

        # Try to find in registry
        config = self.get_config(language_input)
        if config:
            return config.iso_code

        # Return original if not found
        logger.warning(f"Unrecognized language input: {language_input}")
        return language_input

# Global registry instance
_registry = None

def get_language_registry() -> LanguageRegistry:
    """Get the global language registry instance."""
    global _registry
    if _registry is None:
        _registry = LanguageRegistry()
    return _registry