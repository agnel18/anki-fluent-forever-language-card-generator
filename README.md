# Arabic Anki Card Generator

Generate professional Arabic language learning cards for Anki with sentences, audio, images, and IPA transliterations using Google Gemini API.

**Based on the [Fluent Forever method](https://fluent-forever.com/) by Gabriel Wyner** - A proven language learning system using spaced repetition, personalized sentences, and multi-sensory memory techniques.

📖 **Book:** [Fluent Forever: How to Learn Any Language Fast and Never Forget It](https://www.amazon.com/Fluent-Forever-Learn-Language-Forget/dp/0385348118) by Gabriel Wyner

## Features

- 🤖 **AI-Powered Sentences**: Uses Google Gemini API to generate natural Arabic sentences
- 🔊 **Audio**: Downloads native speaker Arabic audio from soundoftext.com
- 🖼️ **Images**: Downloads relevant clean images from Google Images (Unsplash fallback)
- 📝 **IPA Transliteration**: Includes International Phonetic Alphabet for pronunciation
- 📊 **Progress Tracking**: Tracks processing status for each word
- 🔄 **Restartable**: Each script is independent and can be restarted without losing work
- 🌍 **Multi-Language Support**: Easily adaptable to any language (Spanish, French, Japanese, etc.)

## Why Use This Script?

### The Fluent Forever Method: Smart, Not Hard

The **Fluent Forever method** by Gabriel Wyner is proven to accelerate language acquisition through:
- **Spaced Repetition**: Review cards at optimal intervals for long-term retention
- **Personalized Sentences**: Learn words in context, not isolation
- **Multi-Sensory Learning**: Combine text, audio, and images for stronger memory
- **Frequency-Based Learning**: Start with the most common words (80/20 rule)

### Why Automate Card Creation?

**Without this script:**
- ⏰ Creating 1 card manually: 5-10 minutes (find sentence, record/download audio, find image, format)
- 📚 625 Fluent Forever words × 5 sentences = **3,125 cards**
- ⏳ Total manual time: **260-520 hours** of tedious copy-paste work
- 😫 Burnout risk: High — most learners quit before finishing

**With this script:**
- ⚡ Creating 1 card automatically: **45 seconds** (fully automated)
- 📚 3,125 cards = **~39 hours** of mostly unattended runtime
- 🎯 Your time investment: **2-3 hours** (setup + review + import)
- ✅ More time for what matters: **immersion, speaking practice, and actual learning**

### Focus on Real Learning

By automating card creation, you can spend your time on activities that truly matter:

1. **🎧 Immersion**: Watch TV shows, YouTube videos, and movies in your target language
2. **🎙️ Podcasts**: Listen to native speakers while commuting or exercising
3. **📖 Reading**: Consume books, articles, and social media in the target language
4. **💬 Speaking Practice**: Use iTalki, HelloTalk, or language exchange partners
5. **📝 Grammar Study**: Focus on understanding structure, not creating flashcards
6. **🎯 Anki Reviews**: Spend your study time reviewing cards, not making them

**Research shows**: Active immersion and output practice accelerate fluency far more than card creation. This script handles the busywork so you can focus on real language exposure.

## Adapting to Other Languages

This script is designed for Arabic but can be easily adapted to **any language** in just a few minutes:

### Quick Start for Other Languages

1. **Update Script 1** (`1_generate_sentences.py`):
   ```python
   # Line ~65: Change the language name and IPA requirement
   prompt = f"""
   You are a {YOUR_LANGUAGE} language expert. Generate 5 example sentences using the word "{word}" ({meaning}).
   Each sentence must:
   - Use the word naturally in {YOUR_LANGUAGE} context
   - Be 5-12 words long
   - Include IPA transliteration for {YOUR_LANGUAGE} pronunciation
   - Have an accurate English translation
   """
   ```

2. **Update Script 2** (`2_download_audio.py`):
   - **Option A**: Keep soundoftext.com (supports 50+ languages)
     ```python
     # Line ~35: Change voice selection
     voice_dropdown = driver.find_element(By.ID, "voice")
     voice_dropdown.send_keys("{LANGUAGE_CODE}")  # e.g., "Spanish", "French", "Japanese"
     ```
   - **Option B**: Use Google TTS or Azure TTS for better quality (requires code changes)

3. **Update Script 3** (`3_download_images.py`):
   - No changes needed! Image search works for any language
   - Optionally adjust search keywords for better results:
     ```python
     # Line ~80: Add language-specific context
     search_query = f"{english_sentence} pure image {YOUR_LANGUAGE} culture"
     ```

4. **Update Excel File**:
   - Rename `Arabic Frequency Word List.xlsx` → `{Language} Frequency Word List.xlsx`
   - Add your target language's most common words (find frequency lists online)
   - Keep same columns: `Arabic Word` → `{Language} Word`, `English Meaning`, `Status`

5. **Update Output Folder**:
   ```python
   # In all scripts: Change folder name
   OUTPUT_DIR = "FluentForever_{YOUR_LANGUAGE}_Perfect"
   ```

### Language-Specific Considerations

**For Non-Latin Scripts** (Arabic, Japanese, Chinese, Russian, etc.):
- ✅ Script already handles Unicode correctly
- ✅ IPA transliteration automatically generated by Gemini
- ⚠️ Verify soundoftext.com supports your language's TTS

**For Tonal Languages** (Chinese, Vietnamese, Thai):
- ✅ IPA includes tone markers
- ⚠️ Verify audio quality (may need native speaker recordings)

**For Languages with Dialects** (Spanish, Arabic, Chinese):
- 🔧 Specify dialect in prompt: "Mexican Spanish", "Egyptian Arabic", "Mandarin Chinese"
- 🔧 Choose appropriate TTS voice in Script 2

### Example: Adapting to Spanish

1. Update prompt in Script 1:
   ```python
   prompt = f"You are a Spanish language expert. Generate 5 example sentences using '{word}' ({meaning})..."
   ```
2. Update voice in Script 2: `voice_dropdown.send_keys("Spanish")`
3. Rename Excel: `Spanish Frequency Word List.xlsx`
4. Add Spanish frequency words (e.g., "el", "de", "que", "y", "a"...)
5. Update output folder: `FluentForever_Spanish_Perfect`

**Total adaptation time: 10-15 minutes** ⚡

### Resources for Frequency Lists

- **Free**: Wiktionary frequency lists (most languages)
- **Book**: "Fluent Forever" by Gabriel Wyner (includes 625-word lists for major languages)
- **Paid**: Routledge Frequency Dictionaries (academic-quality lists)
- **Online**: Use Corpus databases (e.g., OPUS for parallel corpora)

## System Requirements

- Python 3.10+
- Google Chrome browser (for Selenium automation)
- Internet connection
- Google Gemini API key (free tier)

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/agnel18/anki-fluent-forever-language-card-generator.git
cd anki-fluent-forever-language-card-generator
```

> 💡 **Note:** This repo includes sample files (6 completed Arabic words) for demonstration. See step 6 below for how to start fresh.

### 2. Create Python Virtual Environment
```bash
python -m venv .venv
.\.venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install google-generativeai pandas selenium webdriver-manager openpyxl python-dotenv requests
```

### 4. Set Up Google Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikeys)
2. Click "Create API Key"
3. Create a `.env` file in the workspace root with:
```
GOOGLE_API_KEY=your_api_key_here
```

### 5. Set Up Anki Template (Beginner-Friendly)

**Option A: Use Pre-Made Template** (Recommended for beginners)

1. Open Anki
2. Click **File** → **Import**
3. Navigate to `LanguagLearning/Anki Arabic Template/`
4. Select `Arabic Template.apkg`
5. Click **Open**
6. ✅ Done! You now have the **Arabic** deck with the correct note type

**Option B: Create From Scratch** (Advanced users)

See [ANKI_SETUP.md](ANKI_SETUP.md) for detailed manual setup instructions.

### 6. Prepare Input Excel File

> ⚠️ **Important:** This repository includes **sample output files** (6 completed Arabic words) for demonstration purposes. If you want to start fresh or adapt to another language:
> 
> **Delete these files before running:**
> - `Arabic Frequency Word List.xlsx` (or rename and create your own)
> - `FluentForever_Arabic_Perfect/working_data.xlsx`
> - `FluentForever_Arabic_Perfect/ANKI_IMPORT.tsv`
> - `FluentForever_Arabic_Perfect/audio/*.mp3`
> - `FluentForever_Arabic_Perfect/images/*.jpg`
>
> Then create a fresh Excel file as described below.

Create `Arabic Frequency Word List.xlsx` in `LanguagLearning/` folder with columns:
- **Arabic Word**: The Arabic word (e.g., ال, و, في)
- **English Meaning**: English translation (e.g., the, and, in)
- **Status**: Leave empty (will be auto-populated)

Example:
| Arabic Word | English Meaning | Status |
|-------------|-----------------|--------|
| ال          | the             |        |
| و           | and             |        |
| في         | in              |        |

## Workflow

The system uses a 4-script pipeline:

### Script 1: Generate Sentences (`1_generate_sentences.py`)
Generates 5 natural Arabic sentences for each word using Gemini API.
- Reads next word with empty Status
- Generates 5 sentences with English translation and IPA
- Saves to `working_data.xlsx` for review
- Updates Status → `sentences_done`

**Run:**
```bash
python LanguagLearning/1_generate_sentences.py
```

### Script 2: Download Audio (`2_download_audio.py`)
Downloads native speaker audio from soundoftext.com.
- Finds words with Status=`sentences_done`
- Downloads MP3 for each sentence using Selenium
- Saves to `FluentForever_Arabic_Perfect/audio/`
- Updates Sound column with `[sound:filename.mp3]`
- Updates Status → `audio_done`

**Run:**
```bash
python LanguagLearning/2_download_audio.py
```

### Script 3: Download Images (`3_download_images.py`)
Downloads clean, text-free images from Google Images (Unsplash fallback).
- Finds words with Status=`audio_done`
- Searches Google Images with "pure image" filter for clean photos
- Tries multiple results to find best image
- Saves to `FluentForever_Arabic_Perfect/images/`
- Updates Image column with `<img src="filename.jpg">`
- Updates Status → `images_done`

**Run:**
```bash
python LanguagLearning/3_download_images.py
```

### Script 4: Create Anki TSV (`4_create_anki_tsv.py`)
Exports completed cards to TSV format for Anki import.
- Finds all rows with both Sound and Image populated
- Exports to `ANKI_IMPORT.tsv` (tab-separated values)
- Updates all processed words → Status `complete`
- Ready to import into Anki

**Run:**
```bash
python LanguagLearning/4_create_anki_tsv.py
```

## Data Flow

```
Arabic Frequency Word List.xlsx
           ↓
    Script 1: Sentences
           ↓
    working_data.xlsx (review here!)
           ↓
    Script 2: Audio
           ↓
    FluentForever_Arabic_Perfect/audio/
           ↓
    Script 3: Images
           ↓
    FluentForever_Arabic_Perfect/images/
           ↓
    Script 4: TSV Export
           ↓
    ANKI_IMPORT.tsv
           ↓
    Import into Anki!
```

## Folder Structure

```
LanguagLearning/
├── 1_generate_sentences.py
├── 2_download_audio.py
├── 3_download_images.py
├── 4_create_anki_tsv.py
├── README.md
├── ANKI_SETUP.md
├── .env (keep this secret!)
├── Arabic Frequency Word List.xlsx
├── Anki Arabic Template/
│   └── Arabic Template.apkg       ⭐ PRE-MADE TEMPLATE (INCLUDED!)
└── FluentForever_Arabic_Perfect/
    ├── working_data.xlsx
    ├── ANKI_IMPORT.tsv
    ├── audio/
    │   ├── 0001_ال_01.mp3
    │   ├── 0001_ال_02.mp3
    │   └── ...
    └── images/
        ├── 0001_ال_01.jpg
        ├── 0001_ال_02.jpg
        └── ...
```

## Anki Setup (For Complete Beginners)

### Step 1: Install Anki (if you haven't already)

1. Go to [https://apps.ankiweb.net/](https://apps.ankiweb.net/)
2. Download Anki for your operating system:
   - **Windows**: Click "Download" for Windows
   - **Mac**: Click "Download" for Mac
   - **Linux**: Click "Download" for Linux
3. Run the installer and follow the prompts
4. Open Anki
5. (Optional) Create a free AnkiWeb account to sync cards across devices

### Step 2: Import the Pre-Made Template (Easiest Method!)

This repository includes a ready-to-use Anki template file. **No manual setup required!**

1. In Anki, click **File** → **Import**
2. Navigate to this project folder: `LanguagLearning/Anki Arabic Template/`
3. Select **Arabic Template.apkg**
4. Click **Open** (or **Import**)
5. ✅ Done! You now have an **Arabic** deck with pre-configured fields and card styling

**What's included in the template:**
- ✅ **Arabic** deck (ready to use)
- ✅ **Arabic Card** note type with 8 fields (File Name, Word, Meaning, Sentence, IPA, Translation, Sound, Image)
- ✅ Front/back card templates optimized for language learning
- ✅ Proper styling for Arabic text (right-to-left display)

### Step 3: Import Your Generated Cards

After running scripts 1-4, you'll have `ANKI_IMPORT.tsv` ready to import. See the **Usage Example** section below for import instructions.

---

**Advanced Users:** Want to customize the template or create your own from scratch? See [ANKI_SETUP.md](ANKI_SETUP.md) for detailed manual setup instructions

3. **Import TSV**:
   - File → **Import**
   - Select `ANKI_IMPORT.tsv`
   - Choose note type: **Arabic Card**
   - Select deck: **Arabic**
   - Click **Import**

### Import Media Files

After importing TSV, you need to add the audio and image files:

1. In Anki, click **Tools** → **Check Media**
2. Click **View Files** to open the media folder
3. In your file explorer, navigate to `FluentForever_Arabic_Perfect/audio/`
4. Select all MP3 files (Ctrl+A)
5. Copy them (Ctrl+C)
6. Go back to Anki's media folder
7. Paste (Ctrl+V)
8. Repeat for images from `FluentForever_Arabic_Perfect/images/`

⚠️ **Important**: Copy the individual files, NOT the folders!

## Usage Example

```bash
# Activate virtual environment
.\.venv\Scripts\activate

# Generate sentences for word 1
python LanguagLearning/1_generate_sentences.py
# Output: sentences_done status, 5 rows in working_data.xlsx

# Generate sentences for words 2-10 (repeat script 10 times, or create a loop)
python LanguagLearning/1_generate_sentences.py
python LanguagLearning/1_generate_sentences.py
# ... etc

# After all words have sentences, download audio for all
python LanguagLearning/2_download_audio.py
python LanguagLearning/2_download_audio.py
# ... repeat until audio_done for all words

# Then download images for all
python LanguagLearning/3_download_images.py
python LanguagLearning/3_download_images.py
# ... repeat until images_done for all words

# Finally, generate Anki TSV
python LanguagLearning/4_create_anki_tsv.py

# Import ANKI_IMPORT.tsv into Anki following instructions above
```

## Troubleshooting

### "No rows with Status=sentences_done"
- Run script 1 first to generate sentences
- Check `Arabic Frequency Word List.xlsx` has empty Status column

### Audio download fails
- Ensure Chrome browser is installed and up to date
- Check internet connection
- soundoftext.com may be temporarily down, try again later

### Image download fails
- "pure image" filter might not return results for some search terms
- Script automatically tries Google Images fallback
- Check internet connection
- Manual image download recommended if automatic fails

### Permission denied on Excel
- Close Excel files before running scripts
- Files are locked while open in Excel

### Media files don't show in Anki
- Ensure file paths in TSV match actual filenames
- Copy individual files to collection.media folder (not folders)
- Run **Tools** → **Check Media** again

## Output Fields

Each Anki card contains:

| Field | Example | Format |
|-------|---------|--------|
| File Name | 0001_ال_01 | {freq:04d}_{word}_{sentence:02d} |
| What is the Word? | ال | Arabic word |
| Meaning of the Word | the | English translation |
| Arabic Sentence | البيت كبير. | Full Arabic sentence |
| IPA Transliteration | /al-baytu kabir/ | IPA pronunciation |
| English Sentence | The house is big. | English translation |
| Sound | [sound:0001_ال_01.mp3] | Anki sound tag |
| Image | <img src="0001_ال_01.jpg"> | Anki image tag |

## API Costs

- **Google Gemini API**: Free tier available (up to 15 requests/minute)
- **Audio (soundoftext.com)**: Free
- **Images (Google Images/Unsplash)**: Free

## Tips & Best Practices

### Script Usage

1. **Review working_data.xlsx** before running script 2
   - Check if sentences are appropriate
   - Delete any rows you don't want
   - Status won't update until all 5 are present

2. **Run scripts in order** (1→2→3→4)
   - Each script depends on previous status

3. **Test on small batch first**
   - Try 2-3 words before full workflow

4. **Close Excel files** before running scripts
   - Prevents file lock errors

5. **Check media folder** before importing into Anki
   - Ensure audio/images are present and named correctly

### Learning Strategy

6. **Let the script run in the background**
   - Scripts 2 & 3 can run unattended
   - Use this time for immersion: watch Netflix, listen to podcasts
   - Check progress every 30 minutes

7. **Batch process efficiently**
   - Generate sentences for 50 words (Script 1: ~5 minutes)
   - Run Script 2 for all 50 words (unattended, ~12 minutes)
   - Run Script 3 for all 50 words (unattended, ~17 minutes)
   - Import to Anki and START LEARNING

8. **Prioritize review over creation**
   - 30 minutes of Anki reviews > 30 minutes of card creation
   - This script automates creation so you can focus on actual learning

9. **Use Anki mobile app**
   - Review cards during commute, waiting in line, etc.
   - Audio works on mobile (great for pronunciation practice)

10. **Combine with immersion**
    - After learning 100 words: start watching kids' shows
    - After 300 words: try podcasts for learners
    - After 625 words: dive into native content (news, TV, books)

## Performance

- Script 1 (Sentences): ~5 seconds per word
- Script 2 (Audio): ~15 seconds per word (5 files)
- Script 3 (Images): ~20 seconds per word (5 files)
- Script 4 (TSV): ~2 seconds total

Total time for 1 word: ~45 seconds

## Credits

This project is inspired by and based on the **Fluent Forever method** created by **Gabriel Wyner**.

- 📖 **Book:** [Fluent Forever: How to Learn Any Language Fast and Never Forget It](https://www.amazon.com/Fluent-Forever-Learn-Language-Forget/dp/0385348118)
- 🌐 **Website:** [fluent-forever.com](https://fluent-forever.com/)
- 👤 **Author:** Gabriel Wyner

This tool automates the card creation process described in the Fluent Forever book, making the method accessible to everyone for free.

## License

MIT License - Feel free to use and modify for personal use

**Note:** This is an independent open-source project and is not officially affiliated with Fluent Forever or Gabriel Wyner. Please support the original work by purchasing the book.

## Contributing

Improvements welcome! Feel free to:
- **Share your language adaptations** (Spanish, French, Japanese, etc.)
- Create language-specific prompt templates for better sentence quality
- Add alternative TTS providers (Google TTS, Azure, ElevenLabs)
- Optimize Selenium automation for faster processing
- Improve image quality selection algorithms
- Build a GUI for non-technical users
- Create pre-made .apkg template files for different languages

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review script comments for debugging
3. Check that all dependencies are installed
4. Verify API key is set correctly in .env

---

**Happy Learning! 🚀**
