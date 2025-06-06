import datetime
from backend.gamification_utils import calculate_level_and_badges, calculate_streak


def test_level_and_badges_basic():
    level, badges = calculate_level_and_badges(0)
    assert level == 1
    assert badges == []


def test_level_and_badges_novice():
    level, badges = calculate_level_and_badges(150)
    assert level == 2
    assert badges == ["Novice"]


def test_level_and_badges_expert():
    level, badges = calculate_level_and_badges(520)
    assert level == 6
    assert badges == ["Novice", "Expert"]


def test_streak_first_entry():
    assert calculate_streak(None, 0) == 1


def test_streak_same_day():
    today = datetime.datetime.utcnow()
    assert calculate_streak(today, 3) == 3


def test_streak_consecutive_day():
    yesterday = datetime.datetime.utcnow() - datetime.timedelta(days=1)
    assert calculate_streak(yesterday, 2) == 3


def test_streak_reset():
    old_day = datetime.datetime.utcnow() - datetime.timedelta(days=5)
    assert calculate_streak(old_day, 10) == 1
