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
