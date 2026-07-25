from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np


def _validate_image(image_bgr: np.ndarray) -> None:
    if image_bgr.ndim != 3 or image_bgr.shape[2] != 3:
        raise ValueError("Expected a BGR image with shape (height, width, 3).")
    if image_bgr.size == 0:
        raise ValueError("Image input cannot be empty.")


def build_edge_mask(
    image_bgr: np.ndarray,
    *,
    blur_kernel_size: int = 7,
    edge_block_size: int = 9,
    edge_threshold: int = 9,
) -> np.ndarray:
    _validate_image(image_bgr)

    if blur_kernel_size % 2 == 0 or blur_kernel_size < 1:
        raise ValueError("blur_kernel_size must be a positive odd integer.")
    if edge_block_size % 2 == 0 or edge_block_size < 3:
        raise ValueError("edge_block_size must be an odd integer greater than or equal to 3.")

    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    blurred = cv2.medianBlur(gray, blur_kernel_size)
    return cv2.adaptiveThreshold(
        blurred,
        255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY,
        edge_block_size,
        edge_threshold,
    )


def smooth_colors(
    image_bgr: np.ndarray,
    *,
    smoothing_strength: int = 5,
    diameter: int = 9,
    sigma_color: int = 75,
    sigma_space: int = 75,
) -> np.ndarray:
    _validate_image(image_bgr)

    if smoothing_strength < 1:
        raise ValueError("smoothing_strength must be at least 1.")

    smoothed = image_bgr.copy()
    for _ in range(smoothing_strength):
        smoothed = cv2.bilateralFilter(smoothed, diameter, sigma_color, sigma_space)
    return smoothed


def quantize_colors(
    image_bgr: np.ndarray,
    *,
    palette_size: int = 8,
    attempts: int = 3,
    seed: int = 42,
) -> np.ndarray:
    _validate_image(image_bgr)

    if palette_size < 2:
        raise ValueError("palette_size must be at least 2.")

    pixel_data = image_bgr.reshape((-1, 3)).astype(np.float32)
    criteria = (
        cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
        20,
        1.0,
    )
    cv2.setRNGSeed(seed)
    _, labels, centers = cv2.kmeans(
        pixel_data,
        palette_size,
        None,
        criteria,
        attempts,
        cv2.KMEANS_PP_CENTERS,
    )
    quantized_centers = np.uint8(centers)
    quantized = quantized_centers[labels.flatten()]
    return quantized.reshape(image_bgr.shape)


def cartoonize_image(
    image_bgr: np.ndarray,
    *,
    edge_threshold: int = 9,
    palette_size: int = 8,
    smoothing_strength: int = 5,
    blur_kernel_size: int = 7,
    edge_block_size: int = 9,
) -> np.ndarray:
    _validate_image(image_bgr)

    edge_mask = build_edge_mask(
        image_bgr,
        blur_kernel_size=blur_kernel_size,
        edge_block_size=edge_block_size,
        edge_threshold=edge_threshold,
    )
    smoothed = smooth_colors(image_bgr, smoothing_strength=smoothing_strength)
    quantized = quantize_colors(smoothed, palette_size=palette_size)
    return cv2.bitwise_and(quantized, quantized, mask=edge_mask)


def cartoonize_image_file(
    input_path: str | Path,
    output_path: str | Path,
    *,
    edge_threshold: int = 9,
    palette_size: int = 8,
    smoothing_strength: int = 5,
    blur_kernel_size: int = 7,
    edge_block_size: int = 9,
) -> Path:
    source_path = Path(input_path)
    target_path = Path(output_path)

    image_bgr = cv2.imread(str(source_path))
    if image_bgr is None:
        raise ValueError(f"Unable to read image file: {source_path}")

    cartoon = cartoonize_image(
        image_bgr,
        edge_threshold=edge_threshold,
        palette_size=palette_size,
        smoothing_strength=smoothing_strength,
        blur_kernel_size=blur_kernel_size,
        edge_block_size=edge_block_size,
    )

    target_path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(target_path), cartoon):
        raise ValueError(f"Unable to write cartoonized image to: {target_path}")
    return target_path
