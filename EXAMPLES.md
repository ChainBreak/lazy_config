# GhostConfig Examples

Each example below is a self-contained script demonstrating one aspect of `GhostConfig`. The output shown was produced by running the script directly.

## Config file: `training.yaml`

All examples load from this shared config file:

```yaml
experiment_name: cifar10_baseline

model:
  architecture: resnet18
  number_of_layers: 18
  pretrained: true

training:
  number_of_epochs: 20
  batch_size: 128
  learning_rate: 0.01
  weight_decay: 1.0e-4

optimizer:
  name: sgd
  learning_rate: 0.01
  weight_decay: 1.0e-4

dataset:
  name: cifar10
  data_root: ./data

augmentations:
  pipeline:
    - name: random_crop
      size: 224
    - name: random_horizontal_flip
      probability: 0.5
    - name: color_jitter
      brightness: 0.2
      contrast: 0.2
```

---

## Example 01

Example 01: Loading a config from a YAML file.

Pass a filename string to GhostConfig.create() and it resolves the file from
the current working directory. Access top-level and nested values with get().

### Code

```python
"""Example 01: Loading a config from a YAML file.

Pass a filename string to GhostConfig.create() and it resolves the file from
the current working directory. Access top-level and nested values with get().
"""
import ghostconfig

config = ghostconfig.GhostConfig.create("training.yaml")

experiment_name = config.get("experiment_name", "untitled")

training_config = config["training"]
number_of_epochs = training_config.get("number_of_epochs", 10)
batch_size = training_config.get("batch_size", 32)
learning_rate = training_config.get("learning_rate", 0.001)

print(f"experiment : {experiment_name}")
print(f"epochs     : {number_of_epochs}")
print(f"batch size : {batch_size}")
print(f"lr         : {learning_rate}")

config.check()
print()
print("check() passed — all keys present in the YAML.")
```

### Output

```
experiment : cifar10_baseline
epochs     : 20
batch size : 128
lr         : 0.01

check() passed — all keys present in the YAML.
```

---

## Example 02

Example 02: Navigating nested sub-configs.

Indexing a GhostConfig with a string key that holds a dict returns a child
GhostConfig. Chain these calls to navigate any depth of nesting.

### Code

```python
"""Example 02: Navigating nested sub-configs.

Indexing a GhostConfig with a string key that holds a dict returns a child
GhostConfig. Chain these calls to navigate any depth of nesting.
"""
import ghostconfig

config = ghostconfig.GhostConfig.create("training.yaml")

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
  pretrained   : True

Training:
  epochs       : 20
  batch size   : 128
  learning rate: 0.01

Dataset:
  name         : cifar10
  data root    : ./data

check() passed — no missing keys.
```

---

## Example 03

Example 03: Missing keys return defaults; check() surfaces them all at once.

When a key is absent from the config, get(key, default) silently returns the
default and records the miss. Calling check() at the end raises a
MissingConfigError that lists every missing path and shows exactly what to add.

### Code

```python
"""Example 03: Missing keys return defaults; check() surfaces them all at once.

When a key is absent from the config, get(key, default) silently returns the
default and records the miss. Calling check() at the end raises a
MissingConfigError that lists every missing path and shows exactly what to add.
"""
import ghostconfig

config = ghostconfig.GhostConfig.create("training.yaml")

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

try:
    config.check()
except ghostconfig.MissingConfigError as error:
    print("MissingConfigError caught:")
    print(str(error))
```

### Output

```
batch_size   : 128  (present in config)
dropout      : 0.0  (missing — default used)
warmup_steps : 0  (missing — default used)
seed         : 42  (missing — default used)

MissingConfigError caught:
The following parameters were used but missing from the config:
  - model.dropout
  - training.warmup_steps
  - seed

Since this started from a yaml (training.yaml), you should add:

model:
  dropout: 0.0
training:
  warmup_steps: 0
seed: 42

The following keys were present in the config but never accessed:
  - augmentations.pipeline.0.name
  - augmentations.pipeline.0.size
  - augmentations.pipeline.1.name
  - augmentations.pipeline.1.probability
  - augmentations.pipeline.2.brightness
  - augmentations.pipeline.2.contrast
  - augmentations.pipeline.2.name
  - dataset.data_root
  - dataset.name
  - experiment_name
  - model.architecture
  - model.number_of_layers
  - model.pretrained
  - optimizer.learning_rate
  - optimizer.name
  - optimizer.weight_decay
  - training.learning_rate
  - training.number_of_epochs
  - training.weight_decay
```

---

## Example 04

Example 04: Iterating over a list of sub-configs.

When a key holds a list of dicts, iterating the returned GhostConfig wraps
each element as its own GhostConfig so you can call get() on each item.

### Code

```python
"""Example 04: Iterating over a list of sub-configs.

When a key holds a list of dicts, iterating the returned GhostConfig wraps
each element as its own GhostConfig so you can call get() on each item.
"""
import ghostconfig

config = ghostconfig.GhostConfig.create("training.yaml")

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
  - random_crop
  - random_horizontal_flip
  - color_jitter

check() passed — all keys present in the YAML.
```

---

## Example 05

Example 05: Reading optimizer settings from a sub-config.

Use a sub-config to group related parameters. Each section of the YAML becomes
its own GhostConfig, keeping parameter access organised by concern.

### Code

```python
"""Example 05: Reading optimizer settings from a sub-config.

Use a sub-config to group related parameters. Each section of the YAML becomes
its own GhostConfig, keeping parameter access organised by concern.
"""
import ghostconfig

config = ghostconfig.GhostConfig.create("training.yaml")

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
  weight decay : 0.0001

Training schedule:
  epochs       : 20
  batch size   : 128

check() passed — all keys present in the YAML.
```

---

## Example 06

Example 06: Using GhostConfig to wire up a training script.

This shows a realistic pattern: read all parameters up front via sub-configs,
then call check() once before any expensive work begins. If anything is missing
the error surfaces immediately with a ready-to-paste suggestion.

### Code

```python
"""Example 06: Using GhostConfig to wire up a training script.

This shows a realistic pattern: read all parameters up front via sub-configs,
then call check() once before any expensive work begins. If anything is missing
the error surfaces immediately with a ready-to-paste suggestion.
"""
import ghostconfig


def build_model(architecture: str, number_of_layers: int) -> str:
    return f"{architecture}-{number_of_layers}"


def build_optimizer(model_name: str, optimizer_name: str, learning_rate: float, weight_decay: float) -> str:
    return f"{optimizer_name}(lr={learning_rate}, wd={weight_decay}) on {model_name}"


def run_training(config: ghostconfig.GhostConfig) -> None:
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


config = ghostconfig.GhostConfig.create("training.yaml")
run_training(config)
```

### Output

```
Model     : resnet18-18
Optimizer : sgd(lr=0.01, wd=0.0001) on resnet18-18
Training for 20 epochs …
Done.
```
