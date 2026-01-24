import os
import re

def search_all_files(directory, patterns, exclude_dirs=None, exclude_extensions=None):
    results = {}
    exclude_dirs = exclude_dirs or ['.venv', '__pycache__', '.git', 'node_modules', 'backup_pre_google_migration', '.pytest_cache', 'build', 'dist']
    exclude_extensions = exclude_extensions or ['.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe', '.bin']

    for root, dirs, files in os.walk(directory):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            # Skip excluded file extensions
            if any(file.endswith(ext) for ext in exclude_extensions):
                continue

            filepath = os.path.join(root, file)

            try:
                # Try to read as text, skip binary files
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    for pattern in patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        if matches:
                            if filepath not in results:
                                results[filepath] = []
                            results[filepath].extend([(pattern, match) for match in matches])
            except Exception:
                # Skip files that can't be read as text
                continue

    return results

# Comprehensive patterns to check for legacy references
patterns = [
    r'\bgroq\b',
    r'\bpixabay\b',
    r'\bazure\b',
    r'\bedge.*tts\b',
    r'\bgroq_.*calls?\b',
    r'\bpixabay_.*calls?\b',
    r'\bgroq_.*tokens?\b',
    r'\bgroq_.*api\b',
    r'\bpixabay_.*api\b',
    r'\bgroq.*key\b',
    r'\bpixabay.*key\b',
    r'\bazure.*tts\b',
    r'\bedge.*tts\b',
    r'\bopenai\b',
    r'\banthropic\b',
    r'\bclaude\b',
    r'\bgpt\b',
    r'\bchatgpt\b'
]

print('🔍 COMPREHENSIVE SEARCH: ALL FILES (excluding .venv, build artifacts)')
print('=' * 70)
results = search_all_files('.', patterns)

if results:
    print('❌ FOUND LEGACY REFERENCES:')
    for filepath, matches in sorted(results.items()):
        print(f'\n📁 {filepath}:')
        unique_matches = list(set(matches))  # Remove duplicates
        for pattern, match in unique_matches:
            print(f'  🔍 {pattern}: "{match}"')
    print(f'\n⚠️  Total files with issues: {len(results)}')
else:
    print('✅ NO LEGACY REFERENCES FOUND!')
    print('The entire codebase (all file types) appears to be fully migrated to Google services.')