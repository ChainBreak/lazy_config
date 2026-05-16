from __future__ import annotations

import pathlib
from collections.abc import Iterator
from typing import Any, Literal, TypeVar, cast

import omegaconf

from . import errors as errors_module
from . import tracker as tracker_module

_NOT_FOUND = object()

T = TypeVar("T")


class GhostConfig:
    def __init__(
        self,
        data: dict[str, Any] | list[Any] | None,
        tracker: tracker_module.AccessTracker,
        path_prefix: str = "",
    ) -> None:
        self._data = data
        self._tracker = tracker
        self._path_prefix = path_prefix

    @classmethod
    def create(
        cls,
        source: str | pathlib.Path | dict[str, Any] | None = None,
    ) -> GhostConfig:
        """Create a GhostConfig from a file path, dict, or nothing.

        - str / Path  → load YAML or JSON from disk
        - dict        → wrap the dict directly
        - None        → empty ghost config (all keys missing)
        """
        if isinstance(source, (str, pathlib.Path)):
            path = pathlib.Path(source)
            raw = omegaconf.OmegaConf.load(path)
            source_format: Literal["yaml", "json"] = "json" if path.suffix == ".json" else "yaml"
            data: dict[str, Any] | list[Any] | None = cast(
                "dict[str, Any] | list[Any] | None",
                omegaconf.OmegaConf.to_container(raw, resolve=True),
            )
            tracker = tracker_module.AccessTracker(source_format, source_path=path)
        elif isinstance(source, dict):
            raw = omegaconf.OmegaConf.create(source)
            data = cast(
                "dict[str, Any] | list[Any] | None",
                omegaconf.OmegaConf.to_container(raw, resolve=True),
            )
            tracker = tracker_module.AccessTracker("dict")
        else:
            data = None
            tracker = tracker_module.AccessTracker()
        return cls(data, tracker)

    def __getitem__(self, key: str | int) -> GhostConfig:
        """Navigate into a sub-config or ghost.

        Always returns a GhostConfig — use get(key, default) to extract scalar
        leaf values.

        Raises TypeError if the key resolves to a scalar leaf.
        """
        full_path = _join_path(self._path_prefix, key)
        value = self._lookup(key)
        if isinstance(value, (dict, list)):
            return GhostConfig(value, self._tracker, full_path)
        else:
            return GhostConfig(None, self._tracker, full_path)


    def get(self, key: str | int, default: T) -> T:
        """Retrieve a scalar leaf value, returning default if the key is absent.

        Records the key as missing when it is absent so that check() can surface
        it. Raises TypeError if the key resolves to a dict sub-config — use
        config[key] to navigate into sub-configs.
        """
        full_path = _join_path(self._path_prefix, key)
        value = self._lookup(key)

        if value is _NOT_FOUND:
            self._tracker.record_missing(full_path, default)
            return default

        return value

    def __iter__(self) -> Iterator[GhostConfig]:
        """Iterate over a list-backed config, wrapping dict elements as GhostConfig.

        Ghost configs (missing key) yield two ghost sub-configs (indices 0 and 1)
        so that field accesses inside the loop record the correct missing paths.
        Dict-backed configs are not iterable and raise TypeError.
        """
        if self._data is None:
            for index in range(2):
                yield GhostConfig(None, self._tracker, _join_path(self._path_prefix, index))
            return
        if not isinstance(self._data, list):
            raise TypeError(
                f"Config at '{self._path_prefix}' is not a list and cannot be iterated."
            )
        for index, item in enumerate(self._data):
            child_path = _join_path(self._path_prefix, index)
            if isinstance(item, (dict, list)):
                yield GhostConfig(item, self._tracker, child_path)
            else:
                yield item

    def check(self) -> None:
        """Raise MissingConfigError if any accessed keys were absent from the config."""
        if self._tracker.missing:
            raise errors_module.MissingConfigError(self._tracker)

    def _lookup(self, key: str | int) -> Any:
        if self._data is None:
            return _NOT_FOUND
        if isinstance(self._data, list):
            if not isinstance(key, int) or key < 0 or key >= len(self._data):
                return _NOT_FOUND
            return self._data[key]
        if not isinstance(key, str):
            return _NOT_FOUND
        return self._data.get(key, _NOT_FOUND)


def _join_path(prefix: str, key: str | int) -> str:
    return f"{prefix}.{key}" if prefix else str(key)
