"""
nlp_engine/categorizer.py
Auto-categorization and keyword/tag extraction for memories and documents.
Categories: Personal, Work, Health, Study, Finance, Ideas
"""

import re
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Automatically download required NLTK tokenizers and stopwords quietly
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

# Curated anchor vocabulary for the 6 core categories
CATEGORY_TAXONOMY = {
    "Health": [
        "doctor", "hospital", "medicine", "prescription", "clinic", "symptom", "pain",
        "appointment", "dentist", "therapy", "surgery", "diet", "workout", "fitness",
        "blood", "fever", "pharmacy", "vaccine", "exercise", "mental", "wellness"
    ],
    "Finance": [
        "money", "bank", "salary", "expense", "tax", "invoice", "investment",
        "budget", "crypto", "bitcoin", "payment", "loan", "interest", "insurance",
        "stock", "portfolio", "credit", "debit", "receipt", "audit", "wealth"
    ],
    "Work": [
        "meeting", "project", "deadline", "client", "boss", "colleague", "presentation",
        "report", "sprint", "email", "office", "manager", "team", "contract",
        "task", "deliverable", "kpi", "roadmap", "agile", "standup"
    ],
    "Study": [
        "exam", "assignment", "university", "college", "course", "lecture", "book",
        "research", "study", "homework", "syllabus", "professor", "semester", "grade",
        "thesis", "quiz", "class", "library", "notes", "academic"
    ],
    "Ideas": [
        "startup", "invention", "brainstorm", "concept", "feature", "strategy", "vision",
        "prototype", "creative", "innovation", "product", "pitch", "solution", "design",
        "hackathon", "experiment", "inspiration"
    ],
    "Personal": [
        "family", "vacation", "birthday", "friend", "home", "hobby", "diary",
        "journal", "reflection", "trip", "holiday", "anniversary", "dinner", "weekend",
        "travel", "memory", "celebration", "personal"
    ]
}


class MemoryCategorizer:
    def __init__(self):
        try:
            self.stop_words = set(stopwords.words('english'))
        except Exception:
            self.stop_words = set()

    def predict_category(self, text: str) -> str:
        """
        Classifies input text into one of the 6 core categories.
        Returns the category with the highest keyword relevance match.
        """
        if not text or not text.strip():
            return "Personal"

        text_lower = text.lower()
        scores = {category: 0 for category in CATEGORY_TAXONOMY}

        # Count keyword occurrences with word boundaries
        for category, keywords in CATEGORY_TAXONOMY.items():
            for kw in keywords:
                matches = re.findall(rf"\b{re.escape(kw)}\b", text_lower)
                scores[category] += len(matches)

        best_category = max(scores, key=scores.get)
        # Default to 'Personal' if no specific category score was triggered
        return best_category if scores[best_category] > 0 else "Personal"

    def extract_tags(self, text: str, top_n: int = 5) -> list[str]:
        """
        Extracts top_n meaningful keywords from the text to be used as tags.
        Filters out punctuation, numbers, and common stop words.
        """
        if not text or not text.strip():
            return []

        # Tokenize words
        try:
            tokens = word_tokenize(text.lower())
        except Exception:
            tokens = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())

        # Keep only alphabetic words longer than 3 chars that are not stop words
        cleaned_words = [
            token for token in tokens
            if token.isalpha() and len(token) > 3 and token not in self.stop_words
        ]

        # Return top N most frequent keywords
        word_counts = Counter(cleaned_words)
        return [word for word, _ in word_counts.most_common(top_n)]


# Quick verification test
if __name__ == "__main__":
    categorizer = MemoryCategorizer()

    sample_text = (
        "Visited Dr. John at Apollo Hospital today. He prescribed blood pressure medicine "
        "and advised a strict diet with daily morning workouts."
    )

    category = categorizer.predict_category(sample_text)
    tags = categorizer.extract_tags(sample_text)

    print(f"Detected Category : {category}")
    print(f"Generated Tags    : {tags}")
