from __future__ import annotations

from . import flattened_data as flattened_data_module
from . import suggestions as suggestions_module


class ConfigMismatchError(ValueError):
    """Raised by `GhostConfig.check()` when keys were missing from or unused in the config."""

    def __init__(self, flattened: flattened_data_module.FlattenedData) -> None:
        parts: list[str] = []

        missing = flattened.get_missing_keys()
        if missing:
            suggestion = suggestions_module.format_suggestion(missing, flattened.source_format)
            source_description = _describe_source(flattened)
            missing_paths = "\n".join(f"  - {path}" for path in missing)
            parts.append(
                f"The following parameters were used but missing from the config:\n"
                f"{missing_paths}\n\n"
                f"Since this started from {source_description}, you should add:\n\n"
                f"{suggestion}"
            )

        unused = flattened.get_unused_keys()
        if unused:
            unused_paths = "\n".join(f"  - {path}" for path in sorted(unused))
            parts.append(
                f"The following keys were present in the config but never accessed:\n"
                f"{unused_paths}"
            )

        super().__init__("\n".join(parts))


def _describe_source(flattened: flattened_data_module.FlattenedData) -> str:
    if flattened.source_path is not None:
        return f"a {flattened.source_format} ({flattened.source_path})"
    return f"a {flattened.source_format}"
