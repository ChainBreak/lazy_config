## Usage

Each example below is a self-contained script demonstrating one aspect of `GhostConfig`. The output shown was produced by running the script directly.

### Config file: `training.yaml`

All examples load from this shared config file:

```yaml
experiment_name: cifar10_baseline

model:
  layers:
  - channels: 64
    blocks: 3
  - channels: 128
    blocks: 6
```

---

### Example 01

Standard usage of GhostConfig.

```python
from ghostconfig import GhostConfig

config = GhostConfig.create("training.yaml")

print(f"Experiment name: {config.get('experiment_name', '')}")

# Get a sub-config for the model
model_config = config["model"]

# Iterate over the layers in the model
for block in model_config["layers"]:
    channels = block.get("channels", 128)
    blocks = block.get("blocks", 3)
    print(f"Channels: {channels}, Blocks: {blocks}")

# Check that all required keys are present
config.check()
```

**Output**

```
Experiment name: cifar10_baseline
Channels: 64, Blocks: 3
Channels: 128, Blocks: 6
```

---

### Example 02

No missing errors are raised until check() is called.

```python
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
```

**Output**

```
Block type: conv
Block type: conv
Missing keys:
  - model.layers.0.type
  - model.layers.1.type

Unused keys:
  - experiment_name

Since this started from a yaml (training.yaml), you should add:

model:
  layers:
  - type: conv
  - type: conv
```
