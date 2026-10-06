import os
import sys

import pandas as pd
import pytest

# Make scripts/ importable from the tests folder
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from text_cleaning import TextCleaner

c = TextCleaner()


@pytest.mark.parametrize("raw,expected", [
    ("$500k", "$500000"),
    ("$1.2M", "$1200000"),
    ("$2m", "$2000000"),
    ("priced at 450k", "priced at 450000"),
    ("$750K home", "$750000 home"),
    ("$1.5m", "$1500000"),
    ("5 minutes away", "5 minutes away"),
    ("10 kitchens", "10 kitchens"),
    ("$450,000", "$450,000"),
    ("no price here", "no price here"),
])
def test_prices(raw, expected):
    assert c.normalize_prices(raw) == expected


@pytest.mark.parametrize("raw,expected", [
    ("1,200 sqft", "1200 square feet"),
    ("1500 sq ft", "1500 square feet"),
    ("2000 sq. ft.", "2000 square feet"),
    ("900sf", "900 square feet"),
    ("3,400 sq ft lot", "3400 square feet lot"),
    ("1800 SQFT", "1800 square feet"),
    ("1,515 SF of living", "1515 square feet of living"),
    ("Close to SF Bay Area", "Close to SF Bay Area"),
])
def test_measurements(raw, expected):
    assert c.normalize_measurements(raw) == expected


@pytest.mark.parametrize("raw,expected", [
    ("3 br 2 ba", "3 bedroom 2 bathroom"),
    ("2 brs", "2 bedrooms"),
    ("pool w/ spa", "pool with spa"),
    ("pool w/o spa", "pool without spa"),
    ("mbr suite", "master bedroom suite"),
    ("hdwd floors", "hardwood floors"),
    ("immac condition", "immaculate condition"),
    ("nr schools", "near schools"),
    ("2 bths", "2 bathrooms"),
    ("brand new", "brand new"),
    ("a bath", "a bath"),
    ("3 Bd / 2 Ba", "3 bedroom / 2 bathroom"),
])
def test_abbreviations(raw, expected):
    assert c.expand_abbreviations(raw) == expected


@pytest.mark.parametrize("raw,expected", [
    ("it\u2019s", "it's"),
    ("\u201cnice\u201d", '"nice"'),
    ("a\u2013b", "a-b"),
    ("wait\u2026", "wait..."),
    ("a\u00a0b", "a b"),
])
def test_unicode(raw, expected):
    assert c.normalize_unicode(raw) == expected


@pytest.mark.parametrize("raw,expected", [
    ("<p>Hello</p>", " Hello "),
    ("a&nbsp;b", "a b"),
    ("R&amp;D", "R&D"),
    ("<br/>x", " x"),
])
def test_html(raw, expected):
    assert c.remove_html(raw) == expected


def test_whitespace():
    assert c.normalize_whitespace("  a   b \n c ") == "a b c"
    assert c.normalize_whitespace("") == ""


@pytest.mark.parametrize("raw,expected", [
    ("2br", "2 bedroom"),
    ("3BR/2BA", "3 bedroom/2 bathroom"),
])
def test_number_units(raw, expected):
    assert c.clean_text(raw) == expected


@pytest.mark.parametrize("raw,expected", [
    ("1,200 SF of space", "1200 square feet of space"),
    ("Close to SF Bay Area", "Close to SF Bay Area"),
    ("pool w/spa", "pool with spa"),
    ("w/open floor plan", "with open floor plan"),
    ("pool w/o spa", "pool without spa"),
])
def test_edge_cases(raw, expected):
    assert c.clean_text(raw) == expected


def test_clean_text_pipeline():
    assert c.clean_text(None) == ""
    assert c.clean_text("") == ""
    assert c.clean_text("<p>Nice 3 br home, 1,200 sqft, $850k</p>") == \
        "Nice 3 bedroom home, 1200 square feet, $850000"
    assert c.clean_text("Brand new   home") == "Brand new home"


def test_profiling():
    df = pd.DataFrame({"remarks": ["<p>3 br w/ pool $500k</p>", None, "plain text here"]})
    p = c.profile_column(df, "remarks")
    assert abs(p["null_rate"] - 1 / 3) < 1e-9
    assert "avg_length" in p
    assert p["has_html"] == 1
    assert p["price_mentions"] == 1
    assert "br" in p["common_abbreviations"]