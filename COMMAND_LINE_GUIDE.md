# 🚀 Advanced Command Line Guide

**For power users who want direct control over Python scripts.**

This guide covers running individual scripts with custom parameters, batch processing, database management, and advanced workflows.

---

## 📋 Table of Contents

1. [Individual Script Parameters](#individual-script-parameters)
2. [Batch Processing](#batch-processing)
3. [Database Management](#database-management)
4. [Advanced Workflows](#advanced-workflows)
5. [Troubleshooting](#troubleshooting)

---

## Individual Script Parameters

### Script 1: Generate Sentences (`1_generate_sentences.py`)

**Purpose:** Generate AI-powered sentences using Groq API.

**Basic Usage:**
```bash
python 1_generate_sentences.py
```

**With Parameters:**
```bash
python 1_generate_sentences.py \
  --language Spanish \
  --words 10 \
  --batch-size 2 \
  --difficulty intermediate \
  --min-length 5 \
  --max-length 25
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--language` | string | `language_config.txt` | Target language (e.g., "Spanish", "French") |
| `--words` | int | 1 | Number of words to process |
| `--batch-size` | int | 1 | Batch size per API call (1-5 recommended) |
| `--difficulty` | string | "intermediate" | beginner / intermediate / advanced |
| `--min-length` | int | 5 | Minimum sentence length (words) |
| `--max-length` | int | 20 | Maximum sentence length (words) |
| `--output` | string | `working_data.xlsx` | Output file path |

**Examples:**

```bash
# Generate 5 sentences for 1 word (safest, recommended for first run)
python 1_generate_sentences.py --words 1

# Generate 10 sentences for advanced learner
python 1_generate_sentences.py --words 10 --difficulty advanced --min-length 10 --max-length 30

# Batch process 50 words at once (requires strong API quota)
python 1_generate_sentences.py --words 50 --batch-size 5

# Process entire 625-word list (loop)
for i in {1..625}; do python 1_generate_sentences.py; done
```

---

### Script 2: Download Audio (`2_download_audio.py`)

**Purpose:** Generate audio using Edge TTS (primary) + Google Cloud TTS (fallback).

**Basic Usage:**
```bash
python 2_download_audio.py
```

**With Parameters:**
```bash
python 2_download_audio.py \
  --language Spanish \
  --speed 0.9 \
  --voice-gender female \
  --fallback-only
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--language` | string | `language_config.txt` | Target language |
| `--speed` | float | 0.8 | Audio speed (0.5 = slow, 1.0 = normal, 1.5 = fast) |
| `--voice-gender` | string | "female" | female / male |
| `--fallback-only` | flag | False | Skip Edge TTS, use Google TTS only |
| `--output-dir` | string | `media/` | Output directory for MP3 files |
| `--max-retries` | int | 3 | Number of retry attempts |

**Examples:**

```bash
# Default (0.8x speed, female voice, Edge TTS primary)
python 2_download_audio.py

# Fast audio for advanced learner (1.2x speed)
python 2_download_audio.py --speed 1.2

# Male voice, slow speed for beginners
python 2_download_audio.py --voice-gender male --speed 0.5

# Use only Google Cloud TTS (slower but reliable)
python 2_download_audio.py --fallback-only

# Reprocess with new speed
python 2_download_audio.py --speed 1.0 --max-retries 5
```

---

### Script 3: Download Images (`3_download_images.py`)

**Purpose:** Download images from Pixabay API.

**Basic Usage:**
```bash
python 3_download_images.py
```

**With Parameters:**
```bash
python 3_download_images.py \
  --language Spanish \
  --per-word 10 \
  --randomize \
  --output-dir images/
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--language` | string | `language_config.txt` | Target language |
| `--per-word` | int | 10 | Images to download per word |
| `--randomize` | flag | True | Randomize top results |
| `--output-dir` | string | `images/` | Output directory for JPG files |
| `--max-retries` | int | 3 | Retry attempts on failure |
| `--batch-size` | int | 50 | Words to process per batch |

**Examples:**

```bash
# Download with default settings (10 images per word, randomized)
python 3_download_images.py

# Download fewer images per word (saves bandwidth)
python 3_download_images.py --per-word 5

# Batch process 100 words at once
python 3_download_images.py --batch-size 100

# Disable randomization (always same images)
python 3_download_images.py --randomize false

# Custom output directory
python 3_download_images.py --output-dir /custom/path/images/
```

---

### Script 4: Create Anki TSV (`4_create_anki_tsv.py`)

**Purpose:** Export cards to Anki-compatible TSV format.

**Basic Usage:**
```bash
python 4_create_anki_tsv.py
```

**With Parameters:**
```bash
python 4_create_anki_tsv.py \
  --input working_data.xlsx \
  --output ANKI_IMPORT.tsv \
  --language Spanish \
  --no-header
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--input` | string | `working_data.xlsx` | Input Excel file |
| `--output` | string | `ANKI_IMPORT.tsv` | Output TSV file |
| `--language` | string | Detected | Target language |
| `--no-header` | flag | False | Skip header row in TSV |
| `--sort-by` | string | "status" | Sort by: status / word / meaning / frequency |

**Examples:**

```bash
# Create standard TSV for Anki import
python 4_create_anki_tsv.py

# Export with custom filename
python 4_create_anki_tsv.py --output my_spanish_deck.tsv

# Sort by word frequency (most common first)
python 4_create_anki_tsv.py --sort-by frequency

# Skip header row
python 4_create_anki_tsv.py --no-header
```

---

## Batch Processing

### Process Multiple Languages in Parallel

**Bash Script (macOS/Linux):**

```bash
#!/bin/bash

LANGUAGES=("Spanish" "French" "German" "Italian" "Portuguese")

for lang in "${LANGUAGES[@]}"; do
  echo "🌍 Processing $lang..."
  
  # Sentences
  python 1_generate_sentences.py --language "$lang" --words 25
  
  # Audio
  python 2_download_audio.py --language "$lang"
  
  # Images
  python 3_download_images.py --language "$lang"
  
  # TSV
  python 4_create_anki_tsv.py --language "$lang"
  
  echo "✅ $lang complete!"
  echo ""
done

echo "🎉 All languages processed!"
```

**PowerShell Script (Windows):**

```powershell
$languages = @("Spanish", "French", "German", "Italian", "Portuguese")

foreach ($lang in $languages) {
    Write-Host "🌍 Processing $lang..."
    
    python 1_generate_sentences.py --language $lang --words 25
    python 2_download_audio.py --language $lang
    python 3_download_images.py --language $lang
    python 4_create_anki_tsv.py --language $lang
    
    Write-Host "✅ $lang complete!" -ForegroundColor Green
    Write-Host ""
}

Write-Host "🎉 All languages processed!" -ForegroundColor Cyan
```

### Process Words in Stages

**Stage 1: Generate all sentences first**

```bash
# Process 100 words (will take ~30-50 minutes)
for i in {1..100}; do
  python 1_generate_sentences.py
  echo "✅ Word $i complete"
done
```

**Stage 2: Download audio for all words**

```bash
# After all sentences are generated
python 2_download_audio.py
python 2_download_audio.py
# Repeat until all audio is downloaded
```

**Stage 3: Download images for all words**

```bash
# After audio is complete
python 3_download_images.py
python 3_download_images.py
# Repeat until all images are downloaded
```

**Stage 4: Create final Anki deck**

```bash
# After all media is downloaded
python 4_create_anki_tsv.py
```

---

## Database Management

### SQLite Database Operations

#### View Database Contents

```bash
# List all languages in database
sqlite3 user_data.db "SELECT DISTINCT language FROM words LIMIT 20;"

# Count words per language
sqlite3 user_data.db "SELECT language, COUNT(*) FROM words GROUP BY language;"

# Show progress for a language
sqlite3 user_data.db "SELECT language, COUNT(*) as total, SUM(completed) as done FROM words WHERE language='Spanish' GROUP BY language;"
```

#### Reset Progress for a Language

```bash
# Mark all words as incomplete
sqlite3 user_data.db "UPDATE words SET completed=0, last_generated=NULL WHERE language='Spanish';"

# Delete all generation history for a language
sqlite3 user_data.db "DELETE FROM generation_history WHERE language='Spanish';"
```

#### Export Word List

```bash
# Export completed words to CSV
sqlite3 user_data.db ".mode csv" ".output completed_words.csv" "SELECT word FROM words WHERE language='Spanish' AND completed=1;"
```

#### Delete Database

```bash
# Remove entire database (will be recreated on next run)
rm user_data.db
```

---

## Advanced Workflows

### Workflow 1: Quick Test (Single Word)

Test the entire pipeline with one word before doing full batch:

```bash
# 1. Generate sentences for word 1
python 1_generate_sentences.py --words 1

# 2. Review working_data.xlsx manually
# (Open in Excel, check quality)

# 3. Download audio for word 1
python 2_download_audio.py

# 4. Check audio file manually
# (Listen to audio/1_word_001.mp3)

# 5. Download images for word 1
python 3_download_images.py

# 6. Review images manually
# (Check images/ folder)

# 7. Create TSV for word 1
python 4_create_anki_tsv.py

# 8. Import into Anki
# (File → Import → ANKI_IMPORT.tsv)

echo "✅ Test complete! Ready for full batch."
```

### Workflow 2: Batch Generation (25 Words)

Standard workflow for realistic batch:

```bash
#!/bin/bash

# Generate 25 words (recommended batch size)
echo "📝 Generating sentences..."
python 1_generate_sentences.py --words 25 --batch-size 2

# Download audio
echo "🔊 Downloading audio..."
python 2_download_audio.py

# Download images
echo "🖼️ Downloading images..."
python 3_download_images.py

# Create Anki deck
echo "📊 Creating Anki deck..."
python 4_create_anki_tsv.py

echo "✅ Batch complete!"
echo "📍 TSV ready at: ANKI_IMPORT.tsv"
```

### Workflow 3: Recover Failed Generation

Resume generation if a batch fails halfway:

```bash
# Check which words failed
sqlite3 user_data.db "SELECT word FROM words WHERE language='Spanish' AND completed=0 LIMIT 5;"

# Retry sentence generation
echo "Retrying failed sentences..."
python 1_generate_sentences.py --max-retries 5

# Retry audio
echo "Retrying failed audio..."
python 2_download_audio.py --max-retries 5

# Retry images
echo "Retrying failed images..."
python 3_download_images.py --max-retries 5
```

### Workflow 4: Regenerate with Different Settings

Update an existing deck with different audio speed:

```bash
# Reset audio status
sqlite3 user_data.db "UPDATE words SET completed=0 WHERE language='Spanish';"

# Regenerate audio with new speed
python 2_download_audio.py --speed 1.0 --language Spanish

# Recreate TSV with new audio
python 4_create_anki_tsv.py --language Spanish
```

---

## Performance Optimization

### Parallel Processing (Linux/macOS)

Use GNU Parallel for truly parallel execution:

```bash
# Install parallel (macOS)
brew install parallel

# Generate sentences for 50 words in parallel (8 at a time)
seq 1 50 | parallel -j 8 "python 1_generate_sentences.py"

# Download audio in parallel
sqlite3 user_data.db "SELECT word FROM words WHERE status='sentences_done' LIMIT 100;" | \
  parallel -j 4 "python 2_download_audio.py --word {}"
```

### Monitor Progress

```bash
#!/bin/bash

while true; do
  clear
  echo "📊 GENERATION PROGRESS"
  echo "======================="
  sqlite3 user_data.db "
    SELECT 
      'Spanish' as Language,
      COUNT(*) as Total,
      SUM(completed) as Done,
      ROUND(100.0 * SUM(completed) / COUNT(*), 1) as Percent
    FROM words WHERE language='Spanish'
  ;"
  sleep 5
done
```

---

## Environment Variables

Set these to override defaults:

```bash
# Groq API Key
export GROQ_API_KEY="gsk_your_key_here"

# Pixabay API Key
export PIXABAY_API_KEY="your_key_here"

# Google Cloud TTS
export GOOGLE_APPLICATION_CREDENTIALS="./languagelearning-480303.json"

# Audio settings
export AUDIO_SPEED="0.8"
export AUDIO_VOICE_GENDER="female"

# Processing
export BATCH_WORDS="2"
export MAX_RETRIES="5"

# Output
export OUTPUT_DIR="./output"

# Run script with these env vars
AUDIO_SPEED="1.0" python 2_download_audio.py
```

---

## Troubleshooting

### Issue: "API quota exceeded"

**Solution:** Reduce batch size and add delays:

```bash
python 1_generate_sentences.py --words 1
sleep 60  # Wait 60 seconds
python 1_generate_sentences.py --words 1
sleep 60
```

### Issue: "Audio files failed to generate"

**Solution:** Retry with Google TTS fallback:

```bash
python 2_download_audio.py --fallback-only --max-retries 5
```

### Issue: "Images not downloading"

**Solution:** Check Pixabay rate limit:

```bash
# Check if hitting rate limit
sqlite3 user_data.db "SELECT COUNT(*) FROM words WHERE status='images_done';"

# Wait and retry
sleep 3600  # Wait 1 hour
python 3_download_images.py
```

### Issue: "Memory error with large batches"

**Solution:** Reduce batch size:

```bash
# Instead of:
python 1_generate_sentences.py --words 100 --batch-size 10

# Use:
python 1_generate_sentences.py --words 100 --batch-size 1
```

### Issue: "Excel file is locked"

**Solution:** Close Excel, then retry:

```bash
# macOS
lsof | grep working_data.xlsx

# Windows (PowerShell)
Get-Process | Where-Object { $_.Handles -like "*working_data*" }

# Then run script
python 1_generate_sentences.py
```

---

## Advanced SQL Queries

### Find Longest Generation Time

```sql
SELECT word, generation_time_seconds 
FROM generation_history 
WHERE language='Spanish' 
ORDER BY generation_time_seconds DESC 
LIMIT 5;
```

### Find Failed Words

```sql
SELECT word, error_message 
FROM words 
WHERE error_message IS NOT NULL 
AND language='Spanish';
```

### Track Generation Statistics

```sql
SELECT 
  COUNT(*) as total_words,
  AVG(times_generated) as avg_generations,
  MAX(times_generated) as max_generations,
  SUM(CASE WHEN completed=1 THEN 1 ELSE 0 END) as completed_words
FROM words
WHERE language='Spanish';
```

---

## Next Steps

- Modify sentence generation prompts for different styles
- Integrate with other language tools (Anki plugins, etc.)
- Build custom filtering/ranking systems
- Contribute improvements back to the project!

Happy scripting! 🚀
