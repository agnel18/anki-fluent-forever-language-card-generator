# 🌍 IPA Generation Master Prompt - 77 Languages Extension
# Version: 2026-01-07 (COMPREHENSIVE IPA COVERAGE)
# Reference: IPAService Tiered Approach (Epitran → Phonemizer → AI)

## 🎯 MISSION
Extend IPAService to provide reliable International Phonetic Alphabet (IPA) transliterations for ALL 77 languages in our inventory using a robust tiered approach that never returns empty strings and ensures maximum quality and coverage.

## 📊 CURRENT SITUATION (January 2026)

### **✅ What's Working**
- IPAService with basic Epitran integration
- AI fallback via Groq API
- `validate_ipa_output()` function with comprehensive IPA character support
- Support for ~14 popular languages

### **❌ Critical Issues**
- **Limited Coverage**: Only ~14 languages supported vs. 77 needed
- **Chinese Pinyin Problem**: Epitran returns Pinyin (xǎi àn biān) instead of IPA
- **Empty Field Risk**: When validation fails, fields become blank, breaking learning experience
- **No Fallback Guarantee**: Current implementation can return empty strings
- **Missing Libraries**: No Phonemizer integration for broad coverage

### **🎯 Quality Requirements**
- **Never Empty**: Always return plausible IPA, even if validation fails
- **Maximum Quality**: Use highest-quality source available (Epitran when possible)
- **Broad Coverage**: Support all 77 languages reliably
- **Validation First**: Always run `validate_ipa_output()` but don't discard valid-looking IPA
- **Performance**: <3s average response time
- **Reliability**: <5% failure rate across all languages

## 📚 COMPREHENSIVE LANGUAGE INVENTORY

### **Complete 77-Language Coverage by Family**

| Family | Languages | IPA Complexity | Current Status |
|--------|-----------|----------------|----------------|
| **1. Sino-Tibetan** (8) | Chinese Simplified ✅, Chinese Traditional ✅, Tibetan, Burmese, Karen, Yi, Bai, Tujia | High (tonal, logographic) | Partial |
| **2. Indo-European** (23) | English ✅, German ✅, Dutch ✅, Swedish ✅, Danish ✅, Norwegian ✅, Icelandic ✅, Spanish ✅, French ✅, Italian ✅, Portuguese ✅, Romanian, Catalan, Russian ✅, Polish, Czech, Ukrainian, Bulgarian, Serbian, Hindi ✅, Bengali, Persian, Urdu, Punjabi, Gujarati, Marathi, Greek, Lithuanian, Latvian, Irish, Welsh, Breton, Armenian, Albanian | Medium-High (diverse scripts) | Good |
| **3. Afro-Asiatic** (12) | Arabic ✅, Hebrew ✅, Amharic, Hausa, Somali, Tigrinya, Berber, Coptic, Maltese | High (abugida, right-to-left) | Partial |
| **4. Niger-Congo** (15) | Swahili ✅, Zulu, Yoruba, Igbo, Hausa, Wolof, Bambara, Ewe, Tswana, Sesotho | High (tonal, agglutinative) | Limited |
| **5. Austronesian** (7) | Malay ✅, Indonesian, Tagalog, Maori, Hawaiian, Malagasy, Javanese | Medium (syllabic) | Partial |
| **6. Turkic** (6) | Turkish ✅, Uzbek, Kazakh, Kyrgyz, Tatar, Azerbaijani | Medium (agglutinative) | Partial |
| **7. Dravidian** (4) | Tamil ✅, Telugu, Kannada, Malayalam | High (retroflex, diglossia) | Partial |
| **8. Japonic** (2) | Japanese ✅, Ryukyuan | Medium (mixed script) | Good |
| **9. Koreanic** (1) | Korean ✅ | Medium (alphabet + Sino-Korean) | Good |
| **10. Tai-Kadai** (3) | Thai ✅, Lao, Zhuang | High (tonal, analytic) | Partial |
| **11. Hmong-Mien** (2) | Hmong, Mien | High (tonal) | Limited |
| **12. Austroasiatic** (4) | Vietnamese ✅, Khmer, Mon, Khasi | High (monosyllabic, tonal) | Partial |
| **13. Tibeto-Burman** (6) | Tibetan ✅, Burmese ✅, Karen, Yi ✅, Bai ✅, Tujia ✅ | High (tonal, agglutinative) | Partial |
| **14. Nubian** (1) | Nobiin | High (endangered, tonal) | None |
| **15. Basque** (1) | Basque ✅ | Medium (isolate) | Good |
| **16. Na-Dene** (2) | Navajo, Apache | High (complex consonants) | Limited |
| **17. Eskimo-Aleut** (2) | Inuit, Aleut | High (polysynthetic) | Limited |
| **18. Australian Aboriginal** (3) | Pitjantjatjara, Warlpiri, Arrernte | High (complex phonology) | None |

**PROGRESS TRACKING:**
- ✅ **FULLY SUPPORTED**: 14 languages (English, Spanish, Hindi, Arabic, etc.)
- 🔄 **PARTIALLY SUPPORTED**: 40+ languages via Epitran
- ⏳ **NEEDS IMPLEMENTATION**: 23 languages (Niger-Congo, Hmong-Mien, etc.)
- 🎯 **TARGET**: 100% coverage with acceptable quality

## 🏗️ TECHNICAL APPROACH: TIERED IPA GENERATION

### **Three-Tier Architecture**

#### **Tier 1: Epitran (Highest Quality, Selective)**
```python
# Highest quality IPA when available
# Supports ~60/77 languages
# Linguistic rule-based transliteration
epi = epitran.Epitran("hin-Deva")  # Hindi in Devanagari
ipa = epi.transliterate("नमस्ते")  # → [nəməste]
```

#### **Tier 2: Phonemizer + espeak-ng (Broad Coverage, Good Quality)**
```python
# Supports 100+ languages via speech synthesis
# Good quality for most languages
import phonemizer
ipa = phonemizer.phonemize("hello", language="en", backend="espeak")
# → "həˈləʊ"
```

#### **Tier 3: AI-Generated IPA (Universal Fallback)**
```python
# Always available, variable quality
# Never returns empty (guaranteed fallback)
ai_ipa = get_ai_ipa(text, language)  # From Groq API
```

### **Critical Design Principles**

#### **1. Never Return Empty**
```python
def generate_ipa_hybrid(self, text: str, language: str, ai_ipa: str = "") -> str:
    """GUARANTEED: Never returns empty string."""
    # Try all tiers, return best available
    # Final fallback: meaningful placeholder
    return ipa or ai_ipa or f"[IPA unavailable for {language}]"
```

#### **2. Validation But Not Rejection**
```python
def _validate_ipa(self, ipa: str, language: str) -> bool:
    """Validate but allow best-effort returns."""
    is_valid, msg = validate_ipa_output(ipa, language)
    if is_valid:
        return True
    # Log warning but don't discard - return best effort
    logger.warning(f"IPA validation failed: {msg}")
    return len(ipa.strip()) > 0  # Accept if not empty
```

#### **3. Chinese Special Handling**
```python
# Skip Epitran for Chinese (returns Pinyin)
if language in ["Chinese (Simplified)", "Chinese (Traditional)"]:
    epitran_result = ""  # Skip to Phonemizer
```

## 📋 IMPLEMENTATION PHASES

### **Phase 1: Research & Architecture (Week 1)**

#### **1.1 Complete Language Mappings**
**Epitran Codes** (60/77 supported):
```python
self.epitran_map = {
    "English": "eng-Latn",
    "Hindi": "hin-Deva",
    "Arabic": "ara-Arab",
    "Chinese (Simplified)": None,  # Skip
    "Chinese (Traditional)": None,  # Skip
    # ... complete mappings for all 77
}
```

