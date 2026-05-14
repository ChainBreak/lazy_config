from __future__ import annotations

import json
import pprint
from typing import Any, Literal

import yaml


def build_nested(missing: dict[str, Any]) -> dict:
    """Explode dotted-path keys back into a nested dict."""
    nested: dict = {}
    for dotted_path, default_value in missing.items():
        parts = dotted_path.split(".")
        node = nested
        for part in parts[:-1]:
            if part not in node or not isinstance(node[part], dict):
                node[part] = {}
            node = node[part]
        node[parts[-1]] = default_value
    return nested


def format_suggestion(
    missing: dict[str, Any],
    source_format: Literal["yaml", "json", "dict"],
) -> str:
    nested = build_nested(missing)
    if source_format == "yaml":
        return yaml.safe_dump(nested, sort_keys=False, default_flow_style=False)
    if source_format == "json":
        return json.dumps(nested, indent=2)
    return pprint.pformat(nested, sort_dicts=False)
