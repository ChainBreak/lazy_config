# GhostConfig Examples

Each example below is a self-contained script demonstrating one aspect of `GhostConfig`. The output shown was produced by running the script directly.

## Config file: `training.yaml`

All examples load from this shared config file:

```yaml
experiment_name: cifar10_baseline

model:
  layers:
  - channels: 64
    blocks: 4
  - channels: 128
    blocks: 4
```

---

## Example 01

Example 01: Loading a config from a YAML file.

### Code

```python
from ghostconfig import GhostConfig

config = GhostConfig.create("training.yaml")

for block in config["model"]["layers"]:
    channels = block.get('channels', 128)
    blocks = block.get('blocks', 3)
    print(f"Channels: {channels}, Blocks: {blocks}")
  
config.check()
```

### Output

```
Channels: 64, Blocks: 4
Channels: 128, Blocks: 4
```

---

## Example 02

Example 02: Navigating nested sub-configs.

Indexing a GhostConfig with a string key that holds a dict returns a child
GhostConfig. Chain these calls to navigate any depth of nesting.

### Code

```python
from ghostconfig import GhostConfig

config = GhostConfig.create("training.yaml")

model_config = config["model"]
training_config = config["training"]
dataset_config = config["dataset"]

architecture = model_config.get("architecture", "resnet18")
number_of_layers = model_config.get("number_of_layers", 18)
pretrained = model_config.get("pretrained", False)

number_of_epochs = training_config.get("number_of_epochs", 10)
batch_size = training_config.get("batch_size", 32)
learning_rate = training_config.get("learning_rate", 0.001)

dataset_name = dataset_config.get("name", "imagenet")
data_root = dataset_config.get("data_root", "./data")

print("Model:")
print(f"  architecture : {architecture}")
print(f"  layers       : {number_of_layers}")
print(f"  pretrained   : {pretrained}")
print()
print("Training:")
print(f"  epochs       : {number_of_epochs}")
print(f"  batch size   : {batch_size}")
print(f"  learning rate: {learning_rate}")
print()
print("Dataset:")
print(f"  name         : {dataset_name}")
print(f"  data root    : {data_root}")

config.check()
print()
print("check() passed — no missing keys.")
```

### Output

```
Model:
  architecture : resnet18
  layers       : 18
  pretrained   : False

Training:
  epochs       : 10
  batch size   : 32
  learning rate: 0.001

Dataset:
  name         : imagenet
  data root    : ./data
The following parameters were used but missing from the config:
  - model.architecture
  - model.number_of_layers
  - model.pretrained
  - training.number_of_epochs
  - training.batch_size
  - training.learning_rate
  - dataset.name
  - dataset.data_root

Since this started from a yaml (training.yaml), you should add:

model:
  architecture: resnet18
  number_of_layers: 18
  pretrained: false
training:
  number_of_epochs: 10
  batch_size: 32
  learning_rate: 0.001
dataset:
  name: imagenet
  data_root: ./data

The following keys were present in the config but never accessed:
  - experiment_name
  - model.layers.0.blocks
  - model.layers.0.channels
  - model.layers.1.blocks
  - model.layers.1.channels
```

---

## Example 03

Example 03: Missing keys return defaults; check() surfaces them all at once.

When a key is absent from the config, get(key, default) silently returns the
default and records the miss. Calling check() at the end raises a
MissingConfigError that lists every missing path and shows exactly what to add.

### Code

```python
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
```

### Output

```
batch_size   : 32  (present in config)
dropout      : 0.0  (missing — default used)
warmup_steps : 0  (missing — default used)
seed         : 42  (missing — default used)

The following parameters were used but missing from the config:
  - training.batch_size
  - model.dropout
  - training.warmup_steps
  - seed

Since this started from a yaml (training.yaml), you should add:

training:
  batch_size: 32
  warmup_steps: 0
model:
  dropout: 0.0
seed: 42

The following keys were present in the config but never accessed:
  - experiment_name
  - model.layers.0.blocks
  - model.layers.0.channels
  - model.layers.1.blocks
  - model.layers.1.channels
```

---

## Example 04

Example 04: Iterating over a list of sub-configs.

When a key holds a list of dicts, iterating the returned GhostConfig wraps
each element as its own GhostConfig so you can call get() on each item.

### Code

```python
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
```

### Output

