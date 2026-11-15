# Week 6 Report: Listing Signal Extraction

## What was built
`SignalExtractor` (`scripts/week6/signal_extractor.py`) turns one listing record into a
structured JSON:

```json
{
  "listing_id": "1",
  "entities": {"bedrooms": 3, "bathrooms": 2.0, "price": null, "sqft": null},
  "amenities": ["pool"],
  "condition_keywords": ["move-in ready"],
  "financing_terms": ["seller financing available"],
  "location_features": ["quiet neighborhood"]
}
```

- `entities` come from the Week 3 `EntityExtractor`. The remarks are first cleaned with the
  Week 2 `TextCleaner`, because the Week 3 extractor expects cleaned text
  (for example "1,800 sqft" becomes "1800 square feet").
- The four signal lists come from the Week 1 taxonomy. Terms are grouped by category and
  matched as whole words, case-insensitive:
  amenities = exterior + kitchen + interior features, condition = `condition_quality`,
  financing = `financial_terms`, location = `location_neighborhood`.
- `run_week6.py` processed the 1,000 sample listings and saved the result to
  `data/processed/signals.json` (not committed, it contains listing text).

## Coverage (1,000 sample listings)
| Signal | Listings with at least one |
|---|---|
| amenities | 948 |
| condition_keywords | 631 |
| location_features | 632 |
| financing_terms | 99 |

| Entity | Found (without cleaning -> with cleaning) |
|---|---|
| sqft | 146 -> 314 |
| bathrooms | 567 -> 587 |
| bedrooms | 646 -> 650 |
| price | 28 -> 36 |

Cleaning the text first clearly helped, especially for square footage.

## Accuracy
**Structured fields**, compared with the database columns `beds`, `baths`, `price`
(only listings where both a value was extracted and a column value exists):

| Field | Correct |
|---|---|
| bedrooms | 563 / 650 (87%) |
| bathrooms | 412 / 587 (70%) |
| price | 14 / 36 (39%) |

**The 90% target was not met.** Reading 6 mismatches showed the number mostly measures
agreement with the database, not extraction errors:
- Bedrooms: the text said "main residence offers 4 bedrooms" but the database counted the
  whole property (5); the text said "2 bedroom suites" and a den, the database said 3.
  The extractor read the text correctly.
- Bathrooms: "2.5-bathroom" was extracted as 2.5 but the database stores 3.0
  (half baths rounded up). This is a convention difference, not an extraction error.
  This rule was noticed after looking at the errors, so it was not applied to the score.
- Price: a real problem. The extractor took dollar amounts that are not the list price
  ("$250K VIEW PREMIUM LOT", "over $250k in upgrades"). Price should come from the database
  column, not from the remarks.
- Square footage has no database column, so its accuracy was not measured.

Only 6 mismatches were read by hand; the real extraction error rate for bedrooms and
bathrooms is therefore unknown.

**Free-text signals** (amenities, condition, financing, location): accuracy was
**not measured**. Only coverage is reported above. The 75% target is not verified.

## Limitations
- Taxonomy terms are full phrases (for example "seller financing available"), so variants
  such as "seller financing" or "renovated" are missed. Financing coverage is low (99/1000)
  partly for this reason.
- Prices in remarks are unreliable (39% agreement); use the database price.
- Only 1,000 sample listings were processed, not the full `rets_property` table.
- No second annotator, no hand-labeled set for the four signal lists.

## Next steps
- Hand-label about 30 listings to measure precision and recall of the four signal lists.
- Add term variants (stems and shorter phrases) to the matching.
- Run on the full database table.
