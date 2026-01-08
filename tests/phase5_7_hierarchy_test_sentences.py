# Phase 5.7: Grammatical Analysis Order Standardization - Test Sentences
# Hindi Analyzer Hierarchical Categorization Validation
# Created: January 4, 2026

"""
Test sentences designed to validate children-first hierarchical categorization.
Each sentence contains words that could be classified in multiple grammatical categories.
The hierarchical order should prevent concept overlap and ensure correct classification.

CRITICAL TEST CASES:
1. Auxiliary verbs vs main verbs (auxiliary_verb → verb)
2. Postpositions vs prepositions (postposition → preposition)
3. Particles vs conjunctions (particle → conjunction)
4. Ideophones vs interjections (ideophone → interjection)
5. Specific pronoun subtypes vs general pronoun
6. Numeral adjectives vs general adjectives
"""

# Test Case 1: Auxiliary Verb vs Main Verb
# "राम खाना खा रहा है" (Ram is eating food)
# Expected: "रहा" = auxiliary_verb (not verb)
TEST_SENTENCE_1 = "राम खाना खा रहा है"

# Test Case 2: Postposition vs Preposition
# "मैं स्कूल से आया" (I came from school)
# Expected: "से" = postposition (not preposition)
TEST_SENTENCE_2 = "मैं स्कूल से आया"

# Test Case 3: Particle vs Conjunction
# "वह पढ़ता है तो समझता है" (He reads, then understands)
# Expected: "तो" = particle (not conjunction)
TEST_SENTENCE_3 = "वह पढ़ता है तो समझता है"

# Test Case 4: Ideophone vs Interjection
# "दरवाजा धड़ाम बंद हुआ" (The door slammed shut)
# Expected: "धड़ाम" = ideophone (not interjection)
TEST_SENTENCE_4 = "दरवाजा धड़ाम बंद हुआ"

# Test Case 5: Specific Pronoun Subtypes
# "यह मेरा पुस्तक है, वह तुम्हारा है" (This is my book, that is yours)
# Expected: "यह" = demonstrative_pronoun, "वह" = demonstrative_pronoun
TEST_SENTENCE_5 = "यह मेरा पुस्तक है, वह तुम्हारा है"

# Test Case 6: Numeral Adjective vs General Adjective
# "दो लड़के खेल रहे हैं" (Two boys are playing)
# Expected: "दो" = numeral_adjective (not adjective)
TEST_SENTENCE_6 = "दो लड़के खेल रहे हैं"

# Test Case 7: Echo Word
# "खाना-वाना तैयार है" (Food and stuff is ready)
# Expected: "वाना" = echo_word
TEST_SENTENCE_7 = "खाना-वाना तैयार है"

# Test Case 8: Onomatopoeia
# "घड़ी टिक-टिक कर रही है" (The clock is ticking)
# Expected: "टिक-टिक" = onomatopoeia
TEST_SENTENCE_8 = "घड़ी टिक-टिक कर रही है"

# Test Case 9: Reflexive Pronoun
# "राम खुद खाना खाता है" (Ram eats food himself)
# Expected: "खुद" = reflexive_pronoun
TEST_SENTENCE_9 = "राम खुद खाना खाता है"

# Test Case 10: Relative Pronoun
# "जो लड़का पढ़ता है वह सफल होता है" (The boy who studies becomes successful)
# Expected: "जो" = relative_pronoun, "वह" = demonstrative_pronoun
TEST_SENTENCE_10 = "जो लड़का पढ़ता है वह सफल होता है"

# Test Case 11: Interrogative Pronoun
# "कौन आया है?" (Who has come?)
# Expected: "कौन" = interrogative_pronoun
TEST_SENTENCE_11 = "कौन आया है?"

# Test Case 12: Indefinite Pronoun
# "कोई लड़का आया है" (Some boy has come)
# Expected: "कोई" = indefinite_pronoun
TEST_SENTENCE_12 = "कोई लड़का आया है"

# Test Case 13: Complex Auxiliary Construction
# "मैं जा रहा था" (I was going)
# Expected: "रहा" = auxiliary_verb, "था" = auxiliary_verb
TEST_SENTENCE_13 = "मैं जा रहा था"

