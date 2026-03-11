"""
FoodScout AI — Instagram Reels Discovery Service
Uses Playwright to scrape Instagram food content for a city.
"""

from __future__ import annotations
import re
import time
from typing import Optional
from loguru import logger

try:
    from scrapers.instagram_scraper import scrape_instagram_reels
except ImportError:
    scrape_instagram_reels = None  # type: ignore


SEARCH_QUERIES = [
    "{city} food",
    "{city} street food",
    "{city} foodie",
    "{city} restaurant",
    "{city} musteat",
]


def collect_instagram_content(city: str, max_posts: int = 30) -> list[dict]:
    """
    Collect Instagram reel/post content for restaurant discovery.
    Returns list of post dicts with caption and metadata.
    """
    if scrape_instagram_reels is None:
        logger.warning("Instagram scraper not available — skipping Instagram source.")
        return []

    posts: list[dict] = []
    seen_urls: set[str] = set()
    per_query = max(5, max_posts // len(SEARCH_QUERIES))

    for query_template in SEARCH_QUERIES:
        query = query_template.format(city=city)
        hashtag = query.replace(" ", "").lower()
        try:
            results = scrape_instagram_reels(hashtag=hashtag, max_posts=per_query)
            for post in results:
                url = post.get("url", "")
                if url in seen_urls:
                    continue
                seen_urls.add(url)
                caption = post.get("caption", "")
                comments = post.get("comments", [])
                # Combine caption + top comments for richer extraction
                content = caption + "\n" + "\n".join(comments[:5])
                posts.append(
                    {
                        "source_type": "instagram",
                        "url": url,
                        "content": content,
                        "query": query,
                        "location_tag": post.get("location", ""),
                    }
                )
                if len(posts) >= max_posts:
                    break
        except Exception as e:
            logger.warning(f"Instagram scrape failed for hashtag '{hashtag}': {e}")

        if len(posts) >= max_posts:
            break

    logger.info(f"Instagram: collected {len(posts)} posts for city='{city}'")
    return posts
