import numpy as np

from app.services.emoji.expression import classify_expression_from_landmarks


def build_landmarks(eye_scale: float, mouth_scale: float) -> np.ndarray:
    landmarks = np.zeros((68, 2), dtype=np.float32)

    left_eye = np.array([
        [0.0, 0.0],
        [1.0, -eye_scale],
        [3.0, -eye_scale],
        [4.0, 0.0],
        [3.0, eye_scale],
        [1.0, eye_scale],
    ], dtype=np.float32)
    right_eye = left_eye + np.array([10.0, 0.0], dtype=np.float32)
    landmarks[36:42] = left_eye
    landmarks[42:48] = right_eye

    mouth = np.array([
        [0.0, 0.0],
        [1.0, -mouth_scale * 0.2],
        [2.0, -mouth_scale * 0.5],
        [3.0, -mouth_scale * 0.6],
        [4.0, -mouth_scale * 0.5],
        [5.0, -mouth_scale * 0.2],
        [6.0, 0.0],
        [5.0, mouth_scale * 0.2],
        [4.0, mouth_scale * 0.5],
        [3.0, mouth_scale * 0.6],
        [2.0, mouth_scale * 0.5],
        [1.0, mouth_scale * 0.2],
        [0.0, 0.0],
        [1.0, -mouth_scale * 0.05],
        [2.0, -mouth_scale * 0.08],
        [3.0, -mouth_scale * 0.10],
        [4.0, -mouth_scale * 0.08],
        [5.0, -mouth_scale * 0.05],
        [4.0, mouth_scale * 0.05],
        [1.0, mouth_scale * 0.05],
    ], dtype=np.float32)
    landmarks[48:68] = mouth
    return landmarks


def test_classify_expression_neutral() -> None:
    landmarks = build_landmarks(eye_scale=0.1, mouth_scale=0.1)

    expression = classify_expression_from_landmarks(landmarks)

    assert expression == "neutral"


def test_classify_expression_smiling() -> None:
    landmarks = build_landmarks(eye_scale=0.3, mouth_scale=0.4)

    expression = classify_expression_from_landmarks(landmarks)

    assert expression == "smiling"


def test_classify_expression_surprised() -> None:
    landmarks = build_landmarks(eye_scale=0.25, mouth_scale=0.8)

    expression = classify_expression_from_landmarks(landmarks)

    assert expression == "surprised"
