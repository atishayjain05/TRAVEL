"""
FoodScout AI — Scan History ORM Model
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Numeric, Text, DateTime, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from backend.database import Base


class ScanHistory(Base):
    __tablename__ = "scan_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    city = Column(String(100), nullable=False)
    food_category = Column(String(100), nullable=True)
    sources_scanned = Column(ARRAY(String), nullable=True)
    restaurants_found = Column(Integer, default=0)
    scan_time = Column(Numeric(10, 2), nullable=True)
    status = Column(String(50), default="pending")
    task_id = Column(String(255), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "city": self.city,
            "food_category": self.food_category,
            "sources_scanned": self.sources_scanned or [],
            "restaurants_found": self.restaurants_found,
            "scan_time": float(self.scan_time) if self.scan_time else None,
            "status": self.status,
            "task_id": self.task_id,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
