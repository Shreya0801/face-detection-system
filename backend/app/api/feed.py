"""WebSocket /ws/feed — receives JPEG frames from the browser."""
from __future__ import annotations
import logging
from itertools import count

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import FaceDetection
from app.services.detector import detect_face
from app.services.annotator import annotate_frame
from app.services.frame_store import push_frame

logger = logging.getLogger(__name__)
router = APIRouter()
_frame_counter = count(1)


@router.websocket("/ws/feed")
async def feed_endpoint(websocket: WebSocket, db: AsyncSession = Depends(get_db)):
    await websocket.accept()
    session_id = websocket.query_params.get("session_id", "default")
    logger.info("WS connected  session=%s", session_id)
    try:
        while True:
            jpeg_bytes = await websocket.receive_bytes()
            frame_id   = next(_frame_counter)

            bbox      = detect_face(jpeg_bytes)
            annotated = annotate_frame(jpeg_bytes, bbox)

            if bbox is not None:
                db.add(FaceDetection(
                    frame_id=frame_id, session_id=session_id,
                    x=bbox.x, y=bbox.y,
                    width=bbox.width, height=bbox.height,
                    confidence=bbox.confidence,
                ))
                await db.commit()

            await push_frame(annotated)
            await websocket.send_json({
                "frame_id": frame_id,
                "face": {"x": bbox.x, "y": bbox.y,
                         "width": bbox.width, "height": bbox.height,
                         "confidence": round(bbox.confidence, 3)} if bbox else None,
            })
    except WebSocketDisconnect:
        logger.info("WS disconnected  session=%s", session_id)
    except Exception:
        logger.exception("WS error")
        await websocket.close(code=1011)
