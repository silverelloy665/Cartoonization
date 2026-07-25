from pathlib import Path

import cv2
import numpy as np
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def build_test_video_bytes() -> bytes:
    temp_path = Path.cwd() / "_video_api_test.mp4"
    writer = cv2.VideoWriter(
        str(temp_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        6.0,
        (32, 32),
    )
    assert writer.isOpened()
    try:
        for index in range(2):
            frame = np.full((32, 32, 3), index * 80, dtype=np.uint8)
            writer.write(frame)
    finally:
        writer.release()

    data = temp_path.read_bytes()
    temp_path.unlink()
    return data


def test_cartoonize_video_endpoint_queues_job(monkeypatch) -> None:
    class DummyAsyncResult:
        id = "job-123"

    class DummyDelay:
        def delay(self, *args, **kwargs):
            return DummyAsyncResult()

    monkeypatch.setattr("app.api.routes.process_video_task", DummyDelay())

    response = client.post(
        "/cartoonize/video?palette_size=4&smoothing_strength=2",
        files={"file": ("sample.mp4", build_test_video_bytes(), "video/mp4")},
    )

    assert response.status_code == 202
    payload = response.json()
    assert payload["status"] == "queued"
    assert payload["job_id"] == "job-123"
    assert payload["detail"] == "Video job accepted for processing."


def test_cartoonize_video_status_reports_state(monkeypatch) -> None:
    class DummyResult:
        state = "SUCCESS"
        result = {"output_path": "/tmp/output.mp4"}

        def successful(self) -> bool:
            return True

        def failed(self) -> bool:
            return False

    monkeypatch.setattr("app.api.routes.AsyncResult", lambda job_id, app=None: DummyResult())

    response = client.get("/cartoonize/video/status/job-123")

    assert response.status_code == 200
    payload = response.json()
    assert payload["job_id"] == "job-123"
    assert payload["status"] == "done"
    assert payload["output_path"] == "/tmp/output.mp4"
    assert payload["error"] is None
