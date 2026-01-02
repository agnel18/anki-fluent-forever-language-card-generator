# Deck export module
# Extracted from core_functions.py for better separation of concerns

import os
import tempfile
import shutil
import logging
import pandas as pd
import random
import re
from pathlib import Path
from typing import List, Dict, Any

# Import genanki for APKG creation
try:
    import genanki
except ImportError:
    genanki = None

logger = logging.getLogger(__name__)

# ============================================================================
# TSV & ZIP EXPORT
# ============================================================================
def create_anki_tsv(
    rows: list[dict],
    output_path: str,
) -> bool:
    """Create Anki TSV with headers for proper field mapping."""
    try:
        columns = [
            "File Name",
            "What is the Word?",
            "Meaning of the Word",
            "Sentence",
            "IPA Transliteration",
            "English Translation",
            "Sound",
            "Image",
            "Image Keywords",
            "Colored Sentence",
            "Word Explanations",
            "Grammar Summary",
            "Tags",
        ]

        formatted_rows = []
        for r in rows:
            # Convert word explanations list to JSON string for TSV
            word_explanations_json = ""
            if r.get("word_explanations"):
                try:
                    import json
                    word_explanations_json = json.dumps(r["word_explanations"], ensure_ascii=False)
                except Exception:
                    word_explanations_json = str(r.get("word_explanations", ""))

            formatted_rows.append({
                "File Name": r.get("file_name", ""),
                "What is the Word?": r.get("word", ""),
                "Meaning of the Word": r.get("meaning", ""),
                "Sentence": r.get("sentence", ""),
                "IPA Transliteration": r.get("ipa", ""),
                "English Translation": r.get("english", ""),
                "Sound": r.get("audio", ""),
                "Image": r.get("image", ""),
                "Image Keywords": r.get("image_keywords", ""),
                "Colored Sentence": r.get("colored_sentence", ""),
                "Word Explanations": word_explanations_json,
                "Grammar Summary": r.get("grammar_summary", ""),
                "Tags": r.get("tags", ""),
            })

        df = pd.DataFrame(formatted_rows)
        df.to_csv(output_path, sep="\t", index=False, header=False, encoding="utf-8", quoting=0)  # QUOTE_MINIMAL
        return True

    except Exception as e:
        logger.error(f"TSV creation error: {e}")
        return False

def create_zip_export(
    tsv_path: str,
    media_dir: str,
    output_zip: str,
) -> bool:
    """
    Create ZIP file with TSV + media folder.

    Args:
        tsv_path: Path to ANKI_IMPORT.tsv
        media_dir: Path to media folder (contains audio + images)
        output_zip: Path to save ZIP file

    Returns:
        True if successful
    """
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create structure
            deck_dir = Path(tmpdir) / "AnkiDeck"
            deck_dir.mkdir()

            # Copy files
            shutil.copy(tsv_path, deck_dir / "ANKI_IMPORT.tsv")

            if os.path.exists(media_dir):
                shutil.copytree(media_dir, deck_dir / "media")

            # Create instructions file
            instructions = r"""HOW TO IMPORT TO ANKI
=====================================
1. Extract this ZIP to a folder
2. Open Anki > File > Import
3. Select ANKI_IMPORT.tsv
4. Choose the note type and deck
5. Copy all files from the media/ folder to Anki collection.media folder
6. Start learning!

Finding Anki Media Folder:
  Easy way: In Anki, go to Main Menu > Tools > Check Media > View Files

  Manual locations:
  Windows: C:\Users\<YourUsername>\AppData\Roaming\Anki2\User 1\collection.media
  Mac: ~/Library/Application Support/Anki2/User 1/collection.media
  Linux: ~/.local/share/Anki2/User 1/collection.media
"""
            with open(deck_dir / "IMPORT_INSTRUCTIONS.txt", "w", encoding="utf-8") as f:
                f.write(instructions)

            # Create ZIP
            shutil.make_archive(output_zip.replace(".zip", ""), "zip", tmpdir, "AnkiDeck")
            return True

    except Exception as e:
        logger.error(f"ZIP creation error: {e}")
        return False

def read_tsv_rows(tsv_path: str) -> List[Dict[str, Any]]:
    """
    Read TSV file and convert to rows format expected by create_apkg_export.

    Args:
        tsv_path: Path to the TSV file

    Returns:
        List of dicts with keys: file_name, word, meaning, sentence, ipa, english, audio, image, image_keywords, tags
    """
    try:
        df = pd.read_csv(tsv_path, sep='\t', header=None,
                        names=['file_name', 'word', 'meaning', 'sentence', 'ipa', 'english', 'audio', 'image', 'image_keywords', 'tags'],
                        encoding='utf-8')

        rows = []
        for _, row in df.iterrows():
            rows.append({
                'file_name': str(row.get('file_name', '')),
                'word': str(row.get('word', '')),
                'meaning': str(row.get('meaning', '')),
                'sentence': str(row.get('sentence', '')),
                'ipa': str(row.get('ipa', '')),
                'english': str(row.get('english', '')),
                'audio': str(row.get('audio', '')),
                'image': str(row.get('image', '')),
                'image_keywords': str(row.get('image_keywords', '')),
                'tags': str(row.get('tags', ''))
            })

        return rows

    except Exception as e:
        logger.error(f"Error reading TSV file {tsv_path}: {e}")
        return []

