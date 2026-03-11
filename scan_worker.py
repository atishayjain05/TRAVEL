"""
FoodScout AI — Scan Worker
Celery task that orchestrates the full restaurant discovery pipeline.
"""

from __future__ import annotations
import time
import uuid
from loguru import logger
from sqlalchemy.exc import IntegrityError

from backend.workers.celery_worker import celery_app
from backend.database import SessionLocal
from backend.models.restaurant_model import Restaurant
from backend.models.scan_model import ScanHistory
from backend.services import (
    youtube_service,
    instagram_service,
    tiktok_service,
    blog_service,
    extraction_service,
    maps_service,
    dedupe_service,
    scoring_service,
)


def _update_scan_status(db, scan_id: str, **kwargs):
    """Helper to update scan history record."""
    scan = db.query(ScanHistory).filter(ScanHistory.id == scan_id).first()
    if scan:
        for key, value in kwargs.items():
            setattr(scan, key, value)
        db.commit()


@celery_app.task(bind=True, name="run_city_scan")
def run_city_scan(
    self,
    scan_id: str,
    city: str,
    food_category: str,
    sources: list[str],
    num_sources: int,
) -> dict:
    """
    Full restaurant discovery pipeline for a city.

    Pipeline:
    1. Collect content from selected sources (YouTube, Instagram, TikTok, Blogs)
    2. Extract restaurant mentions using AI
    3. Verify with Google Maps
    4. Deduplicate
    5. Score
    6. Persist to database
    """
    start_time = time.time()
    db = SessionLocal()

    try:
        _update_scan_status(db, scan_id, status="running")
        logger.info(f"[Scan {scan_id}] Starting scan: city={city}, sources={sources}")

        # ── Step 1: Content Collection ─────────────────────────────────────
        all_content: list[dict] = []

        if "youtube" in sources:
            self.update_state(state="PROGRESS", meta={"step": "Collecting YouTube content"})
            yt_content = youtube_service.collect_video_content(city, max_videos=num_sources)
            for item in yt_content:
                item["source_type"] = "youtube"
            all_content.extend(yt_content)
            logger.info(f"[Scan {scan_id}] YouTube: {len(yt_content)} items")

        if "instagram" in sources:
            self.update_state(state="PROGRESS", meta={"step": "Collecting Instagram content"})
            ig_content = instagram_service.collect_instagram_content(city, max_posts=num_sources)
            all_content.extend(ig_content)
            logger.info(f"[Scan {scan_id}] Instagram: {len(ig_content)} items")

        if "tiktok" in sources:
            self.update_state(state="PROGRESS", meta={"step": "Collecting TikTok content"})
            tt_content = tiktok_service.collect_tiktok_content(city, max_videos=num_sources)
            all_content.extend(tt_content)
            logger.info(f"[Scan {scan_id}] TikTok: {len(tt_content)} items")

        if "blogs" in sources:
            self.update_state(state="PROGRESS", meta={"step": "Scanning food blogs"})
            blog_content = blog_service.collect_blog_content(city, max_sources=num_sources)
            all_content.extend(blog_content)
            logger.info(f"[Scan {scan_id}] Blogs: {len(blog_content)} items")

        if not all_content:
            raise ValueError("No content collected from any source. Check API keys.")

        # ── Step 2: Restaurant Extraction ──────────────────────────────────
        self.update_state(state="PROGRESS", meta={"step": "Extracting restaurant mentions"})
        raw_restaurants: list[dict] = []
        source_map: dict[str, dict] = {}  # name_lower → source metadata

        for content_item in all_content:
            text = content_item.get("content", "")
            if not text or len(text) < 50:
                continue
            extracted = extraction_service.extract_restaurants_from_text(text, city)
            for r in extracted:
                name = r.get("name", "").strip()
                if not name:
                    continue
                name_key = name.lower()
                if name_key not in source_map:
                    source_map[name_key] = {
                        "name": name,
                        "speciality": r.get("speciality"),
                        "source_type": content_item.get("source_type", "unknown"),
                        "source_url": content_item.get(
                            "video_url", content_item.get("url", "")
                        ),
                        "youtube_channel": content_item.get("channel", ""),
                        "city": city,
                        "mention_count": 0,
                    }
                source_map[name_key]["mention_count"] += 1

        raw_restaurants = list(source_map.values())
        logger.info(f"[Scan {scan_id}] Extracted {len(raw_restaurants)} raw restaurant mentions")

        # ── Step 3: Google Maps Verification ───────────────────────────────
        self.update_state(state="PROGRESS", meta={"step": "Verifying with Google Maps"})
        enriched = maps_service.enrich_restaurants(raw_restaurants, city)

        # Merge back mention_count and source info
        enriched_names = {r["name"].lower(): r for r in enriched}
        for raw in raw_restaurants:
            key = raw["name"].lower()
            if key in enriched_names:
                enriched_names[key].update({
                    "mention_count": raw.get("mention_count", 1),
                    "source_type": raw.get("source_type"),
                    "source_url": raw.get("source_url"),
                    "youtube_channel": raw.get("youtube_channel"),
                    "speciality": enriched_names[key].get("speciality") or raw.get("speciality"),
                })

        verified_list = list(enriched_names.values())

        # ── Step 4: Deduplication ──────────────────────────────────────────
        self.update_state(state="PROGRESS", meta={"step": "Deduplicating results"})
        unique_restaurants = dedupe_service.deduplicate(verified_list)

        # ── Step 5: Confidence Scoring ─────────────────────────────────────
        self.update_state(state="PROGRESS", meta={"step": "Calculating confidence scores"})
        scored_restaurants = scoring_service.score_restaurants(unique_restaurants)

        # ── Step 6: Persist to Database ────────────────────────────────────
        self.update_state(state="PROGRESS", meta={"step": "Saving to database"})
        saved_count = 0

        for r in scored_restaurants:
            try:
                restaurant = Restaurant(
                    name=r["name"],
                    city=city,
                    area=r.get("area"),
                    google_rating=r.get("google_rating"),
                    review_count=r.get("review_count", 0),
                    speciality=r.get("speciality"),
                    source_type=r.get("source_type", "unknown"),
                    source_url=r.get("source_url"),
                    youtube_channel=r.get("youtube_channel"),
                    google_maps_link=r.get("google_maps_link"),
                    confidence_score=r.get("confidence_score", 0),
                )
                db.add(restaurant)
                db.commit()
                saved_count += 1
            except IntegrityError:
                db.rollback()
                # Already exists — skip (dedup handled above, but SQL unique index catches edge cases)
            except Exception as e:
                db.rollback()
                logger.warning(f"Failed to save restaurant '{r.get('name')}': {e}")

        # ── Final: Update Scan History ─────────────────────────────────────
        elapsed = round(time.time() - start_time, 2)
        _update_scan_status(
            db,
            scan_id,
            status="completed",
            restaurants_found=saved_count,
            scan_time=elapsed,
        )

        logger.info(
            f"[Scan {scan_id}] Completed: {saved_count} restaurants saved in {elapsed}s"
        )
        return {
            "status": "completed",
            "scan_id": scan_id,
            "restaurants_found": saved_count,
            "scan_time": elapsed,
        }

    except Exception as e:
        elapsed = round(time.time() - start_time, 2)
        logger.error(f"[Scan {scan_id}] FAILED after {elapsed}s: {e}")
        _update_scan_status(
            db,
            scan_id,
            status="failed",
            error_message=str(e),
            scan_time=elapsed,
        )
        raise

    finally:
        db.close()
