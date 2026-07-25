from pathlib import Path
from uuid import uuid4

import cv2
import numpy as np
from celery import states
from celery.result import AsyncResult
from kombu.exceptions import OperationalError
from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import Response

from app.celery_app import celery_app
from app.core.config import get_settings
from app.schemas.cartoonize import ImageCartoonizeOptions
from app.schemas.emoji import EmojiSuggestionResponse
from app.schemas.video import VideoJobSubmitResponse, VideoJobStatusResponse
from app.services.cartoonize.image_pipeline import cartoonize_image
from app.services.emoji.matcher import suggest_emoji_from_image
from app.tasks.video_tasks import process_video_task

router = APIRouter()
settings = get_settings()


ALLOWED_IMAGE_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/bmp",
}

ALLOWED_VIDEO_CONTENT_TYPES = {
    "video/mp4",
    "video/quicktime",
    "video/webm",
    "video/x-matroska",
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


@router.post("/cartoonize/video", tags=["cartoonize"], status_code=202)
async def cartoonize_uploaded_video(
    file: UploadFile = File(...),
    edge_threshold: int = Query(default=9, ge=0, le=50),
    palette_size: int = Query(default=8, ge=2, le=16),
    smoothing_strength: int = Query(default=5, ge=1, le=10),
) -> VideoJobSubmitResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="File name is required.")
    if file.content_type not in ALLOWED_VIDEO_CONTENT_TYPES:
        raise HTTPException(status_code=415, detail="Unsupported video format.")

    raw_bytes = await file.read()
    max_upload_bytes = settings.max_upload_size_mb * 1024 * 1024
    if not raw_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(raw_bytes) > max_upload_bytes:
        raise HTTPException(status_code=413, detail="File too large.")

    job_id = str(uuid4())
    job_dir = Path(settings.temp_dir) / "video-jobs" / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    input_suffix = Path(file.filename).suffix or ".mp4"
    input_path = job_dir / f"input{input_suffix}"
    output_path = job_dir / "cartoonized.mp4"
    input_path.write_bytes(raw_bytes)

    try:
        process_video_task.delay(
            str(input_path),
            str(output_path),
            edge_threshold=edge_threshold,
            palette_size=palette_size,
            smoothing_strength=smoothing_strength,
        )
    except OperationalError as exc:
        if input_path.exists():
            input_path.unlink()
        raise HTTPException(status_code=503, detail="Video queue is unavailable.") from exc

    return VideoJobSubmitResponse(
        job_id=job_id,
        status="queued",
        detail="Video job accepted for processing.",
    )


def _map_celery_state(state: str) -> str:
    if state == states.PENDING:
        return "queued"
    if state in {states.STARTED, states.RETRY}:
        return "processing"
    if state == states.SUCCESS:
        return "done"
    if state in {states.FAILURE, states.REVOKED}:
        return "failed"
    return state.lower()


@router.get("/cartoonize/video/status/{job_id}", tags=["cartoonize"])
def cartoonize_video_status(job_id: str) -> VideoJobStatusResponse:
    result = AsyncResult(job_id, app=celery_app)
    status = _map_celery_state(result.state)
    output_path = None
    error = None

    if result.successful() and isinstance(result.result, dict):
        output_path = result.result.get("output_path")
    elif result.failed() and result.result is not None:
        error = str(result.result)

    return VideoJobStatusResponse(
        job_id=job_id,
        status=status,
        output_path=output_path,
        error=error,
    )


@router.post("/suggest-emoji", tags=["emoji"])
async def suggest_emoji(
    file: UploadFile = File(...),
) -> EmojiSuggestionResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="File name is required.")
    if file.content_type not in ALLOWED_IMAGE_CONTENT_TYPES:
        raise HTTPException(status_code=415, detail="Unsupported image format."
        )

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

    suggestion = suggest_emoji_from_image(image_bgr)
    if suggestion is None:
        raise HTTPException(status_code=422, detail="No face detected in the uploaded image.")

    return suggestion
