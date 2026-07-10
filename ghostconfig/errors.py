from __future__ import annotations

from . import flattened_data as flattened_data_module
from . import suggestions as suggestions_module


class ConfigMismatchError(ValueError):
    """Raised by `GhostConfig.check()` when keys were missing from or unused in the config."""

    def __init__(
        self,
        flattened: flattened_data_module.FlattenedData,
        path_prefix: str = "",
    ) -> None:
        parts: list[str] = []

        missing = flattened.get_missing_keys(path_prefix)
        if missing:
            locations = flattened.get_missing_key_locations(path_prefix)
            missing_lines = []
            for path in missing:
                location = locations.get(path)
                if location is not None:
                    file_path, line_number = location
                    missing_lines.append(f"  - {path}  (called at {file_path}:{line_number})")
                else:
                    missing_lines.append(f"  - {path}")
            missing_paths = "\n".join(missing_lines)
            parts.append(f"Missing keys:\n{missing_paths}")

        unused = flattened.get_unused_keys(path_prefix)
        if unused:
            unused_paths = "\n".join(f"  - {path}" for path in sorted(unused))
            parts.append(
                f"Unused keys:\n"
                f"{unused_paths}"
            )

        if missing:
            suggestion = suggestions_module.format_suggestion(missing, flattened.source_format)
            source_description = _describe_source(flattened)
            parts.append(
                f"Since this started from {source_description}, you should add:\n\n"
                f"{suggestion}"
            )

        super().__init__("\n\n".join(parts))


def _describe_source(flattened: flattened_data_module.FlattenedData) -> str:
    if flattened.source_path is not None:
        return f"a {flattened.source_format} ({flattened.source_path})"
    return f"a {flattened.source_format}"
