"""
FoodScout AI — Scan API Routes
POST /scan-city    — Start a new city scan
GET  /scan-history — List scan history
GET  /scan/{id}    — Get scan status
"""

from __future__ import annotations
import uuid
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session
from loguru import logger

from backend.database import get_db
from backend.models.scan_model import ScanHistory
from backend.workers.scan_worker import run_city_scan

router = APIRouter(prefix="/api", tags=["scans"])


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class ScanRequest(BaseModel):
    city: str = Field(..., min_length=2, max_length=100)
    food_category: str = Field(default="", max_length=100)
    sources: list[str] = Field(default=["youtube", "blogs"])
    num_sources: int = Field(default=20, ge=5, le=200)

    @validator("sources")
    def validate_sources(cls, v):
        valid = {"youtube", "instagram", "tiktok", "blogs"}
        for s in v:
            if s not in valid:
                raise ValueError(f"Invalid source: {s}. Must be one of {valid}")
        return v


class ScanResponse(BaseModel):
    scan_id: str
    city: str
    status: str
    message: str


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/scan-city", response_model=ScanResponse)
def start_scan(request: ScanRequest, db: Session = Depends(get_db)):
    """
    Initiate an asynchronous restaurant discovery scan for a city.
    Returns a scan_id that can be polled for status.
    """
    scan_id = str(uuid.uuid4())

    # Create scan history record
    scan = ScanHistory(
        id=scan_id,
        city=request.city,
        food_category=request.food_category or None,
        sources_scanned=request.sources,
        status="pending",
    )
    db.add(scan)
    db.commit()

    # Dispatch Celery task
    try:
        task = run_city_scan.apply_async(
            kwargs={
                "scan_id": scan_id,
                "city": request.city,
                "food_category": request.food_category,
                "sources": request.sources,
                "num_sources": request.num_sources,
            },
            task_id=scan_id,  # Use scan_id as Celery task_id for easy lookup
        )
        scan.task_id = task.id
        db.commit()
        logger.info(f"Scan started: {scan_id} for city='{request.city}'")
    except Exception as e:
        scan.status = "failed"
        scan.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Failed to start scan: {e}")

    return ScanResponse(
        scan_id=scan_id,
        city=request.city,
        status="pending",
        message=f"Scan started for {request.city}. Poll /api/scan/{scan_id} for status.",
    )


@router.get("/scan/{scan_id}")
def get_scan_status(scan_id: str, db: Session = Depends(get_db)):
    """Get the current status of a scan."""
    scan = db.query(ScanHistory).filter(ScanHistory.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan.to_dict()


@router.get("/scan-history")
def get_scan_history(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """List recent scan history records."""
    total = db.query(ScanHistory).count()
    scans = (
        db.query(ScanHistory)
        .order_by(ScanHistory.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return {
        "total": total,
        "items": [s.to_dict() for s in scans],
        "limit": limit,
        "offset": offset,
    }
