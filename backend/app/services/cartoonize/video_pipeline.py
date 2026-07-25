from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

import cv2
import ffmpeg

from app.services.cartoonize.image_pipeline import cartoonize_image


def _transcode_to_supported_format(source_path: Path, target_path: Path) -> None:
    try:
        (
            ffmpeg.input(str(source_path))
            .output(
                str(target_path),
                vcodec="mpeg4",
                qscale=5,
                pix_fmt="yuv420p",
                **{"an": None},
            )
            .run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as exc:
        stderr = exc.stderr.decode(errors="ignore") if isinstance(exc.stderr, bytes) else str(exc)
        raise ValueError(
            f"Unable to transcode video file: {source_path}\n{stderr}"
        ) from exc


def _get_video_properties(capture: cv2.VideoCapture) -> tuple[float, int, int, int]:
    fps = capture.get(cv2.CAP_PROP_FPS)
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    if fps <= 0:
        fps = 24.0
    if width <= 0 or height <= 0:
        raise ValueError("Unable to determine video dimensions.")
    return fps, width, height, frame_count


def _write_cartoonized_silent_video(
    input_path: Path,
    silent_output_path: Path,
    *,
    edge_threshold: int,
    palette_size: int,
    smoothing_strength: int,
) -> int:
    actual_input_path = input_path
    temp_transcoded_path: Path | None = None

    def _open_capture(source: Path) -> cv2.VideoCapture:
        return cv2.VideoCapture(str(source))

    capture = _open_capture(actual_input_path)
    if not capture.isOpened():
        capture.release()
        temp_transcoded_path = input_path.parent / f"{input_path.stem}-transcoded.mp4"
        _transcode_to_supported_format(input_path, temp_transcoded_path)
        actual_input_path = temp_transcoded_path
        capture = _open_capture(actual_input_path)
        if not capture.isOpened():
            raise ValueError(f"Unable to open video file after transcoding: {actual_input_path}")

    fps, width, height, _ = _get_video_properties(capture)
    writer = cv2.VideoWriter(
        str(silent_output_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height),
    )
    if not writer.isOpened():
        capture.release()
        raise ValueError(f"Unable to create video writer for: {silent_output_path}")

    frame_count = 0
    try:
        while True:
            success, frame = capture.read()
            if not success:
                break
            cartoon_frame = cartoonize_image(
                frame,
                edge_threshold=edge_threshold,
                palette_size=palette_size,
                smoothing_strength=smoothing_strength,
            )
            writer.write(cartoon_frame)
            frame_count += 1

        if frame_count == 0 and temp_transcoded_path is None:
            capture.release()
            writer.release()
            temp_transcoded_path = input_path.parent / f"{input_path.stem}-transcoded.mp4"
            _transcode_to_supported_format(input_path, temp_transcoded_path)
            actual_input_path = temp_transcoded_path
            capture = _open_capture(actual_input_path)
            if not capture.isOpened():
                raise ValueError(f"Unable to open video file after transcoding: {actual_input_path}")

            fps, width, height, _ = _get_video_properties(capture)
            writer = cv2.VideoWriter(
                str(silent_output_path),
                cv2.VideoWriter_fourcc(*"mp4v"),
                fps,
                (width, height),
            )
            if not writer.isOpened():
                capture.release()
                raise ValueError(f"Unable to create video writer for: {silent_output_path}")

            while True:
                success, frame = capture.read()
                if not success:
                    break
                cartoon_frame = cartoonize_image(
                    frame,
                    edge_threshold=edge_threshold,
                    palette_size=palette_size,
                    smoothing_strength=smoothing_strength,
                )
                writer.write(cartoon_frame)
                frame_count += 1
    finally:
        capture.release()
        writer.release()
        if temp_transcoded_path is not None and temp_transcoded_path.exists():
            temp_transcoded_path.unlink(missing_ok=True)

    if frame_count == 0:
        raise ValueError(f"Video contains no readable frames: {actual_input_path}")

    return frame_count


def _mux_original_audio(
    original_path: Path,
    silent_video_path: Path,
    output_path: Path,
) -> bool:
    try:
        video_input = ffmpeg.input(str(silent_video_path))
        original_input = ffmpeg.input(str(original_path))
        stream = ffmpeg.output(
            video_input.video,
            original_input.audio,
            str(output_path),
            vcodec="copy",
            acodec="aac",
            shortest=None,
        )
        ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)
        return True
    except (FileNotFoundError, ffmpeg.Error):
        shutil.copyfile(silent_video_path, output_path)
        return False


def cartoonize_video_file(
    input_path: str | Path,
    output_path: str | Path,
    *,
    edge_threshold: int = 9,
    palette_size: int = 8,
    smoothing_strength: int = 5,
) -> Path:
    source_path = Path(input_path)
    target_path = Path(output_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        silent_output_path = temp_root / f"{source_path.stem}-silent.mp4"

        _write_cartoonized_silent_video(
            source_path,
            silent_output_path,
            edge_threshold=edge_threshold,
            palette_size=palette_size,
            smoothing_strength=smoothing_strength,
        )
        _mux_original_audio(source_path, silent_output_path, target_path)

    return target_path
