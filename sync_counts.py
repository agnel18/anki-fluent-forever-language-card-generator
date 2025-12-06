from pathlib import Path
import pandas as pd
from collections import defaultdict

track = Path('109 Languages Frequency Word Lists/Malayalam (ML).xlsx')
work = Path('FluentForever_Malayalam_Perfect/working_data.xlsx')

df_track = pd.read_excel(track)
df_work = pd.read_excel(work)

for col in ['Sentences', 'Audio', 'Images']:
    if col not in df_track.columns:
        df_track[col] = 0

counts = defaultdict(lambda: {'sent': 0, 'audio': 0, 'img': 0})
for _, r in df_work.iterrows():
    fn = str(r['File Name'])
    try:
        freq = int(fn.split('_')[0])
    except Exception:
        continue
    counts[freq]['sent'] += 1
    if isinstance(r.get('Sound', ''), str) and r['Sound']:
        counts[freq]['audio'] += 1
    if isinstance(r.get('Image', ''), str) and r['Image']:
        counts[freq]['img'] += 1

for freq, c in counts.items():
    idx = freq - 1
    if idx < len(df_track):
        df_track.at[idx, 'Sentences'] = max(df_track.at[idx, 'Sentences'], c['sent'])
        df_track.at[idx, 'Audio'] = max(df_track.at[idx, 'Audio'], c['audio'])
        df_track.at[idx, 'Images'] = max(df_track.at[idx, 'Images'], c['img'])

df_track.to_excel(track, index=False)
print(f"Synced counts for {len(counts)} words")
