import json


class SchemaValidator:
    def __init__(self, schema_path="data/schema.json"):
        with open(schema_path) as f:
            self.schema = json.load(f)
        self.valid_cities = set(c.lower() for c in self.schema["valid_cities"])

    def validate_query(self, filters):

        errors = []

        # City must exist in the database
        if "city" in filters:
            if filters["city"].lower() not in self.valid_cities:
                errors.append(f"City '{filters['city']}' not found in database")

        # Price must be in a sensible range
        if "price_max" in filters:
            if filters["price_max"] < 100000 or filters["price_max"] > 10000000:
                errors.append(f"Price {filters['price_max']} outside typical range")

        # Bedroom count must be sensible
        for key in ("bedrooms", "bedrooms_min", "bedrooms_max"):
            if key in filters:
                if filters[key] < 1 or filters[key] > 10:
                    errors.append(f"Bedroom count {filters[key]} seems invalid")

        return len(errors) == 0, errors