"""Example 06: Using GhostConfig to wire up a training script.

This shows a realistic pattern: read all parameters up front via sub-configs,
then call check() once before any expensive work begins. If anything is missing
the error surfaces immediately with a ready-to-paste suggestion.
"""
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
