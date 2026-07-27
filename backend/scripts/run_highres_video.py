from pathlib import Path
import cv2
import numpy as np
from app.services.cartoonize.video_pipeline import cartoonize_video_file


def build_test_video(path: Path, frames: int = 8, size=(1280, 720)) -> Path:
    writer = cv2.VideoWriter(
        str(path), cv2.VideoWriter_fourcc(*"mp4v"), 6.0, size
    )
    if not writer.isOpened():
        raise RuntimeError("Unable to open video writer")
    try:
        for i in range(frames):
            frame = np.zeros((size[1], size[0], 3), dtype=np.uint8)
            # gradient halves to make some variation
            frame[:, : size[0] // 2] = (30 + i * 5, 120, 220)
            frame[:, size[0] // 2 :] = (220, 160 + i * 3, 40)
            cv2.circle(frame, (size[0] // 2, size[1] // 2), 40 + i * 2, (255, 255, 255), -1)
            writer.write(frame)
    finally:
        writer.release()
    return path


def main():
    root = Path.cwd()
    src = root / "sample_highres_input.mp4"
    out = root / "sample_highres_output.mp4"
    print("Building high-res test video...", src)
    build_test_video(src, frames=8, size=(1280, 720))
    print("Cartoonizing high-res video... this may take longer")
    cartoonize_video_file(src, out, palette_size=8, smoothing_strength=6)
    print("Done. Output at:", out)


if __name__ == "__main__":
    main()
