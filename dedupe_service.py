"""
FoodScout AI — Deduplication Service
Uses RapidFuzz to identify and merge duplicate restaurant entries.
Two restaurants are duplicates if name similarity > 90% and city matches.
"""

from __future__ import annotations
from loguru import logger
from rapidfuzz import fuzz


SIMILARITY_THRESHOLD = 90  # percent


def _normalize(name: str) -> str:
    """Normalize restaurant name for comparison."""
    import re
    name = name.lower().strip()
    # Remove common suffixes that vary
    name = re.sub(r"\b(restaurant|cafe|bistro|grill|bar|kitchen|house|eatery|diner)\b", "", name)
    # Remove punctuation
    name = re.sub(r"[^\w\s]", "", name)
    # Collapse whitespace
    name = re.sub(r"\s+", " ", name).strip()
    return name


def deduplicate(restaurants: list[dict]) -> list[dict]:
    """
    Remove duplicate restaurant entries using fuzzy name matching.
    When duplicates are found, the entry with higher confidence or more data is kept.
    The mentions count is aggregated across duplicates.

    Args:
        restaurants: List of restaurant dicts with at least 'name' and 'city' keys.

    Returns:
        Deduplicated list of restaurant dicts.
    """
    if not restaurants:
        return []

    # Group by city first for efficiency
    city_groups: dict[str, list[dict]] = {}
    for r in restaurants:
        city_key = r.get("city", "").lower().strip()
        city_groups.setdefault(city_key, []).append(r)

    unique: list[dict] = []

    for city_key, group in city_groups.items():
        clusters: list[list[dict]] = []  # each cluster = group of duplicates

        for restaurant in group:
            norm_name = _normalize(restaurant.get("name", ""))
            matched_cluster = None

            for cluster in clusters:
                cluster_norm = _normalize(cluster[0].get("name", ""))
                score = fuzz.ratio(norm_name, cluster_norm)
                if score >= SIMILARITY_THRESHOLD:
                    matched_cluster = cluster
                    break

            if matched_cluster is not None:
                matched_cluster.append(restaurant)
            else:
                clusters.append([restaurant])

        # Pick the best entry from each cluster
        for cluster in clusters:
            best = _pick_best(cluster)
            best["mention_count"] = len(cluster)  # Track how many sources mentioned it
            unique.append(best)

    before = len(restaurants)
    after = len(unique)
    logger.info(f"Deduplication: {before} → {after} unique restaurants ({before - after} duplicates removed)")
    return unique


def _pick_best(cluster: list[dict]) -> dict:
    """
    From a cluster of duplicate entries, pick the richest/most reliable one.
    Priority: verified with Google data > most reviews > highest confidence.
    """
    # Sort: prefer verified, then by review count, then by confidence
    def sort_key(r: dict):
        verified = 1 if r.get("verified") else 0
        reviews = r.get("review_count") or 0
        confidence = r.get("confidence_score") or 0
        return (verified, reviews, confidence)

    cluster_sorted = sorted(cluster, key=sort_key, reverse=True)
    best = dict(cluster_sorted[0])  # copy

    # Merge any fields missing in best from other cluster members
    for alt in cluster_sorted[1:]:
        for field in ["speciality", "area", "google_rating", "review_count",
                      "source_url", "youtube_channel", "google_maps_link"]:
            if not best.get(field) and alt.get(field):
                best[field] = alt[field]

    return best
