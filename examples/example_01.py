"""Example 01: Loading a config from a YAML file.
"""
from ghostconfig import GhostConfig

config = GhostConfig.create("training.yaml")

for block in config["model"]["layers"]:
    channels = block.get('channels', 128)
    blocks = block.get('blocks', 3)
    print(f"Channels: {channels}, Blocks: {blocks}")
  
config.check()