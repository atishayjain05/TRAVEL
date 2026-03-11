"""
FoodScout AI — Confidence Scoring Service
Calculates a 0–100 confidence score for each restaurant based on:
  - Number of source mentions (max 40 points)
  - Google review count (max 30 points)
  - Google rating (max 30 points)
"""

from __future__ import annotations
import math
from loguru import logger


def calculate_score(
    mention_count: int,
    review_count: int,
    google_rating: float | None,
) -> int:
    """
    Compute confidence score (0–100) for a restaurant.

    - Mention score (0–40): log-scaled on number of source mentions
    - Review score (0–30): log-scaled on Google review count
    - Rating score (0–30): linear on Google rating (0–5)
    """
    # Mention score: log scale, capped at 40
    # 1 mention → ~0, 3 → ~19, 10 → ~37, 20+ → ~40
    mention_score = min(40, int(math.log1p(mention_count) / math.log1p(20) * 40))

    # Review score: log scale, capped at 30
    # 0 reviews → 0, 100 → ~15, 1000 → ~22, 10000+ → ~30
    review_score = min(30, int(math.log1p(review_count) / math.log1p(10000) * 30))

    # Rating score: linear 0–5 mapped to 0–30
    if google_rating and google_rating > 0:
        rating_score = min(30, int((google_rating / 5.0) * 30))
    else:
        rating_score = 0

    total = mention_score + review_score + rating_score
    return max(0, min(100, total))


def score_restaurants(restaurants: list[dict]) -> list[dict]:
    """
    Apply confidence scoring to a list of restaurant dicts in-place.
    Adds 'confidence_score' field to each restaurant.
    """
    for r in restaurants:
        mention_count = r.get("mention_count", 1)
        review_count = r.get("review_count") or 0
        google_rating = r.get("google_rating")

        score = calculate_score(
            mention_count=mention_count,
            review_count=review_count,
            google_rating=float(google_rating) if google_rating else None,
        )
        r["confidence_score"] = score

    # Log distribution summary
    if restaurants:
        scores = [r["confidence_score"] for r in restaurants]
        avg = sum(scores) / len(scores)
        logger.info(
            f"Scoring: {len(restaurants)} restaurants scored. "
            f"Avg={avg:.1f}, Min={min(scores)}, Max={max(scores)}"
        )

    return restaurants
