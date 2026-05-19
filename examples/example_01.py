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
