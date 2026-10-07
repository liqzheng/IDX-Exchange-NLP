import sys

import pandas as pd

from entity_extractor import EntityExtractor

df = pd.read_csv('data/processed/listing_sample_cleaned.csv')
extractor = EntityExtractor()

# Run extraction on the cleaned remarks
results = df['remarks_cleaned'].apply(extractor.extract_all)

# Coverage: how many listings had each field extracted
for field in ['bedrooms', 'bathrooms', 'price', 'sqft']:
    n = results.apply(lambda r: r[field] is not None).sum()
    print(f"{field}: {n} / {len(df)}")
n = results.apply(lambda r: len(r['amenities']) > 0).sum()
print(f"amenities: {n} / {len(df)}")

# Show 5 extracted prices with their original text, to check by eye
print("\n--- price examples ---")
shown = 0
for text, r in zip(df['remarks_cleaned'], results):
    if r['price'] is not None:
        key = str(r['price'])
        i = text.find(key)
        print(f"price={r['price']}  ...{text[max(0, i-40): i+40]}...")
        shown += 1
        if shown == 5:
            break