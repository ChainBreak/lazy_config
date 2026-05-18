from __future__ import annotations

import pathlib
from collections.abc import Iterator
from typing import Any, Literal, TypeVar, cast

import omegaconf

from . import errors as errors_module
from . import flattened_data as flattened_data_module

_NOT_FOUND = flattened_data_module._NOT_FOUND

T = TypeVar("T")


class GhostConfig:
    def __init__(
        self,
        flattened: flattened_data_module.FlattenedData,
        path_prefix: str = "",
    ) -> None:
        self._flattened = flattened
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
            flattened = flattened_data_module.FlattenedData(data, source_format, source_path=path)
        elif isinstance(source, dict):
            raw = omegaconf.OmegaConf.create(source)
            data = cast(
                "dict[str, Any] | list[Any] | None",
                omegaconf.OmegaConf.to_container(raw, resolve=True),
            )
            flattened = flattened_data_module.FlattenedData(data, "dict")
        else:
            data = None
            flattened = flattened_data_module.FlattenedData(data)

        return cls(flattened)

    def __getitem__(self, key: str | int) -> GhostConfig:
        """Navigate into a sub-config or ghost.

        Always returns a GhostConfig — use get(key, default) to extract scalar
        leaf values.
        """
        full_path = _join_path(self._path_prefix, key)
        return GhostConfig(self._flattened, full_path)

    def get(self, key: str | int, default: T) -> T:
        """Retrieve a value, returning default if the key is absent.

        Records the key as missing when it is absent so that check() can
        surface it.
        """
        full_path = _join_path(self._path_prefix, key)
        return cast(T, self._flattened.retrieve(full_path, default))

    def __iter__(self) -> Iterator[GhostConfig]:
        """Iterate over a list-backed config, wrapping dict elements as GhostConfig.

        Ghost configs (missing key) yield two ghost sub-configs (indices 0 and 1)
        so that field accesses inside the loop record the correct missing paths.
        Dict-backed configs are not iterable and raise TypeError.
        """
        data = self._flattened.retrieve(self._path_prefix, _NOT_FOUND)

        if data is _NOT_FOUND:
            for index in range(2):
                yield GhostConfig(self._flattened, _join_path(self._path_prefix, index))
            return

        if not isinstance(data, list):
            raise TypeError(
                f"Config at '{self._path_prefix}' is not a list and cannot be iterated."
            )

        for index, item in enumerate(data):
            child_path = _join_path(self._path_prefix, index)
            if isinstance(item, (dict, list)):
                yield GhostConfig(self._flattened, child_path)
            else:
                yield item

    def check(self) -> None:
        """Raise MissingConfigError if any accessed keys were absent from the config."""
        if self._flattened.missing:
            raise errors_module.MissingConfigError(self._flattened)


def _join_path(prefix: str, key: str | int) -> str:
    return f"{prefix}.{key}" if prefix else str(key)
