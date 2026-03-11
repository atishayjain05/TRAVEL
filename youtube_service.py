"""
FoodScout AI — YouTube Discovery Service
Searches YouTube for food videos in a city and extracts transcripts.
"""

from __future__ import annotations
import re
from typing import Optional
from loguru import logger
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
from backend.config import get_settings

settings = get_settings()


SEARCH_QUERIES = [
    "best food in {city}",
    "{city} street food",
    "{city} food vlog",
    "{city} food tour",
    "local food {city}",
    "{city} best restaurants",
    "{city} must eat",
]


def _build_youtube_client():
    if not settings.youtube_api_key:
        raise ValueError("YOUTUBE_API_KEY is not configured.")
    return build("youtube", "v3", developerKey=settings.youtube_api_key)


def search_videos(city: str, max_results: int = 50) -> list[dict]:
    """
    Search YouTube for food-related videos in a city.
    Returns a list of video metadata dicts.
    """
    youtube = _build_youtube_client()
    videos: list[dict] = []
    seen_ids: set[str] = set()
    per_query = max(5, max_results // len(SEARCH_QUERIES))

    for query_template in SEARCH_QUERIES:
        query = query_template.format(city=city)
        try:
            response = (
                youtube.search()
                .list(
                    q=query,
                    part="id,snippet",
                    type="video",
                    maxResults=min(per_query, 50),
                    relevanceLanguage="en",
                    videoDuration="medium",
                )
                .execute()
            )
            for item in response.get("items", []):
                video_id = item["id"]["videoId"]
                if video_id in seen_ids:
                    continue
                seen_ids.add(video_id)
                snippet = item["snippet"]
                videos.append(
                    {
                        "video_id": video_id,
                        "title": snippet.get("title", ""),
                        "channel": snippet.get("channelTitle", ""),
                        "description": snippet.get("description", ""),
                        "video_url": f"https://www.youtube.com/watch?v={video_id}",
                        "query": query,
                    }
                )
                if len(videos) >= max_results:
                    break
        except Exception as e:
            logger.warning(f"YouTube search failed for query '{query}': {e}")

        if len(videos) >= max_results:
            break

    logger.info(f"YouTube: collected {len(videos)} videos for city='{city}'")
    return videos


def get_transcript(video_id: str) -> Optional[str]:
    """
    Retrieve transcript text for a YouTube video.
    Falls back to None if unavailable.
    """
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join(entry["text"] for entry in transcript_list)
        # Clean up whitespace
        text = re.sub(r"\s+", " ", text).strip()
        return text
    except (NoTranscriptFound, TranscriptsDisabled):
        return None
    except Exception as e:
        logger.debug(f"Transcript fetch failed for {video_id}: {e}")
        return None


def collect_video_content(city: str, max_videos: int = 50) -> list[dict]:
    """
    Full pipeline: search videos + attach transcript (or description fallback).
    Returns enriched video records ready for restaurant extraction.
    """
    videos = search_videos(city, max_results=max_videos)
    enriched = []

    for video in videos:
        transcript = get_transcript(video["video_id"])
        content = transcript if transcript else video.get("description", "")
        if not content:
            continue
        enriched.append(
            {
                **video,
                "content": content,
                "content_source": "transcript" if transcript else "description",
            }
        )

    logger.info(
        f"YouTube: {len(enriched)} videos with usable content for city='{city}'"
    )
    return enriched
