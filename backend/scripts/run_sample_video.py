from pathlib import Path
import cv2
import numpy as np
from app.services.cartoonize.video_pipeline import cartoonize_video_file


def build_test_video(path: Path, frames: int = 3, size=(64, 64)) -> Path:
    writer = cv2.VideoWriter(
        str(path), cv2.VideoWriter_fourcc(*"mp4v"), 6.0, size
    )
    if not writer.isOpened():
        raise RuntimeError("Unable to open video writer")
    try:
        for i in range(frames):
            frame = np.zeros((size[1], size[0], 3), dtype=np.uint8)
            frame[:, : size[0] // 2] = (20 + i * 20, 100, 200)
            frame[:, size[0] // 2 :] = (200, 150 + i * 10, 40)
            cv2.circle(frame, (size[0] // 2, size[1] // 2), 8 + i, (255, 255, 255), -1)
            writer.write(frame)
    finally:
        writer.release()
    return path


def main():
    root = Path.cwd()
    src = root / "sample_input.mp4"
    out = root / "sample_output.mp4"
    print("Building test video...", src)
    build_test_video(src, frames=4, size=(64, 64))
    print("Cartoonizing video... this may take a few seconds")
    cartoonize_video_file(src, out, palette_size=4, smoothing_strength=2)
    print("Done. Output at:", out)


if __name__ == "__main__":
    main()
