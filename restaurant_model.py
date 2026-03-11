"""
FoodScout AI — Restaurant ORM Model
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Numeric, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from backend.database import Base


class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    area = Column(String(100), nullable=True)
    google_rating = Column(Numeric(2, 1), nullable=True)
    review_count = Column(Integer, default=0)
    speciality = Column(Text, nullable=True)
    source_type = Column(String(50), nullable=True)
    source_url = Column(Text, nullable=True)
    youtube_channel = Column(String(255), nullable=True)
    google_maps_link = Column(Text, nullable=True)
    confidence_score = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "city": self.city,
            "area": self.area,
            "google_rating": float(self.google_rating) if self.google_rating else None,
            "review_count": self.review_count,
            "speciality": self.speciality,
            "source_type": self.source_type,
            "source_url": self.source_url,
            "youtube_channel": self.youtube_channel,
            "google_maps_link": self.google_maps_link,
            "confidence_score": self.confidence_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
