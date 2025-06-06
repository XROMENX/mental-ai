from datetime import datetime
from typing import Optional, Tuple, List


def calculate_level_and_badges(xp: int) -> Tuple[int, List[str]]:
    """Return level and list of badges based on XP."""
    level = xp // 100 + 1
    badges: List[str] = []
    if xp >= 100:
        badges.append("Novice")
    if xp >= 500:
        badges.append("Expert")
    return level, badges


def calculate_streak(last_entry: Optional[datetime], previous_streak: int) -> int:
    """Calculate new streak length based on last entry date."""
    today = datetime.utcnow().date()
    if last_entry is None:
        return 1
    last_date = last_entry.date()
    if last_date == today:
        return previous_streak
    if (today - last_date).days == 1:
        return previous_streak + 1
    return 1
