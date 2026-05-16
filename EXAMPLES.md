# GhostConfig Examples

Each example below is a self-contained script demonstrating one aspect of `GhostConfig`. The output shown was produced by running the script directly.

---

## Example 01

Example 01: Creating a config from a plain Python dict.

The simplest way to get started — no files required.

### Code

```python
"""Example 01: Creating a config from a plain Python dict.

The simplest way to get started — no files required.
"""
import ghostconfig

config = ghostconfig.GhostConfig.create({
    "learning_rate": 0.001,
    "batch_size": 32,
    "number_of_epochs": 10,
    "experiment_name": "baseline",
})

learning_rate = config.get("learning_rate", 0.0)
batch_size = config.get("batch_size", 16)
number_of_epochs = config.get("number_of_epochs", 1)
experiment_name = config.get("experiment_name", "untitled")

print(f"experiment : {experiment_name}")
print(f"learning rate : {learning_rate}")
print(f"batch size : {batch_size}")
print(f"epochs : {number_of_epochs}")

config.check()
print("check() passed — no missing keys.")
```

### Output

```
experiment : baseline
learning rate : 0.001
batch size : 32
epochs : 10
check() passed — no missing keys.
```

---

## Example 02

Example 02: Navigating nested sub-configs.

Calling get(key) without a default on a dict value returns a child GhostConfig.
You can chain these calls to reach deeply nested leaves.

### Code

```python
"""Example 02: Navigating nested sub-configs.

Calling get(key) without a default on a dict value returns a child GhostConfig.
You can chain these calls to reach deeply nested leaves.
"""
import ghostconfig

config = ghostconfig.GhostConfig.create({
    "model": {
        "architecture": "resnet50",
        "number_of_layers": 50,
        "dropout": 0.1,
    },
    "optimizer": {
        "name": "adam",
        "learning_rate": 3e-4,
        "weight_decay": 1e-5,
    },
})

model_config = config["model"]
optimizer_config = config["optimizer"]

architecture = model_config.get("architecture", "resnet18")
number_of_layers = model_config.get("number_of_layers", 18)
dropout = model_config.get("dropout", 0.0)

optimizer_name = optimizer_config.get("name", "sgd")
learning_rate = optimizer_config.get("learning_rate", 0.01)
weight_decay = optimizer_config.get("weight_decay", 0.0)

print("Model:")
print(f"  architecture : {architecture}")
print(f"  layers       : {number_of_layers}")
print(f"  dropout      : {dropout}")
print()
print("Optimizer:")
print(f"  name         : {optimizer_name}")
print(f"  learning rate: {learning_rate}")
print(f"  weight decay : {weight_decay}")

config.check()
print()
print("check() passed — no missing keys.")
```

### Output

```
Model:
  architecture : resnet50
  layers       : 50
  dropout      : 0.1

Optimizer:
  name         : adam
  learning rate: 0.0003
  weight decay : 1e-05

check() passed — no missing keys.
```

---

## Example 03

Example 03: Missing keys return defaults; check() surfaces them all at once.

When a key is absent from the config, get(key, default) silently returns the
default and records the miss. Calling check() at the end of setup raises a
MissingConfigError that lists every missing path and shows exactly what to add.

### Code

```python
"""Example 03: Missing keys return defaults; check() surfaces them all at once.

When a key is absent from the config, get(key, default) silently returns the
default and records the miss. Calling check() at the end of setup raises a
MissingConfigError that lists every missing path and shows exactly what to add.
"""
import ghostconfig

config = ghostconfig.GhostConfig.create({
    "batch_size": 64,
    # learning_rate and model block are intentionally absent
})

batch_size = config.get("batch_size", 16)

model_config = config["model"]
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
```

### Output

```
batch_size    : 64  (present in config)
architecture  : resnet18  (missing — default used)
layers        : 18  (missing — default used)
learning_rate : 0.001  (missing — default used)

MissingConfigError caught:
The following parameters were used but missing from the config:
  - model.architecture
  - model.number_of_layers
  - learning_rate

Since this started from a dict, you should add:

{'model': {'architecture': 'resnet18', 'number_of_layers': 18},
 'learning_rate': 0.001}
```

---

## Example 04

Example 04: Loading config from a YAML file.

Pass any .yaml or .yml path directly to GhostConfig(). OmegaConf is used under
the hood, so interpolations and anchors work out of the box.

### Code

