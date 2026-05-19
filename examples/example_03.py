"""Example 03: Missing keys return defaults; check() surfaces them all at once.

When a key is absent from the config, get(key, default) silently returns the
default and records the miss. Calling check() at the end raises a
MissingConfigError that lists every missing path and shows exactly what to add.
"""
from ghostconfig import GhostConfig

config = GhostConfig.create("training.yaml")

# This key exists in the YAML
batch_size = config["training"].get("batch_size", 32)

# These keys are absent from the YAML — defaults are returned silently
model_config = config["model"]
dropout = model_config.get("dropout", 0.0)

warmup_steps = config["training"].get("warmup_steps", 0)
seed = config.get("seed", 42)

print(f"batch_size   : {batch_size}  (present in config)")
print(f"dropout      : {dropout}  (missing — default used)")
print(f"warmup_steps : {warmup_steps}  (missing — default used)")
print(f"seed         : {seed}  (missing — default used)")
print()

config.check()