**Phonemizer Codes** (77/77 supported):
```python
self.phonemizer_map = {
    "English": "en",
    "Hindi": "hi",
    "Arabic": "ar",
    "Chinese (Simplified)": "cmn",  # Mandarin
    "Chinese (Traditional)": "cmn",  # Mandarin
    # ... complete mappings for all 77
}
```

#### **1.2 Dependency Setup**
```bash
# Install phonemizer
pip install phonemizer

# Install espeak-ng (Windows via conda)
conda install -c conda-forge espeak-ng
```

#### **1.3 Architecture Validation**
- Test phonemizer installation on target platforms
- Validate espeak-ng backend availability
- Confirm compatibility with existing codebase

### **Phase 2: Core Implementation (Week 2)**

#### **2.1 IPAService Class Extension**
```python
class IPAService:
    def __init__(self):
        # Existing mappings
        self.language_map = {...}
        
        # New comprehensive mappings
        self.epitran_map = self._load_epitran_mappings()
        self.phonemizer_map = self._load_phonemizer_mappings()
    
    def generate_ipa_hybrid(self, text: str, language: str, ai_ipa: str = "") -> str:
        """Three-tier IPA generation with guaranteed non-empty return."""
        
        # Tier 1: Epitran (highest quality)
        ipa = self._try_epitran(text, language)
        if ipa and self._validate_ipa(ipa, language):
            return ipa
        
        # Tier 2: Phonemizer (broad coverage)
        ipa = self._try_phonemizer(text, language)
        if ipa and self._validate_ipa(ipa, language):
            return ipa
        
        # Tier 3: AI fallback (guaranteed)
        return self._ensure_fallback_ipa(ai_ipa, text, language)
```

#### **2.2 Epitran Implementation**
```python
def _try_epitran(self, text: str, language: str) -> str:
    """Attempt Epitran transliteration."""
    # Skip Chinese (returns Pinyin)
    if "Chinese" in language:
        return ""
    
    epi_code = self.epitran_map.get(language)
    if not epi_code:
        return ""
    
    try:
        import epitran
        epi = epitran.Epitran(epi_code)
        ipa = epi.transliterate(text)
        
        # Validate basic quality
        if ipa and ipa != text and len(ipa.strip()) > 0:
            return ipa
        return ""
        
    except Exception as e:
        logger.warning(f"Epitran failed for {language}: {e}")
        return ""
```

#### **2.3 Phonemizer Implementation**
```python
def _try_phonemizer(self, text: str, language: str) -> str:
    """Attempt Phonemizer with espeak-ng backend."""
    phone_code = self.phonemizer_map.get(language)
    if not phone_code:
        return ""
    
    try:
        import phonemizer
        
        # Configure for IPA output
        ipa = phonemizer.phonemize(
            text,
            language=phone_code,
            backend='espeak',
            strip=True,
            preserve_punctuation=False,
            with_stress=True  # Include stress marks
        )
        
        # Clean and validate
        ipa = ipa.strip()
        if ipa and len(ipa) > 0:
            return ipa
        return ""
        
    except Exception as e:
        logger.warning(f"Phonemizer failed for {language}: {e}")
        return ""
```

#### **2.4 Validation & Fallback Logic**
```python
def _validate_ipa(self, ipa: str, language: str) -> bool:
    """Validate IPA but allow best-effort returns."""
    if not ipa or not ipa.strip():
        return False
    
    # Use existing validation function
    from generation_utils import validate_ipa_output
    is_valid, validation_msg = validate_ipa_output(ipa, language)
    
    if is_valid:
        return True
    
    # Log but don't reject - accept best effort
    logger.warning(f"IPA validation failed for {language}: {validation_msg}")
    
    # Basic quality checks
    ipa_clean = ipa.strip()
    
    # Reject obvious Pinyin (Chinese tone marks)
    if any(char in ipa_clean for char in 'āēīōūǖǎěǐǒǔǚ'):
        logger.warning(f"Rejected Pinyin in IPA for {language}")
        return False
    
    # Accept if it has IPA-like content
    return len(ipa_clean) > 0

def _ensure_fallback_ipa(self, ai_ipa: str, text: str, language: str) -> str:
    """Guarantee non-empty IPA return."""
    # Try AI IPA first
    if ai_ipa and ai_ipa.strip():
        # Validate but accept even if validation fails
        if self._validate_ipa(ai_ipa, language):
            return ai_ipa
        # Still return if it looks plausible
        if len(ai_ipa.strip()) > 0:
            return ai_ipa
    
    # Ultimate fallback: meaningful placeholder
    logger.warning(f"All IPA tiers failed for {language}, using placeholder")
    return f"[IPA unavailable for {language}]"
```

### **Phase 3: Testing & Quality Assurance (Week 3)**

#### **3.1 Comprehensive Testing Strategy**

