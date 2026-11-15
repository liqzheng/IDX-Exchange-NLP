import sys

import numpy as np
import pytest

sys.path.insert(0, "scripts/week5")
semantic_search = pytest.importorskip("semantic_search")
SemanticSearcher = semantic_search.SemanticSearcher


class FakeModel:
    # maps the first word of a text to a fixed 3-d vector, so no real model is needed
    VECTORS = {"pool": [1, 0, 0], "beach": [0, 1, 0], "garage": [0, 0, 1]}

    def encode(self, texts, show_progress_bar=False):
        return np.array([self.VECTORS[t.split()[0]] for t in texts], dtype="float64")


def make():
    s = SemanticSearcher.__new__(SemanticSearcher)  # skip loading the real model
    s.model = FakeModel()
    s.index = None
    s.remarks = []
    s.build_index(["pool house", "beach condo", "garage unit"])
    return s


def test_best_match_is_first():
    results = make().search("pool", top_k=3)
    assert results[0][0] == 0
    assert results[0][1] == pytest.approx(1.0, abs=1e-5)


def test_other_listing_is_found():
    assert make().search("beach", top_k=1)[0][0] == 1


def test_scores_are_sorted_high_to_low():
    scores = [score for _, score in make().search("garage", top_k=3)]
    assert scores == sorted(scores, reverse=True)


def test_top_k_larger_than_index_drops_padding():
    # FAISS pads missing results with -1; the searcher must remove them
    results = make().search("pool", top_k=10)
    assert len(results) == 3
    assert all(i >= 0 for i, _ in results)


def test_result_types():
    index, score = make().search("pool", top_k=1)[0]
    assert isinstance(index, int)
    assert isinstance(score, float)
