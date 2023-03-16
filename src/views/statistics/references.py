from src.models.api.job.references_job import ReferencesJob
from src.models.api.statistics.references.references_schema import ReferencesSchema
from src.models.file_io.article_file_io import ArticleFileIo
from src.models.file_io.reference_file_io import ReferenceFileIo
from src.views.statistics import StatisticsView


class References(StatisticsView):
    """This returns up to 100 dehydrated references"""

    def __setup_io__(self):
        pass

    job = ReferencesJob  # type: ignore  # (weird error from mypy)
    schema = ReferencesSchema()

    def get(self):
        self.__validate_and_get_job__()
        # load the article json
        articlefileio = ArticleFileIo(wari_id=self.job.wari_id)
        articlefileio.read_from_disk()
        if not articlefileio.data:
            return "No json in cache", 404
        references = articlefileio.data["references"]
        total = len(references)
        offset = 0
        if total > 100:
            # get the offset
            offset = self.job.offset
        hashes = references[offset:]
        # ensure we always return a max of 100 references
        hashes = hashes[:100]
        # get the references details
        details = []
        for hash_ in hashes:
            referencefileio = ReferenceFileIo(hash_based_id=hash_)
            referencefileio.read_from_disk()
            data = referencefileio.data
            if not data:
                return "No json in cache", 404
            # convert to dehydrated reference:
            del data["templates"]
            del data["wikitext"]
            details.append(data)
        data = dict(total=total, references=details)
        return data, 200
