from typing import BinaryIO

from PIL import Image, ImageOps


CANVAS_SIZE = 1600
CANVAS_COLORS = {
    "white": (255, 255, 255),
    "gray": (243, 244, 246),
}


def prepare_listing_image(source: BinaryIO, canvas: str = "white") -> Image.Image:
    background = CANVAS_COLORS[canvas]

    with Image.open(source) as opened:
        oriented = ImageOps.exif_transpose(opened)
        scale = min(CANVAS_SIZE / oriented.width, CANVAS_SIZE / oriented.height)
        fitted_size = (
            max(1, round(oriented.width * scale)),
            max(1, round(oriented.height * scale)),
        )
        fitted = oriented.convert("RGB").resize(fitted_size, Image.Resampling.LANCZOS)

    output = Image.new("RGB", (CANVAS_SIZE, CANVAS_SIZE), background)
    position = (
        (CANVAS_SIZE - fitted.width) // 2,
        (CANVAS_SIZE - fitted.height) // 2,
    )
    output.paste(fitted, position)
    return output

