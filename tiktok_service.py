"""
FoodScout AI — TikTok Discovery Service
Uses Playwright to scrape TikTok food content for a city.
"""

from __future__ import annotations
from loguru import logger

try:
    from scrapers.tiktok_scraper import scrape_tiktok_videos
except ImportError:
    scrape_tiktok_videos = None  # type: ignore


SEARCH_QUERIES = [
    "{city} food",
    "{city} restaurant",
    "{city} streetfood",
    "{city} foodtour",
    "{city} foodie",
]


def collect_tiktok_content(city: str, max_videos: int = 30) -> list[dict]:
    """
    Collect TikTok video content for restaurant discovery.
    Returns list of video dicts with description, hashtags, and comments.
    """
    if scrape_tiktok_videos is None:
        logger.warning("TikTok scraper not available — skipping TikTok source.")
        return []

    videos: list[dict] = []
    seen_urls: set[str] = set()
    per_query = max(5, max_videos // len(SEARCH_QUERIES))

    for query_template in SEARCH_QUERIES:
        query = query_template.format(city=city)
        try:
            results = scrape_tiktok_videos(query=query, max_videos=per_query)
            for video in results:
                url = video.get("url", "")
                if url in seen_urls:
                    continue
                seen_urls.add(url)

                description = video.get("description", "")
                hashtags = " ".join(video.get("hashtags", []))
                comments = "\n".join(video.get("comments", [])[:5])
                content = f"{description}\n{hashtags}\n{comments}"

                videos.append(
                    {
                        "source_type": "tiktok",
                        "url": url,
                        "content": content,
                        "query": query,
                        "channel": video.get("author", ""),
                    }
                )
                if len(videos) >= max_videos:
                    break
        except Exception as e:
            logger.warning(f"TikTok scrape failed for query '{query}': {e}")

        if len(videos) >= max_videos:
            break

    logger.info(f"TikTok: collected {len(videos)} videos for city='{city}'")
    return videos
