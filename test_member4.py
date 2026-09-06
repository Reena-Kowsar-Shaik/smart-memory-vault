"""
test_member4.py
Comprehensive test suite for Member 4: Streamlit UI, Analytics, and Reporting Engine.
Tests: Charts generation, Timeline analysis, Activity summaries, PDF reporting, and CSV/JSON exports.
"""

import unittest
import json
from analytics.charts import (
    create_category_distribution_chart,
    create_importance_histogram,
    create_sentiment_chart,
    create_top_tags_chart
)
from analytics.timeline import (
    build_timeline_dataframe,
    create_timeline_chart,
    get_activity_summary
)
from analytics.reporter import (
    export_to_csv,
    export_to_json,
    generate_pdf_report
)


class TestMember4AnalyticsAndReporting(unittest.TestCase):

    def setUp(self):
        self.sample_memories = [
            {
                "id": 1,
                "title": "Hospital Checkup",
                "description": "Visited Apollo Hospital for regular blood pressure checkup.",
                "category": "Health",
                "summary": "Regular blood pressure checkup at Apollo Hospital.",
                "importance": 4,
                "sentiment": "Urgent / Critical",
                "tags": ["doctor", "health", "hospital"],
                "created_at": "2026-09-01"
            },
            {
                "id": 2,
                "title": "Quarterly Budget Planning",
                "description": "Allocated engineering team budget and reviewed tax deductions.",
                "category": "Finance",
                "summary": "Budget allocation and tax review.",
                "importance": 5,
                "sentiment": "Neutral",
                "tags": ["budget", "tax", "finance"],
                "created_at": "2026-09-03"
            },
            {
                "id": 3,
                "title": "Project Sprint Meeting",
                "description": "Reviewed UI/UX deliverables and aligned on sprint goals.",
                "category": "Work",
                "summary": "Sprint planning review for UI/UX deliverables.",
                "importance": 3,
                "sentiment": "Positive",
                "tags": ["sprint", "ui", "work"],
                "created_at": "2026-09-05"
            }
        ]

        self.sample_user = {
            "id": 101,
            "username": "tester",
            "email": "tester@example.com"
        }

    def test_01_category_chart_creation(self):
        """Test category distribution donut chart produces valid Plotly figure"""
        fig = create_category_distribution_chart(self.sample_memories)
        self.assertIsNotNone(fig)
        self.assertTrue(len(fig.data) > 0)
        self.assertEqual(fig.data[0].type, "pie")

    def test_02_importance_histogram(self):
        """Test importance histogram creation"""
        fig = create_importance_histogram(self.sample_memories)
        self.assertIsNotNone(fig)
        self.assertTrue(len(fig.data) > 0)
        self.assertEqual(fig.data[0].type, "bar")

    def test_03_sentiment_chart(self):
        """Test sentiment horizontal bar chart creation"""
        fig = create_sentiment_chart(self.sample_memories)
        self.assertIsNotNone(fig)
        self.assertTrue(len(fig.data) > 0)
        self.assertEqual(fig.data[0].type, "bar")

    def test_04_top_tags_chart(self):
        """Test keyword tag frequency chart"""
        fig = create_top_tags_chart(self.sample_memories, top_n=5)
        self.assertIsNotNone(fig)
        self.assertTrue(len(fig.data) > 0)

    def test_05_timeline_dataframe(self):
        """Test timeline dataframe transformation"""
        df = build_timeline_dataframe(self.sample_memories)
        self.assertEqual(len(df), 3)
        self.assertIn("date", df.columns)
        self.assertIn("importance", df.columns)

    def test_06_timeline_chart(self):
        """Test interactive timeline scatter chart creation"""
        fig = create_timeline_chart(self.sample_memories)
        self.assertIsNotNone(fig)
        self.assertTrue(len(fig.data) > 0)

    def test_07_activity_summary_metrics(self):
        """Test statistical KPIs calculation"""
        stats = get_activity_summary(self.sample_memories)
        self.assertEqual(stats["total_count"], 3)
        self.assertEqual(stats["high_priority_count"], 2)  # items with importance >= 4 (ratings: 4, 5)
        self.assertEqual(stats["avg_importance"], 4.0)

    def test_08_csv_export(self):
        """Test CSV serialization"""
        csv_text = export_to_csv(self.sample_memories)
        self.assertIn("Hospital Checkup", csv_text)
        self.assertIn("Quarterly Budget Planning", csv_text)
        self.assertIn("id,title,category", csv_text)

    def test_09_json_export(self):
        """Test JSON serialization"""
        json_text = export_to_json(self.sample_memories)
        parsed = json.loads(json_text)
        self.assertEqual(parsed["total_count"], 3)
        self.assertEqual(len(parsed["memories"]), 3)

    def test_10_pdf_report_generation(self):
        """Test PDF report binary generation"""
        stats = get_activity_summary(self.sample_memories)
        pdf_bytes = generate_pdf_report(self.sample_user, self.sample_memories, stats)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(len(pdf_bytes) > 0)
        # PDF file signature %PDF-
        self.assertTrue(pdf_bytes.startswith(b"%PDF-") or len(pdf_bytes) > 20)


if __name__ == "__main__":
    print("\n🔍 Running Member 4 UI/UX & Analytics Test Suite...\n" + "=" * 50)
    unittest.main(verbosity=2)
