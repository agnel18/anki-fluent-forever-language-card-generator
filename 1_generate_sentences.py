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

# ========== CONFIG: File paths and settings ==========
BASE_DIR = Path(__file__).resolve().parent
EXCEL_FILE = BASE_DIR / "Arabic Frequency Word List.xlsx"  # Input: words to process
OUTPUT_DIR = BASE_DIR / "FluentForever_Arabic_Perfect"  # Output: all generated data
AUDIO_DIR = OUTPUT_DIR / "audio"  # MP3 audio files
IMAGE_DIR = OUTPUT_DIR / "images"  # JPG images
WORKING_DATA = OUTPUT_DIR / "working_data.xlsx"  # Review file with all columns
MODEL = "gemini-2.0-flash"  # Google Gemini model for sentence generation

# Create directories if they don't exist
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
IMAGE_DIR.mkdir(parents=True, exist_ok=True)


def ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure the Status column exists in the tracking spreadsheet.
    This column is used to track which words have been processed.
    
    Status values:
    - "" (empty) = not started
    - "sentences_done" = sentences generated, ready for audio
    - "audio_done" = audio downloaded, ready for images
    - "images_done" = images downloaded, ready for TSV export
    - "complete" = fully processed
    """
    if "Status" not in df.columns:
        df["Status"] = ""
    df["Status"] = df["Status"].fillna("")
    return df


def safe_word(word: str) -> str:
    """
    Clean up word for use in filenames.
    Removes special characters that aren't allowed in file names.
    Example: "ب/ج" → "ب-ج"
    """
    return word.replace("/", "-").replace("\\", "-").strip()


def generate_sentences(word: str) -> list[dict] | None:
    """
    Use Google Gemini API to generate 5 natural Arabic sentences for a word.
    
    Each sentence includes:
    - Arabic: The Arabic sentence (with progressive harakat/vowels)
    - English: Natural English translation
    - IPA: International Phonetic Alphabet pronunciation
    
    Returns: List of 5 sentence dicts, or None if failed
    """
    # Crafted prompt to get natural sentences in JSON format
    prompt = f"""You are the best Arabic teacher.\nWord: {word}\nCreate exactly 5 natural sentences using only top 800 words.\n- Progressive difficulty\n- Sentence 1: clean unvoweled Arabic\n- Sentences 2-5: add harakat as difficulty increases\n- Natural collocations\n- < 12 words each\nRespond ONLY with valid JSON in this format, with no extra text, no explanation, no markdown:\n[{{\"arabic\": \"الجملة\", \"english\": \"Natural English\", \"ipa\": \"/strict.IPA/\"}}]\n"""
    try:
        print("Calling Google Gemini for sentences...")
        model = genai.GenerativeModel(MODEL)
        response = model.generate_content(prompt)
        content = response.text.strip() if response.text else ""
        print("Gemini raw response:\n", content)
        
        if not content:
            print("Error: Gemini returned empty response.")
            return None
        
        # Remove markdown code block markers (sometimes Gemini wraps JSON in ```json```)
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        # Parse the JSON response
        try:
            data = json.loads(content)
        except Exception as exc:
            print(f"Error parsing Gemini response as JSON: {exc}")
            return None
        
        # Validate we got exactly 5 sentences in a list
        if not isinstance(data, list) or len(data) != 5:
            print("Error: Did not receive 5 sentences in JSON list.")
            return None
        
        # Normalize the sentence data
        normalized = []
        for item in data:
            arabic = str(item.get("arabic", word)).strip()
            english = str(item.get("english", f"Example: {word}")).strip()
            ipa = str(item.get("ipa", "")).strip()
            normalized.append({"arabic": arabic, "english": english, "ipa": ipa})
        
        return normalized
    except Exception as exc:
        print(f"Error generating sentences: {exc}")
        return None


def append_to_working_data(word: str, word_meaning: str, freq_num: int, sentences: list[dict]) -> bool:
    """
    Append 5 sentence rows to working_data.xlsx for review before further processing.
    
    Each row represents one sentence for the word and includes:
    - File Name: Pattern {freq:04d}_{word}_{sentence:02d} for tracking
    - What is the Word?: The Arabic word
    - Meaning of the Word: English translation
    - Arabic Sentence: Full Arabic sentence
    - IPA Transliteration: Pronunciation guide
    - English Sentence: English translation
    - Sound: (empty, filled by script 2)
    - Image: (empty, filled by script 3)
    
    Returns False if rows already exist (prevents duplicates), True if appended successfully
    """
    # Define correct column order to match Anki import expectations
    CORRECT_COLUMNS = [
        "File Name",
        "What is the Word?",
        "Meaning of the Word",
        "Arabic Sentence",
        "IPA Transliteration",
        "English Sentence",
        "Sound",
        "Image"
    ]
    
    # Check if rows already exist for this word (prevents duplicate processing)
    if WORKING_DATA.exists():
        existing = pd.read_excel(WORKING_DATA)
        pattern = f"{freq_num:04d}_{word}_"
        if existing["File Name"].str.startswith(pattern, na=False).any():
            print(f"Rows for '{word}' already exist in {WORKING_DATA.name}. Skipping.")
            return False
        # Reorder existing columns if needed (for consistency)
        if list(existing.columns) != CORRECT_COLUMNS:
            existing = existing[CORRECT_COLUMNS]
    else:
        existing = pd.DataFrame()
    
    # Create 5 rows (one per sentence) for this word
    rows = []
    for j, sent in enumerate(sentences, start=1):
        file_name = f"{freq_num:04d}_{word}_{j:02d}"
        rows.append({
            "File Name": file_name,
            "What is the Word?": word,
            "Meaning of the Word": word_meaning,
            "Arabic Sentence": sent["arabic"],
            "IPA Transliteration": sent["ipa"],
            "English Sentence": sent["english"],
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
    combined.to_excel(WORKING_DATA, index=False)
    print(f"Appended 5 rows to {WORKING_DATA.name}")
    return True


def main() -> None:
    """
    Main workflow:
    1. Load API key from .env
    2. Read Arabic Frequency Word List.xlsx
    3. Find first word with empty Status (not yet processed)
    4. Generate 5 sentences for that word
    5. Append rows to working_data.xlsx
    6. Update Status to "sentences_done"
    """
    # Get Google API key from environment
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY is not set in .env file. Export it and retry.")
        sys.exit(1)
    genai.configure(api_key=api_key)

    # Load the frequency word list
    if not EXCEL_FILE.exists():
        print(f"Error: Excel file not found at {EXCEL_FILE}")
        sys.exit(1)

    df = ensure_columns(pd.read_excel(EXCEL_FILE))
    
    # Find first word that needs sentences (Status is empty)
    todo = df[df["Status"] == ""]
    if todo.empty:
        print("No rows need sentences. Status column has no empty entries.")
        return

    # Get the first word to process
    idx = todo.index[0]
    word_raw = df.loc[idx, "Arabic Word"]
    word = safe_word(str(word_raw))
    word_meaning = str(df.loc[idx, "English Meaning"]) if "English Meaning" in df.columns else ""
    freq_num = idx + 1  # Position in frequency list (1-indexed)
    
    print(f"Starting sentence generation for word '{word}' (freq #{freq_num})")

    # Generate 5 sentences using Gemini
    sentences = generate_sentences(word)
    if not sentences or len(sentences) != 5:
        print("Critical: Failed to generate sentences. Status not updated.")
        return

    # Save to working_data.xlsx (also checks for duplicates)
    if not append_to_working_data(word, word_meaning, freq_num, sentences):
        print("Rows already exist. Updating status only.")
    
    # Mark this word as "sentences_done" so script 2 can process it
    df.at[idx, "Status"] = "sentences_done"
    df.to_excel(EXCEL_FILE, index=False)
    print(f"Updated Status=sentences_done for '{word}' in {EXCEL_FILE.name}")


if __name__ == "__main__":
    main()

