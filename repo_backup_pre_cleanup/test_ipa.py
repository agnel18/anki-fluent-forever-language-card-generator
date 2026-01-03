#!/usr/bin/env python3
import sys
sys.path.append('streamlit_app')
from generation_utils import validate_ipa_output

print("Testing IPA validation...")

# Test Pinyin (should be rejected)
pinyin = 'wǒmen xǐhuān chī zhōngcān'
is_valid, result = validate_ipa_output(pinyin, 'zh')
print(f'Pinyin test: valid={is_valid}, result="{result}"')

# Test another Pinyin example
pinyin2 = 'nǐ hǎo'
is_valid2, result2 = validate_ipa_output(pinyin2, 'zh')
print(f'Pinyin2 test: valid={is_valid2}, result="{result2}"')

# Test what should be valid IPA (without Pinyin tone marks)
valid_ipa = 'wə̯mən ɕí xwɑn tʂʰə̯ ʈʂʊŋ tsʰɑn'
is_valid3, result3 = validate_ipa_output(valid_ipa, 'zh')
print(f'Valid IPA test: valid={is_valid3}, result="{result3}"')

# Test the actual output from the app
actual_output = 'uǒ ​ʃì zhōng guó rén'
is_valid4, result4 = validate_ipa_output(actual_output, 'zh')
print(f'Actual app output test: valid={is_valid4}, result="{result4}"')