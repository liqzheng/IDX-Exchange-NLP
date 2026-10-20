"""Simple tests for EntityExtractor (Week 3)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts", "week3"))
from entity_extractor import EntityExtractor

ex = EntityExtractor()


def test_bedrooms_digit():
    assert ex.extract_bedrooms("Lovely 3 bedroom home") == 3


def test_bedrooms_hyphen():
    assert ex.extract_bedrooms("A 4-bedroom house") == 4


def test_bedrooms_word():
    assert ex.extract_bedrooms("Charming three bedroom home") == 3


def test_bedrooms_none():
    assert ex.extract_bedrooms("Beautiful home with a pool") is None


def test_bathrooms_decimal():
    assert ex.extract_bathrooms("2.5 baths and a loft") == 2.5


def test_bathrooms_half():
    assert ex.extract_bathrooms("3 bed, 2 1/2 bath") == 2.5


def test_bathrooms_word():
    assert ex.extract_bathrooms("two bathrooms upstairs") == 2


def test_price_with_cue():
    assert ex.extract_price("Offered at $850,000 and ready to move in") == 850000


def test_price_ignores_small_amounts():
    assert ex.extract_price("HOA is $300 per month") is None


def test_sqft():
    assert ex.extract_sqft("This home has 1200 square feet of living space") == 1200


def test_amenities():
    assert "pool" in ex.extract_amenities("Backyard with a pool")


def test_extract_all_keys():
    result = ex.extract_all("3 bedroom 2 bath home")
    assert set(result) == {"bedrooms", "bathrooms", "price", "sqft", "amenities"}
