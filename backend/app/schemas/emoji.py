from pydantic import BaseModel


class EmojiSuggestionResponse(BaseModel):
    expression: str
    skin_tone: str
    emoji_name: str
    asset_path: str
