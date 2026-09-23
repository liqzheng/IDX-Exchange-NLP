import nltk
# Import NLTK — Python's natural language processing toolkit,
# used here for tokenization (splitting text into words)

import pandas as pd
# Import pandas — used to read and handle the CSV table of listing samples

from collections import Counter
# Import Counter — a built-in Python tool that counts how many times
# each item appears in a list

from nltk.util import ngrams
# Import ngrams — an NLTK function that generates groups of N
# consecutive words (here, pairs of two words = bigrams)

# Make sure NLTK's tokenizer model is downloaded
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

# Read the sample data generated in Week 1 step 1
df = pd.read_csv('data/processed/listing_sample.csv')

# Extract bigrams from remarks
all_text = ' '.join(df['remarks'].dropna().str.lower())
# Combine all remarks into one lowercase string, dropping empty entries

tokens = nltk.word_tokenize(all_text)
# Split the combined text into individual words (tokenization)

bigrams = list(ngrams(tokens, 2))
# Generate all pairs of two consecutive words from the token list

freq = Counter(bigrams)
# Count how many times each bigram (word pair) appears

# Top 200 bigrams become taxonomy seed
for bigram, count in freq.most_common(200):
    print(f"{' '.join(bigram)}: {count}")
    # Get the 200 most frequent bigrams and print each one
    # with its occurrence count, e.g. "hardwood floors: 87"
