"""
FoodScout AI — Export API Routes
GET  /export/csv           — Download restaurants as CSV
POST /export/google-sheets — Export to a Google Sheet
"""

from __future__ import annotations
import csv
import io
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from loguru import logger

from backend.database import get_db
from backend.models.restaurant_model import Restaurant
from backend.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/api/export", tags=["export"])


# ── CSV Export ────────────────────────────────────────────────────────────────

@router.get("/csv")
def export_csv(
    city: Optional[str] = Query(None, description="Filter by city"),
    min_confidence: Optional[int] = Query(None, ge=0, le=100),
    db: Session = Depends(get_db),
):
    """
    Download all (or filtered) restaurants as a CSV file.
    """
    query = db.query(Restaurant)
    if city:
        query = query.filter(func.lower(Restaurant.city) == city.lower())
    if min_confidence is not None:
        query = query.filter(Restaurant.confidence_score >= min_confidence)

    restaurants = query.order_by(Restaurant.confidence_score.desc()).all()

    if not restaurants:
        raise HTTPException(status_code=404, detail="No restaurants found to export.")

    # Build CSV in memory
    output = io.StringIO()
    fieldnames = [
        "name", "city", "area", "google_rating", "review_count",
        "speciality", "source_type", "source_url", "youtube_channel",
        "google_maps_link", "confidence_score", "created_at",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for r in restaurants:
        d = r.to_dict()
        writer.writerow({f: d.get(f, "") for f in fieldnames})

    output.seek(0)
    filename = f"foodscout_{city or 'all'}_restaurants.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ── Google Sheets Export ───────────────────────────────────────────────────────

class SheetsExportRequest(BaseModel):
    city: Optional[str] = None
    spreadsheet_name: str = "FoodScout AI Export"
    min_confidence: Optional[int] = None


@router.post("/google-sheets")
def export_to_google_sheets(
    request: SheetsExportRequest,
    db: Session = Depends(get_db),
):
    """
    Export restaurant data to a new Google Sheet.
    Requires GOOGLE_SHEETS_CREDENTIALS_FILE to be configured.
    """
    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="gspread library not installed. Run: pip install gspread google-auth",
        )

    creds_file = settings.google_sheets_credentials_file
    if not creds_file:
        raise HTTPException(
            status_code=400,
            detail="GOOGLE_SHEETS_CREDENTIALS_FILE is not configured.",
        )

    # Fetch data
    query = db.query(Restaurant)
    if request.city:
        query = query.filter(func.lower(Restaurant.city) == request.city.lower())
    if request.min_confidence is not None:
        query = query.filter(Restaurant.confidence_score >= request.min_confidence)

    restaurants = query.order_by(Restaurant.confidence_score.desc()).all()
    if not restaurants:
        raise HTTPException(status_code=404, detail="No restaurants found to export.")

    try:
        scopes = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_file(creds_file, scopes=scopes)
        gc = gspread.authorize(creds)

        # Create / open spreadsheet
        sh = gc.create(request.spreadsheet_name)
        worksheet = sh.get_worksheet(0)
        worksheet.update_title("Restaurants")

        headers = [
            "Name", "City", "Area", "Google Rating", "Review Count",
            "Speciality", "Source Type", "Source URL", "YouTube Channel",
            "Google Maps Link", "Confidence Score", "Discovered At",
        ]
        rows = [headers]
        for r in restaurants:
            d = r.to_dict()
            rows.append([
                d.get("name", ""), d.get("city", ""), d.get("area", ""),
                d.get("google_rating", ""), d.get("review_count", ""),
                d.get("speciality", ""), d.get("source_type", ""),
                d.get("source_url", ""), d.get("youtube_channel", ""),
                d.get("google_maps_link", ""), d.get("confidence_score", ""),
                d.get("created_at", ""),
            ])

        worksheet.update("A1", rows)

        # Make publicly viewable
        sh.share("", perm_type="anyone", role="reader")

        return {
            "message": "Successfully exported to Google Sheets",
            "spreadsheet_url": sh.url,
            "rows_exported": len(restaurants),
        }

    except Exception as e:
        logger.error(f"Google Sheets export failed: {e}")
        raise HTTPException(status_code=500, detail=f"Export failed: {e}")
