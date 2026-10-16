# ListingReady

ListingReady is for small shops and second-hand sellers with a folder of mismatched phone photos.
Drop in JPG or PNG files, pick a canvas, and download a consistently named square-image package.
It runs locally and only rotates, scales, and pads your photos—there is no cropping, background removal, or AI processing.

![A phone photo before processing and the square listing image produced by ListingReady](demo/before-after.jpg)

## Install

You need Python 3.10 or newer.

```bash
git clone <your-copy-of-this-repository>
cd listingready
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

## Use it

Start the local server:

```bash
python run.py
```

Open `http://127.0.0.1:5000`, then:

1. Drop up to 100 JPG or PNG photos into the page.
2. Enter a prefix such as `oakstreet` and choose white or light gray.
3. Click **Build my ZIP**.

The archive contains `oakstreet-001.jpg`, `oakstreet-002.jpg`, and so on. Every output is a 1600 × 1600 JPEG at quality 92. If one file cannot be read, the usable images still export and `_skipped.txt` explains what was left out.

## What it does to a photo

ListingReady applies the source file's EXIF orientation, scales the complete image proportionally, and centers it on the selected square canvas. Transparent PNG pixels are composited onto that canvas. It does not crop, stretch, retouch, remove a background, or call an external service.

## Run the tests

```bash
python -m pip install -e '.[dev]'
pytest
```

## Known issues

- A batch is processed in memory, so 100 large photos can use a noticeable amount of RAM.
- Animated images are not supported as animations; only the first frame is used.
- There is no drag-to-reorder or remove-one-file control after a drop. Reopen the picker to correct the list.
- This is a local development server, not a hardened public upload service.

## Dependency licenses

All direct dependencies use permissive licenses:

| Dependency | Used for | License |
| --- | --- | --- |
| Flask | Local web interface | BSD-3-Clause |
| Pillow | EXIF correction and image rendering | MIT-CMU (HPND-style) |
| pytest | Development tests | MIT |

Flask's installed runtime dependencies are also permissive: Werkzeug, Jinja2, MarkupSafe, ItsDangerous, and Click use BSD-3-Clause; Blinker uses MIT. pytest's test-only dependency set uses MIT, BSD-2-Clause, or the Apache-2.0/BSD-2-Clause dual license.

## License

ListingReady is available under the [MIT License](LICENSE).

