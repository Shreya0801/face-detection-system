"""Pydantic schemas — request/response contracts for the API."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ROIData(BaseModel):
    x: int
    y: int
    width: int  = Field(..., ge=0)
    height: int = Field(..., ge=0)
    confidence: float = Field(..., ge=0.0, le=1.0)


class DetectionRecord(ROIData):
    id: int
    frame_id: int
    session_id: str
    detected_at: datetime

    class Config:
        from_attributes = True


class DetectionListResponse(BaseModel):
    total: int
    items: List[DetectionRecord]


class HealthResponse(BaseModel):
    status: str
    version: str = "1.0.0"
