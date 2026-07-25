from __future__ import annotations

from typing import Final

EMOJI_DATASET: Final = [
    {"expression": "neutral", "skin_tone": "fitzpatrick_1", "emoji_name": "neutral-face", "asset_path": "assets/emoji/neutral/fitzpatrick_1.svg"},
    {"expression": "neutral", "skin_tone": "fitzpatrick_2", "emoji_name": "neutral-face", "asset_path": "assets/emoji/neutral/fitzpatrick_2.svg"},
    {"expression": "neutral", "skin_tone": "fitzpatrick_3", "emoji_name": "neutral-face", "asset_path": "assets/emoji/neutral/fitzpatrick_3.svg"},
    {"expression": "neutral", "skin_tone": "fitzpatrick_4", "emoji_name": "neutral-face", "asset_path": "assets/emoji/neutral/fitzpatrick_4.svg"},
    {"expression": "neutral", "skin_tone": "fitzpatrick_5", "emoji_name": "neutral-face", "asset_path": "assets/emoji/neutral/fitzpatrick_5.svg"},
    {"expression": "neutral", "skin_tone": "fitzpatrick_6", "emoji_name": "neutral-face", "asset_path": "assets/emoji/neutral/fitzpatrick_6.svg"},
    {"expression": "smiling", "skin_tone": "fitzpatrick_1", "emoji_name": "smiling-face", "asset_path": "assets/emoji/smiling/fitzpatrick_1.svg"},
    {"expression": "smiling", "skin_tone": "fitzpatrick_2", "emoji_name": "smiling-face", "asset_path": "assets/emoji/smiling/fitzpatrick_2.svg"},
    {"expression": "smiling", "skin_tone": "fitzpatrick_3", "emoji_name": "smiling-face", "asset_path": "assets/emoji/smiling/fitzpatrick_3.svg"},
    {"expression": "smiling", "skin_tone": "fitzpatrick_4", "emoji_name": "smiling-face", "asset_path": "assets/emoji/smiling/fitzpatrick_4.svg"},
    {"expression": "smiling", "skin_tone": "fitzpatrick_5", "emoji_name": "smiling-face", "asset_path": "assets/emoji/smiling/fitzpatrick_5.svg"},
    {"expression": "smiling", "skin_tone": "fitzpatrick_6", "emoji_name": "smiling-face", "asset_path": "assets/emoji/smiling/fitzpatrick_6.svg"},
    {"expression": "surprised", "skin_tone": "fitzpatrick_1", "emoji_name": "surprised-face", "asset_path": "assets/emoji/surprised/fitzpatrick_1.svg"},
    {"expression": "surprised", "skin_tone": "fitzpatrick_2", "emoji_name": "surprised-face", "asset_path": "assets/emoji/surprised/fitzpatrick_2.svg"},
    {"expression": "surprised", "skin_tone": "fitzpatrick_3", "emoji_name": "surprised-face", "asset_path": "assets/emoji/surprised/fitzpatrick_3.svg"},
    {"expression": "surprised", "skin_tone": "fitzpatrick_4", "emoji_name": "surprised-face", "asset_path": "assets/emoji/surprised/fitzpatrick_4.svg"},
    {"expression": "surprised", "skin_tone": "fitzpatrick_5", "emoji_name": "surprised-face", "asset_path": "assets/emoji/surprised/fitzpatrick_5.svg"},
    {"expression": "surprised", "skin_tone": "fitzpatrick_6", "emoji_name": "surprised-face", "asset_path": "assets/emoji/surprised/fitzpatrick_6.svg"},
    {"expression": "laughing", "skin_tone": "fitzpatrick_1", "emoji_name": "laughing-face", "asset_path": "assets/emoji/laughing/fitzpatrick_1.svg"},
    {"expression": "laughing", "skin_tone": "fitzpatrick_2", "emoji_name": "laughing-face", "asset_path": "assets/emoji/laughing/fitzpatrick_2.svg"},
    {"expression": "laughing", "skin_tone": "fitzpatrick_3", "emoji_name": "laughing-face", "asset_path": "assets/emoji/laughing/fitzpatrick_3.svg"},
    {"expression": "laughing", "skin_tone": "fitzpatrick_4", "emoji_name": "laughing-face", "asset_path": "assets/emoji/laughing/fitzpatrick_4.svg"},
    {"expression": "laughing", "skin_tone": "fitzpatrick_5", "emoji_name": "laughing-face", "asset_path": "assets/emoji/laughing/fitzpatrick_5.svg"},
    {"expression": "laughing", "skin_tone": "fitzpatrick_6", "emoji_name": "laughing-face", "asset_path": "assets/emoji/laughing/fitzpatrick_6.svg"},
]


def match_emoji(expression: str, skin_tone: str) -> dict[str, str]:
    exact_match = next(
        (
            item
            for item in EMOJI_DATASET
            if item["expression"] == expression and item["skin_tone"] == skin_tone
        ),
        None,
    )
    if exact_match is not None:
        return exact_match

    expression_match = next((item for item in EMOJI_DATASET if item["expression"] == expression), None)
    if expression_match is not None:
        return expression_match

    return EMOJI_DATASET[0]
