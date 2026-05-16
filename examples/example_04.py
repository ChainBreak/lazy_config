"""Example 04: Loading config from a YAML file.

Pass any .yaml or .yml path directly to GhostConfig(). OmegaConf is used under
the hood, so interpolations and anchors work out of the box.
"""
import pathlib

import ghostconfig

yaml_path = pathlib.Path(__file__).parent / "configs" / "training.yaml"
config = ghostconfig.GhostConfig(yaml_path)

experiment_name = config.get("experiment_name", "untitled")

model_config = config.get("model")
architecture = model_config.get("architecture", "resnet18")
pretrained = model_config.get("pretrained", False)

training_config = config.get("training")
number_of_epochs = training_config.get("number_of_epochs", 10)
batch_size = training_config.get("batch_size", 32)
learning_rate = training_config.get("learning_rate", 0.001)

dataset_config = config.get("dataset")
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
