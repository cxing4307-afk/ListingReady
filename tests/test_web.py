from io import BytesIO
from zipfile import ZipFile

import pytest
from PIL import Image

from listingready import create_app


def upload_image(size=(640, 320), color=(36, 100, 210), fmt="JPEG") -> BytesIO:
    stream = BytesIO()
    Image.new("RGB", size, color).save(stream, format=fmt)
    stream.seek(0)
    return stream


@pytest.fixture()
def client():
    app = create_app({"TESTING": True})
    return app.test_client()


def test_home_page_explains_the_local_workflow(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"ListingReady" in response.data
    assert b"Choose photos" in response.data


def test_one_photo_downloads_as_a_named_jpeg(client):
    response = client.post(
        "/export",
        data={
            "prefix": "oakshop",
            "canvas": "white",
            "images": (upload_image(), "phone-photo.jpg"),
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    assert response.headers["Content-Disposition"].endswith(
        'filename=oakshop-listing-ready.zip'
    )
    with ZipFile(BytesIO(response.data)) as archive:
        assert archive.namelist() == ["oakshop-001.jpg"]
        with Image.open(BytesIO(archive.read("oakshop-001.jpg"))) as result:
            assert result.size == (1600, 1600)
            assert result.mode == "RGB"


def test_batch_keeps_selection_order_and_contiguous_names(client):
    response = client.post(
        "/export",
        data={
            "prefix": "二手铺",
            "canvas": "white",
            "images": [
                (upload_image(color=(210, 40, 40)), "red.jpg"),
                (upload_image(color=(40, 80, 210)), "blue.jpg"),
            ],
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    with ZipFile(BytesIO(response.data)) as archive:
        assert archive.namelist() == ["二手铺-001.jpg", "二手铺-002.jpg"]
        with Image.open(BytesIO(archive.read("二手铺-001.jpg"))) as first:
            assert first.getpixel((800, 800))[0] > first.getpixel((800, 800))[2]
        with Image.open(BytesIO(archive.read("二手铺-002.jpg"))) as second:
            assert second.getpixel((800, 800))[2] > second.getpixel((800, 800))[0]


@pytest.mark.parametrize("prefix", ["", "two words", "../shop", "shop.name"])
def test_unsafe_or_empty_prefix_is_rejected(client, prefix):
    response = client.post(
        "/export",
        data={
            "prefix": prefix,
            "canvas": "white",
            "images": (upload_image(), "photo.jpg"),
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert b"letters, numbers, hyphens, and underscores" in response.data


def test_bad_file_is_reported_while_good_files_still_export(client):
    response = client.post(
        "/export",
        data={
            "prefix": "closet",
            "canvas": "gray",
            "images": [
                (upload_image(), "front.jpg"),
                (BytesIO(b"not an image"), "broken.png"),
                (upload_image(color=(70, 160, 90)), "back.png"),
            ],
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    with ZipFile(BytesIO(response.data)) as archive:
        assert archive.namelist() == [
            "closet-001.jpg",
            "closet-002.jpg",
            "_skipped.txt",
        ]
        assert "broken.png: could not read this image" in archive.read(
            "_skipped.txt"
        ).decode()


def test_batch_with_no_usable_images_returns_an_error(client):
    response = client.post(
        "/export",
        data={
            "prefix": "closet",
            "canvas": "white",
            "images": (BytesIO(b"plain text"), "notes.txt"),
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert b"No usable JPG or PNG images" in response.data


def test_file_over_the_configured_limit_is_skipped(client):
    client.application.config["MAX_FILE_BYTES"] = 10
    response = client.post(
        "/export",
        data={
            "prefix": "closet",
            "canvas": "white",
            "images": (BytesIO(b"x" * 11), "large.jpg"),
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert b"No usable JPG or PNG images" in response.data


def test_more_than_one_hundred_files_is_rejected(client):
    response = client.post(
        "/export",
        data={
            "prefix": "closet",
            "canvas": "white",
            "images": [(BytesIO(b"x"), f"{number}.jpg") for number in range(101)],
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert b"100 images" in response.data
