from io import BytesIO

from PIL import Image

from listingready.images import CANVAS_SIZE, prepare_listing_image


def image_bytes(size=(800, 400), color=(26, 86, 219), fmt="PNG") -> BytesIO:
    stream = BytesIO()
    Image.new("RGB", size, color).save(stream, format=fmt)
    stream.seek(0)
    return stream


def test_wide_image_is_centered_without_cropping():
    result = prepare_listing_image(image_bytes(), "white")

    assert result.mode == "RGB"
    assert result.size == (CANVAS_SIZE, CANVAS_SIZE)
    assert result.getpixel((800, 100)) == (255, 255, 255)
    assert result.getpixel((800, 800)) == (26, 86, 219)
    assert result.getpixel((800, 1500)) == (255, 255, 255)
