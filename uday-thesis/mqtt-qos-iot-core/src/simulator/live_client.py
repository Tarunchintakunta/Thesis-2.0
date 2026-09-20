"""Live AWS IoT Core publisher — present as a stub, blocked this pass."""
from __future__ import annotations


class LiveAwsBlocked(RuntimeError):
    pass


def connect_and_publish(*_args, **_kwargs):  # noqa: ANN001
    raise LiveAwsBlocked(
        "Live AWS IoT Core publishing is not part of this pass. "
        "Use backend=mock (scripts/dry_run.py). Do not set IOT_ENDPOINT."
    )
