"""
FoodScout AI — TikTok Scraper (Playwright)
Scrapes TikTok search results for food-related videos in a city.

Note: TikTok's anti-bot detection is strong.
Headless Chromium with realistic fingerprints improves success rate.
"""

from __future__ import annotations
import re
import time
import json
from loguru import logger

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


def scrape_tiktok_videos(query: str, max_videos: int = 15) -> list[dict]:
    """
    Scrape TikTok search results for a given query.
    Returns list of video dicts: {url, description, hashtags, author, comments}.
    """
    if not PLAYWRIGHT_AVAILABLE:
        logger.warning("Playwright not installed — cannot scrape TikTok.")
        return []

    videos = []
    search_url = f"https://www.tiktok.com/search?q={query.replace(' ', '%20')}"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                ],
            )
            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36 TikTok"
                ),
                viewport={"width": 1280, "height": 800},
            )

            # Remove navigator.webdriver detection
            context.add_init_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )

            page = context.new_page()

            try:
                page.goto(search_url, timeout=30000, wait_until="networkidle")
            except PWTimeout:
                logger.warning(f"TikTok search timeout for query: {query}")
                # Try to proceed anyway
                pass

            time.sleep(3)

            # Collect video links
            video_links = page.query_selector_all("a[href*='/video/']")
            video_urls = []
            for link in video_links[:max_videos * 2]:
                href = link.get_attribute("href") or ""
                if "/video/" in href:
                    full_url = href if href.startswith("http") else f"https://www.tiktok.com{href}"
                    if full_url not in video_urls:
                        video_urls.append(full_url)

            # Scrape each video for description
            for video_url in video_urls[:max_videos]:
                try:
                    page.goto(video_url, timeout=20000, wait_until="domcontentloaded")
                    time.sleep(2)

                    # Get video description
                    desc = ""
                    desc_el = page.query_selector("h1[data-e2e='browse-video-desc'], span[data-e2e='video-desc']")
                    if desc_el:
                        desc = desc_el.inner_text().strip()

                    # Extract hashtags
                    hashtag_els = page.query_selector_all("a[href*='/tag/']")
                    hashtags = [el.inner_text().strip().lstrip("#") for el in hashtag_els]

                    # Get author name
                    author = ""
                    author_el = page.query_selector("span[data-e2e='browse-username'], a[data-e2e='video-author-uniqueid']")
                    if author_el:
                        author = author_el.inner_text().strip()

                    # Get top comments
                    comment_els = page.query_selector_all("p[data-e2e='comment-level-1']")
                    comments = [el.inner_text().strip() for el in comment_els[:5]]

                    if desc or comments:
                        videos.append({
                            "url": video_url,
                            "description": desc,
                            "hashtags": hashtags,
                            "author": author,
                            "comments": comments,
                        })

                except Exception as e:
                    logger.debug(f"Error scraping TikTok video {video_url}: {e}")
                    continue

            browser.close()

    except Exception as e:
        logger.error(f"TikTok scrape failed for query '{query}': {e}")

    logger.info(f"TikTok scraper: collected {len(videos)} videos for query='{query}'")
    return videos
