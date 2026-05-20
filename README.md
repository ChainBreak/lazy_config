# Ghost Config

## Installation

```bash
pip install ghostconfig
```

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
The following parameters were used but missing from the config:
  - model.layers.0.type
  - model.layers.1.type

Since this started from a yaml (training.yaml), you should add:

model:
  layers:
  - type: conv
  - type: conv

The following keys were present in the config but never accessed:
  - experiment_name
```



## Development

### Setup

```bash
pip install -e ".[dev]"
```

Or install with test dependencies:

```bash
pip install pytest
pip install -e .
```

### Running Tests

```bash
pytest
```

To run with verbose output:

```bash
pytest -v
```

### Linting and Type Checking

```bash
ruff check && mypy ghostconfig/ && pytest
```

## Building and Publishing to PyPI

### Prerequisites

```bash
pip install build twine
```

### Build the distribution

```bash
rm dist/*
python -m build
```

This creates a `dist/` directory containing a `.whl` and `.tar.gz` file.

### Upload to PyPI
```bash
twine upload dist/*
```

You will be prompted for your PyPI credentials. It is recommended to use an [API token](https://pypi.org/manage/account/token/) instead of your password.

To avoid entering credentials each time, create a `~/.pypirc` file:

```ini
[pypi]
  username = __token__
  password = pypi-your-api-token-here
```
