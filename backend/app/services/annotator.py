"""Draw ROI bounding box using Pillow only — zero OpenCV."""
from __future__ import annotations
import io
from typing import Optional
from PIL import Image, ImageDraw, ImageFont
from app.services.detector import BoundingBox

_ROI_COLOR  = (0, 255, 80)
_LINE_WIDTH = 3
_LABEL_BG   = (0, 0, 0, 160)


def annotate_frame(jpeg_bytes: bytes, bbox: Optional[BoundingBox]) -> bytes:
    img = Image.open(io.BytesIO(jpeg_bytes)).convert("RGB")

    if bbox is not None:
        draw = ImageDraw.Draw(img, "RGBA")
        x0, y0 = bbox.x, bbox.y
        x1, y1 = bbox.x + bbox.width, bbox.y + bbox.height

        draw.rectangle([x0, y0, x1, y1], outline=_ROI_COLOR, width=_LINE_WIDTH)

        label = f"face  {bbox.confidence:.0%}"
        try:
            font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
        except (IOError, OSError):
            font = ImageFont.load_default()

        label_y = y0 - 20 if y0 > 20 else y1 + 4
        text_bbox = draw.textbbox((x0, label_y), label, font=font)
        draw.rectangle(
            [text_bbox[0]-2, text_bbox[1]-2, text_bbox[2]+2, text_bbox[3]+2],
            fill=_LABEL_BG)
        draw.text((x0, label_y), label, fill=_ROI_COLOR, font=font)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85, optimize=True)
    return buf.getvalue()
