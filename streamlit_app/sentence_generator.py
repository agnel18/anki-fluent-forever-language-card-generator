# Sentence generation module
# Extracted from core_functions.py for better separation of concerns

import json
import logging
from typing import Optional, List, Dict, Any
from groq import Groq

# Import cache manager and error recovery
from cache_manager import cached_api_call
from error_recovery import resilient_groq_call, with_fallback

logger = logging.getLogger(__name__)

# ============================================================================
# IPA GENERATION (Stub)
# ============================================================================
def generate_ipa_hybrid(text: str, language: str, ai_ipa: str = "") -> str:
    """Stub: Returns the provided ai_ipa or an empty string."""
    return ai_ipa or ""

# ============================================================================
# WORD MEANING GENERATION (Groq)
# ============================================================================
@cached_api_call("groq_meaning", ttl_seconds=86400)  # Cache for 24 hours
@resilient_groq_call(max_retries=3)
@with_fallback(fallback_value=lambda word, **kwargs: word)  # Fallback to word itself
def generate_word_meaning(
    word: str,
    language: str,
    groq_api_key: str = None,
) -> str:
    """
    Generate English meaning and brief explanation for a word.

    Args:
        word: Target language word
        language: Language name (e.g., "Spanish", "Hindi")
        groq_api_key: Groq API key

    Returns:
        String with meaning and brief explanation (e.g., "he (male pronoun, used as subject)")
    """
    if not groq_api_key:
        raise ValueError("Groq API key required")

    client = Groq(api_key=groq_api_key)

    prompt = f"""Provide a brief English meaning for the {language} word \"{word}\".

Format: Return ONLY a single line with the meaning and a brief explanation in parentheses.
Example: \"house (a building where people live)\" or \"he (male pronoun, used as subject)\"

IMPORTANT: Return ONLY the meaning line, nothing else. No markdown, no explanation, no JSON."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,  # Lower temperature for consistency
            max_tokens=100,
        )
        # --- API USAGE TRACKING ---
        try:
            import streamlit as st
            if "groq_api_calls" not in st.session_state:
                st.session_state.groq_api_calls = 0
            if "groq_tokens_used" not in st.session_state:
                st.session_state.groq_tokens_used = 0
            st.session_state.groq_api_calls += 1
            # Estimate tokens used (prompt+completion)
            st.session_state.groq_tokens_used += 100  # rough estimate, adjust if needed
        except Exception:
            pass
        # -------------------------
        meaning = response.choices[0].message.content.strip()

        # Clean up any quotes
        meaning = meaning.strip('"\'')
        logger.info(f"Generated meaning for '{word}': {meaning}")
        return meaning if meaning else word

    except Exception as e:
        logger.error(f"Error generating meaning for '{word}': {e}")
        return word  # Fallback to word itself

# ============================================================================
# SENTENCE GENERATION (Groq)
# ============================================================================
def generate_sentences(
    word: str,
    meaning: str,
    language: str,
    num_sentences: int = 10,
    min_length: int = 5,
    max_length: int = 20,
    difficulty: str = "intermediate",
    groq_api_key: str = None,
    topics: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Generate sentences using optimized 2-pass architecture:
    1. PASS 1: Generate raw sentences (high quality, plain text, no JSON)
    2. PASS 2: Batch validate + enrich ALL sentences in ONE API call

    This approach:
    - Reduces token usage from ~2000 to ~400 per word (5× cheaper than 3-pass)
    - Maintains high quality through separate generation and validation
    - Processes ~250 words/month on 100k free tokens (vs ~50 with 3-pass)

    Args:
        word: Target language word
        meaning: English meaning
        language: Language name (e.g., "Spanish", "Hindi")
        num_sentences: Number of sentences to generate (1-20)
        min_length: Minimum sentence length in words
        max_length: Maximum sentence length in words
        difficulty: "beginner", "intermediate", "advanced"
        groq_api_key: Groq API key
        topics: List of topics to focus sentence generation around (optional)

    Returns:
        List of dicts with keys: sentence, english_translation, ipa, context, image_keywords, role_of_word, word, meaning
    """
    if not groq_api_key:
        raise ValueError("Groq API key required")

    try:
        # PASS 1: Generate raw sentences (plain text, no JSON)
        logger.info(f"PASS 1: Generating {num_sentences} raw sentences for '{word}' ({language})...")
        raw_sentences = _generate_sentences_pass1(
            word=word,
            meaning=meaning,
            language=language,
            num_sentences=num_sentences,
            min_length=min_length,
            max_length=max_length,
            difficulty=difficulty,
            groq_api_key=groq_api_key,
            topics=topics,
        )

        # PASS 2: Batch validate + enrich all sentences in ONE call
        logger.info(f"PASS 2: Batch validating + enriching {len(raw_sentences)} sentences...")
        enriched_results = _validate_and_enrich_batch_pass2(
            sentences=raw_sentences,
            word=word,
            language=language,
            groq_api_key=groq_api_key,
        )

        # Combine with word/meaning metadata
        final_sentences = []
        for result in enriched_results:
            final_sentences.append({
                "sentence": result.get("sentence", ""),
                "english_translation": result.get("english_translation", ""),
                "context": result.get("context", "general"),
                "ipa": result.get("ipa", ""),
                "image_keywords": result.get("image_keywords", ""),
                "role_of_word": result.get("role_of_word", ""),
                "word": word,
                "meaning": meaning,
            })

        logger.info(f"✓ Completed 2-pass generation for '{word}': {len(final_sentences)} sentences")
        return final_sentences
    except Exception as exc:
        logger.error(f"2-pass sentence generation error: {exc}")
        return []

