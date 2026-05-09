"""Face detection — MediaPipe only, no OpenCV."""
from __future__ import annotations
import io
import logging
from dataclasses import dataclass
from typing import Optional

import mediapipe as mp
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

_mp_face  = mp.solutions.face_detection
_detector = _mp_face.FaceDetection(model_selection=0, min_detection_confidence=0.5)


@dataclass(frozen=True)
class BoundingBox:
    x: int
    y: int
    width: int
    height: int
    confidence: float


def detect_face(jpeg_bytes: bytes) -> Optional[BoundingBox]:
    try:
        pil_img  = Image.open(io.BytesIO(jpeg_bytes)).convert("RGB")
        frame_w, frame_h = pil_img.size
        rgb_array = np.array(pil_img, dtype=np.uint8)

        results = _detector.process(rgb_array)
        if not results.detections:
            return None

        best  = max(results.detections, key=lambda d: d.score[0])
        score = float(best.score[0])
        bbox  = best.location_data.relative_bounding_box

        x = max(0, int(bbox.xmin * frame_w))
        y = max(0, int(bbox.ymin * frame_h))
        w = min(int(bbox.width  * frame_w), frame_w - x)
        h = min(int(bbox.height * frame_h), frame_h - y)

        return BoundingBox(x=x, y=y, width=w, height=h, confidence=score)
    except Exception:
        logger.exception("face detection failed")
        return None
