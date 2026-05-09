"""GET /stream  — MJPEG feed   |   GET /roi  — stored detections   |   GET /health"""
from __future__ import annotations
import asyncio, logging
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schemas import DetectionListResponse, DetectionRecord, HealthResponse
from app.db.database import get_db
from app.db.models import FaceDetection
from app.services.frame_store import pop_frame, get_latest

logger   = logging.getLogger(__name__)
router   = APIRouter()
_BOUNDARY = b"--frame"


async def _mjpeg_generator():
    seed = get_latest()
    if seed:
        yield _BOUNDARY + b"\r\nContent-Type: image/jpeg\r\n\r\n" + seed + b"\r\n"
    while True:
        try:
            frame = await asyncio.wait_for(pop_frame(), timeout=5.0)
        except asyncio.TimeoutError:
            frame = get_latest()
            if not frame:
                continue
        yield _BOUNDARY + b"\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"


@router.get("/stream")
async def stream_endpoint():
    return StreamingResponse(
        _mjpeg_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame")


@router.get("/roi", response_model=DetectionListResponse)
async def roi_endpoint(
    session_id: Optional[str] = Query(None),
    limit:  int = Query(50, ge=1, le=500),
    offset: int = Query(0,  ge=0),
    db: AsyncSession = Depends(get_db),
):
    q       = select(FaceDetection)
    count_q = select(func.count()).select_from(FaceDetection)
    if session_id:
        q       = q.where(FaceDetection.session_id == session_id)
        count_q = count_q.where(FaceDetection.session_id == session_id)
    q     = q.order_by(FaceDetection.detected_at.desc()).limit(limit).offset(offset)
    total = (await db.execute(count_q)).scalar_one()
    rows  = (await db.execute(q)).scalars().all()
    return DetectionListResponse(
        total=total,
        items=[DetectionRecord.model_validate(r) for r in rows])


@router.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="ok")
