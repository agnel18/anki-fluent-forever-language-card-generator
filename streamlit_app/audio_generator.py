# Audio generation module
# Extracted from core_functions.py for better separation of concerns

import os
import asyncio
import logging
import re
import base64
import requests
from typing import Optional, List

# Load environment variables
try:
    from dotenv import load_dotenv
    # Load .env file from the project root (parent directory of streamlit_app)
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path)
    # Also try loading from current directory (streamlit_app/.env)
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
except ImportError:
    pass  # dotenv not available, continue without it

# Conditional import for Google Cloud TTS
try:
    from google.cloud import texttospeech
    GOOGLE_TTS_SDK_AVAILABLE = True
except ImportError:
    GOOGLE_TTS_SDK_AVAILABLE = False
    texttospeech = None

# TTS availability now depends on API key, not SDK
GOOGLE_TTS_AVAILABLE = True  # Always available via REST API

# Import error recovery
from error_recovery import graceful_degradation, resilient_audio_generation

# Import error recovery
from error_recovery import graceful_degradation, resilient_audio_generation

logger = logging.getLogger(__name__)

# ============================================================================
# GOOGLE CLOUD TEXT-TO-SPEECH CONFIGURATION
# ============================================================================

def get_google_tts_config():
    """Get Google Cloud Text-to-Speech configuration."""
    api_key = ""
    try:
        # Try to get from centralized config first
        try:
            from config.api_keys import get_api_key
            # This will fail if streamlit is not available
            import streamlit as st
            api_key = get_api_key('text_to_speech', st.session_state) or ""
        except ImportError:
            pass

        # Fallback to direct environment/session check
        if not api_key:
            try:
                import streamlit as st
                api_key = st.session_state.get("google_api_key", os.getenv("GOOGLE_TTS_API_KEY", os.getenv("GOOGLE_API_KEY", "")))
            except ImportError:
                # Streamlit not available, use environment variables only
                api_key = os.getenv("GOOGLE_TTS_API_KEY", os.getenv("GOOGLE_API_KEY", ""))
    except Exception as e:
        logger.warning(f"Error getting TTS config: {e}")
        # Final fallback to environment variables
        api_key = os.getenv("GOOGLE_TTS_API_KEY", os.getenv("GOOGLE_API_KEY", ""))

    return {
        "api_key": api_key,
    }

def get_google_tts_client():
    """Get Google Cloud Text-to-Speech client."""
    if not GOOGLE_TTS_AVAILABLE:
        raise ValueError("Google Cloud Text-to-Speech SDK not available")

    config = get_google_tts_config()
    if not config["api_key"]:
        raise ValueError("GOOGLE_API_KEY not set")

    # For Google Cloud client libraries, we need to use google-auth with API key
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials

        # Create credentials using API key
        # Note: This is a workaround since TTS client library doesn't directly support API keys
        os.environ["GOOGLE_API_KEY"] = config["api_key"]

        # Try to create client - this may work if the environment variable is set
        return texttospeech.TextToSpeechClient()

    except Exception as e:
        logger.warning(f"TTS client creation with API key failed: {e}")
        # Fallback: try creating client without explicit auth
        # This might work in environments where ADC is already set up
        try:
            return texttospeech.TextToSpeechClient()
        except Exception as e2:
            logger.error(f"TTS client fallback also failed: {e2}")
            raise ValueError(f"Failed to create TTS client. Please ensure Google Cloud credentials are properly configured. Error: {e2}")

def is_google_tts_configured():
    """Check if Google Cloud Text-to-Speech is properly configured."""
    try:
        config = get_google_tts_config()
        return bool(config["api_key"])  # Only need API key for REST API
    except Exception as e:
        logger.warning(f"Failed to check TTS configuration: {e}")
        # Fallback: check environment variables directly
        import os
        return bool(os.getenv("GOOGLE_TTS_API_KEY") or os.getenv("GOOGLE_API_KEY"))

# ============================================================================
# GOOGLE CLOUD TEXT-TO-SPEECH REST API FUNCTIONS
# ============================================================================

# Note: TTS now uses REST API with API keys instead of client library
# This eliminates the need for Google Cloud authentication setup

