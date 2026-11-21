"""
categorizer.py
--------------
Intelligent Auto-Categorization Engine.
Classifies unstructured transaction notes/descriptions into standard personal finance categories
using rule-based keyword matching and natural heuristic pattern recognition.
"""

import re
from typing import Dict, List, Tuple


CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "Food & Dining": [
        "starbucks", "mcdonalds", "kfc", "burger", "pizza", "dominos", "subway",
        "restaurant", "cafe", "coffee", "tea", "swiggy", "zomato", "groceries",
        "supermarket", "blinkit", "instamart", "zepto", "dining", "lunch", "dinner",
        "breakfast", "bakery", "snack", "fruits", "vegetables", "milk", "bread"
    ],
    "Rent & Utilities": [
        "rent", "landlord", "apartment", "lease", "electricity", "eb bill", "power",
        "water bill", "gas cylinder", "piped gas", "wifi", "broadband", "internet",
        "maintenance", "dth", "trash", "utility"
    ],
    "Transportation": [
        "uber", "ola", "rapido", "lyft", "taxi", "cab", "auto", "metro", "bus",
        "train", "irctc", "railway", "flight", "indigo", "airline", "fuel", "petrol",
        "diesel", "gas station", "shell", "hpcl", "bpcl", "toll", "fastag", "parking"
    ],
    "Shopping": [
        "amazon", "flipkart", "myntra", "meesho", "ajio", "clothing", "apparel",
        "shoes", "zara", "h&m", "uniqlo", "mall", "electronics", "gadget", "laptop",
        "mobile", "iphone", "watch", "accessories", "t-shirt", "jeans"
    ],
    "Entertainment": [
        "netflix", "spotify", "prime video", "hotstar", "disney", "youtube premium",
        "apple music", "movie", "cinema", "pvr", "inox", "concert", "theatre",
        "steam", "gaming", "playstation", "xbox", "game", "party", "club"
    ],
    "Healthcare": [
        "doctor", "hospital", "clinic", "pharmacy", "medicine", "tablets", "apollo",
        "medplus", "1mg", "dentist", "eye care", "blood test", "diagnostic", "therapy",
        "health insurance", "first aid", "consultation"
    ],
    "Education": [
        "coursera", "udemy", "edx", "course", "tuition", "coaching", "college",
        "university", "school", "exam fee", "books", "textbook", "stationery",
        "certifications", "seminar", "workshop"
    ],
    "Personal Care": [
        "salon", "haircut", "spa", "parlour", "grooming", "gym", "fitness",
        "cult.fit", "yoga", "cosmetics", "skincare", "perfume", "shampoo"
    ]
}


def predict_category(description: str, fallback: str = "Miscellaneous") -> Tuple[str, float]:
    """
    Predicts the expense category based on keywords inside the description string.
    
    Args:
        description: Textual description or merchant name (e.g., 'Starbucks Coffee')
        fallback: Default category if no keywords match.
        
    Returns:
        Tuple of (category_name, confidence_score [0.0 - 1.0])
    """
    if not description or not isinstance(description, str):
        return fallback, 0.0

    clean_text = description.lower()
    # Normalize punctuation
    clean_tokens = set(re.findall(r"\b[a-zA-Z0-9_\-\&]+\b", clean_text))

    best_category = fallback
    max_matches = 0

    for category, keywords in CATEGORY_KEYWORDS.items():
        matches = 0
        for kw in keywords:
            # Check exact token match or substring match for multi-word keywords
            if " " in kw:
                if kw in clean_text:
                    matches += 2
            elif kw in clean_tokens:
                matches += 1
            elif kw in clean_text:
                matches += 0.5

        if matches > max_matches:
            max_matches = matches
            best_category = category

    confidence = min(1.0, max_matches * 0.5) if max_matches > 0 else 0.0
    return best_category, confidence


def auto_categorize_series(descriptions: list) -> list:
    """Helper to categorize a list/series of transaction descriptions."""
    return [predict_category(desc)[0] for desc in descriptions]
