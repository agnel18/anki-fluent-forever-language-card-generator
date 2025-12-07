from __future__ import annotations
import json
import os
import sys
import time
from pathlib import Path
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file (contains GOOGLE_API_KEY)
load_dotenv(Path(__file__).parent.parent / ".env")

# ========== LANGUAGE CONFIGURATION ==========
def load_language_config() -> dict:
    """Load language configuration from language_config.txt"""
    config_file = Path(__file__).parent / "language_config.txt"
    
    if not config_file.exists():
        print("\n❌ ERROR: language_config.txt not found!")
        print("   Please run: python 0_select_language.py")
        sys.exit(1)
    
    config = {}
    with open(config_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if "=" in line:
                key, value = line.split("=", 1)
                config[key.strip()] = value.strip()
    
    return config

# Load configuration
CONFIG = load_language_config()
LANGUAGE_NAME = CONFIG.get("language_name", "Unknown")
LANGUAGE_CODE = CONFIG.get("language_code", "XX")
FREQUENCY_FILE = Path(CONFIG.get("frequency_file"))
OUTPUT_BASE = CONFIG.get("output_dir", "FluentForever_Output")

# ========== FILE PATHS ==========
BASE_DIR = Path(__file__).resolve().parent
EXCEL_FILE = FREQUENCY_FILE  # Input: words to process
OUTPUT_DIR = BASE_DIR / OUTPUT_BASE  # Output: all generated data
AUDIO_DIR = OUTPUT_DIR / "audio"  # MP3 audio files
IMAGE_DIR = OUTPUT_DIR / "images"  # JPG images
WORKING_DATA = OUTPUT_DIR / "working_data.xlsx"  # Review file with all columns
MODEL = "gemini-2.0-flash"  # Google Gemini model for sentence generation
SENTENCES_PER_WORD = 10  # Maximum benefit per token!

# ========== SAFETY LIMITS ==========
MAX_BATCH_WITHOUT_CONFIRMATION = 10  # Hard limit: max 10 words without user confirmation


def resolve_batch_words() -> int:
    """Resolve batch size from CLI arg or env var; default to 1 for safety."""
    cli_value = None
    if len(sys.argv) > 1:
        try:
            cli_value = int(sys.argv[1])
        except ValueError:
            print("⚠️  Ignoring invalid CLI batch size; must be an integer")
    env_value = os.getenv("BATCH_WORDS")
    base = 1  # safest default
    if env_value:
        try:
            base = int(env_value)
        except ValueError:
            print("⚠️  Ignoring invalid BATCH_WORDS in .env; using 1")
            base = 1
    batch_words = cli_value if cli_value is not None else base
    return max(1, batch_words)


BATCH_WORDS = resolve_batch_words()

# Enforce safety limit
if BATCH_WORDS > MAX_BATCH_WITHOUT_CONFIRMATION:
    print(f"\n⚠️  WARNING: You requested {BATCH_WORDS} words")
    print(f"   This will use ~{BATCH_WORDS * SENTENCES_PER_WORD} API requests!")
    print(f"   Daily limit: 1,500 requests")
    print(f"\n   Safety limit is {MAX_BATCH_WITHOUT_CONFIRMATION} words without confirmation.")
    response = input(f"\n   Type 'yes' to proceed with {BATCH_WORDS} words: ").strip().lower()
    if response != "yes":
        print("   Cancelled. Reducing to safety limit.")
        BATCH_WORDS = MAX_BATCH_WITHOUT_CONFIRMATION

# Create directories if they don't exist
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

print(f"\n{'='*60}")
print(f"🌍 GENERATING {SENTENCES_PER_WORD} SENTENCES FOR: {LANGUAGE_NAME}")
print(f"{'='*60}")
print(f"Language Code: {LANGUAGE_CODE}")
print(f"Batch Size: {BATCH_WORDS} words (max {BATCH_WORDS * SENTENCES_PER_WORD} API requests)")
print(f"Output Directory: {OUTPUT_DIR}")
print(f"{'='*60}\n")


def ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure tracking columns exist in the frequency list.
    
    Columns track completion counts at each pipeline stage:
    - Sentences: Number of sentences generated (0-10)
    - Audio: Number of audio files downloaded (0-10)
    - Images: Number of images downloaded (0-10)
    """
    if "Sentences" not in df.columns:
        df["Sentences"] = 0
    if "Audio" not in df.columns:
        df["Audio"] = 0
    if "Images" not in df.columns:
        df["Images"] = 0
    df["Sentences"] = df["Sentences"].fillna(0).astype(int)
    df["Audio"] = df["Audio"].fillna(0).astype(int)
    df["Images"] = df["Images"].fillna(0).astype(int)
    return df


def safe_word(word: str) -> str:
    """
    Clean up word for use in filenames.
    Removes special characters that aren't allowed in file names.
    Example: "ب/ج" → "ب-ج"
    """
    return word.replace("/", "-").replace("\\", "-").strip()


def generate_sentences(word: str, max_retries: int = 3) -> tuple[list[dict] | None, bool]:
    """
    Use Google Gemini API to generate 10 natural sentences for a word.

    Returns: (sentences, stop_flag)
        sentences: List of 10 sentence dicts, or None if failed
        stop_flag: True if we should stop the batch immediately (e.g., quota)
    """
    prompt = f"""You are an expert {LANGUAGE_NAME} language teacher specializing in language learning using the Fluent Forever method.

Word: {word}
Target Language: {LANGUAGE_NAME}

FIRST, provide a brief meaning/definition of this word in English (1-2 sentences).

Then generate exactly 10 natural, authentic sentences that demonstrate all common uses of this word.

Coverage requirements:
1. Different grammatical roles (subject, object, verb, adjective, adverb, preposition)
2. Different tenses and moods (present, past, future, conditional, subjunctive if applicable)
3. Different formality levels (formal, informal, colloquial, slang if applicable)
4. Different real-world contexts (daily life, work, school, family, idioms, proverbs)
5. Natural collocations and word combinations

Requirements for each sentence:
- 4-15 words maximum
- Use only top 1000 most common words (except the target word itself)
- Authentic usage patterns
- Progressive difficulty (simple to slightly complex)
- Age-appropriate and culturally sensitive

Respond ONLY with valid JSON, no extra text, no markdown, no explanation:
{{
  "meaning": "English definition of the word",
  "sentences": [
    {{"sentence": "sentence in {LANGUAGE_NAME}", "english": "English translation", "ipa": "/IPA.pronunciation/"}},
    ...
  ]
}}

Generate the meaning and 10 sentences now:"""

    for attempt in range(1, max_retries + 1):
        try:
            if attempt > 1:
                wait_time = 2 ** attempt  # Exponential backoff: 4s, 8s, 16s
                print(f"   ⏳ Retry {attempt}/{max_retries} after {wait_time}s wait...")
                time.sleep(wait_time)

            print(f"   🔄 Generating {SENTENCES_PER_WORD} sentences for '{word}'...")
            model = genai.GenerativeModel(MODEL)
            response = model.generate_content(prompt)
            content = response.text.strip() if response.text else ""

            if not content:
                print("   ❌ Empty response from API")
                if attempt == max_retries:
                    return None, False
                continue

            # Remove markdown code block markers
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            # Parse JSON
            try:
                data = json.loads(content)
            except json.JSONDecodeError as e:
                print(f"   ❌ JSON parse error: {e}")
                if attempt == max_retries:
                    return None, False
                continue

            # Extract meaning and sentences
            meaning = str(data.get("meaning", "")).strip() if isinstance(data, dict) else ""
            sentences_list = data.get("sentences", data) if isinstance(data, dict) else data

            # Validate
            if not isinstance(sentences_list, list) or len(sentences_list) < SENTENCES_PER_WORD:
                print(f"   ⚠️  Got {len(sentences_list)} sentences, expected {SENTENCES_PER_WORD}")
                if len(sentences_list) < 5:
                    if attempt == max_retries:
                        return None, False
                    continue

            # Normalize
            normalized = []
            for item in sentences_list:
                sentence = str(item.get("sentence", "")).strip()
                english = str(item.get("english", "")).strip()
                ipa = str(item.get("ipa", "")).strip()
                if sentence and english:
                    # Include meaning with each sentence
                    normalized.append({"sentence": sentence, "english": english, "ipa": ipa, "meaning": meaning})

            print(f"   ✅ Generated {len(normalized)} sentences")
            return normalized[:SENTENCES_PER_WORD], False

        except Exception as e:
            error_msg = str(e)
            print(f"   ❌ Error: {error_msg}")

            # Check for quota/rate limit errors
            if "429" in error_msg or "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
                print(f"   ⚠️  QUOTA/RATE LIMIT HIT - Stopping to protect your account")
                print(f"   💡 Wait for quota reset (midnight PT) or upgrade your plan")
                return None, True  # signal to halt entire batch

            if attempt == max_retries:
                print(f"   ❌ Failed after {max_retries} attempts")
                return None, False
            # Otherwise, continue to next retry

    return None, False


def append_to_working_data(word: str, word_meaning: str, freq_num: int, sentences: list[dict]) -> bool:
    """
    Append sentence rows to working_data.xlsx for review before further processing.
    
    Each row represents one sentence for the word and includes:
    - File Name: Pattern {freq:04d}_{word}_{sentence:02d} for tracking
    - What is the Word?: The word
    - Meaning of the Word: English translation
    - Sentence: Full sentence in target language
    - IPA Transliteration: Pronunciation guide
    - English Translation: English translation
    - Sound: (empty, filled by script 2)
    - Image: (empty, filled by script 3)
    
    Returns False if rows already exist (prevents duplicates), True if appended successfully
    """
    # Define correct column order to match Anki import expectations
    CORRECT_COLUMNS = [
        "File Name",
        "What is the Word?",
        "Meaning of the Word",
        "Sentence",
        "IPA Transliteration",
        "English Translation",
        "Sound",
        "Image"
    ]
    
    # Check if rows already exist for this word (prevents duplicate processing)
    if WORKING_DATA.exists():
        existing = pd.read_excel(WORKING_DATA)
        pattern = f"{freq_num:04d}_{word}_"
        if existing["File Name"].str.startswith(pattern, na=False).any():
            print(f"   Rows for '{word}' already exist in {WORKING_DATA.name}. Skipping.")
            return False
        # Reorder existing columns if needed (for consistency)
        if list(existing.columns) != CORRECT_COLUMNS:
            for col in CORRECT_COLUMNS:
                if col not in existing.columns:
                    existing[col] = ""
            existing = existing[CORRECT_COLUMNS]
    else:
        existing = pd.DataFrame()
    
    # Create rows (one per sentence) for this word
    rows = []
    for j, sent in enumerate(sentences, start=1):
        file_name = f"{freq_num:04d}_{word}_{j:02d}"
        # Use meaning from Gemini API if available, otherwise use word_meaning parameter
        meaning_value = sent.get("meaning", word_meaning) or word_meaning
        rows.append({
            "File Name": file_name,
            "What is the Word?": word,
            "Meaning of the Word": meaning_value,
            "Sentence": sent.get("sentence", ""),
            "IPA Transliteration": sent.get("ipa", ""),
            "English Translation": sent.get("english", ""),
            "Sound": "",  # Will be filled by script 2
            "Image": "",  # Will be filled by script 3
        })
    
    # Combine existing rows with new ones
    if not existing.empty:
        combined = pd.concat([existing, pd.DataFrame(rows)], ignore_index=True)
    else:
        combined = pd.DataFrame(rows)
    
    # Ensure correct column order and save
    combined = combined[CORRECT_COLUMNS]
    combined.to_excel(WORKING_DATA, index=False, engine="openpyxl")
    print(f"   ✅ Added {len(rows)} rows to working_data.xlsx")
    return True


def main() -> None:
    """
    Main workflow:
    1. Load API key from .env
    2. Load language configuration from language_config.txt
    3. Read frequency word list for selected language
    4. Find first word with empty Status (not yet processed)
    5. Generate 10 sentences for that word (all use cases)
    6. Append rows to working_data.xlsx
    7. Update Status to "sentences_done"
    """
    # Get Google API key from environment
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ ERROR: GOOGLE_API_KEY is not set in .env file")
        print("   Create .env with: GOOGLE_API_KEY=your_key_here")
        sys.exit(1)
    genai.configure(api_key=api_key)

    # Verify frequency file exists
    if not EXCEL_FILE.exists():
        print(f"❌ ERROR: Frequency file not found: {EXCEL_FILE}")
        print(f"   Make sure to run: python 0_select_language.py")
        sys.exit(1)

    # Load and check frequency list
    df = ensure_columns(pd.read_excel(EXCEL_FILE))
    
    # Find column names dynamically (works with any language)
    word_col = None
    meaning_col = None
    for col in df.columns:
        col_lower = col.lower()
        if 'word' in col_lower:
            word_col = col
        if 'meaning' in col_lower or 'english' in col_lower:
            meaning_col = col
    
    if not word_col:
        print(f"❌ ERROR: Cannot find 'Word' column")
        print(f"   Available columns: {list(df.columns)}")
        sys.exit(1)
    
    # Meaning column is optional - if not found, we'll use just the word
    if not meaning_col:
        print(f"⚠️  No 'Meaning' column found - will use word definition from Gemini")
    
    # Find words that need sentences (Sentences count is 0)
    todo = df[df["Sentences"] == 0]
    if todo.empty:
        print("✅ All words have sentences generated!")
        return

    # Process up to BATCH_WORDS words per run to stay under rate limits
    processed = 0
    for idx in df.index:
        if processed >= BATCH_WORDS:
            print(f"⏸️ Reached batch limit ({BATCH_WORDS} words). Run again for more.")
            break
            
        if df.at[idx, "Sentences"] > 0:
            continue
            
        word_raw = df.loc[idx, word_col]
        word = safe_word(str(word_raw))
        word_meaning = str(df.loc[idx, meaning_col]) if meaning_col and meaning_col in df.columns else ""
        freq_num = idx + 1  # Position in frequency list (1-indexed)
        
        print(f"\n📝 Processing word #{freq_num}: '{word}' ({word_meaning})")

        # Generate 10 sentences using Gemini
        sentences, stop_now = generate_sentences(word)
        if stop_now:
            print("⏸️ Stopping batch due to quota/rate limit.")
            break
        if not sentences or len(sentences) < 5:
            print("❌ Failed to generate sentences. Count not updated for this word.")
            break

        # Save to working_data.xlsx (also checks for duplicates)
        if not append_to_working_data(word, word_meaning, freq_num, sentences):
            print("⚠️  Rows already exist. Updating count only.")
        
        # Update sentence count (10 sentences generated)
        actual_count = len(sentences)
        df.at[idx, "Sentences"] = actual_count
        df.to_excel(EXCEL_FILE, index=False, engine="openpyxl")
        print(f"✅ Updated Sentences={actual_count}/10 for word #{freq_num}")
        print(f"✅ Word '{word}' complete! Run script 2 to download audio.")
        processed += 1


if __name__ == "__main__":
    main()

