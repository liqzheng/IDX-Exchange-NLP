import json
import re


class EntityExtractor:
    def __init__(self, taxonomy_path='data/processed/taxonomy.json'):
        # Load all taxonomy terms once, used for amenity detection
        with open(taxonomy_path) as f:
            taxonomy = json.load(f)
        self.amenity_terms = [t['term'] for t in taxonomy['terms']]

    NUMBER_WORDS = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6,
                    'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10, 'eleven': 11, 'twelve': 12}
    _WORDS = '|'.join(NUMBER_WORDS)
    # "five bedrooms", "three-bedroom"
    BED_WORD_RE = re.compile(r'(?<![A-Za-z])(' + _WORDS + r')[\s-]+bed(?:room)?s?(?![A-Za-z])', re.I)
    # "2 1/2 bathrooms" -> 2.5
    BATH_HALF_RE = re.compile(r'(?<![\d./])(\d+)\s+1/2[\s-]*bath', re.I)
    # "2 baths", "2.5-bathroom", "2 full baths"; blocks fractions like "1/2 bath", "3/4 bath"
    BATH_NUM_RE = re.compile(
        r'(?<![\d.])(?<!\d/)(\d+(?:\.\d+)?)\s*-?\s*(?:full\s+)?bath(?:room)?s?(?![A-Za-z])', re.I)
    # "three full bathrooms", "one bath", "two-bathroom"
    BATH_WORD_RE = re.compile(
        r'(?<![A-Za-z])(' + _WORDS + r')[\s-]+(?:full[\s-]+)?bath(?:room)?s?(?![A-Za-z])', re.I)

    def extract_bedrooms(self, text):
        patterns = [
            # Allows "3 bedroom", "3-bedroom", "4- bedroom"; blocks "4/5 bedroom"
            r'(?<![\d./])(\d+)\s*-?\s*(?:bed|br|bedroom)s?',
            r'(\d+)bd',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.I)
            if match:
                return int(match.group(1))
        # Fall back to number words: "five bedrooms"
        match = self.BED_WORD_RE.search(text)
        return self.NUMBER_WORDS[match.group(1).lower()] if match else None

    def extract_bathrooms(self, text):
        # Bathrooms can be fractional, e.g. "2.5 bathrooms" or "2 1/2 bathrooms"
        match = self.BATH_HALF_RE.search(text)
        if match:
            return int(match.group(1)) + 0.5
        match = self.BATH_NUM_RE.search(text)
        if match:
            return float(match.group(1))
        match = self.BATH_WORD_RE.search(text)
        return float(self.NUMBER_WORDS[match.group(1).lower()]) if match else None

    # Price candidates: "$850,000", "$1.2 Million". "$" is required.
    PRICE_RE = re.compile(r'\$\s?(\d[\d,]*(?:\.\d+)?)(?:\s*(million))?', re.I)
    # Bare numbers are accepted only after a price cue, e.g. "under 1000000"
    BARE_PRICE_RE = re.compile(r'(?:under|priced at|offered at|listed at|asking)\s+(\d{6,7})(?![\d,])', re.I)
    # Context before the amount that marks the listing price
    PRICE_CUE = re.compile(r'(?:offered|priced|listed|asking|list price|price)\b[^$.;!]{0,25}$', re.I)
    # Context that marks an amount that is NOT the listing price
    NOT_PRICE_BEFORE = re.compile(r'(?:appraised|assessed|hoa|dues|taxes|tax|fees?)\b[^$.;!]{0,25}$', re.I)
    NOT_PRICE_AFTER = re.compile(
        r'^[^.;!]{0,30}?(?:upgrades?|remodel|renovations?|incentives?|credits?|improvements?|'
        r'per month|/\s?mo|/\s?month|hoa|dues)', re.I)

    def extract_price(self, text):
        # Assumes cleaned text from Week 2; returns the listing price as int
        fallback = None
        for m in self.PRICE_RE.finditer(text):
            number = m.group(1).rstrip(',')
            if m.group(2):  # "$1.2 Million" (also typo "$1,2 Million")
                value = int(float(number.replace(',', '.')) * 1_000_000)
            else:
                value = int(float(number.replace(',', '')))
            if value < 50000:  # too small to be a home price ($/SF, HOA, ...)
                continue
            before = text[max(0, m.start() - 40):m.start()]
            after = text[m.end():m.end() + 40]
            if self.NOT_PRICE_BEFORE.search(before) or self.NOT_PRICE_AFTER.search(after):
                continue
            if self.PRICE_CUE.search(before):
                return value  # strongest evidence: "offered at $650,000"
            if fallback is None:
                fallback = value
        if fallback is not None:
            return fallback
        match = self.BARE_PRICE_RE.search(text)
        return int(match.group(1)) if match else None

    def extract_sqft(self, text):
        # Assumes cleaned text: "1,500 sqft" -> "1500 square feet"
        match = re.search(r'(\d{3,5})\s*square\s*feet', text, re.I)
        return int(match.group(1)) if match else None

    def extract_amenities(self, text):
        found = []
        for term in self.amenity_terms:
            # Whole-phrase match, case-insensitive
            pattern = r'(?<![A-Za-z])' + re.escape(term) + r'(?![A-Za-z])'
            if re.search(pattern, text, re.I):
                found.append(term)
        return found

    def extract_all(self, text):
        return {
            'bedrooms': self.extract_bedrooms(text),
            'bathrooms': self.extract_bathrooms(text),
            'price': self.extract_price(text),
            'sqft': self.extract_sqft(text),
            'amenities': self.extract_amenities(text),
        }