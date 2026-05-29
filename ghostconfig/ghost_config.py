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
    """A lazy config wrapper that defers all key lookups and tracks missing keys.

    Create an instance with `GhostConfig.create()`, navigate into nested values
    with `[]` or retrieve scalars with `.get()`, then call `.check()` once at
    the end to raise a single `ConfigMismatchError` if any keys were absent from
    or unused in the underlying config.
    """

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
        source: str | pathlib.Path | dict[str, Any] | GhostConfig | None = None,
    ) -> GhostConfig:
        """Create a GhostConfig from a file path, dict, or nothing.

        - GhostConfig → returned as-is
        - str / Path  → load YAML or JSON from disk
        - dict        → wrap the dict directly
        - None        → empty ghost config (all keys missing)
        """
        if isinstance(source, GhostConfig):
            return source
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
        """Iterate over indexed children, yielding a GhostConfig per index.

        When the underlying value is a list, iteration matches the list length.
        When the path is absent or non-list (ghost mode), two iterations are
        yielded so that common two-value tuple unpacking works without raising
        an error even when the key is missing from the config.
        """
        data = self._flattened.retrieve(self._path_prefix, _NOT_FOUND)

        if isinstance(data, list):
            num_items = len(data)
        else:
            num_items = 2

        for index in range(num_items):
            child_path = _join_path(self._path_prefix, index)
            yield GhostConfig(self._flattened, child_path)


    def to_dict(self) -> dict[str, Any]:
        """Return the underlying config as a plain dict at the current path prefix."""
        value = self._flattened.retrieve(self._path_prefix, {})
        return cast("dict[str, Any]", value)

    def check(self) -> None:
        """Raise ConfigMismatchError if any keys were missing from or unused in the config."""
        if self._flattened.get_missing_keys() or self._flattened.get_unused_keys():
            raise errors_module.ConfigMismatchError(self._flattened)


def _join_path(prefix: str, key: str | int) -> str:
    return f"{prefix}.{key}" if prefix else str(key)
