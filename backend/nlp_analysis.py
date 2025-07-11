import os
from functools import lru_cache
from typing import TypedDict

from transformers import pipeline


@lru_cache(maxsize=1)
def get_sentiment_pipeline():
    """Load a sentiment-analysis pipeline for Persian text."""
    model_name = os.getenv(
        "SENTIMENT_MODEL", "HooshvareLab/bert-base-parsbert-uncased-sentiment"
    )
    return pipeline("sentiment-analysis", model=model_name)


class SentimentResult(TypedDict):
    label: str
    score: float


def analyze_mental_state(text: str) -> SentimentResult:
    """Return sentiment scores for the given text."""
    if not text:
        return {"label": "neutral", "score": 0.0}
    nlp = get_sentiment_pipeline()
    result = nlp(text[:512])[0]  # Truncate to avoid very long inputs
    return {"label": result["label"], "score": float(result["score"])}