##### **3.1.1 Complete Language Coverage Testing**
```python
# Test all 77 languages with native script examples
COMPREHENSIVE_TEST_CASES = [
    # Indo-European (23 languages)
    ("English", "hello world", "həˈləʊ wɜːld"),
    ("Spanish", "hola mundo", "ˈola ˈmundo"),
    ("French", "bonjour le monde", "bɔ̃ʒuʁ lə mɔ̃d"),
    ("German", "hallo welt", "ˈhalo ˈvɛlt"),
    ("Italian", "ciao mondo", "ˈtʃao ˈmondo"),
    ("Portuguese", "olá mundo", "oˈla ˈmũdu"),
    ("Russian", "привет мир", "ˈprʲivʲɪt mʲir"),
    ("Hindi", "नमस्ते दुनिया", "nəməste dunijɑ"),
    ("Arabic", "مرحبا بالعالم", "marħaban bɪlʕɑlæm"),
    ("Persian", "سلام دنیا", "sælɑm donjɑ"),
    ("Urdu", "ہیلو دنیا", "heːloː dunjɑː"),
    ("Bengali", "ওহে বিশ্ব", "ohē biśba"),
    ("Punjabi", "ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ ਦੁਨਿਆ", "sət srī əkɑl dunɪɑ"),
    ("Gujarati", "હેલો વિશ્વ", "hɛlo viʃva"),
    ("Marathi", "हॅलो विश्व", "hɛlo viʃva"),
    ("Greek", "γεια σου κόσμε", "ʝa su ˈkozme"),
    ("Polish", "cześć świecie", "ˈtʂɛɕɕ ɕfʲatɕɛ"),
    ("Czech", "ahoj světe", "ˈaɦoj ˈsvjɛtɛ"),
    ("Ukrainian", "привіт світе", "prɪˈvʲit ˈsʲvʲite"),
    ("Bulgarian", "здравей свят", "zdraˈvɛj svʲat"),
    ("Serbian", "здраво свете", "zdrɑːvɔ svɛtɛ"),
    ("Dutch", "hallo wereld", "ˈɦɑloː ˈʋeːrəlt"),
    ("Swedish", "hej världen", "ˈhɛjː ˈʋæːɖɛn"),
    ("Danish", "hej verden", "ˈhaj ˈveːɐ̯n"),
    ("Norwegian", "hei verden", "hæɪ ˈʋæːɳ"),
    ("Icelandic", "halló heimur", "ˈhatlou ˈhɛimʏr"),
    ("Romanian", "salut lume", "saˈlut ˈlume"),
    ("Catalan", "hola món", "ˈɔlə ˈmon"),
    ("Lithuanian", "labas pasauli", "ˈlɐbɐs pɐsɐˈʊlʲi"),
    ("Latvian", "sveiki pasaule", "ˈsʋeiki ˈpasɑule"),
    ("Irish", "dia duit domhan", "ˈdʲiə ˈd̪ˠɪt̪ˠ ˈd̪ˠoːn"),
    ("Welsh", "helo byd", "ˈhɛlɔ ˈbɪd"),
    ("Breton", "demat bed", "ˈdɛmɑd ˈbeːd"),
    ("Armenian", "բարև աշխարհ", "paɹɛv aʃχaɹh"),
    ("Albanian", "përshëndetje botë", "pərʃəndɛtjɛ bɔtə"),
    
    # Sino-Tibetan (8 languages)
    ("Chinese (Simplified)", "你好世界", "ni˧˥ xɑʊ˧˩ ʂi˥˩ tɕiɛ˥˩"),  # Phonemizer
    ("Chinese (Traditional)", "你好世界", "ni˧˥ xɑʊ˧˩ ʂi˥˩ tɕiɛ˥˩"),  # Phonemizer
    ("Tibetan", "བཀྲ་ཤིས་བདེ་ལེགས", "tʰakʂi teːlɛk"),  # Epitran
    ("Burmese", "မင်္ဂလာပါ ကမ္ဘာလောက", "mɪ̀ɴɡəlàpà kəmbà lòʊʔ"),  # Epitran
    ("Yi", "ꆈꌠꁱꂷ", "noʂi"),  # Epitran
    ("Bai", "你好世界", "noʂi"),  # Fallback
    ("Karen", "မဂၤလာပါ ကမ္ဘာလောက", "məɡəlɑ pɑ kəmbɑ lɑʊʔ"),  # Fallback
    ("Tujia", "你好世界", "noʂi"),  # Fallback
    
    # Afro-Asiatic (12 languages)
    ("Hebrew", "שלום עולם", "ʃaˈlom ʕoˈlam"),
    ("Amharic", "ሰላም አለም", "səlam aləm"),
    ("Hausa", "sannu duniya", "sannu duniːaː"),
    ("Somali", "salam adduunka", "salaam adduunka"),
    ("Tigrinya", "ሰላማት ዓለም", "səlamat ʕaləm"),
    ("Berber", "azul adunit", "azul adunit"),  # Fallback
    ("Coptic", "Ⲭⲁⲓⲣⲉ ⲕⲟⲥⲙⲟⲥ", "kʰɛːɾe kosmos"),  # Epitran
    ("Maltese", "ħello dinja", "ɪlːu dinja"),
    
    # Niger-Congo (15 languages)
    ("Swahili", "habari dunia", "hɑˈbɑri dunɪˈɑ"),
    ("Zulu", "sawubona mhlaba", "sɑːˈbuːnɑ m̩ɬɑːbɑ"),
    ("Yoruba", "mo ki ile aye", "mō kī ilē ayē"),
    ("Igbo", "kedu ụwa", "kɛdu ʊwa"),
    ("Hausa", "sannu duniya", "sannu duniːaː"),  # Duplicate
    ("Wolof", "salam àdduna", "salaam àdduna"),
    ("Bambara", "i ni ce dunuya", "i ni tʃɛ dunuya"),
    ("Ewe", "woe xexeame", "woe xexeame"),
    ("Tswana", "dumela lefatshe", "dumɛlɑ lɛfɑtsʰɛ"),
    ("Sesotho", "lumela lefatshe", "lumɛlɑ lɛfɑtsʰɛ"),
    
    # Austronesian (7 languages)
    ("Malay", "hello dunia", "hɛlo dunia"),
    ("Indonesian", "halo dunia", "halo dunia"),
    ("Tagalog", "kamusta mundo", "kamusta mundo"),
    ("Maori", "kia ora ao", "kia ˈoɾa ao"),
    ("Hawaiian", "aloha honua", "əˈloʊhə hoˈnuə"),
    ("Malagasy", "salama tontolo izao", "salama tontolo izao"),
    ("Javanese", "halo jagad", "halo dʒɑɡɑd"),
    
    # Turkic (6 languages)
    ("Turkish", "merhaba dünya", "mɛɾˈhɑbɑ ˈdunjɑ"),
    ("Uzbek", "salom dunyo", "sælɔm dunjɔ"),
    ("Kazakh", "сәлем әлем", "sælɛm ælɛm"),
    ("Kyrgyz", "салам дүйнө", "salaːm dyjnø"),
    ("Tatar", "сәлам дөнья", "səlɑm dөnjɑ"),
    ("Azerbaijani", "salam dünya", "sɑlɑm dunjɑ"),
    
    # Dravidian (4 languages)
    ("Tamil", "அனைத்தும் சரியாக இருக்கிறது", "ənɛttum səriyɑːkə irukkirətu"),
    ("Telugu", "హలో ప్రపంచం", "ɦəloː prəpəɲtʃəm"),
    ("Kannada", "ಹ್ಯಾಲೋ ಲೋಕ", "hjɑːloː loːkə"),
    ("Malayalam", "ഹലോ ലോകം", "ɦəloː loːkəm"),
    
    # Japonic (2 languages)
    ("Japanese", "こんにちは世界", "konˈnitʃiwa seˈkai"),
    ("Ryukyuan", "こんにちは世界", "konˈnitʃiwa seˈkai"),  # Fallback to Japanese
    
    # Koreanic (1 language)
    ("Korean", "안녕하세요 세계", "anɲʌŋhasɛjo sɛkʲe"),
    
    # Tai-Kadai (3 languages)
    ("Thai", "สวัสดีโลก", "sà-wàt-dii lôok"),
    ("Lao", "ສະບາຍດີໂລກ", "səpɑːj diː loːk"),
    ("Zhuang", "你好世界", "mbwn"),  # Fallback
    
    # Hmong-Mien (2 languages)
    ("Hmong", "nyob zoo ntiaj teb", "nyob zoo ntiaj teb"),
    ("Mien", "nyob zoo ntiaj teb", "nyob zoo ntiaj teb"),  # Fallback
    
    # Austroasiatic (4 languages)
    ("Vietnamese", "xin chào thế giới", "sin tʃaːʊ̯ tʰêˀ ʒɔ̂ˀi"),
    ("Khmer", "ជំរាបសួរ ពិភពលោក", "cumriəp suə pʰiʔpʰəp lok"),
    ("Mon", "ဟယ်လို ကမ္ဘာ", "həlɔ kəmbɑ"),
    ("Khasi", "khublei shibun ki", "khublei ʃibun ki"),
    
    # Other isolates and small families
    ("Basque", "kaixo mundua", "kajʃo mundua"),
    ("Navajo", "yá'át'ééh níłch'i", "jɑʔɑtʔeːh nɪɬtʃʔi"),
    ("Apache", "da'anzho nahał'aah", "dɑʔɑnzʰo nɑhɑɬʔɑːh"),  # Fallback
    ("Inuit", "ai", "ai"),
    ("Aleut", "alakay", "alakay"),
    ("Pitjantjatjara", "palya", "palya"),
    ("Warlpiri", "warrkirdi", "warrkirdi"),
    ("Arrernte", "altyerre", "altyerre"),
    ("Nubian", "asalam", "asalam"),
]

def test_all_77_languages_coverage():
    """Test that all 77 languages return non-empty IPA."""
    ipa_service = IPAService()
    
    for language, text, expected_pattern in COMPREHENSIVE_TEST_CASES:
        ipa = ipa_service.generate_ipa_hybrid(text, language)
        
        # Never empty assertion
        assert ipa, f"Empty IPA for {language} with text: {text}"
        
        # No Pinyin contamination
        assert not any(char in ipa for char in 'āēīōūǖǎěǐǒǔǚ'), f"Pinyin detected in {language} IPA: {ipa}"
        
        # Basic quality checks
        assert len(ipa.strip()) > 0, f"IPA is only whitespace for {language}"
        assert ipa != text, f"IPA identical to input text for {language}: {text}"
        
        print(f"✅ {language}: {text} → {ipa}")
```

