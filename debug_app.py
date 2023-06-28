#!/usr/bin/env python3
import os

from src import app
from src.models.identifiers_checking.url import TestdeadlinkKeyError

if not os.getenv("TESTDEADLINK_KEY"):
    raise TestdeadlinkKeyError(
        "No testdeadlink key found, please put it in the environment"
    )

app.run(debug=True, host="0.0.0.0")
