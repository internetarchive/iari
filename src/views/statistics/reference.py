from flask_restful import Resource  # type: ignore

from src.models.file_io.reference_file_io import ReferenceFileIo


class Reference(Resource):
    @staticmethod
    def get(reference_id=""):
        if not reference_id:
            return "No reference id given", 400
        else:
            referencefileio = ReferenceFileIo(hash=reference_id)
            referencefileio.read_from_disk()
            data = referencefileio.data
            if not data:
                return "No json in cache", 404
            return data, 200
