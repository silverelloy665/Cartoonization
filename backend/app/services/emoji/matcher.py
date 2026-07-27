from __future__ import annotations

import cv2
import numpy as np

from app.schemas.emoji import EmojiSuggestionResponse
from app.services.emoji.dataset import match_emoji
from app.services.emoji.expression import classify_expression_from_landmarks
from app.services.emoji.face import detect_face_and_landmarks
from app.services.emoji.skin_tone import estimate_skin_tone


def suggest_emoji_from_image(image_bgr: np.ndarray) -> EmojiSuggestionResponse | None:
    face_result = detect_face_and_landmarks(image_bgr)
    if face_result is None:
        return None

    face_bbox, landmarks = face_result
    expression = classify_expression_from_landmarks(landmarks)
    skin_tone = estimate_skin_tone(image_bgr, face_bbox)
    emoji_match = match_emoji(expression, skin_tone)
    return EmojiSuggestionResponse(
        expression=expression,
        skin_tone=skin_tone,
        emoji_name=emoji_match["emoji_name"],
        asset_path=emoji_match["asset_path"],
    )
