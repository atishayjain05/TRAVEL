"""
FoodScout AI — YouTube Scraper (Playwright-based fallback)
Used when the YouTube Data API quota is exhausted.
Primary method: youtube_service.py uses the official API.
"""

from __future__ import annotations
import time
from loguru import logger

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


def scrape_youtube_search(query: str, max_results: int = 10) -> list[dict]:
    """
    Fallback YouTube scraper using Playwright.
    Searches YouTube and extracts video metadata from the results page.
    Only used when API quota is exceeded.
    """
    if not PLAYWRIGHT_AVAILABLE:
        logger.warning("Playwright not installed — cannot scrape YouTube.")
        return []

    videos = []
    search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                )
            )
            page = context.new_page()
            page.goto(search_url, timeout=30000)
            page.wait_for_selector("ytd-video-renderer", timeout=10000)

            video_elements = page.query_selector_all("ytd-video-renderer")[:max_results]

            for el in video_elements:
                try:
                    title_el = el.query_selector("#video-title")
                    channel_el = el.query_selector("ytd-channel-name")
                    if not title_el:
                        continue

                    title = title_el.inner_text().strip()
                    href = title_el.get_attribute("href") or ""
                    video_id = ""
                    if "v=" in href:
                        video_id = href.split("v=")[1].split("&")[0]

                    channel = channel_el.inner_text().strip() if channel_el else ""

                    if video_id:
                        videos.append({
                            "video_id": video_id,
                            "title": title,
                            "channel": channel,
                            "video_url": f"https://www.youtube.com/watch?v={video_id}",
                            "description": "",
                        })
                except Exception as e:
                    logger.debug(f"Error parsing YouTube result: {e}")
                    continue

            browser.close()
    except PWTimeout:
        logger.warning(f"YouTube scrape timed out for query: {query}")
    except Exception as e:
        logger.error(f"YouTube scrape failed: {e}")

    logger.info(f"YouTube scraper: found {len(videos)} videos for query='{query}'")
    return videos
