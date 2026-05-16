"""Example 03: Missing keys return defaults; check() surfaces them all at once.

When a key is absent from the config, get(key, default) silently returns the
default and records the miss. Calling check() at the end of setup raises a
MissingConfigError that lists every missing path and shows exactly what to add.
"""
import ghostconfig

config = ghostconfig.GhostConfig({
    "batch_size": 64,
    # learning_rate and model block are intentionally absent
})

batch_size = config.get("batch_size", 16)

model_config = config.get("model")
architecture = model_config.get("architecture", "resnet18")
number_of_layers = model_config.get("number_of_layers", 18)

learning_rate = config.get("learning_rate", 0.001)

print(f"batch_size    : {batch_size}  (present in config)")
print(f"architecture  : {architecture}  (missing — default used)")
print(f"layers        : {number_of_layers}  (missing — default used)")
print(f"learning_rate : {learning_rate}  (missing — default used)")
print()

try:
    config.check()
except ghostconfig.MissingConfigError as error:
    print("MissingConfigError caught:")
    print(str(error))
