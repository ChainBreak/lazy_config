"""Example 01: Creating a config from a plain Python dict.

The simplest way to get started — no files required.
"""
import lazy_config

config = lazy_config.LazyConfig({
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
