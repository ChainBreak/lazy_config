"""Example 06: Using LazyConfig to wire up a training script.

This shows a realistic pattern: read all parameters up front, then call
check() once before any expensive work begins. If anything is missing the
error surfaces immediately with a ready-to-paste suggestion.
"""
import lazy_config


def build_model(architecture: str, number_of_layers: int, dropout: float) -> str:
    return f"{architecture}-{number_of_layers} (dropout={dropout})"


def build_optimizer(model_name: str, learning_rate: float, weight_decay: float) -> str:
    return f"AdamW(lr={learning_rate}, wd={weight_decay}) on {model_name}"


def run_training(config: lazy_config.LazyConfig) -> None:
    model_config = config.get("model")
    architecture = model_config.get("architecture", "resnet18")
    number_of_layers = model_config.get("number_of_layers", 18)
    dropout = model_config.get("dropout", 0.0)

    optimizer_config = config.get("optimizer")
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


config = lazy_config.LazyConfig.from_dict({
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
