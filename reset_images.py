from pathlib import Path
import pandas as pd

track = Path('109 Languages Frequency Word Lists/Malayalam (ML).xlsx')
work = Path('FluentForever_Malayalam_Perfect/working_data.xlsx')
img_dir = Path('FluentForever_Malayalam_Perfect/images')

img_dir.mkdir(parents=True, exist_ok=True)

df_track = pd.read_excel(track)
df_work = pd.read_excel(work)

# Ensure columns
for col in ['Sentences','Audio','Images']:
    if col not in df_track.columns:
        df_track[col] = 0

# Reset image column in working data based on actual files
for idx, row in df_work.iterrows():
    fname = f"{row['File Name']}.jpg"
    fpath = img_dir / fname
    if fpath.exists() and fpath.stat().st_size > 1500:
        df_work.at[idx, 'Image'] = f"<img src=\"{fname}\">"
    else:
        df_work.at[idx, 'Image'] = ""

df_work.to_excel(work, index=False)

# Recompute image counts from files
counts = {}
for f in img_dir.glob('*.jpg'):
    if f.stat().st_size <= 1500:
        continue
    try:
        freq = int(f.name.split('_')[0])
    except Exception:
        continue
    counts[freq] = counts.get(freq, 0) + 1

for idx in df_track.index:
    freq_num = idx + 1
    df_track.at[idx, 'Images'] = counts.get(freq_num, 0)

df_track.to_excel(track, index=False)
print('Reset images based on actual files; counts updated.')
