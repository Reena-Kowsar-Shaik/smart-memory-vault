"""
nlp_engine/search_engine.py
Semantic & Natural Language Search using TF-IDF and Cosine Similarity
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class SemanticSearchEngine:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')

    def search(self, query: str, memories: list[dict], top_k: int = 5) -> list[dict]:
        """
        Searches memories by relevance to the query.
        memories: list of dicts [{'id': 1, 'title': '...', 'content': '...'}, ...]
        Returns sorted memories matching user intent with similarity scores.
        """
        if not memories or not query or not query.strip():
            return []

        # Prepare corpus: combine title, content, tags, category
        corpus = [
            f"{m.get('title', '')} {m.get('content', '')} {m.get('category', '')} {' '.join(m.get('tags', []))}"
            for m in memories
        ]

        try:
            tfidf_matrix = self.vectorizer.fit_transform(corpus)
            query_vec = self.vectorizer.transform([query])
            similarities = cosine_similarity(query_vec, tfidf_matrix)[0]

            # Pair memory with similarity score
            results = []
            for idx, score in enumerate(similarities):
                if score > 0.05:  # Relevance threshold
                    mem_copy = memories[idx].copy()
                    mem_copy['similarity_score'] = round(float(score), 3)
                    results.append(mem_copy)

            # Sort descending by similarity
            results.sort(key=lambda x: x['similarity_score'], reverse=True)
            return results[:top_k]

        except Exception:
            # Fallback simple keyword match
            query_lower = query.lower()
            return [m for m in memories if query_lower in m.get('content', '').lower()][:top_k]
