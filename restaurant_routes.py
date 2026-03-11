"""
FoodScout AI — Restaurant API Routes
GET /restaurants            — List all restaurants (with search/filter/sort/pagination)
GET /restaurants/{city}     — Restaurants for a specific city
GET /stats                  — Dashboard analytics
"""

from __future__ import annotations
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc

from backend.database import get_db
from backend.models.restaurant_model import Restaurant

router = APIRouter(prefix="/api", tags=["restaurants"])


@router.get("/restaurants")
def list_restaurants(
    city: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    source_type: Optional[str] = Query(None),
    min_rating: Optional[float] = Query(None, ge=0, le=5),
    min_confidence: Optional[int] = Query(None, ge=0, le=100),
    sort_by: str = Query("confidence_score"),
    sort_dir: str = Query("desc"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """
    List restaurants with filtering, searching, sorting, and pagination.
    """
    query = db.query(Restaurant)

    # Filters
    if city:
        query = query.filter(func.lower(Restaurant.city) == city.lower())
    if search:
        search_term = f"%{search.lower()}%"
        query = query.filter(
            func.lower(Restaurant.name).like(search_term)
            | func.lower(Restaurant.speciality).like(search_term)
            | func.lower(Restaurant.area).like(search_term)
        )
    if source_type:
        query = query.filter(Restaurant.source_type == source_type)
    if min_rating is not None:
        query = query.filter(Restaurant.google_rating >= min_rating)
    if min_confidence is not None:
        query = query.filter(Restaurant.confidence_score >= min_confidence)

    total = query.count()

    # Sorting
    sort_col_map = {
        "confidence_score": Restaurant.confidence_score,
        "google_rating": Restaurant.google_rating,
        "review_count": Restaurant.review_count,
        "name": Restaurant.name,
        "created_at": Restaurant.created_at,
    }
    sort_col = sort_col_map.get(sort_by, Restaurant.confidence_score)
    if sort_dir == "asc":
        query = query.order_by(asc(sort_col))
    else:
        query = query.order_by(desc(sort_col))

    restaurants = query.offset(offset).limit(limit).all()

    return {
        "total": total,
        "items": [r.to_dict() for r in restaurants],
        "limit": limit,
        "offset": offset,
    }


@router.get("/restaurants/{city}")
def get_restaurants_by_city(
    city: str,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Get all restaurants discovered for a specific city."""
    total = (
        db.query(Restaurant)
        .filter(func.lower(Restaurant.city) == city.lower())
        .count()
    )
    restaurants = (
        db.query(Restaurant)
        .filter(func.lower(Restaurant.city) == city.lower())
        .order_by(desc(Restaurant.confidence_score))
        .offset(offset)
        .limit(limit)
        .all()
    )
    if total == 0:
        raise HTTPException(
            status_code=404,
            detail=f"No restaurants found for city: {city}",
        )
    return {
        "city": city,
        "total": total,
        "items": [r.to_dict() for r in restaurants],
    }


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """Dashboard analytics — aggregated stats across all data."""
    total_restaurants = db.query(Restaurant).count()
    cities_scanned = db.query(func.count(func.distinct(Restaurant.city))).scalar()
    avg_rating = db.query(func.avg(Restaurant.google_rating)).scalar()
    sources = db.query(
        Restaurant.source_type, func.count(Restaurant.id)
    ).group_by(Restaurant.source_type).all()

    source_breakdown = {s: c for s, c in sources}

    return {
        "total_restaurants": total_restaurants,
        "cities_scanned": cities_scanned or 0,
        "average_rating": round(float(avg_rating), 2) if avg_rating else 0,
        "sources_analyzed": sum(source_breakdown.values()),
        "source_breakdown": source_breakdown,
    }


@router.delete("/restaurants/{restaurant_id}")
def delete_restaurant(restaurant_id: str, db: Session = Depends(get_db)):
    """Delete a restaurant by ID."""
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    db.delete(restaurant)
    db.commit()
    return {"message": "Restaurant deleted successfully"}
