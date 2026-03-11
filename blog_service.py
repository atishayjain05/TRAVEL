"""
FoodScout AI — Blog / Web Discovery Service
Searches the web for food blogs and travel articles mentioning restaurants in a city.
"""

from __future__ import annotations
import re
import time
import requests
from bs4 import BeautifulSoup
from loguru import logger
from backend.config import get_settings

settings = get_settings()

SEARCH_QUERIES = [
    "best restaurants in {city}",
    "street food guide {city}",
    "must eat food {city}",
    "{city} food travel guide",
    "hidden gem restaurants {city}",
    "{city} local food spots",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

# Domains to skip (social media, aggregators with paywalls, etc.)
SKIP_DOMAINS = {
    "instagram.com", "tiktok.com", "twitter.com", "facebook.com",
    "reddit.com", "youtube.com", "yelp.com", "tripadvisor.com",
}


def _ddg_search(query: str, max_results: int = 5) -> list[str]:
    """
    Use DuckDuckGo HTML search to get organic result URLs.
    Returns list of URLs.
    """
    urls: list[str] = []
    try:
        search_url = "https://html.duckduckgo.com/html/"
        resp = requests.post(
            search_url,
            data={"q": query},
            headers=HEADERS,
            timeout=15,
        )
        soup = BeautifulSoup(resp.text, "lxml")
        for result in soup.select(".result__a"):
            href = result.get("href", "")
            if href.startswith("http"):
                domain = href.split("/")[2].replace("www.", "")
                if domain not in SKIP_DOMAINS:
                    urls.append(href)
                    if len(urls) >= max_results:
                        break
    except Exception as e:
        logger.debug(f"DDG search failed for '{query}': {e}")
    return urls


def _scrape_page_text(url: str, max_chars: int = 8000) -> str:
    """Fetch and extract clean text from a webpage."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        # Remove nav/footer/script noise
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        # Get main content
        text = soup.get_text(separator=" ", strip=True)
        text = re.sub(r"\s+", " ", text)
        return text[:max_chars]
    except Exception as e:
        logger.debug(f"Page scrape failed for '{url}': {e}")
        return ""


def collect_blog_content(city: str, max_sources: int = 15) -> list[dict]:
    """
    Search for food blogs about a city and scrape their content.
    Returns list of content dicts ready for restaurant extraction.
    """
    content_list: list[dict] = []
    seen_urls: set[str] = set()
    urls_to_scrape: list[tuple[str, str]] = []  # (url, query)

    per_query = max(3, max_sources // len(SEARCH_QUERIES))

    for query_template in SEARCH_QUERIES:
        query = query_template.format(city=city)
        found_urls = _ddg_search(query, max_results=per_query)
        for url in found_urls:
            if url not in seen_urls:
                seen_urls.add(url)
                urls_to_scrape.append((url, query))

    logger.info(f"Blog: found {len(urls_to_scrape)} pages to scrape for city='{city}'")

    for url, query in urls_to_scrape[:max_sources]:
        text = _scrape_page_text(url)
        if len(text) > 200:
            content_list.append(
                {
                    "source_type": "blog",
                    "url": url,
                    "content": text,
                    "query": query,
                }
            )
        time.sleep(0.5)  # polite delay

    logger.info(f"Blog: scraped {len(content_list)} pages for city='{city}'")
    return content_list