def get_google_tts_voices_rest(language_code: str = None) -> List[dict]:
    """
    Get available Google Cloud Text-to-Speech voices using REST API.

    Args:
        language_code: Optional BCP-47 language code filter (e.g., "en-US", "zh-CN")

    Returns:
        List of voice dictionaries with name, language_codes, ssml_gender, and natural_sample_rate_hertz
    """
    config = get_google_tts_config()
    if not config["api_key"]:
        logger.warning("No API key available for Google TTS")
        return []

    try:
        # REST API endpoint for listing voices
        url = "https://texttospeech.googleapis.com/v1/voices"
        params = {"key": config["api_key"]}

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        voices = data.get("voices", [])

        if not voices:
            logger.warning("No voices returned from Google TTS REST API")
            return []

        # Filter by language code if provided
        if language_code:
            filtered_voices = []
            for voice in voices:
                if language_code in voice.get("languageCodes", []):
                    filtered_voices.append({
                        'name': voice['name'],
                        'language_codes': voice.get('languageCodes', []),
                        'ssml_gender': voice.get('ssmlGender', 0),
                        'natural_sample_rate_hertz': voice.get('naturalSampleRateHertz', 0)
                    })
            logger.info(f"Found {len(filtered_voices)} voices for language {language_code}")
            return filtered_voices
        else:
            # Return all voices
            logger.info(f"Found {len(voices)} total voices")
            return [{
                'name': voice['name'],
                'language_codes': voice.get('languageCodes', []),
                'ssml_gender': voice.get('ssmlGender', 0),
                'natural_sample_rate_hertz': voice.get('naturalSampleRateHertz', 0)
            } for voice in voices]

    except requests.exceptions.RequestException as e:
        logger.error(f"Network error getting Google TTS voices: {e}")
        return []
    except Exception as exc:
        logger.error(f"Unexpected error getting Google TTS voices via REST API: {exc}")
        return []

async def generate_audio_google_rest_async(
    text: str,
    voice_name: str,
    output_path: str,
    rate: float = 0.8,
    language_code: str = "en-US",
) -> bool:
    """
    Generate audio using Google Cloud Text-to-Speech REST API.

    Args:
        text: Text to synthesize
        voice_name: Google TTS voice name (e.g., "en-US-Neural2-D")
        output_path: Path to save MP3 file
        rate: Playback speed (0.5-2.0; 0.8 is learner-friendly)
        language_code: BCP-47 language code (e.g., "en-US", "zh-CN")

    Returns:
        True if successful, False otherwise
    """
    config = get_google_tts_config()
    if not config["api_key"]:
        logger.warning("No API key available for Google TTS")
        return False

    try:
        # Validate input text
        if not text or not text.strip():
            logger.warning("Empty or whitespace-only text provided for audio generation")
            return False

        # Parse voice name to extract language code and voice type
        voice_parts = voice_name.split('-')
        if len(voice_parts) >= 3:
            lang_code = f"{voice_parts[0]}-{voice_parts[1]}"
            voice_type = voice_parts[2] if len(voice_parts) > 2 else "Neural2"
        else:
            lang_code = language_code
            voice_type = "Neural2"

        # Prepare request data for REST API
        request_data = {
            "input": {
                "text": text.strip()
            },
            "voice": {
                "languageCode": lang_code,
                "name": voice_name
            },
            "audioConfig": {
                "audioEncoding": "MP3",
                "speakingRate": rate
            }
        }

        # Make REST API call
        url = "https://texttospeech.googleapis.com/v1/text:synthesize"
        params = {"key": config["api_key"]}

        response = requests.post(url, params=params, json=request_data, timeout=30)
        response.raise_for_status()

        data = response.json()
        audio_content_base64 = data.get("audioContent")

        if not audio_content_base64:
            logger.error("No audio content received from Google TTS REST API")
            return False

        # Decode base64 audio content and save to file
        try:
            audio_content = base64.b64decode(audio_content_base64)
        except Exception as e:
            logger.error(f"Failed to decode base64 audio content: {e}")
            return False

        with open(output_path, "wb") as out:
            out.write(audio_content)

        logger.info(f"Google TTS REST synthesis completed for voice: {voice_name}")
        return True

    except requests.exceptions.Timeout:
        logger.error(f"Timeout error generating audio with voice {voice_name}")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error generating audio with voice {voice_name}: {e}")
        return False
    except Exception as exc:
        logger.error(f"Unexpected error in Google TTS REST generation for {voice_name}: {exc}")
        # Clean up any empty file that might have been created
        if os.path.exists(output_path) and os.path.getsize(output_path) == 0:
            try:
                os.unlink(output_path)
            except:
                pass  # Ignore cleanup errors
        return False

