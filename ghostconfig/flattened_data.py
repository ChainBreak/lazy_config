from __future__ import annotations

import inspect
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
    key under ``model`` as used.  ``get_unused_keys()`` is then just a set
    subtraction.
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
        self._missing_keys: dict[str, Any] = {}
        self._missing_key_locations: dict[str, tuple[str, int]] = {}

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

        if value is _NOT_FOUND:
            if dotted_path not in self._missing_keys:
                self._missing_keys[dotted_path] = default
                caller = _find_caller_outside_package()
                if caller is not None:
                    self._missing_key_locations[dotted_path] = caller
            return default

        self._accessed_paths.add(dotted_path)

        if isinstance(value, (dict, list)):
            prefix = dotted_path + "."
            for path in self._all_paths:
                if path.startswith(prefix):
                    self._accessed_paths.add(path)
        return value

    def get_missing_keys(self) -> dict[str, Any]:
        """Return paths that were requested but absent from the input, mapped to their defaults."""
        return self._missing_keys

    def get_missing_key_locations(self) -> dict[str, tuple[str, int]]:
        """Return the call-site (file path, line number) for each path requested but absent."""
        return self._missing_key_locations

    def get_unused_keys(self) -> set[str]:
        """Return leaf (scalar) input paths that were never accessed."""
        leaf_paths = {
            path for path, value in self._all_paths.items()
            if path and not isinstance(value, (dict, list))
        }
        return leaf_paths - self._accessed_paths


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _find_caller_outside_package() -> tuple[str, int] | None:
    """Walk the call stack and return the first (file, line) outside this package.

    This identifies the user's code that triggered a `get()` or `__getitem__`
    call, skipping all internal ghostconfig frames.
    """
    package_directory = str(pathlib.Path(__file__).parent.resolve())
    for frame_info in inspect.stack():
        caller_file = str(pathlib.Path(frame_info.filename).resolve())
        if not caller_file.startswith(package_directory):
            return frame_info.filename, frame_info.lineno
    return None


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
