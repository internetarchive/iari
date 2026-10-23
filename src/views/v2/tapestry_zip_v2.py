import io
import re
import traceback
import zipfile

from flask import request, send_file
from flask_restful import Resource  # type: ignore

from iarilib.tapestry_zip import SpecError, build


class TapestryZipV2(Resource):
    """
    Builds a Tapestry-importable .zip from a JSON spec POSTed as the request body.

    The spec format is described in iarilib/build-tapestry-zip.py. Unlike the
    CLI, {"bundle": ...} file references are rejected, since the server has no
    files of the caller's to bundle; all media must be external URLs.
    """

    def post(self):
        from src import app
        app.logger.debug("==> TapestryZipV2::post")

        spec = request.get_json(silent=True)
        if spec is None:
            return {"error": "Request body must be a JSON Tapestry spec"}, 400

        buffer = io.BytesIO()
        try:
            with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                root = build(spec, None, zf)

        except SpecError as e:
            return {"error": f"Spec Error: {str(e)}"}, 400

        except Exception as e:
            traceback.print_exc()
            return {"error": f"General Error: {str(e)}"}, 500

        buffer.seek(0)
        return send_file(
            buffer,
            mimetype="application/zip",
            as_attachment=True,
            download_name=f"{self.__file_stem__(root.get('title'))}.zip",
        )

    @staticmethod
    def __file_stem__(title) -> str:
        stem = re.sub(r"[^A-Za-z0-9._-]+", "_", str(title or "")).strip("._")
        return stem or "tapestry"
