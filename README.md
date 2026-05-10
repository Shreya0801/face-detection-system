# 🎯 Face Detection Video Streaming System

A real-time face detection pipeline that captures webcam video, detects faces using **MediaPipe**, draws bounding boxes using **Pillow**, stores ROI data in **PostgreSQL**, and streams annotated video to a **React** frontend — all containerised with **Docker Compose**.

> ⚠️ **No OpenCV used anywhere** — face detection via MediaPipe, drawing via Pillow (PIL).

---

## 📸 How It Works

* Browser captures webcam frames and sends them via **WebSocket**
* Backend detects faces and draws a **green bounding box** (ROI) around each face
* Annotated video is streamed back as **MJPEG**
* Every detection is stored in **PostgreSQL** and shown in a live history table

---

## 🏗️ Architecture

```text
Browser
  │
  ├── WebSocket (JPEG frames) ──► POST /ws/feed ──┐
  │                                               │  FastAPI Backend
  └── img src=/stream         ◄── GET  /stream  ◄──┤  - MediaPipe detection
                                                  │  - Pillow annotation
  React ROI Table             ◄── GET  /roi     ◄──┘  - asyncio frame queue
                                                          │
                                                    PostgreSQL DB
                                                  (face_detections table)
```

### Docker Compose Services

| Service  | Image                  | Port | Role                                |
| -------- | ---------------------- | ---- | ----------------------------------- |
| db       | postgres:16-alpine     | 5432 | Stores face detection ROI data      |
| backend  | python:3.11-slim       | 8000 | FastAPI — detection, streaming, API |
| frontend | node:20-alpine + nginx | 3000 | React UI — webcam + stream display  |

---

## 🚀 Quick Start

### Prerequisites

* Docker Engine 20+
* Docker Compose v2+

### Run

```bash
# 1. Clone the repository
git clone https://github.com/Shreya0801/face-detection-system.git
cd face-detection-system

# 2. Start all containers
docker compose up --build

# 3. Open the app
# http://localhost:3000

# 4. Click "Start camera" and allow webcam access
```

### Stop

```bash
docker compose down
```

---

## 📡 API Endpoints

| Method    | Path     | Description                              |
| --------- | -------- | ---------------------------------------- |
| WebSocket | /ws/feed | Receives JPEG frames from browser webcam |
| GET       | /stream  | Serves annotated MJPEG video stream      |
| GET       | /roi     | Returns paginated face detection records |
| GET       | /health  | Liveness probe                           |

### Example Requests

**Health check:**

```bash
curl http://localhost:8000/health
# {"status":"ok","version":"1.0.0"}
```

**Get ROI records:**

```bash
curl http://localhost:8000/roi?limit=10
# {"total":42,"items":[...]}
```

**Get ROI by session:**

```bash
curl http://localhost:8000/roi?session_id=session_123&limit=5
```

**Interactive API docs:**

```text
http://localhost:8000/docs
```

---

## 🗄️ Database Schema

```sql
CREATE TABLE face_detections (
    id          SERIAL PRIMARY KEY,
    frame_id    INTEGER NOT NULL,
    session_id  VARCHAR(64) NOT NULL,
    x           INTEGER NOT NULL,
    y           INTEGER NOT NULL,
    width       INTEGER NOT NULL,
    height      INTEGER NOT NULL,
    confidence  FLOAT NOT NULL,
    detected_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX ON face_detections (session_id);
CREATE INDEX ON face_detections (frame_id);
```

---

## 📁 Project Structure

