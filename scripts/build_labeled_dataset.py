"""Build a labeled entity dataset (with character spans) from MLS structured fields.

A label is created ONLY when the remarks text itself states a value that agrees
with the structured MLS field. If the text states a different value, the field
is flagged as a conflict and excluded from scoring (needs manual review).
"""
import json
import re

import pandas as pd

SRC = 'data/processed/listing_sample_cleaned.csv'
OUT = 'data/processed/labeled_dataset.json'
N_ROWS = 250
N_DEV = 150  # remaining rows become the test split

WORDS = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6,
         'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10, 'eleven': 11, 'twelve': 12}
# Number token: digits (optionally decimal) or an English number word.
# The lookbehind blocks "4/5 bedroom" and words like "someone".
NUM = r'(?<![A-Za-z0-9./])(\d+(?:\.\d+)?|' + '|'.join(WORDS) + r')'

PATTERNS = {
    'bedrooms': re.compile(NUM + r'[\s-]*bed(?:room)?s?(?![A-Za-z])', re.I),
    'bathrooms': re.compile(NUM + r'[\s-]*(?:full[\s-]+)?bath(?:room)?s?(?![A-Za-z])', re.I),
    'sqft': re.compile(r'(?<![\d,.])(\d{3,5})\s*square\s*feet', re.I),
}
PRICE_RE = re.compile(r'\$?\d[\d,]{4,}')


def to_number(token):
    t = token.lower()
    return float(WORDS[t]) if t in WORDS else float(t)


def find_numeric(text, label, target):
    """Return (entity, conflict). Entity = first mention equal to the MLS value."""
    mentions = []
    for m in PATTERNS[label].finditer(text):
        mentions.append((to_number(m.group(1)), m))
    for value, m in mentions:
        if abs(value - target) < 1e-9:
            return {'label': label, 'value': value, 'start': m.start(),
                    'end': m.end(), 'text': m.group(0)}, False
    return None, bool(mentions)  # mentions exist but none agree -> conflict


def find_price(text, target):
    dollar_amounts = []
    for m in PRICE_RE.finditer(text):
        raw = m.group(0)
        value = int(raw.replace('$', '').replace(',', ''))
        if abs(value - target) < 1:
            return {'label': 'price', 'value': float(value), 'start': m.start(),
                    'end': m.end(), 'text': raw}, False
        if raw.startswith('$') and value >= 50000:
            dollar_amounts.append(value)
    return None, bool(dollar_amounts)


def build_row(i, row):
    text = row['remarks_cleaned']
    entities, conflicts = [], []

    for label, col in [('bedrooms', 'beds'), ('bathrooms', 'baths'), ('sqft', 'sqft')]:
        if col not in row or pd.isna(row[col]):
            continue
        ent, conflict = find_numeric(text, label, float(row[col]))
        if ent:
            entities.append(ent)
        elif conflict:
            conflicts.append(label)

    if 'price' in row and not pd.isna(row['price']):
        ent, conflict = find_price(text, float(row['price']))
        if ent:
            entities.append(ent)
        elif conflict:
            conflicts.append('price')

    return {'id': i, 'text': text, 'entities': entities, 'conflicts': conflicts}


if __name__ == '__main__':
    df = pd.read_csv(SRC).dropna(subset=['remarks_cleaned'])
    sample = df.sample(n=N_ROWS, random_state=7).reset_index(drop=True)

    rows = []
    for i, (_, row) in enumerate(sample.iterrows()):
        item = build_row(i, row)
        item['split'] = 'dev' if i < N_DEV else 'test'
        rows.append(item)

    with open(OUT, 'w') as f:
        json.dump(rows, f, indent=2)

    print(f"Saved {len(rows)} rows to {OUT}")
    for label in ['bedrooms', 'bathrooms', 'price', 'sqft']:
        n_ent = sum(1 for r in rows for e in r['entities'] if e['label'] == label)
        n_conf = sum(1 for r in rows if label in r['conflicts'])
        print(f"  {label}: {n_ent} labeled, {n_conf} conflicts (excluded)")