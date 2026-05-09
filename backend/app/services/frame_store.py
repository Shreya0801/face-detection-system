"""Async queue — bridges the WebSocket receiver and the MJPEG stream."""
from __future__ import annotations
import asyncio, os
from typing import Optional

_MAX: int = int(os.getenv("MAX_FRAME_QUEUE", 30))

frame_queue: asyncio.Queue[bytes] = asyncio.Queue(maxsize=_MAX)
_latest_frame: Optional[bytes] = None


async def push_frame(jpeg: bytes) -> None:
    global _latest_frame
    _latest_frame = jpeg
    if frame_queue.full():
        try:
            frame_queue.get_nowait()
        except asyncio.QueueEmpty:
            pass
    await frame_queue.put(jpeg)


async def pop_frame() -> bytes:
    return await frame_queue.get()


def get_latest() -> Optional[bytes]:
    return _latest_frame