```text
face-detection-system/
├── docker-compose.yml
├── README.md
├── .env.example
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── pytest.ini
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── feed.py
│   │   │   └── stream.py
│   │   ├── core/
│   │   │   └── schemas.py
│   │   ├── db/
│   │   │   ├── database.py
│   │   │   └── models.py
│   │   └── services/
│   │       ├── detector.py
│   │       ├── annotator.py
│   │       └── frame_store.py
│   └── tests/
│       └── test_api.py
└── frontend/
    ├── Dockerfile
    ├── nginx.conf
    ├── package.json
    ├── public/
    │   └── index.html
    └── src/
        ├── App.js
        ├── App.css
        ├── components/
        │   ├── VideoPanel.js
        │   └── ROITable.js
        └── hooks/
            ├── useWebcamStream.js
            └── useROIHistory.js
```

---

## 🛠️ Tech Stack

| Concern              | Technology       | Reason                                    |
| -------------------- | ---------------- | ----------------------------------------- |
| Face detection       | MediaPipe        | No OpenCV; fast; CPU-friendly             |
| Bounding box drawing | Pillow PIL       | Pure Python; no native deps               |
| Web framework        | FastAPI          | Native async; WebSocket; auto docs        |
| Video streaming      | MJPEG multipart  | Simple; works with HTML img tag           |
| Database             | PostgreSQL       | Relational; ACID; excellent async support |
| ORM                  | SQLAlchemy async | Type-safe; async sessions                 |
| Frontend             | React 18         | Hooks; WebSocket; lightweight             |
| Containerisation     | Docker Compose   | One-command startup                       |

---

## 🧪 Running Tests

```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v
```

### Test Coverage

| Test Class        | What it tests                                         |
| ----------------- | ----------------------------------------------------- |
| TestDetector      | Face detection on blank frames, BoundingBox dataclass |
| TestAnnotator     | Pillow drawing with/without bbox, edge cases          |
| TestFrameStore    | asyncio queue push/pop, overflow handling             |
| TestHTTPEndpoints | /health, /roi pagination, /stream endpoint            |

---

## 🔧 Configuration

Copy .env.example to .env and adjust if needed:

```bash
cp .env.example .env
```

| Variable          | Default                                                   | Description                  |
| ----------------- | --------------------------------------------------------- | ---------------------------- |
| DATABASE_URL      | postgresql+asyncpg://postgres:postgres@db:5432/facedetect | PostgreSQL connection string |
| POSTGRES_USER     | postgres                                                  | Database user                |
| POSTGRES_PASSWORD | postgres                                                  | Database password            |
| POSTGRES_DB       | facedetect                                                | Database name                |
| MAX_FRAME_QUEUE   | 30                                                        | Max frames in MJPEG buffer   |
| CORS_ORIGINS      | [http://localhost:3000](http://localhost:3000)            | Allowed frontend origins     |

---

## 🗑️ Clear Detection History

```bash
docker exec face-detection-system-db-1 psql -U postgres -d facedetect -c "DELETE FROM face_detections;"
```

---

## 🐛 Troubleshooting

**Port already in use:**

```bash
sudo kill -9 $(sudo lsof -t -i :8000)
sudo kill -9 $(sudo lsof -t -i :3000)
docker compose up -d
```

**Backend can't connect to database:**

```bash
docker compose down
docker network prune -f
docker compose up -d
```

**Permission denied on docker commands:**

```bash
sudo chmod 666 /var/run/docker.sock
sudo usermod -aG docker $USER
newgrp docker
```

**Check logs:**

```bash
docker logs face-detection-system-backend-1 --tail 20
docker logs face-detection-system-db-1 --tail 20
docker logs face-detection-system-frontend-1 --tail 20
```

---

## 👩‍💻 Author

**Shreya** — [github.com/Shreya0801](https://github.com/Shreya0801)

## 📝 Note

This project was built with AI assistance.

---

## 🔒 Security Notes

- CORS configured to allow only specified origins
- Input validation via Pydantic on all endpoints
- Security headers added (X-Content-Type-Options, X-Frame-Options, X-XSS-Protection)
- Base image `python:3.11-slim` has known CVEs — for production, pin to a patched digest or use `python:3.11-alpine`

## 📄 License

MIT
