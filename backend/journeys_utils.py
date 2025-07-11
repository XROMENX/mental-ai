"""Utility functions for Fabulous-style habit-building journeys."""

from typing import List, Dict


def get_default_journeys() -> List[Dict[str, object]]:
    """Return a list of default habit-building journeys."""
    return [
        {
            "id": "morning-routine",
            "name": "Morning Routine Kickstart",
            "description": "Simple steps to start your day energized",
            "tasks": [
                "Wake up at the same time each day",
                "Drink a glass of water",
                "Do 5 minutes of stretching or light exercise",
            ],
        },
        {
            "id": "mindfulness-master",
            "name": "Mindfulness Master",
            "description": "Daily practices for a calmer mind",
            "tasks": [
                "Practice 3 minutes of deep breathing",
                "Record a short gratitude note",
                "Take a mindful walk or body scan",
            ],
        },
        {
            "id": "sleep-champion",
            "name": "Sleep Champion",
            "description": "Improve sleep habits for better rest",
            "tasks": [
                "Set a consistent bedtime",
                "Avoid screens 30 minutes before sleep",
                "Create a relaxing pre-sleep ritual",
            ],
        },
    ]
