import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts", "week4"))
from query_parser import QueryParser  # noqa: E402
from schema_validator import SchemaValidator  # noqa: E402

CITIES = ["Irvine", "San Jose", "Fremont", "Palo Alto", "San Francisco"]
parser = QueryParser(CITIES)


# ---------- 1. parsing: (query, expected filters) ----------
PARSE_CASES = [
    # price max
    ("under $700k", {"price_max": 700000}),
    ("under 700k", {"price_max": 700000}),
    ("Under $1m", {"price_max": 1000000}),
    ("under 850000", {"price_max": 850000}),
    ("under $2m", {"price_max": 2000000}),
    ("under 1.2m", {"price_max": 1200000}),
    ("under $1.5m", {"price_max": 1500000}),
    ("under 1 million", {"price_max": 1000000}),
    ("pre-approved for 850k", {"price_max": 850000}),
    # price min / range
    ("over 500k", {"price_min": 500000}),
    ("above $1m", {"price_min": 1000000}),
    ("more than 600k", {"price_min": 600000}),
    ("between $500k and $800k", {"price_min": 500000, "price_max": 800000}),
    ("between 1m and 2m", {"price_min": 1000000, "price_max": 2000000}),
    # bedrooms
    ("3 bed", {"bedrooms": 3}),
    ("3 bedroom house", {"bedrooms": 3}),
    ("3br", {"bedrooms": 3}),
    ("3 BR condo", {"bedrooms": 3}),
    ("4+ bedrooms", {"bedrooms_min": 4}),
    ("2+ bed", {"bedrooms_min": 2}),
    ("2-4 bed", {"bedrooms_min": 2, "bedrooms_max": 4}),
    ("2 to 4 bedrooms", {"bedrooms_min": 2, "bedrooms_max": 4}),
    ("1 bed apartment", {"bedrooms": 1}),
    # bathrooms
    ("2 bath", {"bathrooms": 2.0}),
    ("2.5 bath", {"bathrooms": 2.5}),
    ("2+ baths", {"bathrooms_min": 2.0}),
    ("3 bathrooms", {"bathrooms": 3.0}),
    ("3 bed 2 bath", {"bedrooms": 3, "bathrooms": 2.0}),
    # city
    ("homes in Irvine", {"city": "Irvine"}),
    ("homes in irvine", {"city": "Irvine"}),
    ("house in San Jose", {"city": "San Jose"}),
    ("house in san jose", {"city": "San Jose"}),
    ("condo in Palo Alto", {"city": "Palo Alto"}),
    ("home in San Francisco", {"city": "San Francisco"}),
    ("Fremont houses", {"city": "Fremont"}),
    ("house in Portland", {"city": "Portland"}),
    # amenities
    ("house with a pool", {"amenities": ["pool"]}),
    ("with fireplace", {"amenities": ["fireplace"]}),
    ("ocean views", {"amenities": ["view"]}),
    ("pool and fireplace", {"amenities": ["pool", "fireplace"]}),
    # negation
    ("no pool", {"no_amenities": ["pool"]}),
    ("without a fireplace", {"no_amenities": ["fireplace"]}),
    ("pool but no view", {"amenities": ["pool"], "no_amenities": ["view"]}),
    # combinations
    ("3 bed under 700k in Irvine", {"bedrooms": 3, "price_max": 700000, "city": "Irvine"}),
    ("2-4 bed between $500k and $800k", {"bedrooms_min": 2, "bedrooms_max": 4,
                                         "price_min": 500000, "price_max": 800000}),
    ("4+ bed 3 bath in Fremont with pool", {"bedrooms_min": 4, "bathrooms": 3.0,
                                            "city": "Fremont", "amenities": ["pool"]}),
    ("3 bed in Irvine with a pool, no fireplace", {"bedrooms": 3, "city": "Irvine",
                                                   "amenities": ["pool"], "no_amenities": ["fireplace"]}),
    # things that must NOT be misread
    ("over 3 bedrooms", {"bedrooms": 3}),
    ("homes with pools in Irvine", {"amenities": ["pool"], "city": "Irvine"}),
    ("single family homes in Orange County", {}),
    ("3 bedroom homes in California", {"bedrooms": 3}),
    ("nice house", {}),
    ("house in a quiet area", {}),
    ("", {}),
]


