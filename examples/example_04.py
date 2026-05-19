"""Example 04: Iterating over a list of sub-configs.

When a key holds a list of dicts, iterating the returned GhostConfig wraps
each element as its own GhostConfig so you can call get() on each item.
"""
from ghostconfig import GhostConfig

config = GhostConfig.create("training.yaml")

pipeline_config = config["augmentations"]["pipeline"]

print("Augmentation pipeline:")
for step_config in pipeline_config:
    name = step_config.get("name", "unknown")
    print(f"  - {name}")

config.check()
print()
print("check() passed — all keys present in the YAML.")
