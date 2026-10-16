from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

from flask import Flask, abort, render_template, request, send_file

from .images import prepare_listing_image


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
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
        uploads = request.files.getlist("images")

        package = BytesIO()
        with ZipFile(package, "w", ZIP_DEFLATED) as archive:
            for number, upload in enumerate(uploads, start=1):
                prepared = prepare_listing_image(upload.stream, canvas)
                output = BytesIO()
                prepared.save(output, format="JPEG", quality=92, optimize=True)
                archive.writestr(f"{prefix}-{number:03d}.jpg", output.getvalue())
        package.seek(0)

        return send_file(
            package,
            mimetype="application/zip",
            as_attachment=True,
            download_name=f"{prefix}-listing-ready.zip",
        )

    return app
