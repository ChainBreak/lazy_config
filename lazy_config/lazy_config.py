from __future__ import annotations

import pathlib
from typing import Any, Literal, TypeVar, overload

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
    """

    def __init__(
        self,
        data: omegaconf.DictConfig | None,
        tracker: tracker_module._AccessTracker,
        path_prefix: str = "",
    ) -> None:
        self._data = data
        self._tracker = tracker
        self._path_prefix = path_prefix

    @classmethod
    def from_yaml(cls, path: str | pathlib.Path) -> "LazyConfig":
        data = omegaconf.OmegaConf.load(path)
        tracker = tracker_module._AccessTracker("yaml", source_path=path)
        return cls(data, tracker)

    @classmethod
    def from_json(cls, path: str | pathlib.Path) -> "LazyConfig":
        data = omegaconf.OmegaConf.load(path)
        tracker = tracker_module._AccessTracker("json", source_path=path)
        return cls(data, tracker)

    @classmethod
    def from_dict(cls, data: dict) -> "LazyConfig":
        dict_config = omegaconf.OmegaConf.create(data)
        tracker = tracker_module._AccessTracker("dict")
        return cls(dict_config, tracker)

    @overload
    def get(self, key: str) -> "LazyConfig": ...

    @overload
    def get(self, key: str, default: T) -> T: ...

    def get(self, key: str, default: Any = _MISSING) -> Any:
        full_path = f"{self._path_prefix}.{key}" if self._path_prefix else key
        value = self._lookup(key)

        if default is _MISSING:
            if isinstance(value, omegaconf.DictConfig):
                return LazyConfig(value, self._tracker, full_path)
            return LazyConfig(None, self._tracker, full_path)

        if value is _NOT_FOUND:
            self._tracker.record_missing(full_path, default)
            return default

        if isinstance(value, omegaconf.DictConfig):
            raise TypeError(
                f"'{full_path}' is a sub-config, not a leaf value. "
                f"Call get('{key}') without a default to get a LazyConfig."
            )

        if isinstance(value, omegaconf.ListConfig):
            return omegaconf.OmegaConf.to_object(value)

        return value

    def check(self) -> None:
        """Raise MissingConfigError if any accessed keys were absent from the config."""
        if self._tracker.missing:
            raise errors_module.MissingConfigError(self._tracker)

    def _lookup(self, key: str) -> Any:
        if self._data is None:
            return _NOT_FOUND
        if key not in self._data:
            return _NOT_FOUND
        return self._data[key]
