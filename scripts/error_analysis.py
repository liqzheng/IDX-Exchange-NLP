"""Group extraction errors by field and type, and print the relevant sentences.

Usage: python scripts/error_analysis.py [dev|test] [field] [max_examples]
Error types: MISSED (gold present, pred None), SPURIOUS (gold None, pred present),
             WRONG (both present but different).
"""
import json
import re
import sys
import textwrap
from collections import Counter

split = sys.argv[1] if len(sys.argv) > 1 else 'dev'
only_field = sys.argv[2] if len(sys.argv) > 2 else None
max_examples = int(sys.argv[3]) if len(sys.argv) > 3 else 6

KEYWORD = {
    'bedrooms': r'bed',
    'bathrooms': r'bath',
    'price': r'\$|\d{5,}|million',
    'sqft': r'square|sq\.? ?ft|sqft|\bsf\b',
}

with open(f'data/processed/errors_{split}.json') as f:
    errors = json.load(f)


def error_type(e):
    if e['gold'] is not None and e['pred'] is None:
        return 'MISSED'
    if e['gold'] is None:
        return 'SPURIOUS'
    return 'WRONG'


def relevant_sentences(text, field):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s for s in sentences if re.search(KEYWORD[field], s, re.I)][:2]


print(Counter((e['field'], error_type(e)) for e in errors))

groups = {}
for e in errors:
    if only_field and e['field'] != only_field:
        continue
    groups.setdefault((e['field'], error_type(e)), []).append(e)

for (field, etype), items in sorted(groups.items()):
    print('\n' + '#' * 80)
    print(f"{field} / {etype}: {len(items)} errors")
    for e in items[:max_examples]:
        print(f"\n  id {e['id']}  gold={e['gold']}  pred={e['pred']}")
        for s in relevant_sentences(e['text'], field):
            print(textwrap.fill(s, width=100, initial_indent='    > ', subsequent_indent='      '))