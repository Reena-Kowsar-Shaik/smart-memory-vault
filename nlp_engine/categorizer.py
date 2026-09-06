"""
nlp_engine/categorizer.py
Auto-categorization & Tag Extraction
Categories: Personal, Work, Health, Study, Finance, Ideas
"""

import re
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Quietly ensure NLTK resources are available
for pkg in ['punkt', 'punkt_tab', 'stopwords']:
    try:
        nltk.download(pkg, quiet=True)
    except Exception:
        pass

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
        """Classifies text into the best matching category."""
        if not text or not text.strip():
            return "Personal"

        text_lower = text.lower()
        scores = {category: 0 for category in CATEGORY_TAXONOMY}

        for category, keywords in CATEGORY_TAXONOMY.items():
            for kw in keywords:
                matches = re.findall(rf"\b{re.escape(kw)}\b", text_lower)
                scores[category] += len(matches)

        best_category = max(scores, key=scores.get)
        return best_category if scores[best_category] > 0 else "Personal"

    def extract_tags(self, text: str, top_n: int = 5) -> list[str]:
        """Extracts top_n keywords as tags."""
        if not text or not text.strip():
            return []

        try:
            tokens = word_tokenize(text.lower())
        except Exception:
            tokens = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())

        cleaned = [
            t for t in tokens
            if t.isalpha() and len(t) > 3 and t not in self.stop_words
        ]
        return [word for word, _ in Counter(cleaned).most_common(top_n)]
