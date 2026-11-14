import csv

import pandas as pd
from semantic_search import SemanticSearcher

df = pd.read_csv("data/processed/listing_sample.csv")
remarks = df["remarks"].fillna("").astype(str).tolist()

s = SemanticSearcher()
s.build_index(remarks)

queries = [
    "quiet cul-de-sac with a big backyard",
    "condo with ocean view",
    "house with a swimming pool",
    "updated kitchen with granite countertops",
    "close to good schools",
    "single story home",
    "investment property with rental income",
    "mountain views",
    "newly remodeled bathrooms",
    "three car garage",
]

rows = []
for q in queries:
    for rank, (i, score) in enumerate(s.search(q, top_k=5), start=1):
        text = remarks[i][:300].replace("\n", " ")
        rows.append([q, rank, round(score, 3), text, ""])

with open("data/processed/search_eval.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["query", "rank", "score", "remark", "relevant"])
    writer.writerows(rows)

print(len(rows), "pairs written to data/processed/search_eval.csv")