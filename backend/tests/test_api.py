"""Tests — run with: pytest backend/tests/ -v"""
import io
import pytest
from httpx import AsyncClient, ASGITransport
from PIL import Image
from app.main import app
from app.services.detector import BoundingBox


def _make_jpeg(width=320, height=240, color=(100, 150, 200)) -> bytes:
    img = Image.new("RGB", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


@pytest.fixture
def sample_jpeg():
    return _make_jpeg()

@pytest.fixture
def sample_bbox():
    return BoundingBox(x=50, y=40, width=100, height=120, confidence=0.92)


class TestDetector:
    def test_blank_frame_does_not_crash(self):
        from app.services.detector import detect_face
        result = detect_face(_make_jpeg(color=(200, 180, 160)))
        assert result is None or hasattr(result, "x")

    def test_bounding_box_fields(self, sample_bbox):
        assert sample_bbox.x == 50
        assert 0.0 <= sample_bbox.confidence <= 1.0


class TestAnnotator:
    def test_no_bbox_returns_jpeg(self, sample_jpeg):
        from app.services.annotator import annotate_frame
        result = annotate_frame(sample_jpeg, None)
        assert Image.open(io.BytesIO(result)).format == "JPEG"

    def test_with_bbox_returns_same_size(self, sample_jpeg, sample_bbox):
        from app.services.annotator import annotate_frame
        result = annotate_frame(sample_jpeg, sample_bbox)
        img = Image.open(io.BytesIO(result))
        assert img.format == "JPEG"
        assert img.size == (320, 240)

    def test_edge_bbox_does_not_crash(self, sample_jpeg):
        from app.services.annotator import annotate_frame
        edge = BoundingBox(x=0, y=0, width=320, height=240, confidence=0.5)
        assert len(annotate_frame(sample_jpeg, edge)) > 0


@pytest.mark.asyncio
class TestFrameStore:
    async def test_push_and_pop(self):
        import asyncio
        import app.services.frame_store as fs
        fs.frame_queue = asyncio.Queue(maxsize=30)
        await fs.push_frame(b"hello")
        assert await fs.pop_frame() == b"hello"

    async def test_full_queue_drops_oldest(self):
        import asyncio
        import app.services.frame_store as fs
        fs.frame_queue = asyncio.Queue(maxsize=2)
        await fs.push_frame(b"a")
        await fs.push_frame(b"b")
        await fs.push_frame(b"c")
        assert fs.frame_queue.qsize() <= 2


@pytest.mark.asyncio
class TestHTTPEndpoints:
    @pytest.fixture
    async def client(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            yield ac

    async def test_health_ok(self, client):
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    async def test_roi_returns_list(self, client):
        resp = await client.get("/roi")
        assert resp.status_code == 200
        body = resp.json()
        assert "total" in body and "items" in body

    async def test_stream_is_mjpeg(self, client):
        async with client.stream("GET", "/stream") as resp:
            assert resp.status_code == 200
            assert "multipart" in resp.headers.get("content-type", "")
