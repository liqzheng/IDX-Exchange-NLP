import numpy as np
import faiss
from sentence_transformers import SentenceTransformer


class SemanticSearcher:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.remarks = []

    def build_index(self, remarks_list):
        # Turn every listing description into a vector
        self.remarks = list(remarks_list)
        vectors = self.model.encode(self.remarks, show_progress_bar=False)
        vectors = np.array(vectors, dtype="float32")

        # Normalize so that inner product equals cosine similarity
        faiss.normalize_L2(vectors)

        self.index = faiss.IndexFlatIP(vectors.shape[1])
        self.index.add(vectors)

    def search(self, query, top_k=10):
        # Encode the query the same way, then find the closest listings
        q = np.array(self.model.encode([query]), dtype="float32")
        faiss.normalize_L2(q)
        scores, ids = self.index.search(q, top_k)
        return [(int(i), float(s)) for i, s in zip(ids[0], scores[0]) if i != -1]