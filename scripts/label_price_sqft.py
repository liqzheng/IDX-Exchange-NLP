"""Hand-label price and sqft for rows whose text contains a candidate number.

Rows with no candidate (no 'square feet', no '$', no 5+ digit number) are
marked as having no price / sqft automatically.
Rule: price = the listing/asking price only (NOT upgrades, HOA, $/sqft, zip, street number).
      sqft  = living area of the home only (NOT lot size).
"""
import json
import re
import textwrap

PATH = 'data/processed/labeled_dataset.json'
CANDIDATE = re.compile(r'square\s*feet|\$|(?<![\d,.])\d{5,}', re.I)


def candidate_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    # dict.fromkeys removes duplicated sentences but keeps order
    return list(dict.fromkeys(s for s in sentences if CANDIDATE.search(s)))


def ask(label):
    while True:
        ans = input(f"  {label} (number, Enter=none, q=quit): ").strip().replace(',', '')
        if ans.lower() == 'q':
            raise SystemExit('Saved. Run again to resume.')
        if ans == '':
            return None
        try:
            return float(ans)
        except ValueError:
            print('  Please type a number, Enter or q')


def find_span(text, label, value):
    pattern = r'\$?\d(?:[\d,]*\d)?' if label == 'price' else r'\d(?:[\d,]*\d)?(?=\s*square\s*feet)'
    for m in re.finditer(pattern, text, re.I):
        number = int(m.group(0).replace('$', '').replace(',', ''))
        if number == int(value):
            return m.start(), m.end()
    return None, None


def save(rows):
    with open(PATH, 'w') as f:
        json.dump(rows, f, indent=2)


if __name__ == '__main__':
    with open(PATH) as f:
        rows = json.load(f)

    todo = sum(1 for r in rows if not r.get('ps_done') and candidate_sentences(r['text']))
    print(f"{todo} rows to review")

    for row in rows:
        if row.get('ps_done'):
            continue
        # Replace any automatic price/sqft labels with the human answer
        row['entities'] = [e for e in row['entities'] if e['label'] not in ('price', 'sqft')]
        row['conflicts'] = [c for c in row['conflicts'] if c not in ('price', 'sqft')]

        sentences = candidate_sentences(row['text'])
        if sentences:
            print('\n' + '=' * 80)
            print(f"id {row['id']} ({row['split']})")
            for s in sentences:
                print('*', textwrap.fill(s, width=100, subsequent_indent='  '))
            for label in ('price', 'sqft'):
                value = ask(label)
                if value is not None:
                    start, end = find_span(row['text'], label, value)
                    row['entities'].append({'label': label, 'value': value, 'start': start,
                                            'end': end,
                                            'text': row['text'][start:end] if start is not None else ''})
        row['ps_done'] = True
        save(rows)

    print('Done: price and sqft labeled for all rows.')