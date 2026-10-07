"""Evaluate EntityExtractor on the labeled dataset: precision / recall / F1 per field.

Usage: python scripts/evaluate_extractor.py [dev|test]
Counting rules (value-level, exact match):
  gold present, pred equal       -> TP
  gold present, pred different   -> FP and FN
  gold present, pred missing     -> FN
  gold missing, pred present     -> FP
Fields flagged as 'conflicts' are skipped. price/sqft are only scored on rows
that were hand-reviewed (ps_done).
"""
import json
import sys

from entity_extractor import EntityExtractor

PATH = 'data/processed/labeled_dataset.json'
FIELDS = ['bedrooms', 'bathrooms', 'price', 'sqft']
HAND_LABELED = {'price', 'sqft'}


def prf(tp, fp, fn):
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    f = 2 * p * r / (p + r) if p + r else 0.0
    return p, r, f


if __name__ == '__main__':
    split = sys.argv[1] if len(sys.argv) > 1 else 'dev'
    with open(PATH) as f:
        rows = [r for r in json.load(f) if r['split'] == split]

    extractor = EntityExtractor()
    counts = {f: {'tp': 0, 'fp': 0, 'fn': 0} for f in FIELDS}
    errors = []

    for row in rows:
        pred = extractor.extract_all(row['text'])
        gold = {e['label']: e['value'] for e in row['entities']}
        for field in FIELDS:
            if field in row['conflicts']:
                continue
            if field in HAND_LABELED and not row.get('ps_done'):
                continue
            g, p = gold.get(field), pred[field]
            c = counts[field]
            if g is not None and p is not None and float(p) == float(g):
                c['tp'] += 1
                continue
            if p is not None:
                c['fp'] += 1
            if g is not None:
                c['fn'] += 1
            if p is not None or g is not None:
                errors.append({'id': row['id'], 'field': field, 'gold': g, 'pred': p,
                               'text': row['text']})

    print(f"Split: {split} ({len(rows)} rows)")
    print(f"{'field':<10} {'P':>6} {'R':>6} {'F1':>6}   TP  FP  FN")
    total = {'tp': 0, 'fp': 0, 'fn': 0}
    for field in FIELDS:
        c = counts[field]
        p, r, f1 = prf(c['tp'], c['fp'], c['fn'])
        print(f"{field:<10} {p:6.2f} {r:6.2f} {f1:6.2f}  {c['tp']:3d} {c['fp']:3d} {c['fn']:3d}")
        for k in total:
            total[k] += c[k]
    p, r, f1 = prf(**total)
    print(f"{'micro':<10} {p:6.2f} {r:6.2f} {f1:6.2f}  {total['tp']:3d} {total['fp']:3d} {total['fn']:3d}")

    out = f'data/processed/errors_{split}.json'
    with open(out, 'w') as f:
        json.dump(errors, f, indent=2)
    print(f"\n{len(errors)} errors saved to {out}")