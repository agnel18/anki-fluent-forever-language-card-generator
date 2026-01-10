# IPA Service for Sentence Generation
# Handles IPA (International Phonetic Alphabet) generation and validation

import logging
import time
import unicodedata
from typing import Dict, Optional
from collections import defaultdict

# Import language registry for consistent language handling
from language_registry import get_language_registry

logger = logging.getLogger(__name__)


class IPAService:
    """
    Enhanced IPA Service supporting all 77 languages via tiered approach.

    Tiers:
    1. Epitran (highest quality, ~60 languages)
    2. Phonemizer + espeak-ng (broad coverage, 77 languages)
    3. AI fallback (universal, guaranteed non-empty)
    """

    def __init__(self):
        # Get language registry
        self.registry = get_language_registry()
        
        # Performance monitoring
        self.metrics = {
            'total_requests': 0,
            'tier_usage': defaultdict(int),
            'language_usage': defaultdict(int),
            'response_times': [],
            'errors': defaultdict(int)
        }
        
        # Load mappings from registry
        self.epitran_map = self._load_epitran_mappings()
        self.phonemizer_map = self._load_phonemizer_mappings()
    
    def _load_epitran_mappings(self) -> Dict[str, Optional[str]]:
        """Load Epitran language codes for supported languages (Epitran v1.34.0)."""
        return {
            # Indo-European (23 languages)
            "English": "eng-Latn",  # A) Fully supported
            "German": "deu-Latn",  # A) Fully supported
            "Dutch": "nld-Latn",  # A) Fully supported
            "Swedish": "swe-Latn",  # A) Fully supported
            "Danish": "dan-Latn",  # A) Fully supported
            "Norwegian": "nno-Latn",  # B) Supported as nno-Latn (Nynorsk), not nob-Latn
            "Icelandic": None,  # C) NOT supported
            "Spanish": "spa-Latn",  # A) Fully supported
            "French": "fra-Latn",  # A) Fully supported
            "Italian": "ita-Latn",  # A) Fully supported
            "Portuguese": "por-Latn",  # A) Fully supported
            "Romanian": "ron-Latn",  # A) Fully supported
            "Catalan": "cat-Latn",  # A) Fully supported
            "Russian": "rus-Cyrl",  # A) Fully supported
            "Polish": "pol-Latn",  # A) Fully supported
            "Czech": "ces-Latn",  # A) Fully supported
            "Ukrainian": "ukr-Cyrl",  # A) Fully supported
            "Bulgarian": None,  # C) NOT supported
            "Serbian": "srp-Latn",  # A) Fully supported
            "Hindi": "hin-Deva",  # A) Fully supported
            "Bengali": "ben-Beng",  # A) Fully supported
            "Persian": "fas-Arab",  # A) Fully supported
            "Urdu": "urd-Arab",  # A) Fully supported
            "Punjabi": "pan-Guru",  # A) Fully supported
            "Gujarati": None,  # C) NOT supported
            "Marathi": "mar-Deva",  # A) Fully supported
            "Greek": None,  # C) NOT supported
            "Lithuanian": "lit-Latn",  # A) Fully supported
            "Latvian": "lav-Latn",  # A) Fully supported
            "Irish": "gle-Latn",  # A) Fully supported
            "Welsh": "cym-Latn",  # A) Fully supported
            "Breton": None,  # C) NOT supported
            "Armenian": None,  # C) NOT supported
            "Albanian": "sqi-Latn",  # A) Fully supported
            
            # Afro-Asiatic (12 languages)
            "Arabic": "ara-Arab",  # A) Fully supported
            "Hebrew": None,  # C) NOT supported
            "Amharic": "amh-Ethi",  # A) Fully supported
            "Hausa": "hau-Latn",  # A) Fully supported
            "Somali": "som-Latn",  # A) Fully supported (added in recent versions)
            "Tigrinya": "tir-Ethi",  # A) Fully supported
            "Berber": None,  # C) NOT supported
            "Coptic": None,  # C) NOT supported
            "Maltese": "mlt-Latn",  # A) Fully supported
            
            # Niger-Congo (15 languages)
            "Swahili": "swa-Latn",  # A) Fully supported
            "Zulu": "zul-Latn",  # A) Fully supported
            "Yoruba": "yor-Latn",  # A) Fully supported
            "Igbo": None,  # C) NOT supported
            "Wolof": None,  # C) NOT supported
            "Bambara": None,  # C) NOT supported
            "Ewe": None,  # C) NOT supported
            "Tswana": "tsn-Latn",  # B) Supported as tsn-Latn (capital L), not tsn-latn
            "Sesotho": None,  # C) NOT supported
            
            # Austronesian (7 languages)
            "Malay": "msa-Latn",  # A) Fully supported
            "Indonesian": "ind-Latn",  # A) Fully supported
            "Tagalog": "tgl-Latn",  # A) Fully supported
            "Maori": "mri-Latn",  # A) Fully supported
            "Hawaiian": None,  # C) NOT supported
            "Malagasy": None,  # C) NOT supported
            "Javanese": None,  # C) NOT supported
            
            # Turkic (6 languages)
            "Turkish": "tur-Latn",  # A) Fully supported
            "Uzbek": "uzb-Latn",  # A) Fully supported
            "Kazakh": "kaz-Cyrl",  # A) Fully supported
            "Kyrgyz": "kir-Cyrl",  # A) Fully supported
            "Tatar": None,  # C) NOT supported
            "Azerbaijani": "aze-Latn",  # A) Fully supported
            
            # Dravidian (4 languages)
            "Tamil": "tam-Taml",  # A) Fully supported
            "Telugu": "tel-Telu",  # A) Fully supported
            "Kannada": "kan-Knda",  # A) Fully supported
            "Malayalam": "mal-Mlym",  # A) Fully supported
            
            # Japonic (2 languages)
            "Japanese": "jpn-Hira",  # A) Fully supported
            "Ryukyuan": None,  # C) NOT supported
            
            # Koreanic (1 language)
            "Korean": "kor-Hang",  # A) Fully supported
            
            # Tai-Kadai (3 languages)
            "Thai": "tha-Thai",  # A) Fully supported
            "Lao": "lao-Laoo",  # A) Fully supported
            "Zhuang": None,  # C) NOT supported
            
            # Hmong-Mien (2 languages)
            "Hmong": None,  # C) NOT supported
            "Mien": None,  # C) NOT supported
            
            # Austroasiatic (4 languages)
            "Vietnamese": "vie-Latn",  # A) Fully supported
            "Khmer": "khm-Khmr",  # A) Fully supported
            "Mon": None,  # C) NOT supported
            "Khasi": None,  # C) NOT supported
            
            # Tibeto-Burman (6 languages)
            "Tibetan": None,  # C) NOT supported
            "Burmese": "mya-Mymr",  # A) Fully supported
            "Karen": None,  # C) NOT supported
            "Yi": None,  # C) NOT supported
            "Bai": None,  # C) NOT supported
            "Tujia": None,  # C) NOT supported
            
            # Sino-Tibetan (8 languages) - Chinese handled specially
            "Chinese (Simplified)": None,  # A) Correct - skip Epitran (use Phonemizer/AI)
            "Chinese (Traditional)": None,  # A) Correct - skip Epitran (use Phonemizer/AI)
            
            # Other isolates and small families
            "Nubian": None,  # C) NOT supported
            "Basque": None,  # C) NOT supported
            "Na-Dene": None,  # C) NOT supported
            "Eskimo-Aleut": None,  # C) NOT supported
            "Australian Aboriginal": None,  # C) NOT supported
        }
    
    def _load_phonemizer_mappings(self) -> Dict[str, str]:
        """Load Phonemizer BCP 47 codes for all languages."""
        return {
            # Complete mappings for all 77 languages
            "English": "en",
            "German": "de",
            "Dutch": "nl",
            "Swedish": "sv",
            "Danish": "da",
            "Norwegian": "nb",  # Bokmål
            "Icelandic": "is",
            "Spanish": "es",
            "French": "fr",
            "Italian": "it",
            "Portuguese": "pt",
            "Romanian": "ro",
            "Catalan": "ca",
            "Russian": "ru",
            "Polish": "pl",
            "Czech": "cs",
            "Ukrainian": "uk",
            "Bulgarian": "bg",
            "Serbian": "sr",
            "Hindi": "hi",
            "Bengali": "bn",
            "Persian": "fa",
            "Urdu": "ur",
            "Punjabi": "pa",
            "Gujarati": "gu",
            "Marathi": "mr",
            "Greek": "el",
            "Lithuanian": "lt",
            "Latvian": "lv",
            "Irish": "ga",
            "Welsh": "cy",
            "Breton": "br",
            "Armenian": "hy",
            "Albanian": "sq",
            
            # Afro-Asiatic
            "Arabic": "ar",
            "Hebrew": "he",
            "Amharic": "am",
            "Hausa": "ha",
            "Somali": "so",
            "Tigrinya": "ti",
            "Berber": "ber",  # Generic
            "Coptic": "cop",
            "Maltese": "mt",
            
            # Niger-Congo
            "Swahili": "sw",
            "Zulu": "zu",
            "Yoruba": "yo",
            "Igbo": "ig",
            "Hausa": "ha",  # Duplicate
            "Wolof": "wo",
            "Bambara": "bm",
            "Ewe": "ee",
            "Tswana": "tn",
            "Sesotho": "st",
            
            # Austronesian
            "Malay": "ms",
            "Indonesian": "id",
            "Tagalog": "tl",
            "Maori": "mi",
            "Hawaiian": "haw",
            "Malagasy": "mg",
            "Javanese": "jv",
            
            # Turkic
            "Turkish": "tr",
            "Uzbek": "uz",
            "Kazakh": "kk",
            "Kyrgyz": "ky",
            "Tatar": "tt",
            "Azerbaijani": "az",
            
            # Dravidian
            "Tamil": "ta",
            "Telugu": "te",
            "Kannada": "kn",
            "Malayalam": "ml",
            
            # Japonic
            "Japanese": "ja",
            "Ryukyuan": "ja",  # Fallback to Japanese
            
            # Koreanic
            "Korean": "ko",
            
            # Tai-Kadai
            "Thai": "th",
            "Lao": "lo",
            "Zhuang": "za",
            
            # Hmong-Mien
            "Hmong": "hmn",
            "Mien": "hmn",  # Fallback
            
            # Austroasiatic
            "Vietnamese": "vi",
            "Khmer": "km",
            "Mon": "mnw",
            "Khasi": "kha",
            
            # Tibeto-Burman
            "Tibetan": "bo",
            "Burmese": "my",
            "Karen": "kar",  # Generic
            "Yi": "ii",
            "Bai": "ba",
            "Tujia": "de",  # Fallback
            
            # Sino-Tibetan
            "Chinese (Simplified)": "cmn",  # Mandarin
            "Chinese (Traditional)": "cmn",  # Mandarin
            "Tibetan": "bo",  # Duplicate
            "Burmese": "my",  # Duplicate
            "Karen": "kar",  # Duplicate
            "Yi": "ii",  # Duplicate
            "Bai": "ba",  # Duplicate
            "Tujia": "de",  # Duplicate
            
            # Other
            "Nubian": "fia",  # Generic Nubian
            "Basque": "eu",
            "Navajo": "nv",
            "Apache": "nv",  # Fallback
            "Inuit": "iu",
            "Aleut": "ale",
            "Pitjantjatjara": "pit",
            "Warlpiri": "wbp",
            "Arrernte": "aer",
        }

    def generate_ipa_hybrid(self, text: str, language: str, ai_ipa: str = "") -> str:
        """
        Generate IPA using tiered approach with guaranteed non-empty return.

        Tiers:
        1. Epitran (highest quality when available)
        2. Phonemizer + espeak-ng (broad coverage)
        3. AI fallback (universal guarantee)

        Args:
            text: Text to transliterate
            language: Language identifier (ISO code or full name)
            ai_ipa: AI-generated IPA fallback

        Returns:
            IPA string (never empty)
        """
        start_time = time.time()
        self.metrics['total_requests'] += 1
        
        # Normalize language input using registry
        normalized_lang = self.registry.normalize_language_input(language)
        full_lang_name = self.registry.get_full_name(normalized_lang) or language
        
        self.metrics['language_usage'][full_lang_name] += 1

        try:
            if not text or not text.strip():
                return ""

            # Tier 1: Epitran (highest quality)
            ipa = self._try_epitran(text, normalized_lang)
            if ipa and self._validate_ipa(ipa, normalized_lang, strict=True):
                self.metrics['tier_usage']['epitran'] += 1
                response_time = time.time() - start_time
                self.metrics['response_times'].append(response_time)
                logger.info(f"IPA success via Epitran for {full_lang_name} ({response_time:.3f}s)")
                return ipa

            # Tier 2: Phonemizer (broad coverage)
            ipa = self._try_phonemizer(text, normalized_lang)
            if ipa and self._validate_ipa(ipa, normalized_lang, strict=True):
                self.metrics['tier_usage']['phonemizer'] += 1
                response_time = time.time() - start_time
                self.metrics['response_times'].append(response_time)
                logger.info(f"IPA success via Phonemizer for {full_lang_name} ({response_time:.3f}s)")
                return ipa

            # Tier 3: AI fallback (guaranteed)
            fallback_ipa = self._ensure_fallback_ipa(ai_ipa, text, normalized_lang)
            self.metrics['tier_usage']['ai_fallback'] += 1
            response_time = time.time() - start_time
            self.metrics['response_times'].append(response_time)
            logger.info(f"IPA fallback used for {full_lang_name} ({response_time:.3f}s)")
            return fallback_ipa

        except Exception as e:
            self.metrics['errors']['generation'] += 1
            response_time = time.time() - start_time
            self.metrics['response_times'].append(response_time)
            logger.error(f"IPA generation failed for {full_lang_name}: {e} ({response_time:.3f}s)")
            # Ultimate fallback
            return f"[IPA generation error for {full_lang_name}]"

    def get_metrics(self) -> Dict:
        """Get performance metrics for monitoring."""
        total_requests = self.metrics['total_requests']
        if not total_requests:
            return {
                'total_requests': 0,
                'tier_usage': {},
                'top_languages': [],
                'avg_response_time': 0.0,
                'error_rate': 0.0,
                'uptime_percent': 100.0
            }

        # Calculate averages
        avg_response_time = sum(self.metrics['response_times']) / len(self.metrics['response_times']) if self.metrics['response_times'] else 0.0

        # Calculate error rate
        total_errors = sum(self.metrics['errors'].values())
        error_rate = (total_errors / total_requests) * 100

        # Get top languages
        top_languages = sorted(
            self.metrics['language_usage'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        return {
            'total_requests': total_requests,
            'tier_usage': dict(self.metrics['tier_usage']),
            'top_languages': top_languages,
            'avg_response_time': avg_response_time,
            'error_rate': error_rate,
            'uptime_percent': 100.0 - error_rate
        }

    def reset_metrics(self):
        """Reset metrics for fresh monitoring period."""
        self.metrics = {
            'total_requests': 0,
            'tier_usage': defaultdict(int),
            'language_usage': defaultdict(int),
            'response_times': [],
            'errors': defaultdict(int)
        }
    
    def _try_epitran(self, text: str, language: str) -> str:
        """Attempt Epitran transliteration with backoff for multi-script languages."""
        # Skip Chinese (returns Pinyin-like output)
        if language in ['zh', 'zh-tw']:
            return ""
        
        epi_code = self.registry.get_epitran_code(language)
        if not epi_code:
            return ""
        
        try:
            import epitran
            
            # Multi-script languages that benefit from backoff
            multi_script_langs = {
                "Kazakh": ["kaz-Cyrl", "kaz-Latn"],
                "Uzbek": ["uzb-Latn", "uzb-Cyrl"], 
                "Serbian": ["srp-Latn", "srp-Cyrl"]
            }
            
            if language in multi_script_langs:
                # Use epitran.backoff for multi-script support
                backoff = epitran.backoff(multi_script_langs[language])
                ipa = backoff.transliterate(text)
            else:
                # Standard epitran for single-script languages
                epi = epitran.Epitran(epi_code)
                ipa = epi.transliterate(text)
            
            # Basic quality validation
            if ipa and ipa != text and len(ipa.strip()) > 0:
                # Unicode normalization for consistency
                normalized_ipa = unicodedata.normalize('NFC', ipa.strip())
                return normalized_ipa
            return ""
            
        except UnicodeDecodeError as e:
            logger.warning(f"Epitran encoding issue for {language}: {e}")
            return ""
        except ImportError:
            logger.warning(f"Epitran not available for {language}")
            return ""
        except Exception as e:
            logger.warning(f"Epitran failed for {language}: {e}")
            return ""
    
    def _try_phonemizer(self, text: str, language: str) -> str:
        """Attempt Phonemizer with available backends."""
        phone_code = self.registry.get_phonemizer_code(language)
        if not phone_code:
            return ""
        
        try:
            import phonemizer
            
            # Try different backends in order of preference
            backends = ['espeak', 'festival', 'segments']
            
            for backend in backends:
                try:
                    ipa = phonemizer.phonemize(
                        text,
                        language=phone_code,
                        backend=backend,
                        strip=True,
                        preserve_punctuation=False,
                        with_stress=True
                    )
                    
                    # Clean and validate
                    ipa = ipa.strip()
                    if ipa and len(ipa) > 0:
                        logger.info(f"Phonemizer success with {backend} backend for {language}")
                        return unicodedata.normalize('NFC', ipa)
                        
                except Exception as e:
                    logger.debug(f"Phonemizer {backend} backend failed for {language}: {e}")
                    continue
            
            # All backends failed
            logger.warning(f"All Phonemizer backends failed for {language}")
            return ""
            
        except ImportError:
            logger.warning(f"Phonemizer not available for {language}")
            return ""
        except Exception as e:
            logger.warning(f"Phonemizer failed for {language}: {e}")
            return ""
    
    def _validate_ipa(self, ipa: str, language: str, strict: bool = False) -> bool:
        """Validate IPA with optional strict mode for Tier 1&2 vs lenient for AI."""
        if not ipa or not ipa.strip():
            return False
        
        # Use comprehensive validation
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
        from generation_utils import validate_ipa_output
        is_valid, validation_msg = validate_ipa_output(ipa, language)
        
        if is_valid:
            return True
        
        # In strict mode, reject invalid IPA (for Tier 1&2 quality control)
        if strict:
            logger.warning(f"Strict IPA validation failed for {language}: {validation_msg}")
            return False
        
        # Log warning but don't reject - accept best effort (for AI tier)
        logger.warning(f"IPA validation failed for {language}: {validation_msg}")
        
        # Basic quality checks
        ipa_clean = ipa.strip()
        
        # Reject obvious Pinyin (Chinese-specific check)
        if any(char in ipa_clean for char in 'āēīōūǖǎěǐǒǔǚ'):
            logger.warning(f"Rejected Pinyin contamination in {language} IPA")
            return False
        
        # Accept if it has content and looks IPA-like
        return len(ipa_clean) > 0
    
    def _ensure_fallback_ipa(self, ai_ipa: str, text: str, language: str) -> str:
        """Guarantee non-empty IPA return."""
        # Try AI IPA first
        if ai_ipa and ai_ipa.strip():
            if self._validate_ipa(ai_ipa, language):
                return ai_ipa
            # Accept even if validation fails (best effort)
            if len(ai_ipa.strip()) > 0:
                return ai_ipa
        
        # Ultimate fallback: meaningful placeholder
        logger.warning(f"All IPA tiers failed for {language}, using placeholder")
        return f"[IPA unavailable for {language}]"