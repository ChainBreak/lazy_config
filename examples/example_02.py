"""Example 02: Navigating nested sub-configs.

Calling get(key) without a default on a dict value returns a child LazyConfig.
You can chain these calls to reach deeply nested leaves.
"""
import lazy_config

config = lazy_config.LazyConfig({
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

model_config = config.get("model")
optimizer_config = config.get("optimizer")

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
