from io import BytesIO

import cv2
import numpy as np
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def build_test_image_bytes() -> bytes:
    image = np.full((64, 64, 3), 180, dtype=np.uint8)
    success, encoded = cv2.imencode(".png", image)
    assert success
    return encoded.tobytes()


def test_suggest_emoji_returns_match(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.routes.suggest_emoji_from_image",
        lambda image_bgr: {
            "expression": "smiling",
            "skin_tone": "fitzpatrick_3",
            "emoji_name": "smiling-face",
            "asset_path": "assets/emoji/smiling/fitzpatrick_3.svg",
            "emoji_codepoint": "1f642",
        },
    )

    response = client.post(
        "/suggest-emoji",
        files={"file": ("sample.png", BytesIO(build_test_image_bytes()), "image/png")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["expression"] == "smiling"
    assert payload["skin_tone"] == "fitzpatrick_3"
    assert payload["emoji_name"] == "smiling-face"


def test_suggest_emoji_returns_no_face_error(monkeypatch) -> None:
    monkeypatch.setattr("app.api.routes.suggest_emoji_from_image", lambda image_bgr: None)

    response = client.post(
        "/suggest-emoji",
        files={"file": ("sample.png", BytesIO(build_test_image_bytes()), "image/png")},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "No face detected in the uploaded image."
