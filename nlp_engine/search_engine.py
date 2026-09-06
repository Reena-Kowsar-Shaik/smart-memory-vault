"""
nlp_engine/search_engine.py
Semantic & Natural Language Search using TF-IDF, Intent Expansion & Cosine Similarity.
Understands user intent (e.g. 'hospital visit' matches 'doctor appointment').
"""

import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Semantic intent expansion dictionary
INTENT_EXPANSIONS = {
    "hospital": ["doctor", "medical", "clinic", "health", "prescription", "appointment"],
    "clinic": ["doctor", "hospital", "health", "medicine", "appointment"],
    "doctor": ["hospital", "clinic", "medical", "health", "prescription", "checkup"],
    "medicine": ["prescription", "pharmacy", "doctor", "health", "dosage"],
    "bank": ["finance", "money", "salary", "expense", "tax", "account"],
    "money": ["finance", "bank", "salary", "expense", "budget", "cost"],
    "salary": ["payment", "bank", "finance", "money", "income"],
    "exam": ["study", "university", "test", "course", "assignment", "grade"],
    "office": ["work", "meeting", "project", "deadline", "client", "sprint"],
    "trip": ["vacation", "personal", "travel", "holiday", "flight", "tour"]
}


class SemanticSearchEngine:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')

    def expand_query(self, query: str) -> str:
        """Enriches the user query with semantic synonyms to understand intent."""
        tokens = re.findall(r'\b[a-zA-Z]{3,}\b', query.lower())
        expanded = [query]
        for word in tokens:
            if word in INTENT_EXPANSIONS:
                expanded.extend(INTENT_EXPANSIONS[word])
        return " ".join(expanded)

    def search(self, query: str, memories: list[dict], top_k: int = 5) -> list[dict]:
        """
        Searches memories by semantic relevance.
        memories: list of dicts [{'id': 1, 'title': '...', 'content': '...', 'category': '...', 'tags': [...]}]
        Returns sorted list of matching memories.
        """
        if not memories or not query or not query.strip():
            return []

        # Expand query with intent keywords
        enriched_query = self.expand_query(query)

        # Build corpus by concatenating title, content, category, and tags
        corpus = [
            f"{m.get('title', '')} {m.get('content', '')} {m.get('category', '')} {' '.join(m.get('tags', []))}"
            for m in memories
        ]

        try:
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(corpus)
            query_vec = vectorizer.transform([enriched_query])
            similarities = cosine_similarity(query_vec, tfidf_matrix)[0]

            results = []
            for idx, score in enumerate(similarities):
                if score > 0.01:  # Low threshold to capture semantic intent
                    mem_copy = memories[idx].copy()
                    mem_copy['similarity_score'] = round(float(score), 3)
                    results.append(mem_copy)

            # Sort descending by similarity score
            results.sort(key=lambda x: x['similarity_score'], reverse=True)
            return results[:top_k]

        except Exception:
            return []
