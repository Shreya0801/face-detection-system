"""ORM model for storing face detection ROI data."""
from sqlalchemy import Column, Integer, Float, DateTime, String, func
from app.db.database import Base


class FaceDetection(Base):
    __tablename__ = "face_detections"

    id          = Column(Integer, primary_key=True, index=True)
    frame_id    = Column(Integer, nullable=False, index=True)
    session_id  = Column(String(64), nullable=False, index=True, default="default")
    x           = Column(Integer, nullable=False)
    y           = Column(Integer, nullable=False)
    width       = Column(Integer, nullable=False)
    height      = Column(Integer, nullable=False)
    confidence  = Column(Float, nullable=False)
    detected_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