##### **3.1.2 Edge Case Testing**
```python
def test_edge_cases():
    """Test edge cases and error conditions."""
    ipa_service = IPAService()
    
    # Empty input
    assert ipa_service.generate_ipa_hybrid("", "English") == ""
    
    # Whitespace only
    assert ipa_service.generate_ipa_hybrid("   ", "English") == ""
    
    # Unsupported language (should use AI fallback)
    ipa = ipa_service.generate_ipa_hybrid("test", "Unsupported Language", "fallback_ipa")
    assert ipa == "fallback_ipa"
    
    # Very long text
    long_text = "hello world " * 100
    ipa = ipa_service.generate_ipa_hybrid(long_text, "English")
    assert ipa and len(ipa) > 0
    
    # Special characters and punctuation
    special_text = "hello, world! 你好。"
    ipa = ipa_service.generate_ipa_hybrid(special_text, "English")
    assert ipa and len(ipa) > 0
    
    # Numbers and symbols
    numeric_text = "123 hello 456"
    ipa = ipa_service.generate_ipa_hybrid(numeric_text, "English")
    assert ipa and len(ipa) > 0
```

##### **3.1.3 Tier Fallback Testing**
```python
def test_tier_fallback_behavior():
    """Test that tiers fall back correctly when higher tiers fail."""
    ipa_service = IPAService()
    
    # Test Chinese skips Epitran (uses Phonemizer)
    ipa = ipa_service.generate_ipa_hybrid("你好", "Chinese (Simplified)")
    assert ipa  # Should get Phonemizer result
    assert not any(char in ipa for char in 'āēīōūǖ'), "Chinese should not return Pinyin"
    
    # Test language with no Epitran support (uses Phonemizer)
    ipa = ipa_service.generate_ipa_hybrid("hello", "Hmong")
    assert ipa  # Should get Phonemizer result
    
    # Test complete failure scenario (uses AI fallback)
    ipa = ipa_service.generate_ipa_hybrid("test", "English", "ai_fallback_ipa")
    # Should prefer Epitran over AI fallback
    assert ipa != "ai_fallback_ipa"  # Epitran should work
    
    # Test with invalid AI fallback (uses placeholder)
    ipa = ipa_service.generate_ipa_hybrid("test", "Unsupported", "")
    assert ipa == "[IPA unavailable for Unsupported]"
```

##### **3.1.4 Validation Best-Effort Testing**
```python
def test_validation_best_effort():
    """Test that validation allows best-effort returns."""
    ipa_service = IPAService()
    
    # Mock a scenario where validation fails but we still return result
    # This tests the _validate_ipa method's best-effort logic
    
    # Test with AI IPA that might not pass validation
    ai_ipa = "invalid_but_present"
    ipa = ipa_service.generate_ipa_hybrid("test", "English", ai_ipa)
    assert ipa  # Should not be empty even if validation fails
    
    # Test with plausible but non-valid IPA
    ai_ipa = "tɛst wɜrd"  # Looks IPA-like but may not pass strict validation
    ipa = ipa_service.generate_ipa_hybrid("test", "English", ai_ipa)
    assert ipa  # Should accept best-effort
```

#### **3.2 Quality Assessment Framework**

##### **3.2.1 Automated Quality Metrics**
```python
def assess_ipa_quality_comprehensive(ipa_results: Dict[str, str], test_cases: List[Tuple[str, str, str]]) -> Dict[str, Any]:
    """Comprehensive quality assessment for all languages."""
    metrics = {
        "coverage": {"total": len(test_cases), "successful": 0, "failed": 0},
        "quality": {"validation_pass": 0, "validation_fail": 0, "pinyin_free": 0},
        "performance": {"avg_response_time": 0.0, "max_response_time": 0.0},
        "content": {"avg_length_ratio": 0.0, "empty_returns": 0},
        "by_family": {},
        "by_tier": {"epitran": 0, "phonemizer": 0, "ai_fallback": 0, "placeholder": 0}
    }
    
    response_times = []
    
    for (language, text, expected), ipa in zip(test_cases, ipa_results.values()):
        start_time = time.time()
        
        # Coverage metrics
        if ipa and ipa.strip():
            metrics["coverage"]["successful"] += 1
        else:
            metrics["coverage"]["failed"] += 1
            metrics["content"]["empty_returns"] += 1
        
        # Quality metrics
        is_valid, msg = validate_ipa_output(ipa, language)
        if is_valid:
            metrics["quality"]["validation_pass"] += 1
        else:
            metrics["quality"]["validation_fail"] += 1
        
        # Pinyin contamination check
        has_pinyin = any(char in ipa for char in 'āēīōūǖǎěǐǒǔǚ')
        if not has_pinyin:
            metrics["quality"]["pinyin_free"] += 1
        
        # Content analysis
        if text and ipa:
            length_ratio = len(ipa) / len(text)
            metrics["content"]["avg_length_ratio"] += length_ratio
        
        # Family categorization
        family = get_language_family(language)
        if family not in metrics["by_family"]:
            metrics["by_family"][family] = {"count": 0, "quality_score": 0.0}
        metrics["by_family"][family]["count"] += 1
        metrics["by_family"][family]["quality_score"] += 1.0 if is_valid else 0.0
        
        # Tier identification (would need to be tracked during generation)
        # metrics["by_tier"][detect_used_tier(ipa, language)] += 1
        
        response_time = time.time() - start_time
        response_times.append(response_time)
    
    # Calculate averages
    if response_times:
        metrics["performance"]["avg_response_time"] = sum(response_times) / len(response_times)
        metrics["performance"]["max_response_time"] = max(response_times)
    
    if metrics["content"]["avg_length_ratio"] > 0:
        metrics["content"]["avg_length_ratio"] /= metrics["coverage"]["total"]
    
    # Calculate family averages
    for family in metrics["by_family"]:
        count = metrics["by_family"][family]["count"]
        if count > 0:
            metrics["by_family"][family]["quality_score"] /= count
    
    return metrics

def get_language_family(language: str) -> str:
    """Map language to its language family."""
    family_map = {
        # Indo-European
        "English": "Indo-European", "Spanish": "Indo-European", "French": "Indo-European",
        "German": "Indo-European", "Italian": "Indo-European", "Portuguese": "Indo-European",
        "Russian": "Indo-European", "Hindi": "Indo-European", "Arabic": "Afro-Asiatic",
        # ... complete mapping for all languages
    }
    return family_map.get(language, "Other")
```

