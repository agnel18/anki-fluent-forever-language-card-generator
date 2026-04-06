"""Hungarian response parser tests."""

import json
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from languages.hungarian.domain.hu_config import HuConfig
from languages.hungarian.infrastructure.hu_fallbacks import HuFallbacks
from languages.hungarian.domain.hu_response_parser import HuResponseParser


def _make_parser():
    config = HuConfig()
    fallbacks = HuFallbacks(config)
    return HuResponseParser(config, fallbacks)


def test_parser_creation():
    parser = _make_parser()
    assert parser is not None


def test_parse_valid_json():
    parser = _make_parser()
    response = json.dumps({
        "sentence": "A fiú almát eszik.",
        "words": [
            {"word": "A", "grammatical_role": "definite_article", "individual_meaning": "the"},
            {"word": "fiú", "grammatical_role": "noun", "individual_meaning": "boy"},
            {"word": "almát", "grammatical_role": "noun", "case": "accusative", "individual_meaning": "apple (accusative)"},
            {"word": "eszik", "grammatical_role": "verb", "conjugation_type": "indefinite", "individual_meaning": "eats (indefinite conjugation)"}
        ],
        "explanations": {
            "overall_structure": "SVO with accusative object",
            "key_features": "Accusative -t suffix",
            "complexity_notes": "Beginner level"
        }
    })

    result = parser.parse_response(response, "beginner", "A fiú almát eszik.")
    assert 'word_explanations' in result
    assert len(result['word_explanations']) == 4
    assert result['word_explanations'][0][0] == 'A'
    assert result['word_explanations'][3][0] == 'eszik'


def test_parse_markdown_json():
    parser = _make_parser()
    response = '''Here is the analysis:
```json
{
    "sentence": "Olvasok egy könyvet.",
    "words": [
        {"word": "Olvasok", "grammatical_role": "verb", "conjugation_type": "indefinite", "individual_meaning": "I read (indefinite)"},
        {"word": "egy", "grammatical_role": "indefinite_article", "individual_meaning": "a/an"},
        {"word": "könyvet", "grammatical_role": "noun", "case": "accusative", "individual_meaning": "book (accusative)"}
    ],
    "explanations": {"overall_structure": "VO pattern", "key_features": "Indefinite conjugation", "complexity_notes": "Beginner"}
}
```'''

    result = parser.parse_response(response, "beginner", "Olvasok egy könyvet.")
    assert 'word_explanations' in result
    assert len(result['word_explanations']) == 3


def test_parse_invalid_json_falls_back():
    parser = _make_parser()
    result = parser.parse_response("totally invalid", "beginner", "A fiú almát eszik.")
    assert isinstance(result, dict)
    assert 'word_explanations' in result
    assert result.get('is_fallback', False) is True


def test_parse_batch_response():
    parser = _make_parser()
    batch_response = json.dumps({
        "batch_results": [
            {
                "sentence": "A fiú almát eszik.",
                "words": [
                    {"word": "A", "grammatical_role": "definite_article", "individual_meaning": "the"},
                    {"word": "fiú", "grammatical_role": "noun", "individual_meaning": "boy"},
                    {"word": "almát", "grammatical_role": "noun", "case": "accusative", "individual_meaning": "apple (acc)"},
                    {"word": "eszik", "grammatical_role": "verb", "individual_meaning": "eats"}
                ],
                "explanations": {"overall_structure": "SVO", "key_features": "Accusative"}
            },
            {
                "sentence": "Olvasok egy könyvet.",
                "words": [
                    {"word": "Olvasok", "grammatical_role": "verb", "individual_meaning": "I read"},
                    {"word": "egy", "grammatical_role": "indefinite_article", "individual_meaning": "a/an"},
                    {"word": "könyvet", "grammatical_role": "noun", "individual_meaning": "book (acc)"}
                ],
                "explanations": {"overall_structure": "VO", "key_features": "Indefinite"}
            }
        ]
    })

    results = parser.parse_batch_response(
        batch_response,
        ["A fiú almát eszik.", "Olvasok egy könyvet."],
        "beginner"
    )
    assert len(results) == 2
    assert len(results[0]['word_explanations']) == 4
    assert len(results[1]['word_explanations']) == 3


def test_parse_batch_as_list():
    parser = _make_parser()
    batch_response = json.dumps([
        {
            "sentence": "A macska alszik.",
            "words": [
                {"word": "A", "grammatical_role": "definite_article", "individual_meaning": "the"},
                {"word": "macska", "grammatical_role": "noun", "individual_meaning": "cat"},
                {"word": "alszik", "grammatical_role": "verb", "individual_meaning": "sleeps"}
            ],
            "explanations": {"overall_structure": "SV", "key_features": "Basic"}
        }
    ])

    results = parser.parse_batch_response(batch_response, ["A macska alszik."], "beginner")
    assert len(results) == 1


def test_hungarian_explanation_includes_case():
    parser = _make_parser()
    response = json.dumps({
        "sentence": "A házban lakom.",
        "words": [
            {"word": "A", "grammatical_role": "definite_article", "individual_meaning": "the"},
            {"word": "házban", "grammatical_role": "noun", "case": "inessive", "individual_meaning": "in the house", "vowel_harmony": "back"},
            {"word": "lakom", "grammatical_role": "verb", "conjugation_type": "indefinite", "individual_meaning": "I live"}
        ],
        "explanations": {"overall_structure": "Location + Verb", "key_features": "Inessive case"}
    })

    result = parser.parse_response(response, "intermediate", "A házban lakom.")
    # Check the explanation for házban includes case info
    word_exps = result['word_explanations']
    hazban_exp = [e for e in word_exps if e[0] == 'házban'][0]
    assert 'inessive' in hazban_exp[3].lower() or 'case' in hazban_exp[3].lower()


def test_hungarian_explanation_includes_conjugation():
    parser = _make_parser()
    response = json.dumps({
        "sentence": "Olvasom a könyvet.",
        "words": [
            {"word": "Olvasom", "grammatical_role": "verb", "conjugation_type": "definite", "tense": "present", "individual_meaning": "I read (it)"},
            {"word": "a", "grammatical_role": "definite_article", "individual_meaning": "the"},
            {"word": "könyvet", "grammatical_role": "noun", "case": "accusative", "individual_meaning": "book (accusative)"}
        ],
        "explanations": {"overall_structure": "VOS", "key_features": "Definite conjugation"}
    })

    result = parser.parse_response(response, "intermediate", "Olvasom a könyvet.")
    word_exps = result['word_explanations']
    olvasom_exp = [e for e in word_exps if e[0] == 'Olvasom'][0]
    assert 'definite' in olvasom_exp[3].lower() or 'conjugation' in olvasom_exp[3].lower()
