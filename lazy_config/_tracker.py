from __future__ import annotations

import pathlib
from typing import Any, Literal


class _AccessTracker:
    """Tracks leaf accesses that could not be satisfied from the backing config data."""

    def __init__(
        self,
        source_format: Literal["yaml", "json", "dict"],
        source_path: pathlib.Path | str | None = None,
    ) -> None:
        self.source_format = source_format
        self.source_path = pathlib.Path(source_path) if source_path is not None else None
        self.missing: dict[str, Any] = {}

    def record_missing(self, dotted_path: str, default: Any) -> None:
        """Record a missing key. First write wins (repeated access keeps first default)."""
        if dotted_path not in self.missing:
            self.missing[dotted_path] = default