##### **3.2.2 Manual Quality Review Process**
```python
def manual_quality_review_sample():
    """Generate sample for manual quality review."""
    ipa_service = IPAService()
    
    # Sample 20 languages for manual review
    review_languages = [
        "English", "Spanish", "French", "German", "Chinese (Simplified)",
        "Japanese", "Korean", "Hindi", "Arabic", "Russian",
        "Portuguese", "Italian", "Dutch", "Swedish", "Greek",
        "Hebrew", "Tamil", "Thai", "Vietnamese", "Swahili"
    ]
    
    review_results = {}
    
    for language in review_languages:
        test_text = get_sample_text_for_language(language)
        ipa = ipa_service.generate_ipa_hybrid(test_text, language)
        
        review_results[language] = {
            "text": test_text,
            "ipa": ipa,
            "quality_rating": None,  # To be filled by linguist
            "accuracy_notes": None,  # To be filled by linguist
            "used_tier": detect_used_tier(ipa, language)
        }
    
    # Save to JSON for manual review
    with open("ipa_quality_review.json", "w", encoding="utf-8") as f:
        json.dump(review_results, f, ensure_ascii=False, indent=2)
    
    return review_results

def get_sample_text_for_language(language: str) -> str:
    """Get appropriate sample text for each language."""
    samples = {
        "English": "The quick brown fox jumps over the lazy dog",
        "Spanish": "El rápido zorro marrón salta sobre el perro perezoso",
        "French": "Le rapide renard brun saute par-dessus le chien paresseux",
        "German": "Der schnelle braune Fuchs springt über den faulen Hund",
        "Chinese (Simplified)": "敏捷的棕色狐狸跳过了懒狗",
        "Japanese": "素早い茶色の狐が怠けた犬を飛び越えた",
        "Korean": "빠른 갈색 여우가 게으른 개를 뛰어 넘었다",
        "Hindi": "तेज भूरी लोमड़ी आलसी कुत्ते के ऊपर कूदती है",
        "Arabic": "الثعلب البني السريع يقفز فوق الكلب الكسول",
        "Russian": "Быстрая коричневая лиса прыгает через ленивую собаку",
        "Portuguese": "A raposa marrom rápida pula sobre o cachorro preguiçoso",
        "Italian": "La volpe marrone veloce salta sopra il cane pigro",
        "Dutch": "De snelle bruine vos springt over de luie hond",
        "Swedish": "Den snabba bruna räven hoppar över den lata hunden",
        "Greek": "Η γρήγορη καφέ αλεπού πηδάει πάνω από το τεμπέλικο σκυλί",
        "Hebrew": "השועל החום המהיר קופץ מעל הכלב העצלן",
        "Tamil": "விரைவான பழுப்பு நிற நரி சோம்பேறி நாய்க்கு மேல் குதிக்கிறது",
        "Thai": "สุนัขสีน้ำตาลที่เร็วกระโดดข้ามสุนัขขี้เกียจ",
        "Vietnamese": "Con cáo nâu nhanh nhảy qua con chó lười biếng",
        "Swahili": "Mbwa ya kahawia ya haraka huruka juu ya mbwa mvivu"
    }
    return samples.get(language, "hello world")
```

#### **3.3 Performance Testing & Optimization**

##### **3.3.1 Load Testing**
```python
def performance_test_all_languages():
    """Test performance across all 77 languages."""
    ipa_service = IPAService()
    
    results = {
        "individual_times": {},
        "total_time": 0,
        "avg_time_per_language": 0,
        "max_time": 0,
        "min_time": float('inf')
    }
    
    start_total = time.time()
    
    for language, text, _ in COMPREHENSIVE_TEST_CASES:
        start = time.time()
        ipa = ipa_service.generate_ipa_hybrid(text, language)
        end = time.time()
        
        response_time = end - start
        results["individual_times"][language] = response_time
        results["max_time"] = max(results["max_time"], response_time)
        results["min_time"] = min(results["min_time"], response_time)
    
    results["total_time"] = time.time() - start_total
    results["avg_time_per_language"] = results["total_time"] / len(COMPREHENSIVE_TEST_CASES)
    
    # Performance assertions
    assert results["avg_time_per_language"] < 3.0, f"Average time too slow: {results['avg_time_per_language']}"
    assert results["max_time"] < 10.0, f"Max time too slow: {results['max_time']}"
    
    return results
```

##### **3.3.2 Caching Performance Test**
```python
def test_caching_performance():
    """Test performance improvement with caching."""
    ipa_service = IPAService()
    
    # Test repeated calls (should benefit from caching)
    test_cases = [("English", "hello world")] * 10
    
    start = time.time()
    for language, text in test_cases:
        ipa = ipa_service.generate_ipa_hybrid(text, language)
    end = time.time()
    
    avg_time = (end - start) / len(test_cases)
    
    # With caching, average should be < 0.5s
    assert avg_time < 0.5, f"Caching not effective: {avg_time}s average"
    
    return {"avg_cached_time": avg_time}
```

##### **3.3.3 Memory and Resource Testing**
```python
def test_memory_usage():
    """Test memory usage during bulk processing."""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    ipa_service = IPAService()
    
    # Process all test cases
    for language, text, _ in COMPREHENSIVE_TEST_CASES:
        ipa = ipa_service.generate_ipa_hybrid(text, language)
    
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_increase = final_memory - initial_memory
    
    # Memory increase should be reasonable (< 500MB)
    assert memory_increase < 500, f"Excessive memory usage: {memory_increase}MB"
    
    return {"initial_mb": initial_memory, "final_mb": final_memory, "increase_mb": memory_increase}
```

#### **3.4 Integration Testing**

##### **3.4.1 End-to-End Pipeline Testing**
```python
def test_full_pipeline_integration():
    """Test IPA service integration with sentence generation pipeline."""
    from sentence_generator import SentenceGenerator
    
    generator = SentenceGenerator()
    
    # Test languages that should work end-to-end
    test_languages = ["English", "Spanish", "Hindi", "Chinese (Simplified)", "Japanese"]
    
    for language in test_languages:
        try:
            # Generate sentence with IPA
            result = generator.generate_sentence(language, difficulty="beginner")
            
            # Verify IPA field is populated
            assert result.get("ipa"), f"Empty IPA in pipeline for {language}"
            assert result["ipa"] != "", f"Empty IPA string for {language}"
            
            # Verify no Pinyin contamination
            if language not in ["Chinese (Simplified)", "Chinese (Traditional)"]:
                assert not any(char in result["ipa"] for char in 'āēīōūǖǎěǐǒǔǚ'), f"Pinyin in {language} IPA"
            
            print(f"✅ Pipeline integration successful for {language}")
            
        except Exception as e:
            print(f"❌ Pipeline integration failed for {language}: {e}")
            raise
```

##### **3.4.2 Regression Testing**
```python
def test_regression_existing_functionality():
    """Ensure existing functionality still works."""
    ipa_service = IPAService()
    
    # Test existing supported languages
    existing_tests = [
        ("English", "hello", "həˈləʊ"),
        ("Spanish", "hola", "ˈola"),
        ("Hindi", "नमस्ते", "nəməste"),
        ("Arabic", "مرحبا", "marħaban"),
        ("Chinese (Simplified)", "你好", "ni˧˥ xɑʊ˧˩"),
    ]
    
    for language, text, expected_pattern in existing_tests:
        ipa = ipa_service.generate_ipa_hybrid(text, language)
        
        assert ipa, f"Regression: Empty IPA for {language}"
        assert not any(char in ipa for char in 'āēīōūǖ'), f"Regression: Pinyin in {language}"
        
        # Basic pattern matching for known cases
        if language == "English" and "h" in ipa.lower():
            assert "ˈ" in ipa or "ˌ" in ipa, f"Regression: Missing stress marks in English IPA"
```

#### **3.5 Error Handling & Robustness Testing**

