from __future__ import annotations

from typing import Final

import cv2
import numpy as np


SKIN_TONE_BUCKETS: Final = (
    "fitzpatrick_1",
    "fitzpatrick_2",
    "fitzpatrick_3",
    "fitzpatrick_4",
    "fitzpatrick_5",
    "fitzpatrick_6",
)


def estimate_skin_tone(image_bgr: np.ndarray, face_bbox: tuple[int, int, int, int]) -> str:
    x, y, width, height = face_bbox
    image_height, image_width = image_bgr.shape[:2]
    x = max(0, x)
    y = max(0, y)
    width = min(width, image_width - x)
    height = min(height, image_height - y)
    if width <= 0 or height <= 0:
        raise ValueError("face_bbox must describe a valid region.")

    face_region = image_bgr[y : y + height, x : x + width]
    if face_region.size == 0:
        raise ValueError("face region cannot be empty.")

    forehead = face_region[: max(1, height // 5), width // 4 : (3 * width) // 4]
    left_cheek = face_region[height // 3 : (2 * height) // 3, width // 8 : width // 3]
    right_cheek = face_region[height // 3 : (2 * height) // 3, (2 * width) // 3 : (7 * width) // 8]
    samples = [region for region in (forehead, left_cheek, right_cheek) if region.size > 0]
    if not samples:
        samples = [face_region]

    stacked = np.concatenate([sample.reshape(-1, 3) for sample in samples], axis=0)
    lab_pixels = cv2.cvtColor(stacked.reshape(-1, 1, 3), cv2.COLOR_BGR2LAB).reshape(-1, 3)
    lightness = float(np.mean(lab_pixels[:, 0]))

    thresholds = (50.0, 85.0, 115.0, 145.0, 175.0)
    bucket_index = 0
    for threshold in thresholds:
        if lightness >= threshold:
            bucket_index += 1
    return SKIN_TONE_BUCKETS[min(bucket_index, len(SKIN_TONE_BUCKETS) - 1)]