@pytest.mark.parametrize("query,expected", PARSE_CASES)
def test_parse(query, expected):
    assert parser.parse(query) == expected


def test_over_bedrooms_is_not_a_price():
    assert "price_min" not in parser.parse("over 3 bedrooms")


# ---------- 2. SQL generation ----------
def test_sql_no_filters():
    sql, params = parser.to_sql({})
    assert sql == "SELECT * FROM rets_property" and params == []


def test_sql_price_and_bedrooms():
    sql, params = parser.to_sql(parser.parse("3 bed under 700k"))
    assert sql == "SELECT * FROM rets_property WHERE L_SystemPrice <= %s AND L_Keyword2 = %s"
    assert params == [700000, 3]


def test_sql_city_is_parameter():
    sql, params = parser.to_sql(parser.parse("house in Irvine"))
    assert "Irvine" not in sql and params == ["Irvine"]


def test_sql_amenities():
    sql, params = parser.to_sql(parser.parse("with a pool, no fireplace"))
    assert "PoolPrivateYN = %s" in sql and "FireplaceYN = %s" in sql
    assert params == ["Y", "N"]


@pytest.mark.parametrize("query", [q for q, _ in PARSE_CASES])
def test_placeholder_count_matches_params(query):
    sql, params = parser.to_sql(parser.parse(query))
    assert sql.count("%s") == len(params)


# ---------- 3. SQL injection ----------
EVIL = [
    "house in Irvine'; DROP TABLE rets_property;--",
    "3 bed' OR '1'='1",
    "under 700k; DELETE FROM rets_property",
    "in Irvine UNION SELECT * FROM users",
    "\" OR 1=1 --",
]


@pytest.mark.parametrize("evil", EVIL)
def test_injection_text_never_reaches_sql(evil):
    sql, params = parser.to_sql(parser.parse(evil))
    for bad in ("DROP", "DELETE", "UNION", "OR 1=1", "'1'='1'", "--"):
        assert bad not in sql


# ---------- 4. schema validation ----------
@pytest.fixture
def validator(tmp_path):
    path = tmp_path / "schema.json"
    path.write_text(json.dumps({"valid_cities": CITIES}))
    return SchemaValidator(str(path))


def test_valid_query(validator):
    assert validator.validate_query({"price_max": 700000, "bedrooms": 3, "city": "Irvine"}) == (True, [])


def test_city_case_insensitive(validator):
    assert validator.validate_query({"city": "irvine"})[0]


def test_unknown_city(validator):
    ok, errors = validator.validate_query({"city": "Atlantis"})
    assert not ok and "Atlantis" in errors[0]


def test_price_too_low(validator):
    assert not validator.validate_query({"price_max": 5000})[0]


def test_price_too_high(validator):
    assert not validator.validate_query({"price_max": 50000000})[0]


def test_price_boundaries_ok(validator):
    assert validator.validate_query({"price_max": 100000})[0]
    assert validator.validate_query({"price_max": 10000000})[0]


@pytest.mark.parametrize("key", ["bedrooms", "bedrooms_min", "bedrooms_max"])
def test_bedrooms_out_of_range(validator, key):
    assert not validator.validate_query({key: 50})[0]
    assert not validator.validate_query({key: 0})[0]


def test_empty_filters_valid(validator):
    assert validator.validate_query({}) == (True, [])


def test_multiple_errors(validator):
    ok, errors = validator.validate_query({"city": "Nowhere", "price_max": 1})
    assert not ok and len(errors) == 2


def test_portland_flow(validator):
    filters = parser.parse("2br condo in Portland")
    assert not validator.validate_query(filters)[0]