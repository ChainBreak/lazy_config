"""Example 05: Loading config from a JSON file and iterating over a list.

Pass any .json path directly to LazyConfig(). When a key holds a list of
dicts, iterating the returned LazyConfig wraps each dict element as its own
LazyConfig so you can call get() on each item.
"""
import pathlib

import lazy_config

json_path = pathlib.Path(__file__).parent / "configs" / "augmentations.json"
config = lazy_config.LazyConfig(json_path)

pipeline_config = config.get("pipeline")

print("Augmentation pipeline:")
for step_config in pipeline_config:
    name = step_config.get("name", "unknown")
    print(f"  - {name}")

config.check()
print()
print("check() passed — all keys present in the JSON.")
