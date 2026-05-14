from __future__ import annotations

from typing import Any, Literal

from . import _suggestions as suggestions_module
from . import _tracker as tracker_module


class MissingConfigError(ValueError):
    """Raised by `LazyConfig.check()` when accessed keys were absent from the config."""

    def __init__(self, tracker: tracker_module._AccessTracker) -> None:
        suggestion = suggestions_module.format_suggestion(
            tracker.missing, tracker.source_format
        )
        source_description = _describe_source(tracker)
        missing_paths = "\n".join(f"  - {path}" for path in tracker.missing)
        message = (
            f"The following parameters were used but missing from the config:\n"
            f"{missing_paths}\n\n"
            f"Since this started from {source_description}, you should add:\n\n"
            f"{suggestion}"
        )
        super().__init__(message)


def _describe_source(tracker: tracker_module._AccessTracker) -> str:
    if tracker.source_path is not None:
        return f"a {tracker.source_format} ({tracker.source_path})"
    return f"a {tracker.source_format}"