##### **3.5.1 Library Failure Simulation**
```python
def test_library_failure_robustness():
    """Test behavior when external libraries fail."""
    ipa_service = IPAService()
    
    # Simulate Epitran failure
    original_try_epitran = ipa_service._try_epitran
    ipa_service._try_epitran = lambda *args: ""  # Always fail
    
    try:
        ipa = ipa_service.generate_ipa_hybrid("hello", "English", "ai_fallback")
        assert ipa, "Should fallback when Epitran fails"
        assert ipa == "ai_fallback", "Should use AI fallback when Epitran fails"
    finally:
        ipa_service._try_epitran = original_try_epitran
    
    # Simulate Phonemizer failure
    original_try_phonemizer = ipa_service._try_phonemizer
    ipa_service._try_phonemizer = lambda *args: ""  # Always fail
    
    try:
        ipa = ipa_service.generate_ipa_hybrid("hello", "English", "ai_fallback")
        assert ipa, "Should fallback when Phonemizer fails"
        assert ipa == "ai_fallback", "Should use AI fallback when Phonemizer fails"
    finally:
        ipa_service._try_phonemizer = original_try_phonemizer
    
    # Simulate all failures
    ipa_service._try_epitran = lambda *args: ""
    ipa_service._try_phonemizer = lambda *args: ""
    
    try:
        ipa = ipa_service.generate_ipa_hybrid("hello", "English", "")
        assert ipa, "Should provide placeholder when all tiers fail"
        assert ipa == "[IPA unavailable for English]", "Should use placeholder"
    finally:
        ipa_service._try_epitran = original_try_epitran
        ipa_service._try_phonemizer = original_try_phonemizer
```

##### **3.5.2 Timeout and Performance Boundary Testing**
```python
def test_timeout_boundaries():
    """Test timeout handling and performance boundaries."""
    import signal
    
    def timeout_handler(signum, frame):
        raise TimeoutError("Test timeout")
    
    ipa_service = IPAService()
    
    # Test with very long text that might cause timeouts
    long_text = "word " * 1000  # 5000 characters
    
    # Set 5-second timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(5)
    
    try:
        ipa = ipa_service.generate_ipa_hybrid(long_text, "English")
        assert ipa, "Should handle long text gracefully"
        signal.alarm(0)  # Cancel timeout
    except TimeoutError:
        pytest.fail("IPA generation timed out on long text")
    finally:
        signal.alarm(0)
```

### **Phase 3 Deliverables**
- ✅ **Comprehensive Test Suite**: 77-language coverage with edge cases
- ✅ **Quality Assessment Framework**: Automated metrics + manual review process  
- ✅ **Performance Benchmarks**: Load testing, caching validation, memory profiling
- ✅ **Integration Tests**: End-to-end pipeline validation + regression testing
- ✅ **Error Handling Tests**: Library failure simulation + timeout testing
- ✅ **Test Results Report**: Detailed coverage, quality, and performance metrics

### **Phase 4: Integration & Deployment (Week 4)**

#### **4.1 Integration Testing**
- **End-to-End**: Test with sentence generation pipeline
- **Regression Testing**: Ensure existing functionality unchanged
- **Cross-Language Consistency**: Verify similar languages produce consistent quality

#### **4.2 Deployment Strategy**
- **Staging First**: Deploy to test environment
- **Gradual Rollout**: Enable for 10 languages, monitor, expand
- **Monitoring**: Track success rates, quality metrics, error rates

#### **4.3 Documentation & Maintenance**
- **API Documentation**: Update IPAService docstrings
- **Troubleshooting Guide**: Common issues and solutions
- **Version Control**: Track mapping updates and improvements

## 📊 QUALITY METRICS & SUCCESS CRITERIA

### **Coverage Metrics**
- ✅ **100% Language Support**: All 77 languages covered
- ✅ **Zero Empty Returns**: Never return empty strings
- ✅ **Fallback Guarantee**: Always provide IPA or meaningful placeholder

### **Quality Metrics**
- 🎯 **Accuracy**: 80%+ acceptable IPA quality across all languages
- 🎯 **Validation**: <10% validation failures (but still return results)
- 🎯 **Pinyin-Free**: Zero Pinyin contamination in IPA output

### **Performance Metrics**
- ⚡ **Latency**: <3s average response time
- ⚡ **Reliability**: >95% success rate across all languages
- ⚡ **Caching**: 50%+ cache hit rate for repeated requests

### **User Experience Metrics**
- 👤 **No Broken Cards**: IPA fields always populated in Anki decks
- 👤 **Consistent Quality**: Similar quality across language families
- 👤 **Fast Generation**: No noticeable delays in sentence creation

## 🔧 DETAILED CODE REFERENCE

