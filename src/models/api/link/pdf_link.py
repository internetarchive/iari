from pydantic import BaseModel


class PdfLink(BaseModel):
    """This model a link that is returned to the patron from the pdf-endpoint"""

    url: str
    page: int
