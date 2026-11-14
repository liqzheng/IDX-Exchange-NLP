import re

import pandas as pd
from rank_bm25 import BM25Okapi
from semantic_search import SemanticSearcher

df = pd.read_csv("data/processed/listing_sample.csv")
remarks = df["remarks"].fillna("").astype(str).tolist()


def tokenize(text):
    # lowercase words and numbers only
    return re.findall(r"[a-z0-9]+", text.lower())


bm25 = BM25Okapi([tokenize(r) for r in remarks])
s = SemanticSearcher()
s.build_index(remarks)

queries = [
    "a place to unwind with the family",
    "walk to the ocean",
    "great for entertaining guests",
    "house with a swimming pool",
    "updated kitchen with granite countertops",
]

for q in queries:
    scores = bm25.get_scores(tokenize(q))
    bm25_top = list(scores.argsort()[::-1][:5])
    sem_top = [i for i, _ in s.search(q, top_k=5)]
    overlap = len(set(bm25_top) & set(sem_top))

    print("=" * 60)
    print("QUERY:", q)
    print("top-5 overlap:", overlap, "/ 5")
    print("--- BM25 top 3 ---")
    for i in bm25_top[:3]:
        print("  ", remarks[i][:120].replace("\n", " "))
    print("--- Semantic top 3 ---")
    for i in sem_top[:3]:
        print("  ", remarks[i][:120].replace("\n", " "))