# lazy_config

A config system that is lazily validated as parameters are used.

## Installation

```bash
pip install lazy_config
```

## Usage

### Creating a config

```python
from lazy_config import LazyConfig

# From a YAML file (OmegaConf interpolations supported)
config = LazyConfig.from_yaml("path/to/config.yaml")

# From a JSON file
config = LazyConfig.from_json("path/to/config.json")

# From a plain Python dict
config = LazyConfig.from_dict({"num_epochs": 10, "learning_rate": 0.001})
```

### Reading values

`get(key)` with no default returns a `LazyConfig` sub-config (real or ghost).
`get(key, default)` returns the leaf value (type inferred from the default).

```python
# Given config.yaml:
# model:
#   layers: 4
#   block: resnet
# dataset:
#   path: my/data/
#   augmentations: [crop]

model_config = config.get("model")    # LazyConfig
layers = model_config.get("layers", 1)  # 4

# Accessing a key that doesn't exist in the YAML is fine at this point —
# a "ghost" LazyConfig is returned and the access is recorded.
training_config = config.get("training")
learning_rate = training_config.get("learning_rate", 0.001)  # returns 0.001
```

### Validating at setup time

Call `check()` once all parameters have been read. It raises `MissingConfigError`
with a suggestion showing exactly what to add to your config file.

```python
config.check()
# MissingConfigError:
# The following parameters were used but missing from the config.
# Since this started from a yaml (path/to/config.yaml), you should add:
#
# training:
#   learning_rate: 0.001
```

If multiple keys are missing they are merged into a single suggestion block.
The format matches the source: YAML for `from_yaml`, JSON for `from_json`,
and a Python dict literal for `from_dict`.

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

## Building and Publishing to PyPI

### Prerequisites

```bash
pip install build twine
```

### Build the distribution

```bash
python -m build
```

This creates a `dist/` directory containing a `.whl` and `.tar.gz` file.

### Upload to PyPI

First, upload to [TestPyPI](https://test.pypi.org/) to verify everything looks correct:

```bash
twine upload --repository testpypi dist/*
```

When ready, upload to the real PyPI:

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
