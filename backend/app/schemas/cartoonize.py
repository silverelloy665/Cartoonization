from pydantic import BaseModel, Field


class ImageCartoonizeOptions(BaseModel):
    edge_threshold: int = Field(default=9, ge=0, le=50)
    palette_size: int = Field(default=8, ge=2, le=16)
    smoothing_strength: int = Field(default=5, ge=1, le=10)


class ImageCartoonizeResponse(BaseModel):
    filename: str
    content_type: str
