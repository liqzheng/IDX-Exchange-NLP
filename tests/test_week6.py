import sys

sys.path.insert(0, "scripts/week6")
from signal_extractor import SignalExtractor

# tiny taxonomy so the tests do not depend on data/ (not in the repo)
TAXONOMY = {
    "terms": [
        {"id": "T1", "term": "pool", "category": "exterior_features"},
        {"id": "T2", "term": "move-in ready", "category": "condition_quality"},
        {"id": "T3", "term": "seller financing available", "category": "financial_terms"},
        {"id": "T4", "term": "quiet neighborhood", "category": "location_neighborhood"},
    ]
}


class FakeEntityExtractor:
    def extract_all(self, text):
        return {"bedrooms": 3, "amenities": ["pool"]}


class FakeCleaner:
    def clean_text(self, text):
        return text.upper()


def make(cleaner=None):
    return SignalExtractor(TAXONOMY, FakeEntityExtractor(), cleaner)


def test_finds_each_signal_type():
    text = "Move-in ready home with a pool in a quiet neighborhood. Seller financing available."
    out = make().extract_signals({"L_ListingID": "1", "remarks": text})
    assert out["amenities"] == ["pool"]
    assert out["condition_keywords"] == ["move-in ready"]
    assert out["financing_terms"] == ["seller financing available"]
    assert out["location_features"] == ["quiet neighborhood"]


def test_whole_word_only():
    out = make().extract_signals({"remarks": "Near the carpool lane."})
    assert out["amenities"] == []


def test_case_insensitive():
    out = make().extract_signals({"remarks": "POOL"})
    assert out["amenities"] == ["pool"]


def test_empty_none_and_nan_remarks():
    for bad in ["", None, float("nan")]:
        out = make().extract_signals({"remarks": bad})
        assert out["amenities"] == []


def test_entities_do_not_repeat_amenities():
    out = make().extract_signals({"remarks": "pool"})
    assert "amenities" not in out["entities"]
    assert out["entities"]["bedrooms"] == 3


def test_database_column_name_is_supported():
    out = make().extract_signals({"L_ListingID": "9", "L_Remarks": "pool"})
    assert out["listing_id"] == "9"
    assert out["amenities"] == ["pool"]


def test_signals_use_original_text_not_cleaned_text():
    # the cleaner upper-cases the text; signal matching is case-insensitive anyway,
    # and entities must receive the cleaned text
    class SpyEntityExtractor:
        def extract_all(self, text):
            return {"seen": text}

    ex = SignalExtractor(TAXONOMY, SpyEntityExtractor(), FakeCleaner())
    out = ex.extract_signals({"remarks": "pool"})
    assert out["entities"]["seen"] == "POOL"
    assert out["amenities"] == ["pool"]
