import numpy as np


def validate_image(image, expected_width: int, expected_height: int) -> dict:
    if image.size != (expected_width, expected_height):
        raise ValueError(f"unexpected dimensions: {image.size}")
    arr = np.asarray(image.convert("RGB"))
    if not np.isfinite(arr).all():
        raise ValueError("non-finite pixels")
    std = float(arr.std())
    unique_colors = int(np.unique(arr.reshape(-1, 3), axis=0).shape[0])
    if std <= 1.0 or unique_colors <= 1000:
        raise ValueError("degenerate image")
    return {
        "width": expected_width,
        "height": expected_height,
        "min": int(arr.min()),
        "max": int(arr.max()),
        "mean": float(arr.mean()),
        "std": std,
        "unique_colors": unique_colors,
    }
