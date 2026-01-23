# Audio generation module
# Extracted from core_functions.py for better separation of concerns

import os
import asyncio
import logging
import re
from typing import Optional, List

# Conditional import for Google Cloud TTS
try:
    from google.cloud import texttospeech
    GOOGLE_TTS_AVAILABLE = True
except ImportError:
    GOOGLE_TTS_AVAILABLE = False
    texttospeech = None

# Import error recovery
from error_recovery import graceful_degradation, resilient_audio_generation

logger = logging.getLogger(__name__)

# ============================================================================
# GOOGLE CLOUD TEXT-TO-SPEECH CONFIGURATION
# ============================================================================

def get_google_tts_config():
    """Get Google Cloud Text-to-Speech configuration."""
    import streamlit as st
    api_key = ""
    try:
        api_key = st.session_state.get("google_api_key", os.getenv("GOOGLE_API_KEY", ""))
    except:
        api_key = os.getenv("GOOGLE_API_KEY", "")

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

    # Set the API key as environment variable for authentication
    os.environ["GOOGLE_API_KEY"] = config["api_key"]

    return texttospeech.TextToSpeechClient()

def is_google_tts_configured():
    """Check if Google Cloud Text-to-Speech is properly configured."""
    try:
        get_google_tts_client()
        return True
    except (ValueError, Exception):
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
    Generate audio asynchronously using Google Cloud Text-to-Speech.

    Args:
        text: Text to synthesize
        voice_name: Google TTS voice name (e.g., "en-US-Neural2-D")
        output_path: Path to save MP3 file
        rate: Playback speed (0.5-2.0; 0.8 is learner-friendly)
        language_code: BCP-47 language code (e.g., "en-US", "zh-CN")

    Returns:
        True if successful, False otherwise
    """
    if not GOOGLE_TTS_AVAILABLE:
        logger.warning("Google Cloud Text-to-Speech SDK not available")
        return False

    try:
        # Validate input text
        if not text or not text.strip():
            logger.warning("Empty or whitespace-only text provided for audio generation")
            return False

        # Get Google TTS client
        client = get_google_tts_client()

        # Parse voice name to extract language code and voice type
        # Voice name format: "language-voice" (e.g., "en-US-Neural2-D")
        voice_parts = voice_name.split('-')
        if len(voice_parts) >= 3:
            lang_code = f"{voice_parts[0]}-{voice_parts[1]}"
            voice_type = voice_parts[2] if len(voice_parts) > 2 else "Neural2"
        else:
            lang_code = language_code
            voice_type = "Neural2"

        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(text=text.strip())

        # Build the voice request
        voice = texttospeech.VoiceSelectionParams(
            language_code=lang_code,
            name=voice_name
        )

        # Select the type of audio file you want returned
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=rate,  # Playback speed
        )

        # Perform the text-to-speech request
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        # The response's audio_content is binary
        with open(output_path, "wb") as out:
            out.write(response.audio_content)

        logger.info(f"Google TTS synthesis completed for voice: {voice_name}")
        return True

    except Exception as exc:
        logger.error(f"Google TTS error for {voice_name}: {exc}")
        # Clean up any empty file that might have been created
        if os.path.exists(output_path) and os.path.getsize(output_path) == 0:
            try:
                os.unlink(output_path)
            except:
                pass  # Ignore cleanup errors
        return False
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
    Batch generate audio files synchronously using Google Cloud Text-to-Speech.

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
            tasks.append(generate_audio_google_async(sentence, voice, str(output_path), rate, language_code))

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

def get_google_voices_for_language(language_name: str) -> List[str]:
    """
    Get all available Google TTS voices for a specific language with descriptive names.

    Args:
        language_name: Language name (e.g., "Chinese", "Spanish", "English")

    Returns:
        List of descriptive voice names (e.g., "Xiaoxiao (Female, Neural2)", "Yunxi (Male, Neural2)")
    """
    # Map language names to BCP-47 codes
    bcp47_code = _get_bcp47_code(language_name)
    if not bcp47_code:
        return ["en-US-Neural2-D (Female, Neural2)"]  # Default fallback

    # Get all voices for this language
    voices = get_google_available_voices(bcp47_code)

    if not voices:
        # Fallback to English if no voices found
        return ["en-US-Neural2-D (Female, Neural2)"]

    # Format voice names with gender and quality information
    formatted_voices = []
    for voice in voices:
        voice_name = voice['name']

        # Extract voice type (Neural2, WaveNet, Standard)
        if 'Neural2' in voice_name:
            voice_type = 'Neural2'
        elif 'Wavenet' in voice_name or 'WaveNet' in voice_name:
            voice_type = 'WaveNet'
        elif 'Standard' in voice_name:
            voice_type = 'Standard'
        else:
            voice_type = 'Unknown'

        # Get gender
        gender = voice['ssml_gender']
        if gender == 1:  # SSML_VOICE_GENDER_MALE
            gender_str = 'Male'
        elif gender == 2:  # SSML_VOICE_GENDER_FEMALE
            gender_str = 'Female'
        else:
            gender_str = 'Unknown'

        # Create descriptive name
        # Extract the voice identifier (last part after the last dash)
        name_parts = voice_name.split('-')
        if len(name_parts) >= 3:
            voice_id = name_parts[-1]  # e.g., "D", "A", "C"
            descriptive_name = f"{voice_id} ({gender_str}, {voice_type})"
        else:
            descriptive_name = f"{voice_name} ({gender_str}, {voice_type})"

        formatted_voices.append(descriptive_name)

    # Sort by quality (Neural2 first, then WaveNet, then Standard)
    quality_order = {'Neural2': 0, 'WaveNet': 1, 'Standard': 2}
    formatted_voices.sort(key=lambda x: quality_order.get(x.split(', ')[1].rstrip(')'), 3))

    return formatted_voices if formatted_voices else ["en-US-Neural2-D (Female, Neural2)"]

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
        # Chinese variants
        "Chinese": "zh-CN",
        "Chinese (Simplified)": "zh-CN",
        "Chinese (Traditional)": "zh-TW",
        "Mandarin Chinese": "zh-CN",
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