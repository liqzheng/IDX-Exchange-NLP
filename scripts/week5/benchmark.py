import time

import faiss
import numpy as np
import pandas as pd
from semantic_search import SemanticSearcher

df = pd.read_csv("data/processed/listing_sample.csv")
remarks = df["remarks"].fillna("").astype(str).tolist()

print("building index on", len(remarks), "listings...", flush=True)
s = SemanticSearcher()
s.build_index(remarks)

# Synthetic 10k index for timing only: repeat the 1000 vectors 10 times
base = s.index.reconstruct_n(0, s.index.ntotal)
big = faiss.IndexFlatIP(base.shape[1])
big.add(np.tile(base, (10, 1)))
print("big index size:", big.ntotal, flush=True)

queries = [
    "cozy family home with a big backyard",
    "modern condo close to the beach",
    "quiet street with mountain views",
    "updated kitchen with granite counters",
    "home with a pool and spa for entertaining",
    "walkable to shops and restaurants",
    "investment property with rental income",
    "single story home with a large garage",
    "ocean view townhouse",
    "newly remodeled house near good schools",
]

# warm up so the first call does not distort the timing
s.model.encode(["warm up"])

encode_ms, search_ms = [], []
for q in queries:
    t = time.time()
    v = np.array(s.model.encode([q]), dtype="float32")
    faiss.normalize_L2(v)
    encode_ms.append((time.time() - t) * 1000)

    t = time.time()
    big.search(v, 10)
    search_ms.append((time.time() - t) * 1000)

print()
print(f"query encoding:                 {np.mean(encode_ms):7.1f} ms (mean of {len(queries)})")
print(f"FAISS search over {big.ntotal} listings: {np.mean(search_ms):7.2f} ms (mean of {len(queries)})")
print(f"total per query:                {np.mean(encode_ms) + np.mean(search_ms):7.1f} ms")