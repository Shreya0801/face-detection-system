# Face Detection Video Streaming System

Real-time face detection using **FastAPI**, **MediaPipe**, **Pillow**, **PostgreSQL**, and **React**.
Zero OpenCV used anywhere.

## Quick start

```bash
docker compose up --build
```

Then open http://localhost:3000, click **Start camera**, and allow webcam access.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `WS` | `/ws/feed` | Send webcam JPEG frames |
| `GET` | `/stream` | Annotated MJPEG video stream |
| `GET` | `/roi` | Stored face detection records |
| `GET` | `/health` | Liveness check |

## Architecture

- **Face detection** — MediaPipe FaceDetection (no OpenCV)
- **ROI drawing** — Pillow ImageDraw.rectangle() (no OpenCV)
- **Database** — PostgreSQL via SQLAlchemy async + asyncpg
- **Streaming** — MJPEG multipart over HTTP
- **Frontend** — React with WebSocket frame sender + live ROI table

## Run tests

```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v
```

## AI collaboration

Built with Claude (Anthropic) as coding assistant.
Claude generated the scaffold, service logic, hooks, and tests.
Architecture decisions, integration, and review were human-directed.
