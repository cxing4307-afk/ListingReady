from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from flask import Flask, abort, render_template, request, send_file
from PIL import UnidentifiedImageError

from .images import prepare_listing_image


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(MAX_FILE_BYTES=25 * 1024 * 1024)
    if test_config:
        app.config.update(test_config)

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.post("/export")
    def export():
        prefix = request.form.get("prefix", "").strip()
        if not prefix or not all(char.isalnum() or char in "-_" for char in prefix):
            abort(
                400,
                "Use only letters, numbers, hyphens, and underscores in the prefix.",
            )
        canvas = request.form.get("canvas", "white")
        if canvas not in {"white", "gray"}:
            abort(400, "Choose a valid canvas color.")
        uploads = request.files.getlist("images")
        if len(uploads) > 100:
            abort(400, "Choose no more than 100 images per batch.")

        package = BytesIO()
        skipped = []
        exported = 0
        with ZipFile(package, "w", ZIP_DEFLATED) as archive:
            for upload in uploads:
                filename = upload.filename or "unnamed file"
                if Path(filename).suffix.lower() not in {".jpg", ".jpeg", ".png"}:
                    skipped.append(f"{filename}: only JPG and PNG files are supported")
                    continue

                payload = upload.stream.read(app.config["MAX_FILE_BYTES"] + 1)
                if len(payload) > app.config["MAX_FILE_BYTES"]:
                    skipped.append(f"{filename}: file is larger than 25 MB")
                    continue

                try:
                    prepared = prepare_listing_image(BytesIO(payload), canvas)
                except (UnidentifiedImageError, OSError, ValueError):
                    skipped.append(f"{filename}: could not read this image")
                    continue

                exported += 1
                output = BytesIO()
                prepared.save(output, format="JPEG", quality=92, optimize=True)
                archive.writestr(f"{prefix}-{exported:03d}.jpg", output.getvalue())

            if not exported:
                abort(400, "No usable JPG or PNG images were found.")
            if skipped:
                archive.writestr("_skipped.txt", "\n".join(skipped) + "\n")
        package.seek(0)

        return send_file(
            package,
            mimetype="application/zip",
            as_attachment=True,
            download_name=f"{prefix}-listing-ready.zip",
        )

    return app