```python
"""Example 04: Loading config from a YAML file.

Pass any .yaml or .yml path directly to GhostConfig(). OmegaConf is used under
the hood, so interpolations and anchors work out of the box.
"""
import pathlib

import ghostconfig

yaml_path = pathlib.Path(__file__).parent / "configs" / "training.yaml"
config = ghostconfig.GhostConfig.create(yaml_path)

experiment_name = config.get("experiment_name", "untitled")

model_config = config["model"]
architecture = model_config.get("architecture", "resnet18")
pretrained = model_config.get("pretrained", False)

training_config = config["training"]
number_of_epochs = training_config.get("number_of_epochs", 10)
batch_size = training_config.get("batch_size", 32)
learning_rate = training_config.get("learning_rate", 0.001)

dataset_config = config["dataset"]
dataset_name = dataset_config.get("name", "imagenet")
data_root = dataset_config.get("data_root", "./data")

print(f"Experiment : {experiment_name}")
print()
print(f"Model      : {architecture} ({'pretrained' if pretrained else 'from scratch'})")
print()
print(f"Training   : {number_of_epochs} epochs, batch={batch_size}, lr={learning_rate}")
print()
print(f"Dataset    : {dataset_name} at {data_root}")

config.check()
print()
print("check() passed — all keys present in the YAML.")
```

### Output

```
Experiment : cifar10_baseline

Model      : resnet18 (pretrained)

Training   : 20 epochs, batch=128, lr=0.01

Dataset    : cifar10 at ./data

check() passed — all keys present in the YAML.
```

---

## Example 05

Example 05: Loading config from a JSON file and iterating over a list.

Pass any .json path directly to GhostConfig(). When a key holds a list of
dicts, iterating the returned GhostConfig wraps each dict element as its own
GhostConfig so you can call get() on each item.

### Code

```python
"""Example 05: Loading config from a JSON file and iterating over a list.

Pass any .json path directly to GhostConfig(). When a key holds a list of
dicts, iterating the returned GhostConfig wraps each dict element as its own
GhostConfig so you can call get() on each item.
"""
import pathlib

import ghostconfig

json_path = pathlib.Path(__file__).parent / "configs" / "augmentations.json"
config = ghostconfig.GhostConfig.create(json_path)

pipeline_config = config["pipeline"]

print("Augmentation pipeline:")
for step_config in pipeline_config:
    name = step_config.get("name", "unknown")
    print(f"  - {name}")

config.check()
print()
print("check() passed — all keys present in the JSON.")
```

### Output

```
Augmentation pipeline:
  - random_crop
  - random_horizontal_flip
  - color_jitter

check() passed — all keys present in the JSON.
```

---

## Example 06

Example 06: Using GhostConfig to wire up a training script.

This shows a realistic pattern: read all parameters up front, then call
check() once before any expensive work begins. If anything is missing the
error surfaces immediately with a ready-to-paste suggestion.

### Code

```python
"""Example 06: Using GhostConfig to wire up a training script.

This shows a realistic pattern: read all parameters up front, then call
check() once before any expensive work begins. If anything is missing the
error surfaces immediately with a ready-to-paste suggestion.
"""
import ghostconfig


def build_model(architecture: str, number_of_layers: int, dropout: float) -> str:
    return f"{architecture}-{number_of_layers} (dropout={dropout})"


def build_optimizer(model_name: str, learning_rate: float, weight_decay: float) -> str:
    return f"AdamW(lr={learning_rate}, wd={weight_decay}) on {model_name}"


def run_training(config: ghostconfig.GhostConfig) -> None:
    model_config = config["model"]
    architecture = model_config.get("architecture", "resnet18")
    number_of_layers = model_config.get("number_of_layers", 18)
    dropout = model_config.get("dropout", 0.0)

    optimizer_config = config["optimizer"]
    learning_rate = optimizer_config.get("learning_rate", 1e-3)
    weight_decay = optimizer_config.get("weight_decay", 0.0)

    number_of_epochs = config.get("number_of_epochs", 10)

    # Validate before any expensive initialisation
    config.check()

    model = build_model(architecture, number_of_layers, dropout)
    optimizer = build_optimizer(model, learning_rate, weight_decay)

    print(f"Model     : {model}")
    print(f"Optimizer : {optimizer}")
    print(f"Training for {number_of_epochs} epochs …")
    print("Done.")


config = ghostconfig.GhostConfig.create({
    "model": {
        "architecture": "resnet50",
        "number_of_layers": 50,
        "dropout": 0.2,
    },
    "optimizer": {
        "learning_rate": 3e-4,
        "weight_decay": 1e-5,
    },
    "number_of_epochs": 30,
})

run_training(config)
```

### Output

```
Model     : resnet50-50 (dropout=0.2)
Optimizer : AdamW(lr=0.0003, wd=1e-05) on resnet50-50 (dropout=0.2)
Training for 30 epochs …
Done.
```
