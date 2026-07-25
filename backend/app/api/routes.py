from io import BytesIO

import cv2
import numpy as np
from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import Response

from app.core.config import get_settings
from app.schemas.cartoonize import ImageCartoonizeOptions
from app.services.cartoonize.image_pipeline import cartoonize_image

router = APIRouter()
settings = get_settings()


ALLOWED_IMAGE_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/bmp",
}


@router.get("/", tags=["health"])
def root() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/cartoonize/image", tags=["cartoonize"])
async def cartoonize_uploaded_image(
    file: UploadFile = File(...),
    edge_threshold: int = Query(default=9, ge=0, le=50),
    palette_size: int = Query(default=8, ge=2, le=16),
    smoothing_strength: int = Query(default=5, ge=1, le=10),
) -> Response:
    if not file.filename:
        raise HTTPException(status_code=400, detail="File name is required.")
    if file.content_type not in ALLOWED_IMAGE_CONTENT_TYPES:
        raise HTTPException(status_code=415, detail="Unsupported image format.")

    raw_bytes = await file.read()
    max_upload_bytes = settings.max_upload_size_mb * 1024 * 1024
    if not raw_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(raw_bytes) > max_upload_bytes:
        raise HTTPException(status_code=413, detail="File too large.")

    image_array = np.frombuffer(raw_bytes, dtype=np.uint8)
    image_bgr = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    if image_bgr is None:
        raise HTTPException(status_code=400, detail="Unable to decode image file.")

    options = ImageCartoonizeOptions(
        edge_threshold=edge_threshold,
        palette_size=palette_size,
        smoothing_strength=smoothing_strength,
    )
    cartoon = cartoonize_image(
        image_bgr,
        edge_threshold=options.edge_threshold,
        palette_size=options.palette_size,
        smoothing_strength=options.smoothing_strength,
    )

    success, encoded = cv2.imencode(".png", cartoon)
    if not success:
        raise HTTPException(status_code=500, detail="Unable to encode cartoonized image.")

    return Response(
        content=encoded.tobytes(),
        media_type="image/png",
        headers={"X-Output-Filename": f"cartoonized-{file.filename}.png"},
    )