# ============================================================================
# AUDIO GENERATION (Google Cloud Text-to-Speech)
# ============================================================================
async def generate_audio_google_async(
    text: str,
    voice_name: str,
    output_path: str,
    rate: float = 0.8,  # Playback speed for learners
    language_code: str = "en-US",
) -> bool:
    """
    Generate audio asynchronously using Google Cloud Text-to-Speech REST API.

    Args:
        text: Text to synthesize
        voice_name: Google TTS voice name (e.g., "en-US-Neural2-D")
        output_path: Path to save MP3 file
        rate: Playback speed (0.5-2.0; 0.8 is learner-friendly)
        language_code: BCP-47 language code (e.g., "en-US", "zh-CN")

    Returns:
        True if successful, False otherwise
    """
    # Use REST API implementation instead of client library
    return await generate_audio_google_rest_async(text, voice_name, output_path, rate, language_code)
async def generate_audio_async(
    text: str,
    voice: str,
    output_path: str,
    rate: float = 0.8,  # Playback speed for learners
) -> bool:
    """
    Generate audio asynchronously using Google Cloud Text-to-Speech.

    Args:
        text: Text to synthesize
        voice: Google TTS voice name (e.g., "en-US-Neural2-A")
        output_path: Path to save MP3 file
        rate: Playback speed (0.5-2.0; 0.8 is learner-friendly)

    Returns:
        True if successful, False otherwise
    """
    try:
        # Validate input text
        if not text or not text.strip():
            logger.warning("Empty or whitespace-only text provided for audio generation")
            return False

        # Extract language code from voice name (e.g., "en-US-Neural2-A" -> "en-US")
        language_code = "-".join(voice.split("-")[:2]) if "-" in voice else "en-US"

        # Use Google TTS
        return await generate_audio_google_async(text, voice, output_path, rate, language_code)

    except Exception as exc:
        logger.error(f"Audio generation error for {voice}: {exc}")
        # Clean up any empty file that might have been created
        if os.path.exists(output_path) and os.path.getsize(output_path) == 0:
            try:
                os.unlink(output_path)
            except:
                pass  # Ignore cleanup errors
        return False

@graceful_degradation("Audio generation", continue_on_failure=True)
@resilient_audio_generation(max_retries=1)
def generate_audio(
    sentences: List[str],
    voice: str,
    output_dir: str,
    batch_name: str = "batch",
    rate: float = 0.8,
    exact_filenames: Optional[List[str]] = None,
    language: str = "English",
    unique_id: str = None,
) -> List[str]:
    """
    Batch generate audio files synchronously using Google Cloud Text-to-Speech REST API.

    Args:
        sentences: List of sentences to synthesize
        voice: Google TTS voice name (e.g., "en-US-Neural2-D")
        output_dir: Directory to save MP3 files
        batch_name: Prefix for filenames
        rate: Playback speed
        exact_filenames: Custom filenames for each sentence
        language: Language name (for BCP-47 code lookup)

    Returns:
        List of generated file paths
    """
    # Check if TTS is configured (has API key)
    if not is_google_tts_configured():
        logger.warning("Google Cloud Text-to-Speech not configured - no API key available")
        return []

    os.makedirs(output_dir, exist_ok=True)

    # Get BCP-47 language code from language name
    language_code = _get_bcp47_code(language)

    async def batch_generate():
        tasks = []
        for i, sentence in enumerate(sentences):
            from pathlib import Path
            if exact_filenames and i < len(exact_filenames):
                filename = exact_filenames[i]
            else:
                # Use unique ID to prevent filename conflicts
                unique_suffix = f"_{unique_id}" if unique_id else ""
                filename = f"{batch_name}_{i+1:02d}{unique_suffix}.mp3"
            output_path = Path(output_dir) / filename

            # Use Google TTS REST API
            tasks.append(generate_audio_google_rest_async(sentence, voice, str(output_path), rate, language_code))

        results = await asyncio.gather(*tasks)
        return results

    # Run event loop
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    results = loop.run_until_complete(batch_generate())

    # Maintain correct indices even for failed generations
    generated_files = []
    for i, success in enumerate(results):
        if success:
            if exact_filenames and i < len(exact_filenames):
                filename = exact_filenames[i]
            else:
                # Use unique ID to prevent filename conflicts
                unique_suffix = f"_{unique_id}" if unique_id else ""
                filename = f"{batch_name}_{i+1:02d}{unique_suffix}.mp3"
            generated_files.append(filename)
        else:
            generated_files.append("")  # Empty string for failed generations

    return generated_files

