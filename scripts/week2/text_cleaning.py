"""Text cleaning for listing remarks (Week 2)."""
import re
from collections import Counter

import pandas as pd


class TextCleaner:
    def __init__(self):
        # NOTE: 'sf' is intentionally NOT here (ambiguous: square feet vs San Francisco)
        self.abbrev_map = {
            "w/o": "without", "w/": "with", "br": "bedroom", "brs": "bedrooms",
            "bd": "bedroom", "bds": "bedrooms", "bdrm": "bedroom", "mbr": "master bedroom",
            "ba": "bathroom", "bth": "bathroom", "bths": "bathrooms", "sqft": "square feet",
            "fp": "fireplace", "frplc": "fireplace", "gar": "garage", "hdwd": "hardwood",
            "apx": "approximately", "approx": "approximately", "nbhd": "neighborhood",
            "rm": "room", "cls": "close", "yr": "year", "yrs": "years", "avail": "available",
            "renov": "renovated", "updtd": "updated", "immac": "immaculate", "lg": "large",
            "sm": "small", "nr": "near", "incl": "including", "hoa": "HOA",
        }
        # longest key first so 'bths' wins over 'bth'
        self._ordered = sorted(self.abbrev_map, key=len, reverse=True)

    def normalize_unicode(self, text):
        for a, b in {"\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
                     "\u2013": "-", "\u2014": "-", "\u2026": "...", "\u00a0": " "}.items():
            text = text.replace(a, b)
        return text

    def remove_html(self, text):
        text = re.sub(r"<[^>]+>", " ", text)
        return text.replace("&nbsp;", " ").replace("&amp;", "&")

    def normalize_prices(self, text):
        # 450k -> 450000, $1.2M -> $1200000 ($ is optional)
        def repl(m):
            num = float(m.group(2))
            mult = 1000 if m.group(3).lower() == "k" else 1_000_000
            return f"{m.group(1)}{int(round(num * mult))}"

        return re.sub(r"(?<![\w.])(\$?)(\d+(?:\.\d+)?)([kKmM])(?![A-Za-z])", repl, text)

    def normalize_measurements(self, text):
        # 1,200 sqft -> 1200 sqft (strip comma), then unify unit to "square feet"
        text = re.sub(r"(\d+),(\d{3})(?=\s*(?:sq|square|sf(?![a-z])))", r"\1\2", text, flags=re.I)
        return re.sub(r"(\d+)\s*(?:sq\.?\s*ft\.?|sqft|sf)(?![a-z])", r"\1 square feet", text, flags=re.I)

    def separate_number_units(self, text):
        # 2br -> 2 br
        keys = "|".join(re.escape(k) for k in self._ordered if k.isalpha())
        return re.sub(rf"(\d)({keys})(?![A-Za-z])", r"\1 \2", text, flags=re.I)

    def expand_abbreviations(self, text):
        for k in self._ordered:
            if k.isalpha():
                text = re.sub(rf"(?<![A-Za-z]){k}(?![A-Za-z])", self.abbrev_map[k], text, flags=re.I)
        text = re.sub(r"(?<![A-Za-z])w/o(?![A-Za-z])", "without", text, flags=re.I)
        text = re.sub(r"(?<![A-Za-z])w/(?=[A-Za-z])", "with ", text, flags=re.I)
        text = re.sub(r"(?<![A-Za-z])w/(?![A-Za-z])", "with", text, flags=re.I)
        return text

    def normalize_whitespace(self, text):
        return re.sub(r"\s+", " ", text).strip()

    def clean_text(self, text):
        if not isinstance(text, str):
            return ""
        for step in (self.normalize_unicode, self.remove_html, self.normalize_prices,
                     self.normalize_measurements, self.separate_number_units,
                     self.expand_abbreviations, self.normalize_whitespace):
            text = step(text)
        return text

    def _extract_top_ngrams(self, texts, n=10):
        c = Counter()
        for t in texts:
            w = re.findall(r"[a-z']+", t.lower())
            c.update(zip(w, w[1:]))
        return [" ".join(k) for k, _ in c.most_common(n)]

    def _detect_abbreviations(self, texts):
        c = Counter()
        for t in texts:
            for k in self._ordered:
                if k.isalpha() and re.search(rf"(?<![A-Za-z]){k}(?![A-Za-z])", t, flags=re.I):
                    c[k] += 1
        return dict(c.most_common(10))

    def profile_column(self, df, col):
        s = df[col]
        texts = s.dropna().astype(str)
        return {
            "null_rate": float(s.isna().mean()),
            "avg_length": float(texts.str.len().mean()) if len(texts) else 0.0,
            "common_terms": self._extract_top_ngrams(texts),
            "price_mentions": int(texts.str.contains(r"\$\s?\d").sum()),
            "has_html": int(texts.str.contains("<").sum()),
            "common_abbreviations": self._detect_abbreviations(texts),
        }


if __name__ == "__main__":
    df = pd.read_csv("data/processed/listing_sample.csv")
    cleaner = TextCleaner()
    for k, v in cleaner.profile_column(df, "remarks").items():
        print(f"{k}: {v}")
    df["remarks_cleaned"] = df["remarks"].apply(cleaner.clean_text)
    df.to_csv("data/processed/listing_sample_cleaned.csv", index=False)
    print("Saved data/processed/listing_sample_cleaned.csv")