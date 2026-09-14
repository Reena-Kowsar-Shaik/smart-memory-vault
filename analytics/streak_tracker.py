"""
analytics/streak_tracker.py
Daily Study Streaks, Habit Heatmaps, and Gamified Achievement Badges for Smart Memory Vault.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple


BADGES_DEFINITION = [
    {
        "id": "first_step",
        "title": "🌟 First Step",
        "description": "Created your very first memory in the vault.",
        "icon": "🌟",
        "condition_type": "min_memories",
        "threshold": 1
    },
    {
        "id": "scholar",
        "title": "📚 Scholar",
        "description": "Logged 3 or more Study/Research memories.",
        "icon": "📚",
        "condition_type": "category_count",
        "category": "Study",
        "threshold": 3
    },
    {
        "id": "voice_pioneer",
        "title": "🎙️ Voice Pioneer",
        "description": "Recorded an audio note or voice transcription.",
        "icon": "🎙️",
        "condition_type": "tag_present",
        "tag": "voice",
        "threshold": 1
    },
    {
        "id": "ocr_visionary",
        "title": "📸 OCR Visionary",
        "description": "Extracted text from a whiteboard, certificate, or image.",
        "icon": "📸",
        "condition_type": "tag_present",
        "tag": "image",
        "threshold": 1
    },
    {
        "id": "video_scholar",
        "title": "📺 Video Scholar",
        "description": "Ingested a YouTube video transcript or web article.",
        "icon": "📺",
        "condition_type": "tag_present",
        "tag": "youtube",
        "threshold": 1
    },
    {
        "id": "streak_3",
        "title": "🔥 3-Day Streak",
        "description": "Maintained an active study habit for 3 consecutive days.",
        "icon": "🔥",
        "condition_type": "min_streak",
        "threshold": 3
    },
    {
        "id": "streak_7",
        "title": "⚡ 7-Day Master",
        "description": "Maintained a streak for 7 consecutive days.",
        "icon": "⚡",
        "condition_type": "min_streak",
        "threshold": 7
    },
    {
        "id": "vault_grandmaster",
        "title": "💎 Vault Master",
        "description": "Built a rich knowledge repository with 10+ memories.",
        "icon": "💎",
        "condition_type": "min_memories",
        "threshold": 10
    }
]


def calculate_user_streaks(memories: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculates consecutive active day streaks and weekly activity breakdown.
    """
    if not memories:
        return {
            "current_streak": 0,
            "longest_streak": 0,
            "active_today": False,
            "today_count": 0,
            "total_active_days": 0,
            "weekly_activity": {day: 0 for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]}
        }

    # Extract dates of memory creations
    active_dates = set()
    today_date = datetime.utcnow().date()
    today_count = 0

    weekly_activity = {"Mon": 0, "Tue": 0, "Wed": 0, "Thu": 0, "Fri": 0, "Sat": 0, "Sun": 0}
    seven_days_ago = today_date - timedelta(days=6)

    for m in memories:
        raw_date = m.get("created_at", "")
        if not raw_date:
            continue
        try:
            # Format: 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'
            date_str = str(raw_date)[:10]
            dt = datetime.strptime(date_str, "%Y-%m-%d").date()
            active_dates.add(dt)

            if dt == today_date:
                today_count += 1

            if dt >= seven_days_ago:
                day_name = dt.strftime("%a")
                if day_name in weekly_activity:
                    weekly_activity[day_name] += 1
        except Exception:
            pass

    if not active_dates:
        return {
            "current_streak": 0,
            "longest_streak": 0,
            "active_today": False,
            "today_count": 0,
            "total_active_days": 0,
            "weekly_activity": weekly_activity
        }

    sorted_dates = sorted(list(active_dates))

    # Calculate Current Streak
    current_streak = 0
    check_date = today_date
    active_today = today_date in active_dates

    # If not active today, check if active yesterday (grace period)
    if not active_today:
        check_date = today_date - timedelta(days=1)

    while check_date in active_dates:
        current_streak += 1
        check_date -= timedelta(days=1)

    # Calculate Longest Streak
    longest_streak = 1 if sorted_dates else 0
    running_streak = 1

    for i in range(1, len(sorted_dates)):
        if sorted_dates[i] == sorted_dates[i - 1] + timedelta(days=1):
            running_streak += 1
            longest_streak = max(longest_streak, running_streak)
        else:
            running_streak = 1

    longest_streak = max(longest_streak, current_streak)

    return {
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "active_today": active_today,
        "today_count": today_count,
        "total_active_days": len(active_dates),
        "weekly_activity": weekly_activity
    }


def calculate_achievement_badges(memories: List[Dict[str, Any]], streak_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Evaluates which achievement badges the user has unlocked.
    """
    total_memories = len(memories)
    current_streak = streak_data.get("current_streak", 0)
    longest_streak = streak_data.get("longest_streak", 0)
    max_streak = max(current_streak, longest_streak)

    # Pre-compute counts
    category_counts = {}
    all_tags = set()

    for m in memories:
        cat = m.get("category", "General")
        category_counts[cat] = category_counts.get(cat, 0) + 1
        tags = m.get("tags", [])
        if isinstance(tags, list):
            for t in tags:
                all_tags.add(str(t).lower())

    results = []
    for badge in BADGES_DEFINITION:
        unlocked = False
        progress = 0
        target = badge["threshold"]
        c_type = badge["condition_type"]

        if c_type == "min_memories":
            progress = min(total_memories, target)
            unlocked = total_memories >= target

        elif c_type == "min_streak":
            progress = min(max_streak, target)
            unlocked = max_streak >= target

        elif c_type == "category_count":
            cat_name = badge.get("category", "")
            cnt = category_counts.get(cat_name, 0)
            progress = min(cnt, target)
            unlocked = cnt >= target

        elif c_type == "tag_present":
            target_tag = badge.get("tag", "")
            has_tag = any(target_tag in t for t in all_tags)
            progress = 1 if has_tag else 0
            unlocked = has_tag

        results.append({
            "id": badge["id"],
            "title": badge["title"],
            "description": badge["description"],
            "icon": badge["icon"],
            "unlocked": unlocked,
            "progress": progress,
            "target": target,
            "pct": int((progress / target) * 100) if target > 0 else 100
        })

    return results
