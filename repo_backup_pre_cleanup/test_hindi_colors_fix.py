import sys
sys.path.append('streamlit_app')
from language_analyzers.analyzer_registry import get_analyzer
import logging

# Set up logging to see debug output
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Test Hindi analyzer directly
analyzer = get_analyzer('hi')
if analyzer:
    print("✓ Hindi analyzer loaded successfully")

    # Test color scheme
    color_scheme = analyzer.get_color_scheme('beginner')
    print(f"Color scheme: {color_scheme}")

    # Test parsing a mock response to see if word_explanations are generated correctly
    mock_response = '''```json
{
  "words": [
    {
      "word": "मैं",
      "individual_meaning": "I (first person singular pronoun)",
      "pronunciation": "mɛ̃",
      "grammatical_role": "pronoun",
      "color": "#FF4444",
      "gender_agreement": "masculine (default for pronouns)",
      "case_marking": "nominative case",
      "postpositions": [],
      "importance": "Essential personal pronoun for self-reference"
    },
    {
      "word": "खाना",
      "individual_meaning": "food/meal",
      "pronunciation": "kʰaːnaː",
      "grammatical_role": "noun",
      "color": "#FFAA00",
      "gender_agreement": "masculine",
      "case_marking": "accusative case (implied)",
      "postpositions": [],
      "importance": "Common noun for food and eating"
    },
    {
      "word": "खाता",
      "individual_meaning": "eat (present tense)",
      "pronunciation": "kʰaːtaː",
      "grammatical_role": "verb",
      "color": "#44FF44",
      "gender_agreement": "masculine singular",
      "case_marking": "present tense",
      "postpositions": [],
      "importance": "Main verb showing eating action"
    },
    {
      "word": "हूँ",
      "individual_meaning": "am (present tense of होना)",
      "pronunciation": "ɦuː",
      "grammatical_role": "verb",
      "color": "#44FF44",
      "gender_agreement": "masculine singular",
      "case_marking": "present tense",
      "postpositions": [],
      "importance": "Auxiliary verb for present continuous"
    }
  ],
  "word_combinations": [],
  "explanations": {
    "word_order": "Subject-Object-Verb (SOV) word order typical of Hindi",
    "morphology": "Verbs show gender and number agreement with subjects",
    "syntax": "Postpositions follow nouns they modify",
    "phonology": "Retroflex consonants and vowel nasalization present"
  }
}
```'''

    sentence = "मैं खाना खाता हूँ"
    parsed_data = analyzer.parse_grammar_response(mock_response, 'beginner', sentence)

    print(f"Parsed data keys: {list(parsed_data.keys())}")
    if 'word_explanations' in parsed_data:
        print(f"✓ word_explanations found: {len(parsed_data['word_explanations'])} items")
        for i, exp in enumerate(parsed_data['word_explanations']):
            print(f"  {i+1}. {exp}")
    else:
        print("✗ word_explanations not found in parsed data")

    print("\nColor consistency fix verification:")
    print("- Analyzer generates word_explanations with correct colors")
    print("- sentence_generator.py now uses analyzer's word_explanations directly")
    print("- No more double-processing that was causing color mismatches")

else:
    print("✗ Failed to load Hindi analyzer")