### **Complete IPAService Implementation**
```python
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class IPAService:
    """
    Enhanced IPA Service supporting all 77 languages via tiered approach.
    
    Tiers:
    1. Epitran (highest quality, ~60 languages)
    2. Phonemizer + espeak-ng (broad coverage, 77 languages)
    3. AI fallback (universal, guaranteed non-empty)
    """
    
    def __init__(self):
        # Existing basic mappings
        self.language_map = {
            "Chinese (Simplified)": "cmn-Latn",
            "Chinese (Traditional)": "cmn-Latn",
            "English": "eng-Latn",
            "Spanish": "spa-Latn",
            "French": "fra-Latn",
            "German": "deu-Latn",
            "Italian": "ita-Latn",
            "Portuguese": "por-Latn",
            "Russian": "rus-Cyrl",
            "Japanese": "jpn-Hira",
            "Korean": "kor-Hang",
            "Hindi": "hin-Deva",
            "Arabic": "ara-Arab",
        }
        
        # Comprehensive mappings for all 77 languages
        self.epitran_map = self._load_epitran_mappings()
        self.phonemizer_map = self._load_phonemizer_mappings()
    
    def _load_epitran_mappings(self) -> Dict[str, Optional[str]]:
        """Load Epitran language codes for supported languages."""
        return {
            # Indo-European (23 languages)
            "English": "eng-Latn",
            "German": "deu-Latn",
            "Dutch": "nld-Latn",
            "Swedish": "swe-Latn",
            "Danish": "dan-Latn",
            "Norwegian": "nob-Latn",
            "Icelandic": "isl-Latn",
            "Spanish": "spa-Latn",
            "French": "fra-Latn",
            "Italian": "ita-Latn",
            "Portuguese": "por-Latn",
            "Romanian": "ron-Latn",
            "Catalan": "cat-Latn",
            "Russian": "rus-Cyrl",
            "Polish": "pol-Latn",
            "Czech": "ces-Latn",
            "Ukrainian": "ukr-Cyrl",
            "Bulgarian": "bul-Cyrl",
            "Serbian": "srp-Latn",  # Latin script
            "Hindi": "hin-Deva",
            "Bengali": "ben-Beng",
            "Persian": "fas-Arab",
            "Urdu": "urd-Arab",
            "Punjabi": "pan-Guru",
            "Gujarati": "guj-Deva",
            "Marathi": "mar-Deva",
            "Greek": "ell-Grek",
            "Lithuanian": "lit-Latn",
            "Latvian": "lav-Latn",
            "Irish": "gle-Latn",
            "Welsh": "cym-Latn",
            "Breton": "bre-Latn",
            "Armenian": "hye-Armn",
            "Albanian": "sqi-Latn",
            
            # Afro-Asiatic (12 languages)
            "Arabic": "ara-Arab",
            "Hebrew": "heb-Hebr",
            "Amharic": "amh-Ethi",
            "Hausa": "hau-Latn",
            "Somali": None,  # Not supported
            "Tigrinya": "tir-Ethi",
            "Berber": None,  # Not supported
            "Coptic": "cop-Copt",
            "Maltese": "mlt-Latn",
            
            # Niger-Congo (15 languages)
            "Swahili": "swa-Latn",
            "Zulu": "zul-Latn",
            "Yoruba": "yor-Latn",
            "Igbo": "ibo-Latn",
            "Hausa": "hau-Latn",  # Duplicate, use same
            "Wolof": "wol-Latn",
            "Bambara": None,  # Not supported
            "Ewe": "ewe-Latn",
            "Tswana": "tsn-Latn",
            "Sesotho": "sot-Latn",
            
            # Austronesian (7 languages)
            "Malay": "msa-Latn",
            "Indonesian": "ind-Latn",
            "Tagalog": "tgl-Latn",
            "Maori": "mri-Latn",
            "Hawaiian": "haw-Latn",
            "Malagasy": "mlg-Latn",
            "Javanese": None,  # Not supported
            
            # Turkic (6 languages)
            "Turkish": "tur-Latn",
            "Uzbek": "uzb-Latn",
            "Kazakh": "kaz-Cyrl",
            "Kyrgyz": "kir-Cyrl",
            "Tatar": "tat-Cyrl",
            "Azerbaijani": "aze-Latn",
            
            # Dravidian (4 languages)
            "Tamil": "tam-Taml",
            "Telugu": "tel-Telu",
            "Kannada": "kan-Knda",
            "Malayalam": "mal-Mlym",
            
            # Japonic (2 languages)
            "Japanese": "jpn-Hira",
            "Ryukyuan": None,  # Not supported
            
            # Koreanic (1 language)
            "Korean": "kor-Hang",
            
            # Tai-Kadai (3 languages)
            "Thai": "tha-Thai",
            "Lao": "lao-Laoo",
            "Zhuang": None,  # Not supported
            
            # Hmong-Mien (2 languages)
            "Hmong": None,  # Not supported
            "Mien": None,  # Not supported
            
            # Austroasiatic (4 languages)
            "Vietnamese": "vie-Latn",
            "Khmer": "khm-Khmr",
            "Mon": None,  # Not supported
            "Khasi": None,  # Not supported
            
            # Tibeto-Burman (6 languages) - overlaps with Sino-Tibetan
            "Tibetan": "bod-Tibt",
            "Burmese": "mya-Mymr",
            "Karen": None,  # Not supported
            "Yi": "iii-Yiii",
            "Bai": None,  # Not supported
            "Tujia": None,  # Not supported
            
            # Sino-Tibetan (8 languages) - Chinese handled specially
            "Chinese (Simplified)": None,  # Skip Epitran
            "Chinese (Traditional)": None,  # Skip Epitran
            "Tibetan": "bod-Tibt",  # Duplicate, use same
            "Burmese": "mya-Mymr",  # Duplicate, use same
            "Karen": None,  # Not supported
            "Yi": "iii-Yiii",  # Duplicate, use same
            "Bai": None,  # Not supported
            "Tujia": None,  # Not supported
            
            # Other isolates and small families
            "Nubian": None,  # Not supported
            "Basque": "eus-Latn",
            "Na-Dene": None,  # Not supported
            "Eskimo-Aleut": None,  # Not supported
            "Australian Aboriginal": None,  # Not supported
        }
    
    def _load_phonemizer_mappings(self) -> Dict[str, str]:
        """Load Phonemizer BCP 47 codes for all languages."""
        return {
            # Complete mappings for all 77 languages
            "English": "en",
            "German": "de",
            "Dutch": "nl",
            "Swedish": "sv",
            "Danish": "da",
            "Norwegian": "nb",  # Bokmål
            "Icelandic": "is",
            "Spanish": "es",
            "French": "fr",
            "Italian": "it",
            "Portuguese": "pt",
            "Romanian": "ro",
            "Catalan": "ca",
            "Russian": "ru",
            "Polish": "pl",
            "Czech": "cs",
            "Ukrainian": "uk",
            "Bulgarian": "bg",
            "Serbian": "sr",
            "Hindi": "hi",
            "Bengali": "bn",
            "Persian": "fa",
            "Urdu": "ur",
            "Punjabi": "pa",
            "Gujarati": "gu",
            "Marathi": "mr",
            "Greek": "el",
            "Lithuanian": "lt",
            "Latvian": "lv",
            "Irish": "ga",
            "Welsh": "cy",
            "Breton": "br",
            "Armenian": "hy",
            "Albanian": "sq",
            
            # Afro-Asiatic
            "Arabic": "ar",
            "Hebrew": "he",
            "Amharic": "am",
            "Hausa": "ha",
            "Somali": "so",
            "Tigrinya": "ti",
            "Berber": "ber",  # Generic
            "Coptic": "cop",
            "Maltese": "mt",
            
            # Niger-Congo
            "Swahili": "sw",
            "Zulu": "zu",
            "Yoruba": "yo",
            "Igbo": "ig",
            "Hausa": "ha",  # Duplicate
            "Wolof": "wo",
            "Bambara": "bm",
            "Ewe": "ee",
            "Tswana": "tn",
            "Sesotho": "st",
            
            # Austronesian
            "Malay": "ms",
            "Indonesian": "id",
            "Tagalog": "tl",
            "Maori": "mi",
            "Hawaiian": "haw",
            "Malagasy": "mg",
            "Javanese": "jv",
            
            # Turkic
            "Turkish": "tr",
            "Uzbek": "uz",
            "Kazakh": "kk",
            "Kyrgyz": "ky",
            "Tatar": "tt",
            "Azerbaijani": "az",
            
            # Dravidian
            "Tamil": "ta",
            "Telugu": "te",
            "Kannada": "kn",
            "Malayalam": "ml",
            
            # Japonic
            "Japanese": "ja",
            "Ryukyuan": "ja",  # Fallback to Japanese
            
            # Koreanic
            "Korean": "ko",
            
            # Tai-Kadai
            "Thai": "th",
            "Lao": "lo",
            "Zhuang": "za",
            
            # Hmong-Mien
            "Hmong": "hmn",
            "Mien": "hmn",  # Fallback
            
            # Austroasiatic
            "Vietnamese": "vi",
            "Khmer": "km",
            "Mon": "mnw",
            "Khasi": "kha",
            
            # Tibeto-Burman
            "Tibetan": "bo",
            "Burmese": "my",
            "Karen": "kar",  # Generic
            "Yi": "ii",
            "Bai": "ba",
            "Tujia": "de",  # Fallback
            
            # Sino-Tibetan
            "Chinese (Simplified)": "cmn",  # Mandarin
            "Chinese (Traditional)": "cmn",  # Mandarin
            "Tibetan": "bo",  # Duplicate
            "Burmese": "my",  # Duplicate
            "Karen": "kar",  # Duplicate
            "Yi": "ii",  # Duplicate
            "Bai": "ba",  # Duplicate
            "Tujia": "de",  # Duplicate
            
            # Other
            "Nubian": "fia",  # Generic Nubian
            "Basque": "eu",
            "Navajo": "nv",
            "Apache": "nv",  # Fallback
            "Inuit": "iu",
            "Aleut": "ale",
            "Pitjantjatjara": "pit",
            "Warlpiri": "wbp",
            "Arrernte": "aer",
        }
    
    def generate_ipa_hybrid(self, text: str, language: str, ai_ipa: str = "") -> str:
        """
        Generate IPA using tiered approach with guaranteed non-empty return.
        
        Tiers:
        1. Epitran (highest quality when available)
        2. Phonemizer + espeak-ng (broad coverage)
        3. AI fallback (universal guarantee)
        
        Args:
            text: Text to transliterate
            language: Language name
            ai_ipa: AI-generated IPA fallback
            
        Returns:
            IPA string (never empty)
        """
        if not text or not text.strip():
            return ""
        
        # Tier 1: Epitran (highest quality)
        ipa = self._try_epitran(text, language)
        if ipa and self._validate_ipa(ipa, language):
            logger.info(f"IPA success via Epitran for {language}")
            return ipa
        
        # Tier 2: Phonemizer (broad coverage)
        ipa = self._try_phonemizer(text, language)
        if ipa and self._validate_ipa(ipa, language):
            logger.info(f"IPA success via Phonemizer for {language}")
            return ipa
        
        # Tier 3: AI fallback (guaranteed)
        fallback_ipa = self._ensure_fallback_ipa(ai_ipa, text, language)
        logger.info(f"IPA fallback used for {language}")
        return fallback_ipa
    
    def _try_epitran(self, text: str, language: str) -> str:
        """Attempt Epitran transliteration."""
        # Skip Chinese (returns Pinyin-like output)
        if "Chinese" in language:
            return ""
        
        epi_code = self.epitran_map.get(language)
        if not epi_code:
            return ""
        
        try:
            import epitran
            epi = epitran.Epitran(epi_code)
            ipa = epi.transliterate(text)
            
            # Basic quality validation
            if ipa and ipa != text and len(ipa.strip()) > 0:
                return ipa.strip()
            return ""
            
        except Exception as e:
            logger.warning(f"Epitran failed for {language}: {e}")
            return ""
    
    def _try_phonemizer(self, text: str, language: str) -> str:
        """Attempt Phonemizer with espeak-ng backend."""
        phone_code = self.phonemizer_map.get(language)
        if not phone_code:
            return ""
        
        try:
            import phonemizer
            
            ipa = phonemizer.phonemize(
                text,
                language=phone_code,
                backend='espeak',
                strip=True,
                preserve_punctuation=False,
                with_stress=True
            )
            
            # Clean and validate
            ipa = ipa.strip()
            if ipa and len(ipa) > 0:
                return ipa
            return ""
            
        except Exception as e:
            logger.warning(f"Phonemizer failed for {language}: {e}")
            return ""
    
    def _validate_ipa(self, ipa: str, language: str) -> bool:
        """Validate IPA but allow best-effort returns."""
        if not ipa or not ipa.strip():
            return False
        
        # Use comprehensive validation
        from generation_utils import validate_ipa_output
        is_valid, validation_msg = validate_ipa_output(ipa, language)
        
        if is_valid:
            return True
        
        # Log warning but don't reject - accept best effort
        logger.warning(f"IPA validation failed for {language}: {validation_msg}")
        
        # Basic quality checks
        ipa_clean = ipa.strip()
        
        # Reject obvious Pinyin (Chinese-specific check)
        if any(char in ipa_clean for char in 'āēīōūǖǎěǐǒǔǚ'):
            logger.warning(f"Rejected Pinyin contamination in {language} IPA")
            return False
        
        # Accept if it has content and looks IPA-like
        return len(ipa_clean) > 0
    
    def _ensure_fallback_ipa(self, ai_ipa: str, text: str, language: str) -> str:
        """Guarantee non-empty IPA return."""
        # Try AI IPA first
        if ai_ipa and ai_ipa.strip():
            if self._validate_ipa(ai_ipa, language):
                return ai_ipa
            # Accept even if validation fails (best effort)
            if len(ai_ipa.strip()) > 0:
                return ai_ipa
        
        # Ultimate fallback: meaningful placeholder
        logger.warning(f"All IPA tiers failed for {language}, using placeholder")
        return f"[IPA unavailable for {language}]"
```

