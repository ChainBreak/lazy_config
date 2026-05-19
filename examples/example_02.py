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
