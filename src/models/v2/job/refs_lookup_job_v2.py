from src import MissingInformationError
from src.models.v2.job import JobV2
from src.constants.constants import OutputFormats


class RefsLookupJobV2(JobV2):
    """job that supports ExtractRefsV2 endpoint"""

    # using marshmallow to describe parameters

    url: str = ""
    raw: bool = False
    output: str = OutputFormats['JSON']['key']
    # output: str = OutputFormat.JSON.value  # maybe ONKLY use JSON cause this is a provide and DB is the source?

    def validate_fields(self):
        """
        parameter checking here...

        Cannot have TSV output format if "raw" references is specified

        we can modify job field values before returning if we want

        """

        from src import app

        app.logger.debug(f"==> RefsLookupJobV2::validate_fields: self.output before is: {self.output}")
        original_output = self.output
        self.output = self.output.upper()
        app.logger.debug(f"==> RefsLookupJobV2::validate_fields: self.output after is: {self.output}")

        # ensure output format is valid
        if OutputFormats.get(self.output) is None:
            raise MissingInformationError(
                f"Invalid output format: {original_output}"
            )

        # special raw / TSV relation
        if self.raw:
            if self.output == OutputFormats['TSV']['key']:
                raise MissingInformationError(
                    f"Cannot use {OutputFormats['TSV']['value']} output format with 'raw' reference format"
                )
