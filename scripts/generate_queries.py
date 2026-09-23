import json

queries = [
    # Browsing - casual/broad searches
    {"query": "show me homes in San Diego", "intent": "browsing"},
    {"query": "homes with pools in Irvine", "intent": "browsing"},
    {"query": "luxury homes in Beverly Hills", "intent": "browsing"},
    {"query": "houses for sale near me", "intent": "browsing"},
    {"query": "condos in Los Angeles", "intent": "browsing"},
    {"query": "new listings this week", "intent": "browsing"},
    {"query": "homes with a view", "intent": "browsing"},
    {"query": "single family homes in Orange County", "intent": "browsing"},
    {"query": "townhouses in Sacramento", "intent": "browsing"},
    {"query": "waterfront properties in California", "intent": "browsing"},
    {"query": "homes with big backyards", "intent": "browsing"},
    {"query": "properties in gated communities", "intent": "browsing"},
    {"query": "houses with pools near San Francisco", "intent": "browsing"},
    {"query": "new construction homes", "intent": "browsing"},
    {"query": "homes in quiet neighborhoods", "intent": "browsing"},
    {"query": "properties with mountain views", "intent": "browsing"},
    {"query": "3 bedroom homes in California", "intent": "browsing"},

    # Researching - comparison, area/market research
    {"query": "condos near UC Irvine with low HOA", "intent": "researching"},
    {"query": "areas in San Diego with low property taxes", "intent": "researching"},
    {"query": "best school districts in Orange County", "intent": "researching"},
    {"query": "average home price in Sacramento", "intent": "researching"},
    {"query": "which neighborhoods have the lowest HOA fees", "intent": "researching"},
    {"query": "compare home prices in Irvine vs Anaheim", "intent": "researching"},
    {"query": "homes near top-rated schools in San Jose", "intent": "researching"},
    {"query": "property tax rates in Los Angeles county", "intent": "researching"},
    {"query": "safest neighborhoods in San Diego", "intent": "researching"},
    {"query": "walkable neighborhoods near San Francisco", "intent": "researching"},
    {"query": "homes with the best resale value", "intent": "researching"},
    {"query": "which cities have the best commute to Silicon Valley", "intent": "researching"},
    {"query": "condo vs townhouse investment comparison", "intent": "researching"},
    {"query": "areas with rising home values in California", "intent": "researching"},
    {"query": "best neighborhoods for families near Sacramento", "intent": "researching"},
    {"query": "HOA fee comparison in Irvine communities", "intent": "researching"},
    {"query": "market trends for condos in Los Angeles", "intent": "researching"},

    # High-intent inquiry - ready to act, specific criteria
    {"query": "move-in ready homes in San Diego under 1.2m", "intent": "high_intent_inquiry"},
    {"query": "homes available this weekend with open houses", "intent": "high_intent_inquiry"},
    {"query": "new listings in Irvine under 900k with seller financing", "intent": "high_intent_inquiry"},
    {"query": "3 bed 2 bath under 700k in Irvine", "intent": "high_intent_inquiry"},
    {"query": "homes with open houses this weekend", "intent": "high_intent_inquiry"},
    {"query": "4 bedroom homes under 1 million in Sacramento", "intent": "high_intent_inquiry"},
    {"query": "properties I can tour tomorrow in San Jose", "intent": "high_intent_inquiry"},
    {"query": "move-in ready condos under 500k in Los Angeles", "intent": "high_intent_inquiry"},
    {"query": "homes accepting offers this week", "intent": "high_intent_inquiry"},
    {"query": "2 bed 1 bath under 600k near San Diego", "intent": "high_intent_inquiry"},
    {"query": "houses under 800k with no HOA in Anaheim", "intent": "high_intent_inquiry"},
    {"query": "homes ready to close within 30 days", "intent": "high_intent_inquiry"},
    {"query": "single family homes under 900k with seller financing", "intent": "high_intent_inquiry"},
    {"query": "condos for sale this week in Irvine", "intent": "high_intent_inquiry"},
    {"query": "3 bed homes under 700k with pool in Sacramento", "intent": "high_intent_inquiry"},
    {"query": "homes I can make an offer on today", "intent": "high_intent_inquiry"},
    {"query": "move-in ready 4 bedroom homes in San Diego", "intent": "high_intent_inquiry"},
]

output = {"queries": queries}

with open('data/processed/sample_queries.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"Generated {len(queries)} labeled queries")
intent_counts = {}
for q in queries:
    intent_counts[q['intent']] = intent_counts.get(q['intent'], 0) + 1
for intent, count in intent_counts.items():
    print(f"  {intent}: {count} queries")
    