@graceful_degradation("Audio generation", continue_on_failure=True)
@resilient_audio_generation(max_retries=1)
def generate_audio_google(
    sentences: List[str],
    voice_name: str,
    output_dir: str,
    batch_name: str = "batch",
    rate: float = 0.8,
    exact_filenames: Optional[List[str]] = None,
    language: str = "English",
    unique_id: str = None,
) -> List[str]:
    """
    Batch generate audio files synchronously using Google Cloud Text-to-Speech.

    Args:
        sentences: List of sentences to synthesize
        voice_name: Google TTS voice name (e.g., "en-US-Neural2-D")
        output_dir: Directory to save MP3 files
        batch_name: Prefix for filenames
        rate: Playback speed
        exact_filenames: Custom filenames for each sentence
        language: Language name (for BCP-47 code lookup)

    Returns:
        List of generated file paths
    """
    if not GOOGLE_TTS_AVAILABLE:
        logger.warning("Google Cloud Text-to-Speech SDK not available")
        return []

    os.makedirs(output_dir, exist_ok=True)

    # Get BCP-47 language code from language name
    language_code = _get_bcp47_code(language)

    async def batch_generate():
        tasks = []
        for i, sentence in enumerate(sentences):
            from pathlib import Path
            if exact_filenames and i < len(exact_filenames):
                filename = exact_filenames[i]
            else:
                # Use unique ID to prevent filename conflicts
                unique_suffix = f"_{unique_id}" if unique_id else ""
                filename = f"{batch_name}_{i+1:02d}{unique_suffix}.mp3"
            output_path = Path(output_dir) / filename

            # Use Google TTS
            tasks.append(generate_audio_google_async(sentence, voice_name, str(output_path), rate, language_code))

        results = await asyncio.gather(*tasks)
        return results

    # Run event loop
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    results = loop.run_until_complete(batch_generate())

    # Maintain correct indices even for failed generations
    generated_files = []
    for i, success in enumerate(results):
        if success:
            if exact_filenames and i < len(exact_filenames):
                filename = exact_filenames[i]
            else:
                # Use unique ID to prevent filename conflicts
                unique_suffix = f"_{unique_id}" if unique_id else ""
                filename = f"{batch_name}_{i+1:02d}{unique_suffix}.mp3"
            generated_files.append(filename)
        else:
            generated_files.append("")  # Empty string for failed generations

    return generated_files
    """Sanitize word for filesystem-safe names."""
    safe = re.sub(r"[^\w\-]+", "_", word.strip())
    return safe or "word"

# ============================================================================
# GOOGLE TTS VOICE DISCOVERY AND MAPPING
# ============================================================================

