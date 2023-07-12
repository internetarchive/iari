import hashlib
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, Optional

from src.models.api.handlers.pdf import PdfHandler
from src.models.api.job.check_url_job import UrlJob
from src.models.api.schema.check_url_schema import UrlSchema
from src.models.exceptions import MissingInformationError
from src.models.file_io.pdf_file_io import PdfFileIo
from src.views.statistics.write_view import StatisticsWriteView


class Pdf(StatisticsWriteView):
    """
    This models all action based on requests from the frontend/patron
    It is instantiated at every request

    This view does not contain any of the checking logic.
    See src/models/checking
    """

    job: Optional[UrlJob] = None
    schema: UrlSchema = UrlSchema()
    serving_from_json: bool = False
    headers: Dict[str, Any] = {
        "Access-Control-Allow-Origin": "*",
    }
    data: Dict[str, Any] = {}

    @property
    def __url_hash_id__(self) -> str:
        """This generates an 8-char long id based on the md5 hash of
        the raw upper cased URL supplied by the user"""
        if not self.job:
            raise MissingInformationError()
        return hashlib.md5(f"{self.job.unquoted_url.upper()}".encode()).hexdigest()[:8]

    def get(self):
        """This is the main method and the entrypoint for flask
        Every branch in this method has to return a tuple (Any,response_code)"""
        from src import app

        app.logger.debug("get: running")
        self.__validate_and_get_job__()
        if self.job:
            return self.__return_from_cache_or_analyze_and_return__()

    def __setup_io__(self):
        self.io = PdfFileIo(hash_based_id=self.__url_hash_id__)

    def __handle_debug_job__(self, data):
        if not self.job.html:
            del data["debug_html"]
        if not self.job.xml:
            del data["debug_xml"]
        if not self.job.json_:
            del data["debug_json"]
        if not self.job.blocks:
            del data["debug_blocks"]
        return data, 200

    def __return_from_cache_or_analyze_and_return__(self):
        from src import app

        app.logger.debug("__handle_valid_job__; running")

        self.__setup_and_read_from_cache__()
        if self.io.data and not self.job.refresh:
            return self.io.data, 200
        else:
            url_string = self.job.unquoted_url
            app.logger.info(f"Got {url_string}")
            pdf = PdfHandler(job=self.job)
            pdf.download_and_extract()
            if pdf.error:
                if not isinstance(pdf.error_details, tuple):
                    raise TypeError()
                return pdf.error_details[1], pdf.error_details[0]
            data = pdf.get_dict()
            timestamp = datetime.timestamp(datetime.utcnow())
            data["timestamp"] = int(timestamp)
            isodate = datetime.isoformat(datetime.utcnow())
            data["isodate"] = str(isodate)
            url_hash_id = self.__url_hash_id__
            data["id"] = url_hash_id
            # Remove debug information
            data_without_debug_information = deepcopy(data)
            del data_without_debug_information["debug_url_annotations"]
            del data_without_debug_information["debug_text_original"]
            del data_without_debug_information["debug_text_without_linebreaks"]
            del data_without_debug_information["debug_text_without_spaces"]
            del data_without_debug_information["debug_html"]
            del data_without_debug_information["debug_xml"]
            del data_without_debug_information["debug_json"]
            del data_without_debug_information["debug_blocks"]
            # console.print(data)
            # sys.exit()
            # We don't write during tests because it breaks the CI
            if not self.job.testing:
                write = PdfFileIo(
                    data=data_without_debug_information, hash_based_id=url_hash_id
                )
                write.write_to_disk()
            if self.job.refresh:
                self.__print_log_message_about_refresh__()
                data["refreshed_now"] = True
            else:
                data["refreshed_now"] = False
            if self.job.debug:
                return self.__handle_debug_job__(data=data)
            else:
                return data_without_debug_information, 200
