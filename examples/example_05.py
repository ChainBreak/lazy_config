"""Example 05: Loading config from a JSON file and iterating over a list.

Pass any .json path directly to GhostConfig(). When a key holds a list of
dicts, iterating the returned GhostConfig wraps each dict element as its own
GhostConfig so you can call get() on each item.
"""
import pathlib

import ghostconfig

json_path = pathlib.Path(__file__).parent / "configs" / "augmentations.json"
config = ghostconfig.GhostConfig(json_path)

pipeline_config = config.get("pipeline")

print("Augmentation pipeline:")
for step_config in pipeline_config:
    name = step_config.get("name", "unknown")
    print(f"  - {name}")

config.check()
print()
print("check() passed — all keys present in the JSON.")
