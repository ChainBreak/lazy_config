from __future__ import annotations

import json
import pprint
from typing import Any, Literal, cast

import yaml


def build_nested(missing: dict[str, Any]) -> Any:
    """Explode dotted-path keys back into a nested dict.

    Path segments that are consecutive integers starting from 0 are converted
    to lists so the YAML/JSON suggestion uses proper list syntax.
    """
    nested: dict[str, Any] = {}
    for dotted_path, default_value in missing.items():
        parts = dotted_path.split(".")
        node = nested
        for part in parts[:-1]:
            if part not in node or not isinstance(node[part], dict):
                node[part] = {}
            node = node[part]
        node[parts[-1]] = default_value
    return _convert_integer_keys_to_lists(nested)


def _convert_integer_keys_to_lists(node: Any) -> Any:
    """Recursively replace dicts whose keys are consecutive ints (0, 1, …) with lists."""
    if not isinstance(node, dict):
        return node
    converted = {key: _convert_integer_keys_to_lists(value) for key, value in node.items()}
    try:
        integer_keys = sorted(int(key) for key in converted)
        if integer_keys == list(range(len(integer_keys))):
            return [converted[str(i)] for i in integer_keys]
    except ValueError:
        pass
    return converted


def format_suggestion(
    missing: dict[str, Any],
    source_format: Literal["yaml", "json", "dict"],
) -> str:
    nested = build_nested(missing)
    if source_format == "yaml":
        return cast(str, yaml.safe_dump(nested, sort_keys=False, default_flow_style=False))
    if source_format == "json":
        return json.dumps(nested, indent=2)
    return pprint.pformat(nested, sort_dicts=False)
