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
        # Core languages with full configurations
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

        # Add more languages as needed
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