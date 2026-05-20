from __future__ import annotations

import pathlib
from typing import Any, Literal

_NOT_FOUND = object()


class FlattenedData:
    """Stores the input config as a single flat dict of dot-path keys.

    On creation the input data is traversed once and every reachable path is
    stored — both leaf scalars (``"model.layers" → 4``) and intermediate
    containers (``"model" → {"layers": 4}``).  The intermediate entries are
    kept so that navigation via ``GhostConfig.__getitem__`` and iteration via
    ``GhostConfig.__iter__`` can look up list/dict values by path without any
    GhostConfig instance needing to hold its own copy of the data.

    ``_accessed_paths`` collects every path touched by ``retrieve()``.  When an
    intermediate node is accessed, all of its descendants are also marked as
    accessed so that a single ``get("model", {})`` call correctly counts every
    key under ``model`` as used.  The ``unused_input_paths`` property is then
    just a set subtraction.
    """

    def __init__(
        self,
        data: dict[str, Any] | list[Any] | None,
        source_format: Literal["yaml", "json", "dict"] = "dict",
        source_path: pathlib.Path | str | None = None,
    ) -> None:
        self.source_format = source_format
        self.source_path = pathlib.Path(source_path) if source_path is not None else None
        self._all_paths: dict[str, Any] = {}
        self._accessed_paths: set[str] = set()
        self.missing: dict[str, Any] = {}

        if data is not None:
            _flatten_recursive(data, "", self._all_paths)


    def retrieve(self, dotted_path: str, default: Any) -> Any:
        """Return the value at *dotted_path*, recording access or absence.

        On a hit the path — and all of its descendants — are marked as
        accessed (for unused-key reporting).  On a miss the path and its
        default are recorded (for missing-key reporting) and *default* is
        returned.  First write wins — repeated misses on the same path keep
        the first default.
        """
        value = self._all_paths.get(dotted_path, _NOT_FOUND)

        # If the value is not found, record the missing path and return the default
        if value is _NOT_FOUND:
            if dotted_path not in self.missing:
                self.missing[dotted_path] = default
            return default

        self._accessed_paths.add(dotted_path)

        # If the value is a dict or list, mark all of its descendants as accessed
        if isinstance(value, (dict, list)):
            prefix = dotted_path + "."
            for path in self._all_paths:
                if path.startswith(prefix):
                    self._accessed_paths.add(path)
        return value

    @property
    def unused_input_paths(self) -> set[str]:
        """Leaf (scalar) input paths that were never accessed."""
        leaf_paths = {
            path for path, value in self._all_paths.items()
            if path and not isinstance(value, (dict, list))
        }
        return leaf_paths - self._accessed_paths


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _flatten_recursive(
    data: Any,
    prefix: str,
    all_paths: dict[str, Any],
) -> None:
    """Recursively walk *data* and populate *all_paths*.

    Both intermediate container nodes and leaf scalar nodes are stored so the
    rest of the system can look up any path by its dot-notation key.
    """
    if isinstance(data, dict):
        all_paths[prefix] = data
        for key, value in data.items():
            child_path = f"{prefix}.{key}" if prefix else key
            _flatten_recursive(value, child_path, all_paths)
    elif isinstance(data, list):
        all_paths[prefix] = data
        for index, value in enumerate(data):
            child_path = f"{prefix}.{index}" if prefix else str(index)
            _flatten_recursive(value, child_path, all_paths)
    else:
        all_paths[prefix] = data
