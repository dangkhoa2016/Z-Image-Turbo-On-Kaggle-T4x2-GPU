import numpy as np
from PIL import Image
import pytest
from zimage_server.validation import validate_image


def test_validator_accepts_non_degenerate_rgb_image():
    yy, xx = np.indices((512, 512), dtype=np.uint32)
    arr = np.stack((xx % 256, yy % 256, (xx * 17 + yy * 31) % 256), axis=-1).astype(np.uint8)
    image = Image.fromarray(arr, "RGB")
    stats = validate_image(image, 512, 512)
    assert stats["width"] == 512
    assert stats["height"] == 512
    assert stats["std"] > 1
    assert stats["unique_colors"] > 1000


def test_validator_rejects_black_image():
    image = Image.new("RGB", (512, 512), (0, 0, 0))
    with pytest.raises(ValueError, match="degenerate"):
        validate_image(image, 512, 512)


def test_validator_rejects_wrong_dimensions():
    image = Image.new("RGB", (256, 256), (1, 2, 3))
    with pytest.raises(ValueError, match="dimensions"):
        validate_image(image, 512, 512)
