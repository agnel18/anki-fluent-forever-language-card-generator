"""Check how many words got processed and API usage"""
import pandas as pd

df = pd.read_excel('109 Languages Frequency Word Lists/Malayalam (ML).xlsx')
completed = df[df['Sentences'] > 0]

print(f'\n⚠️  QUOTA DAMAGE ASSESSMENT:\n')
print(f'Words with sentences: {len(completed)}')
print(f'Total API requests used: ~{len(completed) * 10}')
print(f'Daily limit: 1,500')
print(f'\n📊 First 20 words processed:')
print(completed[['Malayalam Word', 'Sentences']].head(20).to_string(index=False))

if len(completed) > 20:
    print(f'\n... and {len(completed) - 20} more words')
