import unittest
from datetime import datetime, timedelta
from analytics.streak_tracker import calculate_user_streaks, calculate_achievement_badges, BADGES_DEFINITION


class TestStreakTracker(unittest.TestCase):

    def setUp(self):
        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)
        two_days_ago = today - timedelta(days=2)

        self.sample_memories = [
            {
                "id": 1,
                "title": "Study Note 1",
                "category": "Study",
                "tags": ["python", "voice"],
                "created_at": two_days_ago.strftime("%Y-%m-%d")
            },
            {
                "id": 2,
                "title": "Study Note 2",
                "category": "Study",
                "tags": ["image", "ocr"],
                "created_at": yesterday.strftime("%Y-%m-%d")
            },
            {
                "id": 3,
                "title": "Study Note 3",
                "category": "Study",
                "tags": ["youtube", "video"],
                "created_at": today.strftime("%Y-%m-%d")
            }
        ]

    def test_calculate_user_streaks(self):
        streak = calculate_user_streaks(self.sample_memories)
        self.assertEqual(streak["current_streak"], 3)
        self.assertGreaterEqual(streak["longest_streak"], 3)
        self.assertTrue(streak["active_today"])
        self.assertEqual(streak["today_count"], 1)
        self.assertEqual(streak["total_active_days"], 3)

    def test_empty_streaks(self):
        streak = calculate_user_streaks([])
        self.assertEqual(streak["current_streak"], 0)
        self.assertFalse(streak["active_today"])
        self.assertEqual(streak["total_active_days"], 0)

    def test_calculate_achievement_badges(self):
        streak = calculate_user_streaks(self.sample_memories)
        badges = calculate_achievement_badges(self.sample_memories, streak)

        self.assertEqual(len(badges), len(BADGES_DEFINITION))
        
        # Check First Step unlocked
        first_step = next(b for b in badges if b["id"] == "first_step")
        self.assertTrue(first_step["unlocked"])

        # Check Scholar unlocked (3 study notes)
        scholar = next(b for b in badges if b["id"] == "scholar")
        self.assertTrue(scholar["unlocked"])

        # Check Voice Pioneer unlocked
        voice = next(b for b in badges if b["id"] == "voice_pioneer")
        self.assertTrue(voice["unlocked"])

        # Check 3-Day Streak unlocked
        streak_3 = next(b for b in badges if b["id"] == "streak_3")
        self.assertTrue(streak_3["unlocked"])


if __name__ == "__main__":
    unittest.main()
