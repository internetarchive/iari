import logging

from marshmallow import fields

from src.models.api.enums import Subset
from src.models.api.get_statistics.get_statistics_schema import GetStatisticsSchema

logger = logging.getLogger(__name__)


class GetUrlsSchema(GetStatisticsSchema):
    subset = fields.Enum(enum=Subset, required=False)
