import pandas as pd
import glob

files = glob.glob('data/*.csv')
all_colls = set()
for f in sorted(files):
    df = pd.read_csv(f)
    c = set(df['Institute'].dropna().unique())
    print(f'{f}: {len(c)} colleges')
    all_colls.update(c)
print(f'Total unique across all years: {len(all_colls)}')
