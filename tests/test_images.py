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


def test_exif_orientation_is_applied_before_fitting():
    source = Image.new("RGB", (60, 30), (220, 40, 40))
    source.paste((40, 80, 220), (30, 0, 60, 30))
    exif = Image.Exif()
    exif[274] = 6
    stream = BytesIO()
    source.save(stream, format="JPEG", quality=100, exif=exif)
    stream.seek(0)

    result = prepare_listing_image(stream, "white")

    assert result.getpixel((800, 100))[0] > 180
    assert result.getpixel((800, 1500))[2] > 180
    assert result.getpixel((100, 800)) == (255, 255, 255)


def test_transparent_png_uses_the_selected_canvas_color():
    source = BytesIO()
    image = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    image.paste((190, 35, 55, 255), (25, 25, 75, 75))
    image.save(source, format="PNG")
    source.seek(0)

    result = prepare_listing_image(source, "gray")

    assert result.getpixel((10, 10)) == (243, 244, 246)
    assert result.getpixel((800, 800)) == (190, 35, 55)