# ============================================================================
# PASS 1: SENTENCE GENERATION (Raw sentences, no JSON)
# ============================================================================
def _generate_sentences_pass1(
    word: str,
    meaning: str,
    language: str,
    num_sentences: int = 10,
    min_length: int = 5,
    max_length: int = 20,
    difficulty: str = "intermediate",
    groq_api_key: Optional[str] = None,
    topics: Optional[List[str]] = None,
) -> List[str]:

    try:
        client = Groq(api_key=groq_api_key)

        # Build topic section if topics are provided
        topic_section = ""
        if topics:
            topic_section = """===========================
TOPIC FOCUS
===========================
Focus the sentences around these topics: """ + ', '.join(topics) + """
Ensure the sentences are relevant to these topics while maintaining natural language use.
"""

        prompt = f"""
You are a native-level expert linguist in {language} with professional experience teaching it to non-native learners.

Your task:
Generate exactly {num_sentences} highly natural, idiomatic, culturally appropriate sentences in {language} for the word \"{word}\" ({meaning}).

{topic_section}===========================
QUALITY RULES (STRICT)
===========================
- Every sentence must sound like it was written by an educated native speaker. Native speakers should NOT cringe at the sentence.
- Absolutely no unnatural, robotic, or literal-translation phrasing.
- Grammar, syntax, spelling, diacritics, gender agreement, case, politeness level, and punctuation must all be correct.
- The target word \"{word}\" MUST:
    * be used correctly in context,
    * match its real meaning,
    * NOT be forced into an unnatural construction.
- If the word cannot be used naturally, do NOT use it. Instead, create a sentence that clearly conveys the meaning of \"{word}\" in context, even if the word itself isn't used.
- Avoid rare or archaic vocabulary (unless difficulty=\"advanced\").
- All sentences must be semantically meaningful (no filler templates).
- No repeated sentence structures or patterns — each sentence must be unique.

- Each sentence must be {min_length}-{max_length} words long.
- Difficulty: {difficulty}
    - beginner: Use only simple vocabulary and grammar, mostly present tense.
    - intermediate: Use mixed tenses, richer but still natural language.
    - advanced: Use complex structures, nuanced vocabulary, and advanced grammar.

===========================
VARIETY REQUIREMENTS
===========================
Across the {num_sentences} sentences:
- Use different tenses (if applicable to {language}).
- Use different sentence types: declarative, interrogative, imperative.
- Use the target word in different grammatical roles if possible.
- Use diverse real-life contexts: home, travel, food, emotions, work, social life, daily actions.

===========================
IMPORTANT
===========================
- RETURN ONLY the {language} sentences, one per line.
- NO English translation.
- NO explanation.
- NO JSON.
- NO numbering.
- NO extra text.
- Each line = ONE sentence only.
"""
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1200,
        )
        response_text = response.choices[0].message.content.strip()
        # Split by newlines and filter empty lines
        sentences = [s.strip() for s in response_text.split("\n") if s.strip()]
        return sentences[:num_sentences]
    except Exception as e:
        logger.error(f"PASS 1 (sentence generation) error: {e}")
        return []

