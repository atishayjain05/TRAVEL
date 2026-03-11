"""
FoodScout AI — Instagram Reels Scraper (Playwright)
Scrapes public hashtag pages to collect food reel captions and metadata.

Note: Instagram's anti-bot measures are aggressive.
This scraper works on public pages without login.
For production use, consider using an official partner API or proxy rotation.
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


def scrape_instagram_reels(hashtag: str, max_posts: int = 15) -> list[dict]:
    """
    Scrape Instagram hashtag page for reel captions and location tags.
    Returns a list of post dicts: {url, caption, location, comments}.
    """
    if not PLAYWRIGHT_AVAILABLE:
        logger.warning("Playwright not installed — cannot scrape Instagram.")
        return []

    posts = []
    url = f"https://www.instagram.com/explore/tags/{hashtag.replace(' ', '')}/"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 "
                    "Mobile/15E148 Safari/604.1"
                ),
                viewport={"width": 390, "height": 844},
            )
            page = context.new_page()

            # Intercept XHR to capture post data
            captured_data: list[dict] = []

            def handle_response(response):
                if "graphql" in response.url or "api/v1/tags" in response.url:
                    try:
                        body = response.json()
                        captured_data.append(body)
                    except Exception:
                        pass

            page.on("response", handle_response)

            try:
                page.goto(url, timeout=30000, wait_until="networkidle")
            except PWTimeout:
                logger.warning(f"Instagram load timeout for #{hashtag}")

            time.sleep(3)

            # Extract post links from the page
            post_links = page.query_selector_all("a[href*='/p/']")
            post_urls = []
            for link in post_links[:max_posts]:
                href = link.get_attribute("href") or ""
                if "/p/" in href:
                    full_url = f"https://www.instagram.com{href}"
                    if full_url not in post_urls:
                        post_urls.append(full_url)

            # Scrape each post for caption
            for post_url in post_urls[:max_posts]:
                try:
                    page.goto(post_url, timeout=20000, wait_until="domcontentloaded")
                    time.sleep(2)

                    # Get caption
                    caption = ""
                    caption_el = page.query_selector("h1, [data-testid='post-comment-root-0']")
                    if caption_el:
                        caption = caption_el.inner_text().strip()

                    # Get location if tagged
                    location = ""
                    loc_el = page.query_selector("a[href*='/explore/locations/']")
                    if loc_el:
                        location = loc_el.inner_text().strip()

                    # Get top comments
                    comment_els = page.query_selector_all("ul li span")
                    comments = [el.inner_text().strip() for el in comment_els[:5] if el.inner_text().strip()]

                    posts.append({
                        "url": post_url,
                        "caption": caption,
                        "location": location,
                        "comments": comments,
                    })
                except Exception as e:
                    logger.debug(f"Error scraping Instagram post {post_url}: {e}")
                    continue

            browser.close()

    except Exception as e:
        logger.error(f"Instagram scrape failed for #{hashtag}: {e}")

    logger.info(f"Instagram scraper: collected {len(posts)} posts for #{hashtag}")
    return posts
