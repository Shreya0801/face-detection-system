"""FastAPI entry point."""
from __future__ import annotations
import logging, os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api import feed, stream
from app.db.database import init_db

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(name)s  %(message)s")
logger = logging.getLogger(__name__)

_CORS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initialising database...")
    await init_db()
    logger.info("Database ready.")
    yield
    logger.info("Shutdown.")


app = FastAPI(
    title="Face Detection Streaming API",
    version="1.0.0",
    description=(
        "Receives webcam frames via WebSocket, detects faces with MediaPipe, "
        "stores ROI in PostgreSQL, and serves an annotated MJPEG stream. "
        "No OpenCV used anywhere."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_CORS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled error on %s: %s", request.url, exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(feed.router,   tags=["feed"])
app.include_router(stream.router, tags=["stream"])
