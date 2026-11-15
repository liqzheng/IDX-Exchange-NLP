import json
import sys

import pandas as pd

sys.path.insert(0, "scripts/week2")
sys.path.insert(0, "scripts/week3")
sys.path.insert(0, "scripts/week6")
from entity_extractor import EntityExtractor
from signal_extractor import SignalExtractor
from text_cleaning import TextCleaner

taxonomy = json.load(open("data/processed/taxonomy.json"))
extractor = SignalExtractor(taxonomy, EntityExtractor(), TextCleaner())

df = pd.read_csv("data/processed/listing_sample.csv")
results = [extractor.extract_signals(r) for r in df.to_dict("records")]

with open("data/processed/signals.json", "w") as f:
    json.dump(results, f, indent=2, default=str)

print("processed", len(results), "listings")
for key in ["amenities", "condition_keywords", "financing_terms", "location_features"]:
    n = sum(1 for r in results if r[key])
    print(f"{key}: {n} / {len(results)} listings have at least one")

for key in ["bedrooms", "bathrooms", "price", "sqft"]:
    n = sum(1 for r in results if r["entities"].get(key) is not None)
    print(f"entity {key}: found in {n} / {len(results)} listings")