# Test Case 14: Multiple Postpositions
# "मैं घर पर था" (I was at home)
# Expected: "पर" = postposition
TEST_SENTENCE_14 = "मैं घर पर था"

# Test Case 15: Particle in Question
# "क्या आप जा रहे हैं?" (Are you going?)
# Expected: "क्या" = particle (question particle)
TEST_SENTENCE_15 = "क्या आप जा रहे हैं?"

# Test Case 16: Mixed Categories
# "यह किताब मेरी है, वह तुम्हारी है" (This book is mine, that is yours)
# Expected: "यह" = demonstrative_pronoun, "वह" = demonstrative_pronoun, "मेरी" = possessive adjective
TEST_SENTENCE_16 = "यह किताब मेरी है, वह तुम्हारी है"

# Test Case 17: Honorific with Auxiliary
# "आप खाना खा रहे हैं" (You are eating food - honorific)
# Expected: "रहे" = auxiliary_verb
TEST_SENTENCE_17 = "आप खाना खा रहे हैं"

# Test Case 18: Conjunction vs Particle
# "या तो पढ़ो या सो जाओ" (Either study or go to sleep)
# Expected: "या" = conjunction, "तो" = particle
TEST_SENTENCE_18 = "या तो पढ़ो या सो जाओ"

# Test Case 19: Ideophone in Action
# "बिजली चमक चमक कर रही है" (Lightning is flashing)
# Expected: "चमक" = ideophone
TEST_SENTENCE_19 = "बिजली चमक चमक कर रही है"

# Test Case 20: Complex Sentence with Multiple Overlaps
# "जो लड़का खाना खा रहा है वह मेरा भाई है" (The boy who is eating food is my brother)
# Expected: "जो" = relative_pronoun, "रहा" = auxiliary_verb, "वह" = demonstrative_pronoun
TEST_SENTENCE_20 = "जो लड़का खाना खा रहा है वह मेरा भाई है"

# Collection of all test sentences for batch testing
TEST_SENTENCES = [
    TEST_SENTENCE_1, TEST_SENTENCE_2, TEST_SENTENCE_3, TEST_SENTENCE_4, TEST_SENTENCE_5,
    TEST_SENTENCE_6, TEST_SENTENCE_7, TEST_SENTENCE_8, TEST_SENTENCE_9, TEST_SENTENCE_10,
    TEST_SENTENCE_11, TEST_SENTENCE_12, TEST_SENTENCE_13, TEST_SENTENCE_14, TEST_SENTENCE_15,
    TEST_SENTENCE_16, TEST_SENTENCE_17, TEST_SENTENCE_18, TEST_SENTENCE_19, TEST_SENTENCE_20
]

# Expected classifications for validation
EXPECTED_CLASSIFICATIONS = {
    # Test 1: Auxiliary verb
    "रहा": "auxiliary_verb",

    # Test 2: Postposition
    "से": "postposition",

    # Test 3: Particle
    "तो": "particle",

    # Test 4: Ideophone
    "धड़ाम": "ideophone",

    # Test 5: Demonstrative pronouns
    "यह": "demonstrative_pronoun",
    "वह": "demonstrative_pronoun",

    # Test 6: Numeral adjective
    "दो": "numeral_adjective",

    # Test 7: Echo word
    "वाना": "echo_word",

    # Test 8: Onomatopoeia
    "टिक-टिक": "onomatopoeia",

    # Test 9: Reflexive pronoun
    "खुद": "reflexive_pronoun",

    # Test 10: Relative and demonstrative pronouns
    "जो": "relative_pronoun",

    # Test 11: Interrogative pronoun
    "कौन": "interrogative_pronoun",

    # Test 12: Indefinite pronoun
    "कोई": "indefinite_pronoun",

    # Test 13: Auxiliary verbs
    "था": "auxiliary_verb",

    # Test 14: Postposition
    "पर": "postposition",

    # Test 15: Question particle
    "क्या": "particle",

    # Test 17: Auxiliary verb (honorific)
    "रहे": "auxiliary_verb",

    # Test 18: Conjunction and particle
    "या": "conjunction",

    # Test 19: Ideophone
    "चमक": "ideophone",

    # Test 20: Multiple categories
    # "रहा" already covered above
}