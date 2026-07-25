from __future__ import annotations

from typing import Final

import numpy as np

LEFT_EYE: Final = slice(36, 42)
RIGHT_EYE: Final = slice(42, 48)
MOUTH: Final = slice(48, 68)


def _euclidean_distance(point_a: np.ndarray, point_b: np.ndarray) -> float:
    return float(np.linalg.norm(point_a - point_b))


def eye_aspect_ratio(eye_points: np.ndarray) -> float:
    if eye_points.shape != (6, 2):
        raise ValueError("eye_points must have shape (6, 2).")

    vertical_one = _euclidean_distance(eye_points[1], eye_points[5])
    vertical_two = _euclidean_distance(eye_points[2], eye_points[4])
    horizontal = _euclidean_distance(eye_points[0], eye_points[3])
    if horizontal == 0:
        raise ValueError("eye_points horizontal distance cannot be zero.")
    return (vertical_one + vertical_two) / (2.0 * horizontal)


def mouth_aspect_ratio(mouth_points: np.ndarray) -> float:
    if mouth_points.shape != (20, 2):
        raise ValueError("mouth_points must have shape (20, 2).")

    vertical_one = _euclidean_distance(mouth_points[2], mouth_points[10])
    vertical_two = _euclidean_distance(mouth_points[4], mouth_points[8])
    horizontal = _euclidean_distance(mouth_points[0], mouth_points[6])
    if horizontal == 0:
        raise ValueError("mouth_points horizontal distance cannot be zero.")
    return (vertical_one + vertical_two) / (2.0 * horizontal)


def classify_expression(eye_ratio: float, mouth_ratio: float) -> str:
    if mouth_ratio >= 0.16 and eye_ratio >= 0.12:
        return "laughing"
    if mouth_ratio >= 0.11:
        return "surprised"
    if mouth_ratio >= 0.06 and eye_ratio >= 0.10:
        return "smiling"
    return "neutral"


def classify_expression_from_landmarks(landmarks: np.ndarray) -> str:
    if landmarks.shape != (68, 2):
        raise ValueError("landmarks must have shape (68, 2).")

    left_eye_ratio = eye_aspect_ratio(landmarks[LEFT_EYE])
    right_eye_ratio = eye_aspect_ratio(landmarks[RIGHT_EYE])
    mouth_ratio = mouth_aspect_ratio(landmarks[MOUTH])
    return classify_expression((left_eye_ratio + right_eye_ratio) / 2.0, mouth_ratio)
