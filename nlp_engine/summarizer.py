"""
nlp_engine/summarizer.py
Extractive Text & Document Summarizer (Paragraphs & Bullet points)
"""

import re
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize

class TextSummarizer:
    def __init__(self):
        try:
            self.stop_words = set(stopwords.words('english'))
        except Exception:
            self.stop_words = set()

    def summarize(self, text: str, max_sentences: int = 3) -> str:
        """Generates a concise paragraph summary from text."""
        if not text or not text.strip():
            return ""

        try:
            sentences = sent_tokenize(text)
        except Exception:
            sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]

        if len(sentences) <= max_sentences:
            return text.strip()

        words = [w.lower() for w in re.findall(r'\b[a-zA-Z]{3,}\b', text) if w.lower() not in self.stop_words]
        if not words:
            return " ".join(sentences[:max_sentences])

        word_freq = Counter(words)
        max_freq = max(word_freq.values()) if word_freq else 1
        norm_freq = {k: v / max_freq for k, v in word_freq.items()}

        sentence_scores = {}
        for idx, sent in enumerate(sentences):
            sent_words = re.findall(r'\b[a-zA-Z]{3,}\b', sent.lower())
            sentence_scores[idx] = sum(norm_freq.get(w, 0) for w in sent_words)

        # Select top scoring sentences and maintain chronological order
        top_indices = sorted(sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:max_sentences])
        return " ".join([sentences[i] for i in top_indices])

    def generate_bullets(self, text: str, max_points: int = 4) -> list[str]:
        """Generates key bullet points."""
        summary = self.summarize(text, max_sentences=max_points)
        try:
            sentences = sent_tokenize(summary)
        except Exception:
            sentences = [s.strip() for s in summary.split(". ") if s.strip()]
        return [f"• {s.strip()}" for s in sentences if s.strip()]
