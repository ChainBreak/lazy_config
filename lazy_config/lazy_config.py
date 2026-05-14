from __future__ import annotations

import pathlib
from collections.abc import Iterator
from typing import Any, TypeVar, overload

import omegaconf

from . import _errors as errors_module
from . import _tracker as tracker_module

_MISSING = object()
_NOT_FOUND = object()

T = TypeVar("T")


class LazyConfig:
    """A config system that is lazily validated as parameters are used.

    Build a LazyConfig from a YAML file, JSON file, or plain dict, then access
    parameters with `get()`. Call `check()` at the end of setup to surface any
    keys that were accessed but absent from the backing config.

    get(key) with no default:
        - dict value  → LazyConfig (sub-config)
        - list value  → LazyConfig (iterable; each dict element is a LazyConfig)
        - scalar leaf → the scalar value directly
        - missing key → ghost LazyConfig (records missing on subsequent leaf access)

    get(key, default) with a default:
        - dict value  → TypeError (use get(key) to navigate into sub-configs)
        - list value  → plain list
        - scalar leaf → the scalar value
        - missing key → records missing, returns default
    """

    def __init__(
        self,
        data: dict | list | None,
        tracker: tracker_module._AccessTracker,
        path_prefix: str = "",
    ) -> None:
        self._data = data
        self._tracker = tracker
        self._path_prefix = path_prefix

    @classmethod
    def from_yaml(cls, path: str | pathlib.Path) -> LazyConfig:
        raw = omegaconf.OmegaConf.load(path)
        data = omegaconf.OmegaConf.to_container(raw, resolve=True)
        tracker = tracker_module._AccessTracker("yaml", source_path=path)
        return cls(data, tracker)

    @classmethod
    def from_json(cls, path: str | pathlib.Path) -> LazyConfig:
        raw = omegaconf.OmegaConf.load(path)
        data = omegaconf.OmegaConf.to_container(raw, resolve=True)
        tracker = tracker_module._AccessTracker("json", source_path=path)
        return cls(data, tracker)

    @classmethod
    def from_dict(cls, data: dict) -> LazyConfig:
        raw = omegaconf.OmegaConf.create(data)
        data = omegaconf.OmegaConf.to_container(raw, resolve=True)
        tracker = tracker_module._AccessTracker("dict")
        return cls(data, tracker)

    @overload
    def get(self, key: str | int) -> LazyConfig: ...

    @overload
    def get(self, key: str | int, default: T) -> T: ...

    def get(self, key: str | int, default: Any = _MISSING) -> Any:
        full_path = _join_path(self._path_prefix, key)
        value = self._lookup(key)

        if default is _MISSING:
            if isinstance(value, (dict, list)):
                return LazyConfig(value, self._tracker, full_path)
            if value is _NOT_FOUND:
                return LazyConfig(None, self._tracker, full_path)
            return value

        if value is _NOT_FOUND:
            self._tracker.record_missing(full_path, default)
            return default

        if isinstance(value, dict):
            raise TypeError(
                f"'{full_path}' is a sub-config, not a leaf value. "
                f"Call get('{key}') without a default to get a LazyConfig."
            )

        return value

    def __iter__(self) -> Iterator[Any]:
        """Iterate over a list-backed config, wrapping dict elements as LazyConfig.

        Ghost configs (missing key) yield two ghost sub-configs (indices 0 and 1)
        so that field accesses inside the loop record the correct missing paths.
        Dict-backed configs are not iterable and raise TypeError.
        """
        if self._data is None:
            for index in range(2):
                yield LazyConfig(None, self._tracker, _join_path(self._path_prefix, index))
            return
        if not isinstance(self._data, list):
            raise TypeError(
                f"Config at '{self._path_prefix}' is not a list and cannot be iterated."
            )
        for index, item in enumerate(self._data):
            child_path = _join_path(self._path_prefix, index)
            if isinstance(item, (dict, list)):
                yield LazyConfig(item, self._tracker, child_path)
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
        return self._data.get(key, _NOT_FOUND)


def _join_path(prefix: str, key: str | int) -> str:
    return f"{prefix}.{key}" if prefix else str(key)
