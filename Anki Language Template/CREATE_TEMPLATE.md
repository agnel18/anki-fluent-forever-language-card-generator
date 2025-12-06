# How to Create the Language Learning Template.apkg File

## Overview

The `Language Learning Template.apkg` file needs to be created **once** by following these steps. After creation, it can be shared with all users to eliminate manual Anki setup.

## Step-by-Step Instructions

### 1. Open Anki

- Launch the Anki application on your computer

### 2. Create the Deck

1. In the main screen, click the **Create Deck** button at the bottom
2. Name it with your target language (e.g., `Malayalam`)
3. Click **OK**

### 3. Create the Note Type

1. Click **Tools** → **Manage Note Types**
2. Click **Add**
3. Select **Clone: Basic**
4. Name it something like `Language Card`
5. Click **OK**

### 4. Add Fields

1. With your new note type selected, click **Fields**
2. Select the default "Front" field → Click **Delete**
3. Select the default "Back" field → Click **Delete**
4. Now add these 8 fields (click **Add** for each):
   - `File Name`
   - `What is the Word?`
   - `Meaning of the Word`
   - `Arabic Sentence`
   - `IPA Transliteration`
   - `English Sentence`
   - `Sound`
   - `Image`
5. Click **Save**

### 5. Customize Card Templates

1. With your new note type selected, click **Cards**
2. Replace the **Front Template** with:
   ```html
   <div class="arabic-sentence" dir="rtl">
     {{Arabic Sentence}}
   </div>
   
   <div class="sound">
     {{Sound}}
   </div>
   ```

3. Replace the **Back Template** with:
   ```html
   {{FrontSide}}
   
   <hr id="answer">
   
   <div class="english-sentence">
     {{English Sentence}}
   </div>
   
   <div class="ipa">
     {{IPA Transliteration}}
   </div>
   
   <div class="word-info">
     <strong>Word:</strong> {{What is the Word?}} ({{Meaning of the Word}})
   </div>
   
   <div class="image">
     {{Image}}
   </div>
   ```

4. Replace the **Styling** section with:
   ```css
   .card {
     font-family: arial;
     font-size: 20px;
     text-align: center;
     color: black;
     background-color: white;
   }

   .arabic-sentence {
     font-size: 40px;
     color: #0066cc;
     margin: 20px;
     font-family: "Traditional Arabic", "Arial Unicode MS", sans-serif;
     direction: rtl;
   }

   .sound {
     margin: 20px;
   }

   .english-sentence {
     font-size: 24px;
     color: #009900;
     margin: 15px;
   }

   .ipa {
     font-size: 16px;
     color: #666;
     font-family: "Charis SIL", "Doulos SIL", serif;
     margin: 10px;
   }

   .word-info {
     font-size: 14px;
     color: #333;
     margin: 15px;
   }

   .image {
     margin: 20px;
   }

   .image img {
     max-width: 500px;
     max-height: 400px;
   }
   ```

5. Click **Save**
6. Click **Close**

### 6. Export the Template

1. In the main Anki window, find your new deck in the deck list
2. Click on the deck name to select it (don't open it)
3. At the bottom of the window, click the **gear icon** ⚙️ next to the deck name
4. Select **Export**
5. In the export dialog:
   - **Export format:** Select `Anki Deck Package (*.apkg)`
  - **Include:** Select `All decks` or just the deck you created
   - **Include scheduling information:** Uncheck this (we only want the template)
   - **Include media:** Can be unchecked (no media yet)
6. Click **Export**
7. Save the file as: `Language Learning Template.apkg`
8. Move it to: `LanguagLearning/Anki Arabic Template/` folder

### 7. Verify the Template

1. Close Anki completely
2. Reopen Anki
3. Click **File** → **Import**
4. Select the `Language Learning Template.apkg` you just created
5. Click **Open**
6. Check that:
  - ✅ Your deck appears in your deck list
  - ✅ Deck has 0 cards
  - ✅ Click **Browse** → Select your deck → Right-click → **Note Type** shows your chosen name
   - ✅ All 8 fields are present

### 8. Commit to Repository

```bash
git add "Anki Arabic Template/Language Learning Template.apkg"
git commit -m "Add Anki template file for easy setup"
git push
```

## Alternative: Use a Test Card

If you want the template to include a sample card (to verify styling):

1. Before exporting, create one test card in the deck:
  - File Name: `0000_test_01`
  - What is the Word?: `hello`
  - Meaning of the Word: `hello`
  - Arabic Sentence: `Hello, how are you?` (or your target language)
  - IPA Transliteration: `/həˈloʊ/`
  - English Sentence: `Hello, how are you?`
  - Sound: (leave empty)
  - Image: (leave empty)

2. Then export as described in step 6

This way, users can immediately see how the cards will look!

## Done!

The `Language Learning Template.apkg` file is now ready to be shared with users. They can import it in seconds instead of spending 10-15 minutes on manual setup.
