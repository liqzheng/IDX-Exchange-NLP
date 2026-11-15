import json

import pandas as pd

df = pd.read_csv("data/processed/listing_sample.csv")
signals = json.load(open("data/processed/signals.json"))

pairs = {"bedrooms": "beds", "bathrooms": "baths", "price": "price"}
for key, col in pairs.items():
    checked = 0
    correct = 0
    wrong = []
    for i, sig in enumerate(signals):
        found = sig["entities"].get(key)
        truth = df.loc[i, col]
        if found is None or pd.isna(truth):
            continue  # nothing to compare
        checked += 1
        if float(found) == float(truth):
            correct += 1
        else:
            wrong.append((i, found, truth))
    if checked:
        print(f"{key}: {correct}/{checked} correct ({correct / checked:.0%})")
    else:
        print(f"{key}: nothing to check")
    for w in wrong[:5]:
        print("   mismatch (row, extracted, db):", w)
