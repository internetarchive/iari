from src.models.api.job.references_job import ReferencesJob
from src.models.api.schema.references_schema import ReferencesSchema
from src.models.exceptions import MissingInformationError
from src.models.file_io.article_file_io import ArticleFileIo
from src.models.file_io.reference_file_io import ReferenceFileIo
from src.views.statistics import StatisticsView


class References(StatisticsView):
    """This returns all references as dehydrated references"""

    def __setup_io__(self):
        pass

    job = ReferencesJob  # type: ignore  # (weird error from mypy)
    schema = ReferencesSchema()

    def get(self):
        self.__validate_and_get_job__()
        # load the article json
        article_file_io = ArticleFileIo(wari_id=self.job.wari_id)
        article_file_io.read_from_disk()
        if not article_file_io.data:
            return "No json in cache", 404
        # console.print(article_file_io.data)
        # references = article_file_io.data["dehydrated_references"]
        references = article_file_io.data["references"]
        # get the references details
        details = []
        if self.job.all:
            for reference in references:
                if "id" not in reference or not reference["id"]:
                    raise MissingInformationError()
                reference_file_io = ReferenceFileIo(hash_based_id=reference["id"])
                reference_file_io.read_from_disk()
                data = reference_file_io.data
                if not data:
                    return "No json in cache", 404
                # convert to dehydrated reference:
                details.append(data)
        else:
            # We use offset and chunk size
            for reference in references[
                self.job.offset : self.job.offset + self.job.chunk_size
            ]:
                if not reference:
                    raise MissingInformationError("reference was empty")
                if not isinstance(reference, dict):
                    raise TypeError(f"has was: {reference}")
                reference_file_io = ReferenceFileIo(hash_based_id=reference["id"])
                reference_file_io.read_from_disk()
                data = reference_file_io.data
                if not data:
                    return "No json in cache", 404
                # convert to dehydrated reference:
                details.append(data)
        data = {"total": len(references), "references": details}
        return data, 200
