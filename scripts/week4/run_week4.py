import json
import sys

sys.path.insert(0, "scripts/week4")
from query_parser import QueryParser
from schema_validator import SchemaValidator

cities = json.load(open("data/schema.json"))["valid_cities"]
parser = QueryParser(cities)
validator = SchemaValidator()

queries = json.load(open("data/processed/sample_queries.json"))["queries"]

empty = 0
for i, item in enumerate(queries):
    filters = parser.parse(item["query"])
    ok, errors = validator.validate_query(filters)
    if not filters:
        empty += 1
    print(i, "|", item["query"], "->", filters, "" if ok else errors)

print()
print("total:", len(queries), "| no filter found:", empty)