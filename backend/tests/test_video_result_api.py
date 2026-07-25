from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_cartoonize_video_result_returns_file(monkeypatch, tmp_path: Path) -> None:
    output_path = tmp_path / "result.mp4"
    output_path.write_bytes(b"fake-video-bytes")

    class DummyResult:
        state = "SUCCESS"
        result = {"output_path": str(output_path)}

        def successful(self) -> bool:
            return True

        def failed(self) -> bool:
            return False

    monkeypatch.setattr("app.api.routes.AsyncResult", lambda job_id, app=None: DummyResult())

    response = client.get("/cartoonize/video/result/job-123")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("video/mp4")
    assert response.content == b"fake-video-bytes"


def test_cartoonize_video_result_returns_processing(monkeypatch) -> None:
    class DummyResult:
        state = "STARTED"

        def successful(self) -> bool:
            return False

        def failed(self) -> bool:
            return False

    monkeypatch.setattr("app.api.routes.AsyncResult", lambda job_id, app=None: DummyResult())

    response = client.get("/cartoonize/video/result/job-123")

    assert response.status_code == 202
    assert response.json()["detail"] == "Video job is still processing."
