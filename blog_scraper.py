"""
FoodScout AI — Blog Scraper (Playwright)
Handles JavaScript-heavy blog pages that requests + BeautifulSoup cannot render.
Used as fallback when the requests-based blog_service fails.
"""

from __future__ import annotations
import re
import time
from loguru import logger

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


def scrape_blog_page(url: str, max_chars: int = 8000) -> str:
    """
    Scrape a blog page using Playwright (for JS-rendered content).
    Returns the visible page text, truncated to max_chars.
    """
    if not PLAYWRIGHT_AVAILABLE:
        logger.warning("Playwright not installed — cannot use Playwright blog scraper.")
        return ""

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

            try:
                page.goto(url, timeout=20000, wait_until="domcontentloaded")
            except PWTimeout:
                logger.warning(f"Blog page timeout: {url}")
                browser.close()
                return ""

            time.sleep(1)  # Let lazy-loaded content render

            # Remove nav/footer
            page.evaluate("""
                () => {
                    ['nav', 'footer', 'header', 'aside', '.sidebar', '.ads', '.advertisement']
                        .forEach(sel => {
                            document.querySelectorAll(sel).forEach(el => el.remove());
                        });
                }
            """)

            # Extract text from main content areas
            text = page.evaluate("""
                () => {
                    const selectors = ['article', 'main', '.post-content', '.entry-content', '.content'];
                    for (const sel of selectors) {
                        const el = document.querySelector(sel);
                        if (el) return el.innerText;
                    }
                    return document.body.innerText;
                }
            """)

            browser.close()

            if text:
                text = re.sub(r"\s+", " ", text).strip()
                return text[:max_chars]
            return ""

    except Exception as e:
        logger.error(f"Blog Playwright scrape failed for {url}: {e}")
        return ""


def scrape_multiple_blogs(urls: list[str], max_chars: int = 6000) -> list[dict]:
    """
    Scrape multiple blog URLs and return content list.
    """
    results = []
    for url in urls:
        text = scrape_blog_page(url, max_chars=max_chars)
        if len(text) > 200:
            results.append({"url": url, "content": text, "source_type": "blog"})
        time.sleep(0.5)
    return results