def create_apkg_export(
    rows: List[Dict[str, Any]],
    media_dir: str,
    output_path: str,
    language: str = "English",
    deck_name: str = None
) -> bool:
    """
    Create .apkg file (Anki deck package) from card data.

    Args:
        rows: List of card data dicts
        media_dir: Path to media folder (contains audio + images)
        output_path: Path to save .apkg file
        language: Target language name
        deck_name: Name of the Anki deck

    Returns:
        True if successful, False otherwise
    """
    try:
        # Set default deck name to language if not provided
        if deck_name is None:
            deck_name = language
        return _create_apkg_from_rows(rows, media_dir, output_path, language, deck_name)
    except Exception as e:
        logger.error(f"Error creating APKG export: {e}")
        return False

def _create_apkg_from_rows(
    rows: List[Dict[str, Any]],
    media_dir: str,
    output_apkg: str,
    language: str,
    deck_name: str = None,
) -> bool:
    """
    Create .apkg file (Anki deck package) with 3-card template.

    Args:
        rows: List of card data dicts
        media_dir: Path to media folder (contains audio + images)
        output_apkg: Path to save .apkg file
        language: Target language name (e.g., "Spanish")
        deck_name: Name of the Anki deck

    Returns:
        True if successful, False otherwise
    """
    if genanki is None:
        logger.error("genanki library not available. Cannot create APKG file.")
        return False

    logger.info(f"Preparing to create .apkg at: {output_apkg}")
    output_path = Path(output_apkg)
    if not output_path.parent.exists():
        logger.warning(f"Output parent directory does not exist. Attempting to create: {output_path.parent}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
    if not output_path.parent.exists():
        logger.error(f"Failed to create output parent directory: {output_path.parent}")
        return False

    # Set default deck name to language if not provided
    if deck_name is None:
        deck_name = language

    # Create note model with 12 fields and 3 card templates
    model_id = random.randrange(1 << 30, 1 << 31)
    model = genanki.Model(
        model_id,
        'Fluent Forever Language Learning',
        fields=[
            {'name': 'File Name'},
            {'name': 'What is the Word?'},
            {'name': 'Meaning of the Word'},
            {'name': 'Sentence'},
            {'name': 'IPA Transliteration'},
            {'name': 'English Translation'},
            {'name': 'Sound'},
            {'name': 'Image'},
            {'name': 'Image Keywords'},
            {'name': 'Colored Sentence'},
            {'name': 'Word Explanations'},
            {'name': 'Grammar Summary'},
            {'name': 'Tags'}
        ],
        templates=[
            {
                'name': 'Card 1: Listening',
                'qfmt': '''<div class="hint">🎧 Listen and understand</div>\n<div class="sound">{{Sound}}</div>''',
                'afmt': '''{{FrontSide}}\n<hr id="answer">\n<div class="colored-sentence">{{Colored Sentence}}</div>\n<div class="image">{{Image}}</div>\n<div class="english">{{English Translation}}</div>\n<div class="word-info"><strong>Word:</strong> {{What is the Word?}} ({{Meaning of the Word}})</div>\n<div class="ipa">{{IPA Transliteration}}</div>\n<div class="grammar-summary">{{Grammar Summary}}</div>\n{{Word Explanations}}\n<div class="keywords">Keywords: {{Image Keywords}}</div>'''
            },
            {
                'name': 'Card 2: Production',
                'qfmt': '''<div class="hint">💬 Say this in ''' + language + ''':</div>\n<div class="english-prompt">{{English Translation}}</div>''',
                'afmt': '''{{FrontSide}}\n<hr id="answer">\n<div class="colored-sentence">{{Colored Sentence}}</div>\n<div class="sound">{{Sound}}</div>\n<div class="image">{{Image}}</div>\n<div class="ipa">{{IPA Transliteration}}</div>\n<div class="word-info"><strong>Word:</strong> {{What is the Word?}} ({{Meaning of the Word}})</div>\n<div class="grammar-summary">{{Grammar Summary}}</div>\n{{Word Explanations}}\n<div class="keywords">Keywords: {{Image Keywords}}</div>'''
            },
            {
                'name': 'Card 3: Reading',
                'qfmt': '''<div class="hint">📖 Read and understand:</div>\n<div class="colored-sentence">{{Colored Sentence}}</div>''',
                'afmt': '''{{FrontSide}}\n<hr id="answer">\n<div class="sound">{{Sound}}</div>\n<div class="image">{{Image}}</div>\n<div class="english">{{English Translation}}</div>\n<div class="ipa">{{IPA Transliteration}}</div>\n<div class="word-info"><strong>Word:</strong> {{What is the Word?}} ({{Meaning of the Word}})</div>\n<div class="grammar-summary">{{Grammar Summary}}</div>\n{{Word Explanations}}\n<div class="keywords">Keywords: {{Image Keywords}}</div>'''
            }
        ],
        css='''.card {\n    font-family: arial;\n    font-size: 20px;\n    text-align: center;\n    color: var(--text-color, black);\n    background-color: var(--card-bg, white);\n}\n\n.hint {\n    font-size: 16px;\n    color: var(--subtle-text, #666);\n    margin: 10px;\n    font-style: italic;\n}\n\n.sentence {\n    font-size: 32px;\n    color: var(--accent-color, #0066cc);\n    margin: 20px;\n    font-weight: bold;\n}\n\n.colored-sentence {\n    font-size: 32px;\n    margin: 20px;\n    font-weight: bold;\n    line-height: 1.4;\n}\n\n.colored-sentence span {\n    display: inline;\n    margin: 0 2px;\n}\n\n/* Grammar element color classes for Anki compatibility */\n.grammar-pronouns { color: #FF4444 !important; font-weight: bold; }\n.grammar-verbs { color: #44FF44 !important; font-weight: bold; }\n.grammar-postpositions { color: #4444FF !important; font-weight: bold; }\n.grammar-nouns { color: #FFAA00 !important; font-weight: bold; }\n.grammar-adjectives { color: #FF44FF !important; font-weight: bold; }\n.grammar-adverbs { color: #44FFFF !important; font-weight: bold; }\n.grammar-aspect_markers { color: #AAFF44 !important; font-weight: bold; }\n.grammar-case_markers { color: #FF8844 !important; font-weight: bold; }\n.grammar-honorifics { color: #AA44FF !important; font-weight: bold; }\n.grammar-causative_markers { color: #FFAA88 !important; font-weight: bold; }\n.grammar-discourse_particles { color: #88FFAA !important; font-weight: bold; }\n.grammar-compound_verbs { color: #FFFF44 !important; font-weight: bold; }\n.grammar-other { color: #888888 !important; font-weight: bold; }\n\n/* Additional grammar elements for other languages */\n.grammar-articles { color: #FF6B6B !important; font-weight: bold; }\n.grammar-prepositions { color: #4ECDC4 !important; font-weight: bold; }\n.grammar-conjunctions { color: #45B7D1 !important; font-weight: bold; }\n.grammar-interjections { color: #FFA07A !important; font-weight: bold; }\n.grammar-particles { color: #98D8C8 !important; font-weight: bold; }\n.grammar-auxiliaries { color: #F7DC6F !important; font-weight: bold; }\n.grammar-modals { color: #BB8FCE !important; font-weight: bold; }\n.grammar-determiners { color: #85C1E9 !important; font-weight: bold; }\n\n.english-prompt {\n    font-size: 28px;\n    color: var(--accent-secondary, #009900);\n    margin: 20px;\n    font-weight: bold;\n}\n\n.sound {\n    margin: 20px;\n}\n\n.english {\n    font-size: 22px;\n    color: var(--accent-secondary, #009900);\n    margin: 15px;\n}\n\n.ipa {\n    font-size: 16px;\n    color: var(--subtle-text, #666);\n    font-family: "Charis SIL", "Doulos SIL", serif;\n    margin: 10px;\n}\n\n.word-info {\n    font-size: 14px;\n    color: var(--text-color, #333);\n    margin: 15px;\n}\n\n.grammar-summary {\n    font-size: 16px;\n    color: var(--text-color, #555);\n    margin: 15px;\n    font-style: italic;\n    background-color: var(--card-bg-secondary, #f9f9f9);\n    padding: 10px;\n    border-radius: 5px;\n    border-left: 4px solid var(--accent-color, #0066cc);\n}\n\n.explanations-toggle {\n    font-size: 14px;\n    color: var(--accent-color, #0066cc);\n    margin: 10px;\n    cursor: pointer;\n    text-decoration: underline;\n    font-weight: bold;\n}\n\n.word-explanations {\n    font-size: 12px;\n    color: var(--text-color, #444);\n    margin: 10px;\n    background-color: var(--card-bg-secondary, #f5f5f5);\n    padding: 8px;\n    border-radius: 3px;\n    max-height: 150px;\n    overflow-y: auto;\n}\n\n.explanation-item {\n    margin: 5px 0;\n    padding: 3px 0;\n    border-bottom: 1px solid var(--subtle-text, #ddd);\n}\n\n.explanation-item:last-child {\n    border-bottom: none;\n}\n\n.word-highlight {\n    font-weight: bold;\n    text-decoration: underline;\n}\n\n.keywords {\n    font-size: 12px;\n    color: var(--subtle-text, #999);\n    margin: 10px;\n    font-style: italic;\n}\n\n.image {\n    margin: 20px auto;\n    display: flex;\n    justify-content: center;\n    align-items: center;\n    width: 100%;\n    max-width: 100vw;\n}\n\n.image img {\n    display: block;\n    margin: 0 auto;\n    max-width: 95vw;\n    max-height: 40vh;\n    width: auto;\n    height: auto;\n    object-fit: contain;\n    border-radius: 10px;\n    box-shadow: 0 2px 12px rgba(0,0,0,0.2);\n}\n\n.instructions {\n    font-size: 18px;\n    color: var(--text-color, #333);\n    margin: 15px;\n    line-height: 1.5;\n}\n\n.user-recording {\n    font-size: 16px;\n    color: var(--accent-color, #0066cc);\n    margin: 15px;\n}\n\n.tts-voice {\n    font-size: 16px;\n    color: var(--accent-secondary, #009900);\n    margin: 15px;\n}\n\n.comparison-instructions {\n    font-size: 14px;\n    color: var(--subtle-text, #666);\n    margin: 15px;\n    font-style: italic;\n}'''
    )

    # Create deck
    deck_id = random.randrange(1 << 30, 1 << 31)
    deck = genanki.Deck(deck_id, deck_name)

    # Collect media files
    media_files = []
    for row in rows:
        # Extract audio and image filenames
        audio_match = re.search(r'\[sound:(.*?)\]', row.get('audio', ''))
        audio_file = audio_match.group(1) if audio_match else ''

        # Handle image field - could be HTML <img src="file"> or just filename
        image_field = row.get('image', '').strip()
        if image_field.startswith('<img src="') and image_field.endswith('">'):
            # Extract from HTML
            image_match = re.search(r'src="(.*?)"', image_field)
            image_file = image_match.group(1) if image_match else ''
        else:
            # Assume it's just the filename
            image_file = image_field
        # Add media files to list
        if audio_file:
            audio_path = os.path.join(media_dir, audio_file)
            if os.path.exists(audio_path):
                media_files.append(audio_path)
                logger.debug(f"Added audio media file: {audio_path}")
            else:
                logger.warning(f"Missing audio file, skipping: {audio_path}")
        if image_file:
            image_path = os.path.join(media_dir, image_file)
            if os.path.exists(image_path):
                media_files.append(image_path)
                logger.debug(f"Added image media file: {image_path}")
            else:
                logger.warning(f"Missing image file, skipping: {image_path}")

    logger.info(f"Collected {len(media_files)} media files for .apkg package")

    # Create notes
    for row in rows:
        # Create note
        import math
        def _s(val):
            if val is None:
                return ""
            if isinstance(val, float):
                if math.isnan(val):
                    return ""
                return str(val)
            return str(val)
        note = genanki.Note(
            model=model,
            fields=[
                _s(row.get('file_name', '')),
                _s(row.get('word', '')),
                _s(row.get('meaning', '')),
                _s(row.get('sentence', '')),
                _s(row.get('ipa', '')),
                _s(row.get('english', '')),
                _s(row.get('audio', '')),
                _s(row.get('image', '')),
                _s(row.get('image_keywords', '')),
                _s(row.get('colored_sentence', '')),
                _s(row.get('word_explanations', '')),
                _s(row.get('grammar_summary', '')),
                _s(row.get('tags', ''))
            ]
        )
        deck.add_note(note)

    # Create package
    try:
        package = genanki.Package(deck)
        package.media_files = media_files
        logger.info(f"Set {len(media_files)} media files in package: {[os.path.basename(f) for f in media_files]}")
        package.write_to_file(str(output_path))
        logger.info(f"Created .apkg file with {len(rows)} notes at {output_apkg}")
        return True
    except FileNotFoundError as fnf_err:
        logger.error(f"FileNotFoundError during .apkg creation: {fnf_err}")
        logger.error(f"Current working directory: {os.getcwd()}")
        logger.error(f"Attempted output path: {output_path}")
        return False
    except Exception as e:
        logger.error(f"General error during .apkg creation: {e}")
        logger.error(f"Current working directory: {os.getcwd()}")
        logger.error(f"Attempted output path: {output_path}")
        return False