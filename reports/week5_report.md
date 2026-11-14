Week 5: Semantic Search

This week I built a search tool that finds listings by meaning, not just by exact words. It turns each listing description into numbers (a 384-number vector) with a small language model, and uses FAISS to find the closest listings to a user’s question.

I tested it three ways. First, speed: searching 10,000 vectors takes under 1 ms, but encoding the question takes about 160 ms on my laptop CPU, so the total is about 162 ms. This is slower than the 100 ms goal. Second, I compared it with BM25 keyword search. Semantic search worked better when the question used different words than the listing, like “a place to unwind with the family”. Third, I checked 50 results by hand. About 30% were fully correct under a strict rule.

It does well with general ideas (like “swimming pool”) but struggles with numbers (like “three car garage”) and exact details (like “granite”). My next step is to combine it with the Week 4 query parser, so filters handle the exact conditions and semantic search handles the meaning.
## Details

### Latency
| Step | Time |
|---|---|
| FAISS search (10,000 vectors) | ~0.88 ms |
| Query encoding (CPU) | ~161 ms |
| Total per query | ~162 ms |

- Target was < 100 ms. Not met on a laptop CPU; query encoding is the slow part.
- The 10k index is synthetic (1,000 real vectors repeated 10 times), so it is valid for timing only, not for search quality.
- Ideas: cache repeated queries, use a GPU, use an ONNX or quantized model.

### Semantic search vs BM25 (5 example queries)
- Top-5 overlap between the two methods: 0, 1, 0, 1, 1 out of 5.
- For queries worded differently from the listings ("a place to unwind with the family", "great for entertaining guests"), overlap was 0/5. BM25 matched generic words (welcome, family, home); semantic search returned listings closer in meaning.
- For keyword-style queries ("swimming pool", "granite countertops"), there was no clear winner from reading snippets.
- Only 5 queries and short snippets, so this is directional, not statistical.

### Relevance evaluation (10 queries x top-5 = 50 pairs)
Overall precision@5 = 0.30 (15 / 50).

| Query | Precision@5 |
|---|---|
| house with a swimming pool | 0.6 |
| close to good schools | 0.4 |
| single story home | 0.4 |
| investment property with rental income | 0.4 |
| newly remodeled bathrooms | 0.4 |
| quiet cul-de-sac with a big backyard | 0.2 |
| condo with ocean view | 0.2 |
| updated kitchen with granite countertops | 0.2 |
| mountain views | 0.2 |
| three car garage | 0.0 |

Labeling rule: a result is relevant (1) only if every part of the query is clearly visible in the first 300 characters of the description; otherwise 0. This makes 0.30 a lower bound. Labels were made by one person with AI assistance and a fixed rule, with no second annotator. BM25 was not scored on the same 50 pairs, so this report does not claim a numeric win for either method.

### Failure patterns
- Numbers are ignored: "three car garage" returned 1-car and 2-car garages.
- Specific nouns are missed: "granite" appeared in only 1 of 5 results.
- Names are mistaken for meaning: "Ocean Blvd", "Oceana South", "Mountain Shadows".
- Near-synonyms are confused: "single family home" returned for "single story home".
- In two-part queries, mainly the first part is matched (cul-de-sac found, backyard often not visible).

### Limitations and next steps
- 1,000 listings, 10 queries, one annotator, labels from truncated text.
- Next: hybrid search (Week 4 filters for numbers and exact terms, then semantic ranking), and evaluate with full descriptions and a second annotator.
