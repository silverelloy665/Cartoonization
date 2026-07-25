from pathlib import Path

import cv2
import numpy as np

from app.services.cartoonize.image_pipeline import (
    cartoonize_image,
    cartoonize_image_file,
    quantize_colors,
)


def build_test_image() -> np.ndarray:
    image = np.zeros((64, 64, 3), dtype=np.uint8)
    image[:, :32] = (25, 90, 200)
    image[:, 32:] = (210, 120, 40)
    cv2.rectangle(image, (16, 16), (48, 48), (255, 255, 255), -1)
    return image


def test_quantize_colors_limits_palette_size() -> None:
    image = build_test_image()

    quantized = quantize_colors(image, palette_size=4)

    assert quantized.shape == image.shape
    assert quantized.dtype == np.uint8
    unique_colors = np.unique(quantized.reshape(-1, 3), axis=0)
    assert len(unique_colors) <= 4


def test_cartoonize_image_preserves_shape_and_dtype() -> None:
    image = build_test_image()

    cartoon = cartoonize_image(image, palette_size=4, smoothing_strength=2)

    assert cartoon.shape == image.shape
    assert cartoon.dtype == np.uint8
    assert not np.array_equal(cartoon, image)


def test_cartoonize_image_file_writes_output(tmp_path: Path) -> None:
    source_path = tmp_path / "source.png"
    target_path = tmp_path / "cartoon.png"
    image = build_test_image()
    assert cv2.imwrite(str(source_path), image)

    result_path = cartoonize_image_file(source_path, target_path, palette_size=4, smoothing_strength=2)

    assert result_path == target_path
    assert target_path.exists()
    output = cv2.imread(str(target_path))
    assert output is not None
    assert output.shape == image.shape
