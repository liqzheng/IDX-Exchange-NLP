import re

# a price number: "700k", "$1.2m", "1 million", "850000"
PRICE = r"\$?(\d+(?:\.\d+)?)\s?(million|thousand|k|m)?\b"

# amenity name -> (regex for the word, database column)
AMENITIES = {
    "pool": ("pools?", "PoolPrivateYN"),
    "fireplace": ("fireplace", "FireplaceYN"),
    "view": ("views?", "ViewYN"),
}


class QueryParser:
    def __init__(self, cities=None):
        # Longest names first, so "San Jose" is tried before "San"
        self.cities = sorted(cities or [], key=len, reverse=True)

    def _parse_number(self, digits, suffix):
        # "700" + "k" -> 700000, "1.2" + "m" -> 1200000, "1" + "million" -> 1000000
        value = float(digits)
        suffix = (suffix or "").lower()
        if suffix in ("k", "thousand"):
            value *= 1000
        elif suffix in ("m", "million"):
            value *= 1000000
        return int(value)

    def parse(self, query):
        filters = {}

        # Price max: "under $700k", "under 1.2m", "pre-approved for 850k"
        match = re.search(
            r"(?:under|below|less than|up to|budget of|pre-approved for)\s+" + PRICE
            + r"(?!\s*(?:bed|br|bath))", query, re.I)
        if match:
            filters["price_max"] = self._parse_number(match.group(1), match.group(2))

        # Price range: "between $500k and $800k"
        match = re.search(r"between\s+" + PRICE + r"\s+and\s+" + PRICE, query, re.I)
        if match:
            filters["price_min"] = self._parse_number(match.group(1), match.group(2))
            filters["price_max"] = self._parse_number(match.group(3), match.group(4))

        # Price minimum: "over $500k" (not "over 3 bedrooms")
        match = re.search(
            r"(?:over|above|more than)\s+" + PRICE + r"(?!\d)(?!\s*(?:bed|br|bath))",
            query, re.I)
        if match:
            filters["price_min"] = self._parse_number(match.group(1), match.group(2))

        # Bedrooms: "2-4 bed" (range) first, then "3+ bed", then "3 bed"
        match = re.search(r"(\d+)\s*(?:-|to)\s*(\d+)\s*(?:bed|br)", query, re.I)
        if match:
            filters["bedrooms_min"] = int(match.group(1))
            filters["bedrooms_max"] = int(match.group(2))
        else:
            match = re.search(r"(\d+)(\+?)\s*(?:bed|br)", query, re.I)
            if match:
                if match.group(2) == "+":
                    filters["bedrooms_min"] = int(match.group(1))
                else:
                    filters["bedrooms"] = int(match.group(1))

        # Bathrooms: "2 bath", "2.5 bath", "2+ baths"
        match = re.search(r"(\d+(?:\.\d+)?)(\+?)\s*(?:bath|ba\b)", query, re.I)
        if match:
            if match.group(2) == "+":
                filters["bathrooms_min"] = float(match.group(1))
            else:
                filters["bathrooms"] = float(match.group(1))

        # City: known cities first (not a county), then "in <Capitalized Name>" as a guess
        lowered = query.lower()
        for city in self.cities:
            if re.search(r"(?<![a-z])" + re.escape(city.lower()) + r"(?![a-z])(?!\s+county)", lowered):
                filters["city"] = city
                break
        else:
            match = re.search(r"\bin\s+([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)", query)
            if match:
                guess = match.group(1)
                # a state or a county is not a city
                if guess.lower() not in ("california", "ca") and not guess.lower().endswith(" county"):
                    filters["city"] = guess

        # Amenities: "with a pool" -> wanted, "no pool" / "without a pool" -> excluded
        wanted, excluded = [], []
        for name, (pattern, column) in AMENITIES.items():
            match = re.search(r"\b(no|without)?\s*(?:a\s+|an\s+)?" + pattern + r"\b", query, re.I)
            if match:
                if match.group(1):
                    excluded.append(name)
                else:
                    wanted.append(name)
        if wanted:
            filters["amenities"] = wanted
        if excluded:
            filters["no_amenities"] = excluded

        return filters

    def to_sql(self, filters):
        conditions = []
        params = []

        if "price_min" in filters:
            conditions.append("L_SystemPrice >= %s")
            params.append(filters["price_min"])

        if "price_max" in filters:
            conditions.append("L_SystemPrice <= %s")
            params.append(filters["price_max"])

        if "bedrooms" in filters:
            conditions.append("L_Keyword2 = %s")
            params.append(filters["bedrooms"])

        if "bedrooms_min" in filters:
            conditions.append("L_Keyword2 >= %s")
            params.append(filters["bedrooms_min"])

        if "bedrooms_max" in filters:
            conditions.append("L_Keyword2 <= %s")
            params.append(filters["bedrooms_max"])

        if "bathrooms" in filters:
            conditions.append("LM_Dec_3 = %s")
            params.append(filters["bathrooms"])

        if "bathrooms_min" in filters:
            conditions.append("LM_Dec_3 >= %s")
            params.append(filters["bathrooms_min"])

        if "city" in filters:
            conditions.append("L_City = %s")
            params.append(filters["city"])

        for name in filters.get("amenities", []):
            conditions.append(AMENITIES[name][1] + " = %s")
            params.append("Y")

        for name in filters.get("no_amenities", []):
            conditions.append(AMENITIES[name][1] + " = %s")
            params.append("N")

        sql = "SELECT * FROM rets_property"
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        return sql, params