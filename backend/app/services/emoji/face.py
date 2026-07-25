from __future__ import annotations

import os
from pathlib import Path

import cv2
import numpy as np


def detect_face_bbox(image_bgr: np.ndarray) -> tuple[int, int, int, int] | None:
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    cascade_path = Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(str(cascade_path))
    faces = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(48, 48))
    if len(faces) == 0:
        return None
    x, y, width, height = max(faces, key=lambda item: item[2] * item[3])
    return int(x), int(y), int(width), int(height)


def _template_point(cx: float, cy: float, rx: float, ry: float, angle: float) -> tuple[float, float]:
    return cx + rx * np.cos(angle), cy + ry * np.sin(angle)


def approximate_landmarks_from_bbox(face_bbox: tuple[int, int, int, int]) -> np.ndarray:
    x, y, width, height = face_bbox
    landmarks = np.zeros((68, 2), dtype=np.float32)

    center_x = x + width / 2.0
    center_y = y + height / 2.0
    jaw_center_y = y + height * 0.72
    for index, angle in enumerate(np.linspace(np.pi, 2.0 * np.pi, 17)):
        landmarks[index] = _template_point(center_x, jaw_center_y, width * 0.42, height * 0.30, angle)

    for index, offset in enumerate(np.linspace(-0.28, 0.28, 5), start=17):
        landmarks[index] = (center_x + offset * width, y + height * 0.28 + abs(offset) * height * 0.03)

    landmarks[22] = landmarks[21] + np.array([width * 0.05, -height * 0.01])
    landmarks[23] = landmarks[22] + np.array([width * 0.05, 0.01])
    landmarks[24] = landmarks[23] + np.array([width * 0.05, 0.02])
    landmarks[25] = landmarks[24] + np.array([width * 0.05, 0.01])
    landmarks[26] = landmarks[25] + np.array([width * 0.05, -0.01])

    nose_bridge_x = center_x
    for index, progress in enumerate(np.linspace(0.0, 1.0, 4), start=27):
        landmarks[index] = (nose_bridge_x, y + height * (0.30 + 0.20 * progress))
    landmarks[31] = (center_x - width * 0.08, y + height * 0.55)
    landmarks[32] = (center_x, y + height * 0.57)
    landmarks[33] = (center_x + width * 0.08, y + height * 0.55)
    landmarks[34] = (center_x - width * 0.05, y + height * 0.62)
    landmarks[35] = (center_x + width * 0.05, y + height * 0.62)

    left_eye_center = (x + width * 0.32, y + height * 0.38)
    right_eye_center = (x + width * 0.68, y + height * 0.38)
    for eye_center, start_index in ((left_eye_center, 36), (right_eye_center, 42)):
        cx, cy = eye_center
        eye_points = [
            (cx - width * 0.07, cy),
            (cx - width * 0.03, cy - height * 0.035),
            (cx + width * 0.03, cy - height * 0.035),
            (cx + width * 0.07, cy),
            (cx + width * 0.03, cy + height * 0.035),
            (cx - width * 0.03, cy + height * 0.035),
        ]
        for offset, point in enumerate(eye_points):
            landmarks[start_index + offset] = point

    mouth_center = (center_x, y + height * 0.70)
    mouth_points = [
        (mouth_center[0] - width * 0.15, mouth_center[1]),
        (mouth_center[0] - width * 0.10, mouth_center[1] - height * 0.03),
        (mouth_center[0] - width * 0.05, mouth_center[1] - height * 0.04),
        (mouth_center[0], mouth_center[1] - height * 0.045),
        (mouth_center[0] + width * 0.05, mouth_center[1] - height * 0.04),
        (mouth_center[0] + width * 0.10, mouth_center[1] - height * 0.03),
        (mouth_center[0] + width * 0.15, mouth_center[1]),
        (mouth_center[0] + width * 0.10, mouth_center[1] + height * 0.03),
        (mouth_center[0] + width * 0.05, mouth_center[1] + height * 0.04),
        (mouth_center[0], mouth_center[1] + height * 0.045),
        (mouth_center[0] - width * 0.05, mouth_center[1] + height * 0.04),
        (mouth_center[0] - width * 0.10, mouth_center[1] + height * 0.03),
        (mouth_center[0] - width * 0.15, mouth_center[1]),
        (mouth_center[0] - width * 0.10, mouth_center[1] - height * 0.015),
        (mouth_center[0] - width * 0.05, mouth_center[1] - height * 0.02),
        (mouth_center[0], mouth_center[1] - height * 0.022),
        (mouth_center[0] + width * 0.05, mouth_center[1] - height * 0.02),
        (mouth_center[0] + width * 0.10, mouth_center[1] - height * 0.015),
        (mouth_center[0] + width * 0.05, mouth_center[1] + height * 0.015),
        (mouth_center[0] - width * 0.05, mouth_center[1] + height * 0.015),
    ]
    for offset, point in enumerate(mouth_points, start=48):
        landmarks[offset] = point

    return landmarks


def detect_dlib_landmarks(image_bgr: np.ndarray) -> np.ndarray | None:
    predictor_path = os.getenv("DLIB_LANDMARK_MODEL_PATH")
    if not predictor_path or not Path(predictor_path).exists():
        return None

    try:
        import dlib  # type: ignore
    except ImportError:
        return None

    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    predictor = dlib.shape_predictor(str(predictor_path))
    detector = dlib.get_frontal_face_detector()
    faces = detector(gray)
    if not faces:
        return None

    shape = predictor(gray, faces[0])
    return np.array([[shape.part(i).x, shape.part(i).y] for i in range(68)], dtype=np.float32)


def detect_face_and_landmarks(image_bgr: np.ndarray) -> tuple[tuple[int, int, int, int], np.ndarray] | None:
    face_bbox = detect_face_bbox(image_bgr)
    if face_bbox is None:
        return None

    dlib_landmarks = detect_dlib_landmarks(image_bgr)
    if dlib_landmarks is not None:
        return face_bbox, dlib_landmarks

    return face_bbox, approximate_landmarks_from_bbox(face_bbox)