# ============================================================================
# PASS 2: BATCH VALIDATION + ENRICHMENT (All sentences in one call)
# ============================================================================
@cached_api_call("groq_sentences_pass2", ttl_seconds=86400)  # Cache for 24 hours
@resilient_groq_call(max_retries=3)
@with_fallback(fallback_value=lambda sentences, **kwargs: [
    {
        "sentence": s,
        "valid": True,  # Assume valid if API fails
        "english_translation": "",
        "ipa": "",
        "context": "general",
        "image_keywords": "",
        "role_of_word": "",
    } for s in sentences
])
def _validate_and_enrich_batch_pass2(
    sentences: List[str],
    word: str,
    language: str,
    groq_api_key: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    PASS 2: Validate and enrich ALL sentences in a single batched API call.
    This is 5× more efficient than separate validation + enrichment per sentence.

    Args:
        sentences: List of raw sentences from Pass 1
        word: Target word used in sentences
        language: Language name
        groq_api_key: Groq API key

    Returns:
        List of dicts, each with keys: sentence, valid, english_translation, ipa, context, image_keywords, role_of_word
    """
    if not groq_api_key:
        raise ValueError("Groq API key required")

    client = Groq(api_key=groq_api_key)

    # Build numbered sentence list for prompt
    sentences_text = "\n".join([f"{i+1}. {s}" for i, s in enumerate(sentences)])

    prompt = f"""You are a native linguist for {language}.

Task: For each sentence below, validate it and provide enrichment data.

Sentences:
{sentences_text}

For EACH sentence, check:
- Is it natural and grammatically correct?
- Is "{word}" used correctly?
- Are spelling/accents/diacritics correct?
- Is it culturally appropriate?

Return a JSON array with one object per sentence (in order):

[
  {{
    "sentence": "corrected sentence if needed, otherwise original",
    "valid": true/false,
    "english_translation": "natural English translation",
    "ipa": "full IPA transcription using correct symbols",
    "context": "one short phrase (e.g., office, family, travel)",
    "image_keywords": "2-3 concrete nouns or actions for images",
    "role_of_word": "grammatical role of '{word}' (subject, verb, adjective, etc.)"
  }},
  ...
]

IMPORTANT:
- Return ONLY valid JSON array, no markdown, no explanation.
- IPA must use official IPA symbols only.
- Image keywords must be visually representable.
- If sentence is valid, keep it unchanged in "sentence" field.
- If invalid, provide corrected version in "sentence" field."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=2000,  # Enough for 10 sentences with full enrichment
        )

        response_text = response.choices[0].message.content.strip()

        # Extract JSON
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        results = json.loads(response_text)

        # Validate structure
        if not isinstance(results, list):
            logger.error("PASS 2 batch: Expected JSON array")
            return []

        # Ensure we have the right number of results
        validated_results = []
        for i, result in enumerate(results[:len(sentences)]):
            if isinstance(result, dict):
                validated_results.append({
                    "sentence": result.get("sentence", sentences[i]),
                    "valid": result.get("valid", False),
                    "english_translation": result.get("english_translation", ""),
                    "ipa": result.get("ipa", ""),
                    "context": result.get("context", "general"),
                    "image_keywords": result.get("image_keywords", ""),
                    "role_of_word": result.get("role_of_word", ""),
                })

        return validated_results

    except json.JSONDecodeError as e:
        logger.error(f"PASS 2 batch JSON parse error: {e}")
        # Return fallback data
        return [{
            "sentence": s,
            "valid": False,
            "english_translation": "",
            "ipa": "",
            "context": "general",
            "image_keywords": "",
            "role_of_word": "",
        } for s in sentences]
    except Exception as e:
        logger.error(f"PASS 2 batch error: {e}")
        return [{
            "sentence": s,
            "valid": False,
            "english_translation": "",
            "ipa": "",
            "context": "general",
            "image_keywords": "",
            "role_of_word": "",
        } for s in sentences]