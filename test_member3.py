"""
test_nlp.py
Comprehensive test suite for Member 3: AI & NLP Intelligence Engine
Tests: Categorization, Tagging, Sentiment, Importance, Summarization, and Semantic Search.
"""

import unittest
from nlp_engine import categorizer, sentiment_engine, summarizer, search_engine, process_memory


class TestNLPEngine(unittest.TestCase):

    def test_01_categorization_health(self):
        """Test health-related classification"""
        text = "Dr. Robert prescribed blood pressure medicine at Apollo Hospital."
        category = categorizer.predict_category(text)
        self.assertEqual(category, "Health")

    def test_02_categorization_finance(self):
        """Test finance-related classification"""
        text = "Transferred monthly salary and paid income tax via bank investment portal."
        category = categorizer.predict_category(text)
        self.assertEqual(category, "Finance")

    def test_03_categorization_work(self):
        """Test work-related classification"""
        text = "Attended sprint planning meeting with the project manager and client."
        category = categorizer.predict_category(text)
        self.assertEqual(category, "Work")

    def test_04_categorization_study(self):
        """Test study-related classification"""
        text = "Preparing for university semester exams and submitted research thesis."
        category = categorizer.predict_category(text)
        self.assertEqual(category, "Study")

    def test_05_tag_extraction(self):
        """Test keyword tag extraction"""
        text = "Doctor appointment tomorrow morning to check blood sugar levels."
        tags = categorizer.extract_tags(text, top_n=3)
        self.assertIsInstance(tags, list)
        self.assertTrue(len(tags) > 0)
        self.assertIn("doctor", tags)

    def test_06_urgency_and_importance_high(self):
        """Test urgency detection and max importance score (5 stars)"""
        text = "URGENT: Emergency hospital visit required immediately, strict deadline!"
        result = sentiment_engine.analyze(text)
        self.assertEqual(result["sentiment"], "Urgent / Critical")
        self.assertEqual(result["importance"], 5)

    def test_07_sentiment_positive(self):
        """Test positive sentiment detection"""
        text = "Had a wonderful family vacation at the beach with amazing friends!"
        result = sentiment_engine.analyze(text)
        self.assertEqual(result["sentiment"], "Positive")
        self.assertGreater(result["polarity_score"], 0)

    def test_08_summarizer(self):
        """Test paragraph summarization and bullet point generation"""
        long_text = (
            "The team met on Monday to discuss the quarterly product roadmap. "
            "Several key bugs were identified and assigned to the backend engineers. "
            "A new release candidate is scheduled for deployment next Friday. "
            "All stakeholders approved the proposed timeline and budget."
        )
        summary = summarizer.summarize(long_text, max_sentences=2)
        bullets = summarizer.generate_bullets(long_text, max_points=2)

        self.assertTrue(len(summary) > 0)
        self.assertTrue(len(summary) < len(long_text))
        self.assertIsInstance(bullets, list)
        self.assertTrue(len(bullets) <= 2)

    def test_09_semantic_search(self):
        """Test semantic search matching intent (hospital visit -> doctor appointment)"""
        memories = [
            {"id": 1, "title": "Trip to Paris", "content": "Visited Eiffel Tower and had croissants", "category": "Personal", "tags": ["travel"]},
            {"id": 2, "title": "Health Checkup", "content": "Doctor appointment and prescription refill", "category": "Health", "tags": ["medicine"]},
            {"id": 3, "title": "Budget Review", "content": "Reviewed monthly bank expenses and taxes", "category": "Finance", "tags": ["money"]}
        ]

        # Search query intent
        query = "hospital visit"
        results = search_engine.search(query, memories, top_k=1)

        self.assertTrue(len(results) > 0)
        # Should match Memory #2 (Health Checkup) with highest relevance
        self.assertEqual(results[0]["id"], 2)

    def test_10_facade_process_memory(self):
        """Test the all-in-one process_memory helper for teammates"""
        result = process_memory(
            text="Meeting with client to sign consulting contract next week.",
            title="Work Contract"
        )
        self.assertIn("category", result)
        self.assertIn("tags", result)
        self.assertIn("summary", result)
        self.assertIn("sentiment", result)
        self.assertIn("importance", result)
        self.assertEqual(result["category"], "Work")


if __name__ == "__main__":
    print("\n🔍 Running Member 3 NLP Engine Test Suite...\n" + "=" * 50)
    unittest.main(verbosity=2)