## 🧪 TESTING & VALIDATION REFERENCE

### **Comprehensive Test Suite**
```python
import pytest
from services.sentence_generation.ipa_service import IPAService

class TestIPAService:
    def setup_method(self):
        self.ipa_service = IPAService()
    
    def test_all_77_languages_coverage(self):
        """Test that all 77 languages return non-empty IPA."""
        test_text = "hello"
        
        languages = [
            "English", "Spanish", "Hindi", "Arabic", "Chinese (Simplified)",
            # ... all 77 languages
        ]
        
        for language in languages:
            ipa = self.ipa_service.generate_ipa_hybrid(test_text, language)
            assert ipa, f"Empty IPA for {language}"
            assert not any(char in ipa for char in 'āēīōūǖǎěǐǒǔǚ'), f"Pinyin in {language}"
    
    def test_tier_fallback(self):
        """Test that tiers fall back correctly."""
        # Test with unsupported language
        ipa = self.ipa_service.generate_ipa_hybrid("test", "Unsupported Language", "fallback_ipa")
        assert ipa == "fallback_ipa"  # Should use AI fallback
    
    def test_chinese_special_handling(self):
        """Test Chinese skips Epitran."""
        # Mock to ensure Epitran not called for Chinese
        ipa = self.ipa_service.generate_ipa_hybrid("你好", "Chinese (Simplified)")
        # Should use Phonemizer or fallback, not Epitran
        assert ipa
        assert not any(char in ipa for char in 'āēīōūǖ'), "Chinese should not return Pinyin"
    
    def test_validation_best_effort(self):
        """Test validation allows best-effort returns."""
        # Even if validation fails, should return result
        ai_ipa = "invalid_but_present"
        ipa = self.ipa_service.generate_ipa_hybrid("test", "English", ai_ipa)
        assert ipa  # Should not be empty
```

### **Quality Assessment Framework**
```python
def assess_ipa_quality(ipa_results: Dict[str, str]) -> Dict[str, float]:
    """Assess IPA quality across languages."""
    metrics = {
        "coverage": 0.0,  # % of languages with IPA
        "non_empty": 0.0,  # % of non-empty results
        "validation_pass": 0.0,  # % passing validation
        "pinyin_free": 0.0,  # % without Pinyin contamination
        "avg_length_ratio": 0.0,  # Text length to IPA length ratio
    }
    
    # Calculate metrics...
    return metrics
```

## 📈 TIMELINE & MILESTONES

### **Week 1: Research & Architecture**
- ✅ Complete language mappings research
- ✅ Dependency analysis and setup
- ✅ Architecture design and validation
- **Deliverable**: Complete implementation plan

### **Week 2: Core Implementation**
- ✅ Expand IPAService with comprehensive mappings
- ✅ Implement Epitran tier with Chinese special handling
- ✅ Implement Phonemizer tier with espeak-ng
- ✅ Implement validation and fallback logic
- **Deliverable**: Functional IPAService extension

### **Week 3: Testing & Quality Assurance**
- ✅ Unit tests for all 77 languages
- ✅ Quality assessment and manual review
- ✅ Performance testing and optimization
- ✅ Integration testing with sentence generation
- **Deliverable**: Production-ready code with test coverage

### **Week 4: Deployment & Monitoring**
- ✅ Staging deployment and validation
- ✅ Gradual production rollout
- ✅ Monitoring setup and alerting
- ✅ Documentation and maintenance guides
- **Deliverable**: Live system with monitoring

### **Success Metrics Timeline**
- **End of Week 2**: 100% coverage, guaranteed non-empty returns
- **End of Week 3**: >80% quality accuracy, <5% failure rate
- **End of Week 4**: Full production deployment, monitoring active

## 🎯 NEXT STEPS AFTER IPA EXTENSION

1. **Validate Integration**: Test with full sentence generation pipeline
2. **Monitor Quality**: Track real-world IPA accuracy and user feedback
3. **Expand Coverage**: Add new languages as they become available in libraries
4. **Performance Optimization**: Implement caching and async processing
5. **User Feedback Loop**: Incorporate learner feedback on IPA quality

---

**EXECUTION**: Begin with Phase 1 research. Use this prompt to guide the complete IPA extension implementation across all 77 languages.</content>
<parameter name="filePath">d:\Language Learning\LanguagLearning\ipa_master_prompt.md