def get_google_available_voices(language_code: str = None) -> List[dict]:
    """
    Get all available Google Cloud Text-to-Speech voices.

    Args:
        language_code: Optional BCP-47 language code filter (e.g., "en-US", "zh-CN")

    Returns:
        List of voice dictionaries with name, language_codes, ssml_gender, and natural_sample_rate_hertz
    """
    if not GOOGLE_TTS_AVAILABLE:
        logger.warning("Google Cloud Text-to-Speech SDK not available")
        return []

    try:
        client = get_google_tts_client()

        # Get all available voices
        response = client.list_voices()
        voices = response.voices

        # Filter by language code if provided
        if language_code:
            filtered_voices = []
            for voice in voices:
                if language_code in voice.language_codes:
                    filtered_voices.append({
                        'name': voice.name,
                        'language_codes': voice.language_codes,
                        'ssml_gender': voice.ssml_gender,
                        'natural_sample_rate_hertz': voice.natural_sample_rate_hertz
                    })
            return filtered_voices
        else:
            # Return all voices
            return [{
                'name': voice.name,
                'language_codes': voice.language_codes,
                'ssml_gender': voice.ssml_gender,
                'natural_sample_rate_hertz': voice.natural_sample_rate_hertz
            } for voice in voices]

    except Exception as exc:
        logger.error(f"Error getting Google TTS voices: {exc}")
        return []