```
Augmentation pipeline:
  - unknown
  - unknown
The following parameters were used but missing from the config:
  - augmentations.pipeline
  - augmentations.pipeline.0.name
  - augmentations.pipeline.1.name

Since this started from a yaml (training.yaml), you should add:

augmentations:
  pipeline:
  - name: unknown
  - name: unknown

The following keys were present in the config but never accessed:
  - experiment_name
  - model.layers.0.blocks
  - model.layers.0.channels
  - model.layers.1.blocks
  - model.layers.1.channels
```

---

## Example 05

Example 05: Reading optimizer settings from a sub-config.

Use a sub-config to group related parameters. Each section of the YAML becomes
its own GhostConfig, keeping parameter access organised by concern.

### Code

```python
from ghostconfig import GhostConfig

config = GhostConfig.create("training.yaml")

optimizer_config = config["optimizer"]
optimizer_name = optimizer_config.get("name", "sgd")
learning_rate = optimizer_config.get("learning_rate", 0.01)
weight_decay = optimizer_config.get("weight_decay", 0.0)

training_config = config["training"]
number_of_epochs = training_config.get("number_of_epochs", 10)
batch_size = training_config.get("batch_size", 32)

print("Optimizer:")
print(f"  name         : {optimizer_name}")
print(f"  learning rate: {learning_rate}")
print(f"  weight decay : {weight_decay}")
print()
print("Training schedule:")
print(f"  epochs       : {number_of_epochs}")
print(f"  batch size   : {batch_size}")

config.check()
print()
print("check() passed — all keys present in the YAML.")
```

### Output

```
Optimizer:
  name         : sgd
  learning rate: 0.01
  weight decay : 0.0

Training schedule:
  epochs       : 10
  batch size   : 32
The following parameters were used but missing from the config:
  - optimizer.name
  - optimizer.learning_rate
  - optimizer.weight_decay
  - training.number_of_epochs
  - training.batch_size

Since this started from a yaml (training.yaml), you should add:

optimizer:
  name: sgd
  learning_rate: 0.01
  weight_decay: 0.0
training:
  number_of_epochs: 10
  batch_size: 32

The following keys were present in the config but never accessed:
  - experiment_name
  - model.layers.0.blocks
  - model.layers.0.channels
  - model.layers.1.blocks
  - model.layers.1.channels
```

---

## Example 06

Example 06: Using GhostConfig to wire up a training script.

This shows a realistic pattern: read all parameters up front via sub-configs,
then call check() once before any expensive work begins. If anything is missing
the error surfaces immediately with a ready-to-paste suggestion.

### Code

```python
from ghostconfig import GhostConfig


def build_model(architecture: str, number_of_layers: int) -> str:
    return f"{architecture}-{number_of_layers}"


def build_optimizer(model_name: str, optimizer_name: str, learning_rate: float, weight_decay: float) -> str:
    return f"{optimizer_name}(lr={learning_rate}, wd={weight_decay}) on {model_name}"


def run_training(config: GhostConfig) -> None:
    model_config = config["model"]
    architecture = model_config.get("architecture", "resnet18")
    number_of_layers = model_config.get("number_of_layers", 18)

    optimizer_config = config["optimizer"]
    optimizer_name = optimizer_config.get("name", "sgd")
    learning_rate = optimizer_config.get("learning_rate", 1e-3)
    weight_decay = optimizer_config.get("weight_decay", 0.0)

    number_of_epochs = config["training"].get("number_of_epochs", 10)

    # Validate before any expensive initialisation
    config.check()

    model = build_model(architecture, number_of_layers)
    optimizer = build_optimizer(model, optimizer_name, learning_rate, weight_decay)

    print(f"Model     : {model}")
    print(f"Optimizer : {optimizer}")
    print(f"Training for {number_of_epochs} epochs …")
    print("Done.")


config = GhostConfig.create("training.yaml")
run_training(config)
```

### Output

```
The following parameters were used but missing from the config:
  - model.architecture
  - model.number_of_layers
  - optimizer.name
  - optimizer.learning_rate
  - optimizer.weight_decay
  - training.number_of_epochs

Since this started from a yaml (training.yaml), you should add:

model:
  architecture: resnet18
  number_of_layers: 18
optimizer:
  name: sgd
  learning_rate: 0.001
  weight_decay: 0.0
training:
  number_of_epochs: 10

The following keys were present in the config but never accessed:
  - experiment_name
  - model.layers.0.blocks
  - model.layers.0.channels
  - model.layers.1.blocks
  - model.layers.1.channels
```
