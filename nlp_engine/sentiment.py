"""
nlp_engine/sentiment.py
Sentiment Analysis & Urgency/Importance Level (1 to 5)
"""

import re
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# VADER loaded safely with fallback

URGENT_KEYWORDS = [
    "urgent", "asap", "emergency", "deadline", "immediately", "critical",
    "due tomorrow", "penalty", "due date", "warning", "crucial", "must", "expire"
]

HIGH_PRIORITY_KEYWORDS = [
    "hospital", "doctor", "surgery", "prescription", "tax", "loan", "bank",
    "payment", "exam", "interview", "flight", "visa", "court"
]

class SentimentAndImportanceEngine:
    def __init__(self):
        try:
            self.sia = SentimentIntensityAnalyzer()
        except Exception:
            self.sia = None

    def analyze(self, text: str) -> dict:
        """
        Analyzes memory text for:
        - sentiment: 'Positive', 'Neutral', 'Negative', or 'Urgent / Critical'
        - polarity_score: float (-1.0 to 1.0)
        - importance: int (1 to 5 stars)
        """
        if not text or not text.strip():
            return {"sentiment": "Neutral", "polarity_score": 0.0, "importance": 1}

        text_lower = text.lower()

        # Check urgency and high priority markers
        has_urgency = any(re.search(rf"\b{re.escape(w)}\b", text_lower) for w in URGENT_KEYWORDS)
        has_high_priority = any(re.search(rf"\b{re.escape(w)}\b", text_lower) for w in HIGH_PRIORITY_KEYWORDS)

        # Sentiment polarity calculation
        if self.sia:
            scores = self.sia.polarity_scores(text)
            compound = scores['compound']
        else:
            pos_words = {'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'happy', 'joy', 'love', 'best', 'blessed', 'success', 'successful', 'achieved', 'achievement', 'peace', 'celebrate', 'fun', 'proud', 'awesome'}
            neg_words = {'bad', 'terrible', 'horrible', 'awful', 'sad', 'depressed', 'unhappy', 'angry', 'pain', 'loss', 'fail', 'failed', 'failure', 'crisis', 'disaster', 'worried', 'stress', 'disappointed'}
            words = set(re.findall(r'[a-z]+', text_lower))
            pos_matches = len(words & pos_words)
            neg_matches = len(words & neg_words)
            if pos_matches > neg_matches:
                compound = min(1.0, 0.4 + 0.2 * (pos_matches - neg_matches))
            elif neg_matches > pos_matches:
                compound = max(-1.0, -0.4 - 0.2 * (neg_matches - pos_matches))
            else:
                compound = 0.0

        if has_urgency:
            sentiment_label = "Urgent / Critical"
        elif compound >= 0.05:
            sentiment_label = "Positive"
        elif compound <= -0.05:
            sentiment_label = "Negative"
        else:
            sentiment_label = "Neutral"

        # Calculate Importance Level from 1 to 5
        importance = 2  # base level
        if has_high_priority:
            importance += 1
        if has_urgency:
            importance += 2
        if len(text.split()) > 100:  # Long detailed memory
            importance += 1

        importance = max(1, min(5, importance))

        return {
            "sentiment": sentiment_label,
            "polarity_score": round(compound, 2),
            "importance": importance
        }