def get_google_voices_for_language(language_name: str) -> tuple[List[str], bool, dict]:
    """
    Get all available Google TTS voices for a specific language with descriptive names.

    Args:
        language_name: Language name (e.g., "Chinese", "Spanish", "English")

    Returns:
        Tuple of (voice_options, is_fallback, display_to_voice_map) where:
        - voice_options: List of descriptive voice names for display
        - is_fallback: True if using fallback voices due to API failure
        - display_to_voice_map: Dict mapping display names to actual Google TTS voice names
    """
    # Map language names to BCP-47 codes
    bcp47_code = _get_bcp47_code(language_name)
    if not bcp47_code:
        return ["D (Female, Neural2)"], True  # Default fallback

    # Get all voices for this language using REST API
    voices = get_google_tts_voices_rest(bcp47_code)

    # If no voices found (likely due to auth issues), provide language-specific fallbacks
    if not voices:
        logger.warning(f"No voices found for {language_name} ({bcp47_code}), using fallbacks")

        # Language-specific fallback voices for all 77 supported languages
        # These return display names that the UI expects
        fallbacks = {
            # European Languages
            "af": ["A (Female, Standard)", "B (Male, Standard)"],  # Afrikaans
            "sq": ["A (Female, Standard)", "B (Male, Standard)"],  # Albanian
            "hy": ["A (Female, Standard)", "B (Male, Standard)"],  # Armenian
            "az": ["A (Female, Standard)", "B (Male, Standard)"],  # Azerbaijani
            "eu": ["A (Female, Standard)", "B (Male, Standard)"],  # Basque
            "be": ["A (Female, Standard)", "B (Male, Standard)"],  # Belarusian
            "bs": ["A (Female, Standard)", "B (Male, Standard)"],  # Bosnian
            "bg": ["A (Female, Standard)", "B (Male, Standard)"],  # Bulgarian
            "ca": ["A (Female, Standard)", "B (Male, Standard)"],  # Catalan
            "hr": ["A (Female, Standard)", "B (Male, Standard)"],  # Croatian
            "cs": ["A (Female, Standard)", "B (Male, Standard)"],  # Czech
            "da": ["A (Female, Standard)", "B (Male, Standard)"],  # Danish
            "nl": ["A (Female, Standard)", "B (Male, Standard)"],  # Dutch
            "en": ["Emma (Female, Standard)", "Liam (Male, Standard)"],  # English
            "et": ["A (Female, Standard)", "B (Male, Standard)"],  # Estonian
            "fi": ["A (Female, Standard)", "B (Male, Standard)"],  # Finnish
            "fr": ["Sophie (Female, Standard)", "Pierre (Male, Standard)"],  # French
            "gl": ["A (Female, Standard)", "B (Male, Standard)"],  # Galician
            "ka": ["A (Female, Standard)", "B (Male, Standard)"],  # Georgian
            "de": ["Anna (Female, Standard)", "Max (Male, Standard)"],  # German
            "el": ["A (Female, Standard)", "B (Male, Standard)"],  # Greek
            "hu": ["A (Female, Standard)", "B (Male, Standard)"],  # Hungarian
            "is": ["A (Female, Standard)", "B (Male, Standard)"],  # Icelandic
            "ga": ["A (Female, Standard)", "B (Male, Standard)"],  # Irish
            "it": ["Giulia (Female, Standard)", "Marco (Male, Standard)"],  # Italian
            "lv": ["A (Female, Standard)", "B (Male, Standard)"],  # Latvian
            "lt": ["A (Female, Standard)", "B (Male, Standard)"],  # Lithuanian
            "mk": ["A (Female, Standard)", "B (Male, Standard)"],  # Macedonian
            "mt": ["A (Female, Standard)", "B (Male, Standard)"],  # Maltese
            "no": ["A (Female, Standard)", "B (Male, Standard)"],  # Norwegian
            "pl": ["A (Female, Standard)", "B (Male, Standard)"],  # Polish
            "pt": ["Ana (Female, Standard)", "João (Male, Standard)"],  # Portuguese
            "ro": ["A (Female, Standard)", "B (Male, Standard)"],  # Romanian
            "ru": ["Olga (Female, Standard)", "Dmitri (Male, Standard)"],  # Russian
            "sr": ["A (Female, Standard)", "B (Male, Standard)"],  # Serbian
            "sk": ["A (Female, Standard)", "B (Male, Standard)"],  # Slovak
            "sl": ["A (Female, Standard)", "B (Male, Standard)"],  # Slovenian
            "es": ["Maria (Female, Standard)", "Carlos (Male, Standard)"],  # Spanish
            "sv": ["A (Female, Standard)", "B (Male, Standard)"],  # Swedish
            "tr": ["A (Female, Standard)", "B (Male, Standard)"],  # Turkish
            "uk": ["A (Female, Standard)", "B (Male, Standard)"],  # Ukrainian
            "cy": ["A (Female, Standard)", "B (Male, Standard)"],  # Welsh

            # Asian Languages
            "am": ["A (Female, Standard)", "B (Male, Standard)"],  # Amharic
            "ar": ["Fatima (Female, Standard)", "Ahmed (Male, Standard)"],  # Arabic
            "bn": ["A (Female, Standard)", "B (Male, Standard)"],  # Bengali
            "my": ["A (Female, Standard)", "B (Male, Standard)"],  # Burmese
            "zh": ["Li (Female, Standard)", "Wang (Male, Standard)"],  # Chinese
            "gu": ["A (Female, Standard)", "B (Male, Standard)"],  # Gujarati
            "iw": ["A (Female, Standard)", "B (Male, Standard)"],  # Hebrew
            "hi": ["Priya (Female, Standard)", "Raj (Male, Standard)"],  # Hindi
            "id": ["A (Female, Standard)", "B (Male, Standard)"],  # Indonesian
            "ja": ["Yumi (Female, Standard)", "Hiroshi (Male, Standard)"],  # Japanese
            "jw": ["A (Female, Standard)", "B (Male, Standard)"],  # Javanese
            "kn": ["A (Female, Standard)", "B (Male, Standard)"],  # Kannada
            "kk": ["A (Female, Standard)", "B (Male, Standard)"],  # Kazakh
            "km": ["A (Female, Standard)", "B (Male, Standard)"],  # Khmer
            "ko": ["Ji-yeon (Female, Standard)", "Min-jun (Male, Standard)"],  # Korean
            "lo": ["A (Female, Standard)", "B (Male, Standard)"],  # Lao
            "ml": ["A (Female, Standard)", "B (Male, Standard)"],  # Malayalam
            "ms": ["A (Female, Standard)", "B (Male, Standard)"],  # Malay
            "mr": ["A (Female, Standard)", "B (Male, Standard)"],  # Marathi
            "mn": ["A (Female, Standard)", "B (Male, Standard)"],  # Mongolian
            "ne": ["A (Female, Standard)", "B (Male, Standard)"],  # Nepali
            "fa": ["A (Female, Standard)", "B (Male, Standard)"],  # Persian
            "ps": ["A (Female, Standard)", "B (Male, Standard)"],  # Pashto
            "si": ["A (Female, Standard)", "B (Male, Standard)"],  # Sinhala
            "su": ["A (Female, Standard)", "B (Male, Standard)"],  # Sundanese
            "ta": ["A (Female, Standard)", "B (Male, Standard)"],  # Tamil
            "te": ["A (Female, Standard)", "B (Male, Standard)"],  # Telugu
            "th": ["A (Female, Standard)", "B (Male, Standard)"],  # Thai
            "ur": ["A (Female, Standard)", "B (Male, Standard)"],  # Urdu
            "uz": ["A (Female, Standard)", "B (Male, Standard)"],  # Uzbek
            "vi": ["A (Female, Standard)", "B (Male, Standard)"],  # Vietnamese

            # African Languages
            "so": ["A (Female, Standard)", "B (Male, Standard)"],  # Somali
            "sw": ["A (Female, Standard)", "B (Male, Standard)"],  # Swahili
            "zu": ["A (Female, Standard)", "B (Male, Standard)"]   # Zulu
        }
        lang_prefix = bcp47_code.split('-')[0]
        fallback_voices = fallbacks.get(lang_prefix, ["D (Female, Neural2)"])
        return fallback_voices, True, {}

    # Format voice names with gender and quality information
    formatted_voices = []
    
    # Create a mapping for more user-friendly voice names
    friendly_names = {
        # English voices - map some to recognizable names
        "Achernar": "Emma",
        "Achird": "James", 
        "Algenib": "Michael",
        "Algieba": "David",
        "Alnilam": "Christopher",
        "Aoede": "Sarah",
        "Autonoe": "Jessica",
        "Callirrhoe": "Jennifer",
        "Charon": "Matthew",
        "Despina": "Amanda",
        # Add more mappings as needed
    }
    
    for voice in voices:
        voice_name = voice['name']

        # Get gender
        gender = voice['ssml_gender']
        if gender == 1 or gender == 'MALE' or gender == 'MALE':  # SSML_VOICE_GENDER_MALE
            gender_str = 'Male'
        elif gender == 2 or gender == 'FEMALE' or gender == 'FEMALE':  # SSML_VOICE_GENDER_FEMALE
            gender_str = 'Female'
        else:
            gender_str = 'Unknown'

        # Use friendly name if available, otherwise use the constellation name
        display_name = friendly_names.get(voice_name, voice_name)
        
        # For the new constellation-named voices, use a simpler format
        # These appear to be high-quality neural voices
        descriptive_name = f"{display_name} ({gender_str})"

        formatted_voices.append(descriptive_name)

    # Sort voices to prioritize Standard voices first, then alphabetically
    def sort_key(voice_name):
        # Check if this is a Standard voice (prioritize them)
        if "Standard" in voice_name:
            return (0, voice_name)  # Standard voices first
        else:
            return (1, voice_name)  # Other voices second
    
    formatted_voices.sort(key=sort_key)

    # Create mapping from display names back to actual voice names
    display_to_voice_map = {}
    for voice in voices:
        voice_name = voice['name']
        gender = voice['ssml_gender']
        if gender == 1 or gender == 'MALE' or gender == 'MALE':
            gender_str = 'Male'
        elif gender == 2 or gender == 'FEMALE' or gender == 'FEMALE':
            gender_str = 'Female'
        else:
            gender_str = 'Unknown'
        
        display_name = friendly_names.get(voice_name, voice_name)
        descriptive_name = f"{display_name} ({gender_str})"
        display_to_voice_map[descriptive_name] = voice_name

    return formatted_voices if formatted_voices else ["Emma (Female)"], False, display_to_voice_map

