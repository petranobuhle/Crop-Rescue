from dataclasses import dataclass
from io import BytesIO

import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError
from PIL.ImageStat import Stat


MAX_IMAGE_PIXELS = 16_000_000
MIN_IMAGE_SIDE = 224
DARK_IMAGE_THRESHOLD = 45.0
BLUR_VARIANCE_THRESHOLD = 35.0


@dataclass(frozen=True)
class ImageCheckResult:
    image: Image.Image | None
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    @property
    def is_valid(self) -> bool:
        return self.image is not None and not self.errors


def _quality_metrics(image: Image.Image) -> tuple[float, float]:
    width, height = image.size
    scale = min(256 / width, 256 / height, 1.0)
    sample_size = (max(3, int(width * scale)), max(3, int(height * scale)))
    sample = ImageOps.grayscale(
        image.resize(sample_size, Image.Resampling.BILINEAR)
    )
    brightness = float(Stat(sample).mean[0])
    pixels = np.asarray(sample, dtype=np.float32)
    if min(pixels.shape) < 3:
        return brightness, 0.0

    center = pixels[1:-1, 1:-1]
    laplacian = (
        pixels[:-2, 1:-1]
        + pixels[2:, 1:-1]
        + pixels[1:-1, :-2]
        + pixels[1:-1, 2:]
        - 4 * center
    )
    return brightness, float(np.var(laplacian))


def inspect_image(image_bytes: bytes) -> ImageCheckResult:
    if not image_bytes:
        return ImageCheckResult(None, errors=("Choose an image to continue.",))

    try:
        with Image.open(BytesIO(image_bytes)) as opened_image:
            width, height = opened_image.size
            if width <= 0 or height <= 0:
                return ImageCheckResult(
                    None, errors=("The image has invalid dimensions.",)
                )
            if width * height > MAX_IMAGE_PIXELS:
                return ImageCheckResult(
                    None,
                    errors=(
                        "This image is too large to process. Choose a smaller photo.",
                    ),
                )
            opened_image.verify()

        with Image.open(BytesIO(image_bytes)) as opened_image:
            image = ImageOps.exif_transpose(opened_image).convert("RGB")
    except (
        UnidentifiedImageError,
        OSError,
        ValueError,
        Image.DecompressionBombError,
    ):
        return ImageCheckResult(
            None,
            errors=(
                "This photo could not be opened. Choose a valid JPG or PNG image.",
            ),
        )

    warnings: list[str] = []
    if min(image.size) < MIN_IMAGE_SIDE:
        warnings.append(
            "The photo has limited detail. A closer, sharper leaf photo may help."
        )

    brightness, blur_variance = _quality_metrics(image)
    if brightness < DARK_IMAGE_THRESHOLD:
        warnings.append(
            "The photo looks very dark. Try again in natural light and keep the "
            "leaf clear in the frame."
        )

    if blur_variance < BLUR_VARIANCE_THRESHOLD:
        warnings.append(
            "The photo may be blurry. Hold the camera steady and focus on the leaf."
        )

    return ImageCheckResult(image=image, warnings=tuple(warnings))