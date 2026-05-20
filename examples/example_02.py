"""No missing errors are raised until check() is called.
"""
from ghostconfig import GhostConfig

config = GhostConfig.create("training.yaml")

# Get a sub-config for the model
model_config = config["model"]

# Iterate over the layers in the model
for block in model_config["layers"]:
    block_type = block.get("type", "conv")
    print(f"Block type: {block_type}")

# Check that all required keys are present
config.check()
