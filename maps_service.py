"""
FoodScout AI — Google Maps / Places API Enrichment Service
Verifies restaurant existence and enriches with official data.
"""

from __future__ import annotations
import re
import time
import requests
from typing import Optional
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
from backend.config import get_settings

settings = get_settings()

PLACES_FIND_URL = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
PLACES_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"
GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"


def _city_in_address(address: str, city: str) -> bool:
    """Check that the verified address belongs to the requested city."""
    city_lower = city.lower().strip()
    address_lower = address.lower()
    # Also handle common city name variations
    city_words = city_lower.split()
    return any(word in address_lower for word in city_words if len(word) > 3)


@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=5))
def verify_restaurant(name: str, city: str) -> Optional[dict]:
    """
    Search Google Places for a restaurant and return enriched data.
    Returns None if not found or not in the requested city.
    """
    if not settings.google_maps_api_key:
        logger.debug("No GOOGLE_MAPS_API_KEY — returning unverified entry.")
        return _unverified_entry(name, city)

    try:
        # Step 1: Find place
        find_params = {
            "input": f"{name} restaurant {city}",
            "inputtype": "textquery",
            "fields": "place_id,name,formatted_address",
            "key": settings.google_maps_api_key,
        }
        find_resp = requests.get(PLACES_FIND_URL, params=find_params, timeout=10)
        find_data = find_resp.json()

        candidates = find_data.get("candidates", [])
        if not candidates:
            return None

        candidate = candidates[0]
        address = candidate.get("formatted_address", "")
        place_id = candidate.get("place_id", "")
        found_name = candidate.get("name", name)

        # Check it's actually in the requested city
        if not _city_in_address(address, city):
            logger.debug(f"Place '{found_name}' not in city '{city}' — discarding.")
            return None

        # Step 2: Get details
        details_params = {
            "place_id": place_id,
            "fields": "name,rating,user_ratings_total,formatted_address,url,vicinity",
            "key": settings.google_maps_api_key,
        }
        details_resp = requests.get(PLACES_DETAILS_URL, params=details_params, timeout=10)
        details = details_resp.json().get("result", {})

        rating = details.get("rating")
        review_count = details.get("user_ratings_total", 0)
        full_address = details.get("formatted_address", address)
        maps_url = details.get("url", f"https://www.google.com/maps/place/?q=place_id:{place_id}")
        area = _extract_area(full_address, city)

        return {
            "name": details.get("name", found_name),
            "city": city,
            "area": area,
            "google_rating": float(rating) if rating else None,
            "review_count": int(review_count),
            "google_maps_link": maps_url,
            "verified": True,
        }

    except Exception as e:
        logger.warning(f"Google Maps lookup failed for '{name}': {e}")
        raise


def _extract_area(address: str, city: str) -> Optional[str]:
    """Try to extract neighborhood/area from a formatted address."""
    parts = [p.strip() for p in address.split(",")]
    city_lower = city.lower()
    for i, part in enumerate(parts):
        if city_lower in part.lower() and i > 0:
            return parts[i - 1]
    return None


def _unverified_entry(name: str, city: str) -> dict:
    """Return a minimal unverified entry when no API key is available."""
    return {
        "name": name,
        "city": city,
        "area": None,
        "google_rating": None,
        "review_count": 0,
        "google_maps_link": f"https://www.google.com/maps/search/{name.replace(' ', '+')}+{city.replace(' ', '+')}",
        "verified": False,
    }


def enrich_restaurants(
    restaurants: list[dict], city: str, delay: float = 0.3
) -> list[dict]:
    """
    Batch-enrich a list of extracted restaurant names via Google Places.
    Drops restaurants that cannot be verified in the city.
    """
    enriched: list[dict] = []

    for r in restaurants:
        name = r.get("name", "")
        if not name:
            continue
        result = verify_restaurant(name, city)
        if result:
            result["speciality"] = r.get("speciality")
            enriched.append(result)
        time.sleep(delay)  # Rate limiting

    logger.info(
        f"Maps: enriched {len(enriched)}/{len(restaurants)} restaurants for '{city}'"
    )
    return enriched
