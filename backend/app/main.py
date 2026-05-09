"""FastAPI entry point."""
from __future__ import annotations
import logging, os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import feed, stream
from app.db.database import init_db

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(name)s  %(message)s")

_CORS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title="Face Detection API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=_CORS,
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(feed.router,   tags=["feed"])
app.include_router(stream.router, tags=["stream"])
