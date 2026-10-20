"""Evaluate entity extraction: precision / recall / F1 per entity."""
import json
import sys
from collections import Counter

from entity_extractor import EntityExtractor

ENTITIES = ['bedrooms', 'bathrooms', 'price', 'sqft']


def main(split='dev'):
    with open('data/processed/labeled_dataset.json') as f:
        rows = [r for r in json.load(f) if r['split'] == split]

    extractor = EntityExtractor()
    tp, fp, fn = Counter(), Counter(), Counter()

    for row in rows:
        pred = extractor.extract_all(row['text'])
        gold = {e['label']: e['value'] for e in row['entities']}

        for label in ENTITIES:
            # skip rows where the text and MLS data disagree
            if label in row.get('conflicts', []):
                continue
            # price / sqft are only scored on hand-labeled rows
            if label in ('price', 'sqft') and not row.get('ps_done'):
                continue

            g, p = gold.get(label), pred.get(label)
            if g is not None and p == g:
                tp[label] += 1
            elif g is not None and p is None:
                fn[label] += 1
            elif g is None and p is not None:
                fp[label] += 1
            elif g is not None and p is not None:  # wrong value
                fp[label] += 1
                fn[label] += 1

    print(f'split = {split}, rows = {len(rows)}')
    print(f'{"entity":<10} {"prec":>6} {"recall":>6} {"f1":>6} {"tp":>4} {"fp":>4} {"fn":>4}')
    for label in ENTITIES + ['micro']:
        if label == 'micro':
            t, f_p, f_n = sum(tp.values()), sum(fp.values()), sum(fn.values())
        else:
            t, f_p, f_n = tp[label], fp[label], fn[label]
        prec = t / (t + f_p) if t + f_p else 0
        rec = t / (t + f_n) if t + f_n else 0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0
        print(f'{label:<10} {prec:>6.2f} {rec:>6.2f} {f1:>6.2f} {t:>4} {f_p:>4} {f_n:>4}')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'dev')

