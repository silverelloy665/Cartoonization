from __future__ import annotations

from pathlib import Path

from app.celery_app import celery_app
from app.services.cartoonize.video_pipeline import cartoonize_video_file


@celery_app.task(name="cartoonverse.process_video")
def process_video_task(
    input_path: str,
    output_path: str,
    *,
    edge_threshold: int = 9,
    palette_size: int = 8,
    smoothing_strength: int = 5,
) -> dict[str, str]:
    source_path = Path(input_path)
    target_path = Path(output_path)

    try:
        cartoonized_path = cartoonize_video_file(
            source_path,
            target_path,
            edge_threshold=edge_threshold,
            palette_size=palette_size,
            smoothing_strength=smoothing_strength,
        )
        return {"output_path": str(cartoonized_path)}
    finally:
        if source_path.exists():
            source_path.unlink()
