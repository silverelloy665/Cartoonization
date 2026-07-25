from pathlib import Path

import cv2
import numpy as np

from app.services.cartoonize.video_pipeline import cartoonize_video_file


def build_test_video(path: Path) -> Path:
    writer = cv2.VideoWriter(
        str(path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        6.0,
        (48, 48),
    )
    assert writer.isOpened()

    try:
        for index in range(3):
            frame = np.zeros((48, 48, 3), dtype=np.uint8)
            frame[:, :24] = (20 + index * 20, 90, 200)
            frame[:, 24:] = (220, 150 + index * 10, 40)
            cv2.circle(frame, (24, 24), 8 + index, (255, 255, 255), -1)
            writer.write(frame)
    finally:
        writer.release()

    return path


def test_cartoonize_video_file_writes_output(tmp_path: Path) -> None:
    source_path = build_test_video(tmp_path / "source.mp4")
    target_path = tmp_path / "cartoonized.mp4"

    result_path = cartoonize_video_file(source_path, target_path, palette_size=4, smoothing_strength=2)

    assert result_path == target_path
    assert target_path.exists()

    capture = cv2.VideoCapture(str(target_path))
    try:
        frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        assert frame_count == 3
        success, frame = capture.read()
        assert success
        assert frame is not None
        assert frame.shape[:2] == (48, 48)
    finally:
        capture.release()
