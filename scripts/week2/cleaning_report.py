import re
import pandas as pd
from text_cleaning import TextCleaner

df = pd.read_csv('data/processed/listing_sample.csv')
cleaner = TextCleaner()
raw = df['remarks']

steps = [
    ('normalize_unicode', cleaner.normalize_unicode),
    ('remove_html', cleaner.remove_html),
    ('normalize_prices', cleaner.normalize_prices),
    ('normalize_measurements', cleaner.normalize_measurements),
    ('expand_abbreviations',
     lambda t: cleaner.expand_abbreviations(cleaner.separate_number_units(t))),
    ('normalize_whitespace', cleaner.normalize_whitespace),
]

print("Listings changed by each step (applied alone to the raw text):")
for name, fn in steps:
    n = (raw != raw.apply(fn)).sum()
    print(f"{name}: {n}")


def window(before, after, width=50):
    i = next((k for k, (a, b) in enumerate(zip(before, after)) if a != b),
             min(len(before), len(after)))
    s = max(0, i - width)
    return before[s:i + width], after[s:i + width]


print("\nExamples where the text itself changed (not whitespace only):")
shown = 0
for b in raw:
    a = cleaner.clean_text(b)
    nb = cleaner.normalize_whitespace(b)
    if a != nb and shown < 5:
        shown += 1
        wb, wa = window(nb, a)
        print(f"\n--- Example {shown} ---")
        print(f"BEFORE: ...{wb}...")
        print(f"AFTER:  ...{wa}...")

print("\nContexts where a standalone 'sf' appears:")
pat = re.compile(r'(?<![A-Za-z])sf(?![A-Za-z])', re.I)
count = 0
for b in raw:
    m = pat.search(b)
    if m and count < 8:
        count += 1
        ctx = b[max(0, m.start() - 40): m.end() + 30].replace('\n', ' ')
        print(f"  ...{ctx}...")