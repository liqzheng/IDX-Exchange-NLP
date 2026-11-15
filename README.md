# IDX Exchange NLP

Natural-language search over real-estate listings (12-week NLP internship project).
Turns free-text listing remarks and buyer queries into structured data and searchable
vectors.

## What is in this repo
| Folder | Content |
|---|---|
| `scripts/week1` | Data loading, taxonomy of real-estate terms, sample query generation |
| `scripts/week2` | Text cleaning (HTML, unicode, units, abbreviations) |
| `scripts/week3` | Entity extraction (bedrooms, bathrooms, price, sqft) |
| `scripts/week4` | Query parser (text -> filters -> parameterized SQL) and schema validator |
| `scripts/week5` | Semantic search (sentence embeddings + FAISS), BM25 comparison, latency benchmark |
| `scripts/week6` | `SignalExtractor`: entities + amenities, condition, financing, location signals |
| `tests/` | pytest tests |
| `reports/` | Reports and evaluation results for each week |

Raw data, the sample CSVs and generated outputs are **not** in the repo (`data/` is
git-ignored, except `data/schema.json`).

## Setup
Python 3.11 (conda environment recommended).

```bash
pip install -r requirements.txt
```

Note: on an Intel Mac, newer PyTorch versions are not available, so older pinned versions
of `sentence-transformers` and `transformers` are used.

## Run
Run all commands from the project root.

```bash
pytest -q                                      # run the tests
python scripts/week4/run_week4.py              # parse the sample queries
python scripts/week5/benchmark.py              # semantic search latency
python scripts/week5/compare.py                # semantic search vs BM25
python scripts/week6/run_week6.py              # extract signals for sample listings
python scripts/week6/check_structured.py       # compare extracted entities with DB columns
```

The scripts expect the sample data in `data/processed/` (not included).

## Results (details in `reports/`)
- **Week 4:** the rule-based query parser handled 89 of 91 sample queries correctly after
  fixes. It was tuned on the same 91 queries, so this is an optimistic number.
  Queries are turned into parameterized SQL (no string concatenation); SQL-injection tests
  are included.
- **Week 5:** semantic search over 1,000 listings. FAISS search takes under 1 ms for 10,000
  vectors, but encoding a query takes about 160 ms on a laptop CPU (target was 100 ms,
  not met). Precision@5 on 50 hand-judged pairs was 0.30 under a strict rule (a lower
  bound). Semantic search is weak on numbers ("three car garage") and exact terms
  ("granite").
- **Week 6:** signals were extracted for 1,000 sample listings. Structured fields agree with
  the database 87% (bedrooms), 70% (bathrooms) and 39% (price) of the time; the 90% target
  was not met, and many mismatches are convention differences (see the report).
  Accuracy of the free-text signals was not measured.

## Known limitations
- Only a 1,000-listing sample was used; the full database table was not processed.
- City names for validation come from the sample, so some valid cities are missing.
- Amenity filters assume the database stores `Y`/`N`; this is not verified.
- Evaluation sets are small and were labeled by one person.
