import logging

from marshmallow import post_load
from marshmallow.fields import Bool, Int, String

from src.models.v2.schema import BaseSchemaV2

from src.models.v2.job.probe_job_v2 import ProbeJobV2

logger = logging.getLogger(__name__)


class ProbeSchemaV2(BaseSchemaV2):
    """
    Schema for probe endpoint
    """

    url = String(required=True)
    probe = String(required=False)  # NB must have probe or probes defined
    probes = String(required=False)
    timeout = Int(required=False)

    # noinspection PyUnusedLocal
    @post_load
    # **kwargs is needed here despite what the validator claims
    def post_load_for_probe(self, data, **kwargs) -> ProbeJobV2:  # type: ignore # dead: disable
        """Return job object as schema return value"""

        job = ProbeJobV2(**data)
        job.validate_fields()

        return job