def _voice_for_language(language: str) -> str:
    """
    Get default Google TTS voice for a language.

    Args:
        language: Language name (e.g., "Spanish", "Chinese (Simplified)")

    Returns:
        Google TTS voice name (e.g., "es-ES-Standard-A", "zh-CN-Standard-C")
    """
    voice_map = {
        "Spanish": "es-ES-Standard-A",
        "French": "fr-FR-Standard-A",
        "German": "de-DE-Standard-B",
        "Italian": "it-IT-Standard-A",
        "Portuguese": "pt-BR-Standard-A",
        "Russian": "ru-RU-Standard-A",
        "Japanese": "ja-JP-Standard-B",
        "Korean": "ko-KR-Standard-A",
        "Chinese": "cmn-CN-Standard-C",
        "Chinese (Simplified)": "cmn-CN-Standard-C",
        "Chinese (Traditional)": "zh-TW-Standard-A",
        "Arabic": "ar-XA-Standard-B",
        "Hindi": "hi-IN-Standard-A",
        "Mandarin Chinese": "cmn-CN-Standard-C",
        "English": "en-US-Standard-D",
    }
    return voice_map.get(language, "en-US-Standard-D")

def _get_bcp47_code(language_name: str) -> str:
    """
    Convert language name to BCP-47 code for Google TTS.

    Args:
        language_name: Language name (e.g., "Chinese", "Spanish")

    Returns:
        BCP-47 language code (e.g., "zh-CN", "es-ES")
    """
    # Comprehensive mapping from language names to BCP-47 codes
    bcp47_map = {
        # Chinese variants - use cmn-CN for Neural2 voice names
        "Chinese": "cmn-CN",
        "Chinese (Simplified)": "cmn-CN",
        "Chinese (Traditional)": "zh-TW",
        "Mandarin Chinese": "cmn-CN",
        "Cantonese": "zh-HK",

        # Major European languages
        "English": "en-US",
        "Spanish": "es-ES",
        "French": "fr-FR",
        "German": "de-DE",
        "Italian": "it-IT",
        "Portuguese": "pt-BR",
        "Russian": "ru-RU",
        "Dutch": "nl-NL",
        "Polish": "pl-PL",
        "Turkish": "tr-TR",
        "Swedish": "sv-SE",
        "Norwegian": "nb-NO",
        "Danish": "da-DK",
        "Finnish": "fi-FI",
        "Greek": "el-GR",
        "Czech": "cs-CZ",
        "Hungarian": "hu-HU",
        "Romanian": "ro-RO",
        "Bulgarian": "bg-BG",
        "Croatian": "hr-HR",
        "Slovak": "sk-SK",
        "Slovenian": "sl-SI",
        "Ukrainian": "uk-UA",
        "Serbian": "sr-RS",
        "Bosnian": "bs-BA",

        # Asian languages
        "Japanese": "ja-JP",
        "Korean": "ko-KR",
        "Hindi": "hi-IN",
        "Arabic": "ar-SA",
        "Hebrew": "he-IL",
        "Thai": "th-TH",
        "Vietnamese": "vi-VN",
        "Indonesian": "id-ID",
        "Malay": "ms-MY",
        "Tamil": "ta-IN",
        "Telugu": "te-IN",
        "Kannada": "kn-IN",
        "Bengali": "bn-IN",
        "Gujarati": "gu-IN",
        "Marathi": "mr-IN",
        "Urdu": "ur-IN",
        "Persian": "fa-IR",
        "Pashto": "ps-AF",

        # Other languages
        "Afrikaans": "af-ZA",
        "Albanian": "sq-AL",
        "Amharic": "am-ET",
        "Armenian": "hy-AM",
        "Azerbaijani": "az-AZ",
        "Basque": "eu-ES",
        "Belarusian": "be-BY",
        "Estonian": "et-EE",
        "Georgian": "ka-GE",
        "Icelandic": "is-IS",
        "Irish": "ga-IE",
        "Kazakh": "kk-KZ",
        "Khmer": "km-KH",
        "Lao": "lo-LA",
        "Latvian": "lv-LV",
        "Lithuanian": "lt-LT",
        "Macedonian": "mk-MK",
        "Maltese": "mt-MT",
        "Mongolian": "mn-MN",
        "Nepali": "ne-NP",
        "Sinhala": "si-LK",
        "Swahili": "sw-KE",
        "Welsh": "cy-GB",
        "Zulu": "zu-ZA",
        "Burmese": "my-MM",
        "Javanese": "jv-ID",
        "Sundanese": "su-ID",
        "Uzbek": "uz-UZ",
    }

    return bcp47_map.get(language_name, "en-US")

def get_voice_name_from_display(display_name: str) -> str:
    """
    Convert descriptive voice display name back to Google TTS voice name.

    Args:
        display_name: Descriptive name (e.g., "D (Female, Neural2)")

    Returns:
        Google TTS voice name (e.g., "en-US-Neural2-D")
    """
    # This is a simplified mapping - in practice, we'd need to maintain a mapping
    # For now, return a default voice
    # TODO: Implement proper reverse mapping
    return "en-US-Neural2-D"