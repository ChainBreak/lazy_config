"""Standard usage of GhostConfig.
"""
from ghostconfig import GhostConfig

config = GhostConfig.create("training.yaml")

# Get a sub-config for the model
model_config = config["model"]

# Iterate over the layers in the model
for block in model_config["layers"]:
    channels = block.get("channels", 128)
    blocks = block.get("blocks", 3)
    print(f"Channels: {channels}, Blocks: {blocks}")

# Check that all required keys are present
config.check()
