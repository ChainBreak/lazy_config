from __future__ import annotations

from . import flattened_data as flattened_data_module
from . import suggestions as suggestions_module


class MissingConfigError(ValueError):
    """Raised by `GhostConfig.check()` when accessed keys were absent from the config."""

    def __init__(self, flattened: flattened_data_module.FlattenedData) -> None:
        suggestion = suggestions_module.format_suggestion(
            flattened.missing, flattened.source_format
        )
        source_description = _describe_source(flattened)
        missing_paths = "\n".join(f"  - {path}" for path in flattened.missing)
        message = (
            f"The following parameters were used but missing from the config:\n"
            f"{missing_paths}\n\n"
            f"Since this started from {source_description}, you should add:\n\n"
            f"{suggestion}"
        )

        unused = flattened.unused_input_paths
        if unused:
            unused_paths = "\n".join(f"  - {path}" for path in sorted(unused))
            message += (
                f"\nThe following keys were present in the config but never accessed:\n"
                f"{unused_paths}"
            )

        super().__init__(message)


def _describe_source(flattened: flattened_data_module.FlattenedData) -> str:
    if flattened.source_path is not None:
        return f"a {flattened.source_format} ({flattened.source_path})"
    return f"a {flattened.source_format}"
