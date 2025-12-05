# Anki Setup Guide

## Quick Start (Recommended for Beginners)

**Good news!** This repository includes a pre-made Anki template file: `Anki Arabic Template/Arabic Template.apkg`

### Using the Pre-Made Template (2 minutes)

1. Open Anki
2. Click **File** → **Import**
3. Navigate to `LanguagLearning/Anki Arabic Template/`
4. Select `Arabic Template.apkg`
5. Click **Open**
6. ✅ Done! You now have the **Arabic** deck ready to use

**The template includes:**
- ✅ Pre-configured **Arabic Card** note type with 8 fields
- ✅ Optimized card styling for language learning
- ✅ Right-to-left text support for Arabic
- ✅ Ready to import TSV files

**Skip to [Importing TSV Files](#importing-tsv-files) below.**

---

## Manual Setup (Advanced Users Only)

Only follow this section if you want to customize the template or create it from scratch.

## Creating the .apkg File (One-time Setup)

1. **In Anki, create the deck structure:**
   - Right-click on "Default" deck
   - Click "New Deck"
   - Name it "Arabic"

2. **Create the Note Type:**
   - Click **Tools** → **Manage Note Types**
   - Click **Add**
   - Select **Clone: Basic**
   - Name it "Arabic Card"
   
3. **Add Fields:**
   - Click **Fields**
   - Delete default fields (Front, Back)
   - Click **Add** and add these fields in order:
     - File Name
     - What is the Word?
     - Meaning of the Word
     - Arabic Sentence
     - IPA Transliteration
     - English Sentence
     - Sound
     - Image
   - Click **Save**

4. **Customize Card Template (Optional):**
   - Click **Cards** while still in the note type editor
   - Customize the front/back templates if desired
   - Example template for Front:
     ```
     <div style="font-size: 40px; color: #0066cc;">{{Arabic Sentence}}</div>
     <div style="font-size: 20px; margin-top: 20px;">{{Sound}}</div>
     ```
   - Example template for Back:
     ```
     <div style="font-size: 20px; color: #009900;">{{English Sentence}}</div>
     <div style="font-size: 14px; margin-top: 10px;">{{IPA Transliteration}}</div>
     <div style="font-size: 12px; margin-top: 10px;">Word: {{What is the Word?}} ({{Meaning of the Word}})</div>
     <div style="margin-top: 15px;">{{Image}}</div>
     ```

5. **Export the Deck:**
   - Click **Decks** at the bottom
   - Right-click on "Arabic" deck
   - Select **Export**
   - Choose **Export format: Single file (.apkg)**
   - Choose the save location
   - Save as **ANKI_IMPORT.apkg**

6. **Move the file:**
   - Copy `ANKI_IMPORT.apkg` to `FluentForever_Arabic_Perfect/` directory

## Importing TSV Files

After you have the Anki template set up (either using the pre-made `.apkg` or manual setup), import your generated cards:

1. Click **File** → **Import**
2. Select your generated `ANKI_IMPORT.tsv`
3. Ensure these settings:
   - **Deck**: Arabic
   - **Type**: Arabic Card
   - **Map columns**: Match columns to fields
   - **Options**: Duplicate handling = Replace
4. Click **Import**

Your cards are now in Anki!

## Import Media Files

1. In Anki, go to **Tools** → **Check Media**
2. Click **View Files** (opens collection.media folder)
3. Copy audio files from `FluentForever_Arabic_Perfect/audio/` to this folder
4. Copy image files from `FluentForever_Arabic_Perfect/images/` to this folder
5. ⚠️ Copy FILES, not FOLDERS!
6. Close the media check window

Done! Your cards now have audio and images.

---

**Note:** The .apkg file is just a template. You can recreate it anytime by following the "Creating the .apkg File" steps above.
