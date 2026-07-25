from io import BytesIO

import cv2
import numpy as np
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def build_test_image_bytes() -> bytes:
    image = np.zeros((48, 48, 3), dtype=np.uint8)
    image[:, :24] = (30, 120, 220)
    image[:, 24:] = (220, 160, 40)
    success, encoded = cv2.imencode(".png", image)
    assert success
    return encoded.tobytes()


def test_cartoonize_image_endpoint_returns_png() -> None:
    response = client.post(
        "/cartoonize/image?palette_size=4&smoothing_strength=2",
        files={"file": ("sample.png", BytesIO(build_test_image_bytes()), "image/png")},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.content

    image_array = np.frombuffer(response.content, dtype=np.uint8)
    cartoon = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    assert cartoon is not None
    assert cartoon.shape == (48, 48, 3)


def test_cartoonize_image_endpoint_rejects_bad_type() -> None:
    response = client.post(
        "/cartoonize/image",
        files={"file": ("sample.txt", BytesIO(b"not an image"), "text/plain")},
    )

    assert response.status_code == 415
    assert response.json()["detail"] == "Unsupported image format."
