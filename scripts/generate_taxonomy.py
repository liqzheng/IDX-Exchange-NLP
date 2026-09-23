import json

category_terms = {
    "room_types": [
        "primary suite", "primary bedroom", "master bedroom", "living room",
        "family room", "dining room", "dining area", "home office",
        "laundry room", "bonus room", "game room", "media room",
        "guest room", "in-law suite", "mudroom", "sunroom", "den", "loft",
        "nursery", "walk-in closet", "powder room", "great room",
        "breakfast nook", "formal dining room", "formal living room", "flex room",
        "living area", "living spaces", "room for entertaining", "bedroom suite"
    ],
    "kitchen_features": [
        "granite countertops", "quartz countertops", "stainless steel appliances",
        "kitchen island", "custom cabinetry", "farmhouse sink", "gas range",
        "double oven", "wine fridge", "breakfast bar", "pantry",
        "subway tile backsplash", "open kitchen", "chef's kitchen",
        "butler's pantry", "soft-close cabinets", "tile backsplash",
        "kitchen features", "updated kitchen", "eat-in kitchen",
        "kitchen with island", "walk-in pantry", "kitchen with granite",
        "modern kitchen", "kitchen countertops"
    ],
    "interior_features": [
        "hardwood floors", "natural light", "vaulted ceilings", "crown molding",
        "recessed lighting", "open floor plan", "high ceilings",
        "custom lighting", "built-in shelving", "fireplace", "skylights",
        "tile flooring", "carpet flooring", "luxury vinyl plank",
        "ceiling fans", "smart home features", "security system",
        "central air", "dual pane windows", "floor plan", "sq ft",
        "square feet", "upstairs bedrooms", "downstairs bedroom",
       "abundant natural light", "open concept", "open floor concept"
    ],
    "exterior_features": [
        "backyard", "front yard", "private backyard", "covered patio",
        "deck", "pool", "spa", "outdoor kitchen", "fire pit", "garage",
        "two-car garage", "driveway", "fenced yard", "landscaping",
        "mature trees", "drought-tolerant landscaping", "solar panels",
        "RV parking", "gated entry", "covered porch", "backyard oasis",
        "outdoor entertaining", "side yard", "private patio"
    ],
    "location_neighborhood": [
        "close to shopping", "near schools", "walking distance", "cul-de-sac",
        "gated community", "quiet neighborhood", "top-rated schools",
        "easy access", "minutes from", "conveniently located",
        "heart of the city", "tree-lined street", "corner lot",
        "near freeway", "near public transit", "near parks", "waterfront",
        "mountain views", "city views", "ocean views", "close to restaurants",
        "near restaurants", "just minutes from", "located near",
        "close to freeway access"
    ],
    "condition_quality": [
        "move-in ready", "newly renovated", "recently updated", "turnkey",
        "brand new construction", "thoughtfully designed",
        "meticulously maintained", "pride of ownership", "rare opportunity",
        "exceptional home", "beautifully designed", "single-story",
        "two-story", "ranch style", "contemporary design", "modern finishes",
        "custom-built", "energy efficient", "new roof", "new HVAC",
        "beautifully appointed", "exceptional opportunity", "rare find"
    ],
    "financial_terms": [
        "HOA fees", "price reduced", "seller financing available", "no HOA",
        "low property taxes", "motivated seller", "multiple offers",
        "as-is sale", "short sale", "investment opportunity",
        "cash buyers only", "assumable loan", "seller credit",
        "closing cost credit", "first-time homebuyer", "fixer-upper",
        "income property", "cap rate", "rental potential", "owner may carry",
        "rare investment opportunity", "priced to sell", "great value"
    ],
    "lifestyle_amenities": [
        "perfect for entertaining", "ideal for families", "work from home",
        "indoor-outdoor living", "resort-style living", "everyday living",
        "comfort and privacy", "entertaining guests", "family gatherings",
        "weekend getaways", "low-maintenance living", "active lifestyle",
        "community amenities", "clubhouse access", "tennis courts",
        "walking trails", "dog park", "playground", "fitness center",
        "24-hour security", "for both comfort", "blend of comfort",
        "designed for everyday living"
    ]
}

taxonomy = {"categories": list(category_terms.keys()), "terms": []}
term_id = 1
for category, terms in category_terms.items():
    for term in terms:
        taxonomy["terms"].append({"id": f"T{term_id:04d}", "term": term, "category": category})
        term_id += 1

with open('data/processed/taxonomy.json', 'w') as f:
    json.dump(taxonomy, f, indent=2)

print(f"Generated {len(taxonomy['terms'])} terms across {len(taxonomy['categories'])} categories")
for cat in taxonomy["categories"]:
    count = sum(1 for t in taxonomy["terms"] if t["category"] == cat)
    print(f"  {cat}: {count} terms")