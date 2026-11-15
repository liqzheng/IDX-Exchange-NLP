import re
from collections import defaultdict


class SignalExtractor:
    def __init__(self, taxonomy, entity_extractor, cleaner=None):
        self.entity_extractor = entity_extractor
        self.cleaner = cleaner
        # group terms by category
        self.terms_by_category = defaultdict(list)
        for item in taxonomy["terms"]:
            self.terms_by_category[item["category"]].append(item["term"])

    def _match_terms(self, text, categories):
        text = text.lower()
        found = []
        for category in categories:
            for term in self.terms_by_category[category]:
                pattern = r"\b" + re.escape(term.lower()) + r"\b"
                if re.search(pattern, text):
                    found.append(term)
        return found

    def _match_amenities(self, text):
        return self._match_terms(
            text, ["exterior_features", "kitchen_features", "interior_features"]
        )

    def _extract_condition(self, text):
        return self._match_terms(text, ["condition_quality"])

    def _extract_financing(self, text):
        return self._match_terms(text, ["financial_terms"])

    def _extract_location(self, text):
        return self._match_terms(text, ["location_neighborhood"])

    def extract_signals(self, listing_record):
        remarks = listing_record.get("L_Remarks") or listing_record.get("remarks")
        if not isinstance(remarks, str):  # empty cell (NaN/None) -> empty text
            remarks = ""
        # Week 3 extractor expects cleaned text ("1,800 sqft" -> "1800 square feet")
        cleaned = self.cleaner.clean_text(remarks) if self.cleaner else remarks
        entities = self.entity_extractor.extract_all(cleaned)
        entities.pop("amenities", None)  # reported separately below
        return {
            "listing_id": listing_record.get("L_ListingID"),
            "entities": entities,
            "amenities": self._match_amenities(remarks),
            "condition_keywords": self._extract_condition(remarks),
            "financing_terms": self._extract_financing(remarks),
            "location_features": self._extract_location(remarks),
        }
