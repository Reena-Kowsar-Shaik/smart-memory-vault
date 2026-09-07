"""
nlp_engine package
Central NLP intelligence facade for Smart Memory Vault
"""

from .categorizer import MemoryCategorizer
from .sentiment import SentimentAndImportanceEngine
from .summarizer import TextSummarizer
from .search_engine import SemanticSearchEngine
from .quiz_generator import StudyQuizEngine

# Instantiate singleton engines
categorizer = MemoryCategorizer()
sentiment_engine = SentimentAndImportanceEngine()
summarizer = TextSummarizer()
search_engine = SemanticSearchEngine()
quiz_engine = StudyQuizEngine()

def process_memory(text: str, title: str = "") -> dict:
    """
    All-in-one helper for Member 1 & Member 2:
    Takes note or document text and returns full AI metadata.
    """
    full_text = f"{title}\n{text}".strip()
    category = categorizer.predict_category(full_text)
    tags = categorizer.extract_tags(full_text)
    summary = summarizer.summarize(text)
    sentiment_data = sentiment_engine.analyze(full_text)

    return {
        "category": category,
        "tags": tags,
        "summary": summary,
        "sentiment": sentiment_data["sentiment"],
        "polarity_score": sentiment_data["polarity_score"],
        "importance": sentiment_data["importance"]
    }
