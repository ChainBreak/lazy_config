from __future__ import annotations

import json
import pathlib
import textwrap

import pytest

import ghostconfig
from ghostconfig import GhostConfig, MissingConfigError

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def write_yaml(tmp_path: pathlib.Path, content: str) -> pathlib.Path:
    path = tmp_path / "config.yaml"
    path.write_text(textwrap.dedent(content))
    return path


def write_json(tmp_path: pathlib.Path, data: dict) -> pathlib.Path:
    path = tmp_path / "config.json"
    path.write_text(json.dumps(data, indent=2))
    return path


# ---------------------------------------------------------------------------
# from_dict basics
# ---------------------------------------------------------------------------

# Good
def test_from_dict_returns_ghost_config():
    config = GhostConfig.create({"number": 42})
    assert isinstance(config, GhostConfig)

# Good
def test_from_dict_get_existing_leaf():
    config = GhostConfig.create({"number": 42})
    assert config.get("number", 0) == 42

# Good
def test_from_dict_get_missing_leaf_returns_default():
    config = GhostConfig.create({})
    assert config.get("learning_rate", 0.001) == 0.001

# Good
def test_from_dict_check_passes_when_nothing_missing():
    config = GhostConfig.create({"number": 42})
    config.get("number", 0)
    config.check()  # should not raise

# Good
def test_from_dict_check_raises_with_dict_suggestion():
    config = GhostConfig.create({})
    config.get("learning_rate", 0.001)
    with pytest.raises(MissingConfigError) as exc_info:
        config.check()
    message = str(exc_info.value)
    assert "learning_rate" in message
    assert "0.001" in message
    assert "dict" in message

# Good
def test_from_dict_empty_source_suggests_full_structure():
    config = GhostConfig.create({})
    config["model"].get("layers", 4)
    config["model"].get("block", "resnet")
    with pytest.raises(MissingConfigError) as exc_info:
        config.check()
    message = str(exc_info.value)
    assert "model" in message
    assert "layers" in message
    assert "block" in message


# ---------------------------------------------------------------------------
# from_yaml
# ---------------------------------------------------------------------------

# Good
def test_from_yaml_returns_ghost_config(tmp_path):
    path = write_yaml(tmp_path, "number: 42\n")
    config = GhostConfig.create(path)
    assert isinstance(config, GhostConfig)

# Good
def test_from_yaml_get_existing_leaf(tmp_path):
    path = write_yaml(tmp_path, "layers: 4\n")
    config = GhostConfig.create(path)
    assert config.get("layers", 1) == 4

# Good
def test_from_yaml_sub_config_navigation(tmp_path):
    path = write_yaml(
        tmp_path,
        """
        model:
          layers: 4
          block: resnet
        dataset:
          path: my/data/
          augmentations:
            - crop
        """,
    )
    config = GhostConfig.create(path)

    model_config = config["model"]
    assert isinstance(model_config, GhostConfig)
    assert model_config.get("layers", 1) == 4
    assert model_config.get("block", "vgg") == "resnet"

    dataset_config = config["dataset"]
    assert dataset_config.get("path", "") == "my/data/"
    assert dataset_config.get("augmentations", []) == ["crop"]

# Good
def test_from_yaml_check_passes_when_all_present(tmp_path):
    path = write_yaml(tmp_path, "layers: 4\n")
    config = GhostConfig.create(path)
    config.get("layers", 1)
    config.check()  # should not raise

# Good
def test_from_yaml_check_raises_with_yaml_suggestion(tmp_path):
    path = write_yaml(tmp_path, "layers: 4\n")
    config = GhostConfig.create(path)
    config.get("learning_rate", 0.001)
    with pytest.raises(MissingConfigError) as exc_info:
        config.check()
    message = str(exc_info.value)
    assert "yaml" in message
    assert str(path) in message
    assert "learning_rate" in message
    assert "0.001" in message

# Good
def test_from_yaml_check_raises_with_merged_suggestion_for_multiple_missing(tmp_path):
    path = write_yaml(tmp_path, "layers: 4\n")
    config = GhostConfig.create(path)
    training_config = config["training"]
    training_config.get("learning_rate", 0.001)
    training_config.get("batch_size", 32)
    with pytest.raises(MissingConfigError) as exc_info:
        config.check()
    message = str(exc_info.value)
    assert "training" in message
    assert "learning_rate" in message
    assert "batch_size" in message


# ---------------------------------------------------------------------------
# Ghost chains (missing sub-config)
# ---------------------------------------------------------------------------

# Good
def test_ghost_sub_config_returns_ghost_config(tmp_path):
    path = write_yaml(tmp_path, "layers: 4\n")
    config = GhostConfig.create(path)
    training_config = config["training"]
    assert isinstance(training_config, GhostConfig)

# Good
def test_ghost_chain_returns_default_leaf():
    config = GhostConfig.create({"layers": 4})
    result = config["training"].get("learning_rate", 0.001)
    assert result == 0.001

# Good
def test_ghost_chain_records_full_dotted_path():
    config = GhostConfig.create({})
    config["training"].get("learning_rate", 0.001)
    with pytest.raises(MissingConfigError) as exc_info:
        config.check()
    message = str(exc_info.value)
    assert "training.learning_rate" in message or (
        "training" in message and "learning_rate" in message
    )

# Good
def test_ghost_chain_preserves_first_default_on_repeated_access():
    config = GhostConfig.create({})
    config.get("lr", 0.1)
    config.get("lr", 0.9)
    with pytest.raises(MissingConfigError) as exc_info:
        config.check()
    message = str(exc_info.value)
    assert "0.1" in message
    assert "0.9" not in message


# ---------------------------------------------------------------------------
# from_json
# ---------------------------------------------------------------------------

# Good
def test_from_json_check_raises_with_json_suggestion(tmp_path):
    path = write_json(tmp_path, {"layers": 4})
    config = GhostConfig.create(path)
    config.get("learning_rate", 0.001)
    with pytest.raises(MissingConfigError) as exc_info:
        config.check()
    message = str(exc_info.value)
    assert "json" in message
    assert "learning_rate" in message

# Good
def test_from_json_existing_leaf(tmp_path):
    path = write_json(tmp_path, {"layers": 4})
    config = GhostConfig.create(path)
    assert config.get("layers", 1) == 4


# ---------------------------------------------------------------------------
# Type preservation
# ---------------------------------------------------------------------------

# Good
def test_type_preservation_int():
    config = GhostConfig.create({"count": 10})
    result = config.get("count", 0)
    assert result == 10
    assert isinstance(result, int)

# Good
def test_type_preservation_float():
    config = GhostConfig.create({"ratio": 0.5})
    result = config.get("ratio", 1.0)
    assert result == 0.5
    assert isinstance(result, float)

# Good
def test_type_preservation_list():
    config = GhostConfig.create({"items": [1, 2, 3]})
    result = config.get("items", [])
    assert result == [1, 2, 3]
    assert isinstance(result, list)

# Good
def test_type_preservation_bool():
    config = GhostConfig.create({"enabled": True})
    result = config.get("enabled", False)
    assert result is True


# ---------------------------------------------------------------------------
# TypeError: get() on sub-config, __getitem__() on scalar
# ---------------------------------------------------------------------------

# Good
def test_get_with_default_on_sub_config_raises():
    config = GhostConfig.create({"model": {"layers": 4}})
    assert config.get("model", {}) == {"layers": 4}


# ---------------------------------------------------------------------------
# OmegaConf interpolation
# ---------------------------------------------------------------------------

# Good
def test_omegaconf_interpolation_in_yaml(tmp_path):
    path = write_yaml(
        tmp_path,
        """
        base_path: /data
        train_path: ${base_path}/train
        """,
    )
    config = GhostConfig.create(path)
    assert config.get("train_path", "") == "/data/train"


# ---------------------------------------------------------------------------
# Lists — top-level list YAML (integer indexing)
# ---------------------------------------------------------------------------

PEOPLE_YAML = """\
- name: Alice
  age: 30
  city: New York
- name: Bob
  age: 25
  city: London
- name: Carol
  age: 35
  city: Sydney
"""


def test_top_level_list_integer_index(tmp_path):
    path = write_yaml(tmp_path, PEOPLE_YAML)
    config = GhostConfig.create(path)
    assert config[0].get("name", "") == "Alice"
    assert config[1].get("name", "") == "Bob"
    assert config[2].get("city", "") == "Sydney"


def test_top_level_list_integer_index_returns_ghost_config(tmp_path):
    path = write_yaml(tmp_path, PEOPLE_YAML)
    config = GhostConfig.create(path)
    alice = config[0]
    assert isinstance(alice, GhostConfig)


def test_top_level_list_leaf_values(tmp_path):
    path = write_yaml(tmp_path, PEOPLE_YAML)
    config = GhostConfig.create(path)
    assert config[0].get("age", 0) == 30
    assert isinstance(config[0].get("age", 0), int)


def test_top_level_list_out_of_bounds_returns_ghost(tmp_path):
    path = write_yaml(tmp_path, PEOPLE_YAML)
    config = GhostConfig.create(path)
    ghost = config[99]
    assert isinstance(ghost, GhostConfig)
    result = ghost.get("name", "default_name")
    assert result == "default_name"


# ---------------------------------------------------------------------------
# Lists — iteration over a list-valued key
# ---------------------------------------------------------------------------

LAYERS_YAML = """\
layers:
  - norm: BatchNorm
    size: 64
  - norm: BatchNorm
    size: 128
  - norm: LayerNorm
    size: 256
"""


def test_iteration_yields_ghost_config_for_dict_elements(tmp_path):
    path = write_yaml(tmp_path, LAYERS_YAML)
    config = GhostConfig.create(path)
    for layer_config in config["layers"]:
        assert isinstance(layer_config, GhostConfig)
        assert layer_config.get("norm", "") in ("BatchNorm", "LayerNorm")


def test_iteration_correct_values(tmp_path):
    path = write_yaml(tmp_path, LAYERS_YAML)
    config = GhostConfig.create(path)
    sizes = [layer.get("size", 0) for layer in config["layers"]]
    assert sizes == [64, 128, 256]


def test_iteration_length(tmp_path):
    path = write_yaml(tmp_path, LAYERS_YAML)
    config = GhostConfig.create(path)
    assert len(list(config["layers"])) == 3


def test_getitem_on_scalar_still_returns_ghost_config():
    config = GhostConfig.create({"learning_rate": 0.001})
    assert isinstance(config["learning_rate"], GhostConfig)

def test_getitem_counter():
    num_people = 10
    data = {"people": [{"name": f"Person {i}"} for i in range(num_people)]}
    config = GhostConfig.create(data)

    counter = 0
    for _ in config["people"]:
        counter += 1
    assert counter == num_people


# ---------------------------------------------------------------------------
# Lists — iteration recording missing sub-fields
# ---------------------------------------------------------------------------

PEOPLE_NO_AGE_YAML = """\
people:
  - name: Alice
  - name: Bob
"""


def test_iteration_over_real_list_records_missing_sub_fields(tmp_path):
    """Real list exists but items are missing 'age'; check() reports both paths."""
    path = write_yaml(tmp_path, PEOPLE_NO_AGE_YAML)
    config = GhostConfig.create(path)

    for person in config["people"]:
        assert isinstance(person, GhostConfig)
        age = person.get("age", 42)
        assert age == 42

    with pytest.raises(MissingConfigError) as exc_info:
        config.check()
    message = str(exc_info.value)
    assert "people.0.age" in message
    assert "people.1.age" in message


def test_ghost_list_index_access_records_correct_paths():
    """'people' key is entirely absent; index access into the ghost records paths."""
    config = GhostConfig.create()
    people = config["people"]
    assert isinstance(people, GhostConfig)

    for index in range(2):
        person = people[index]
        assert isinstance(person, GhostConfig)
        age = person.get("age", 42)
        assert age == 42

    with pytest.raises(MissingConfigError) as exc_info:
        config.check()
    message = str(exc_info.value)
    assert "people.0.age" in message
    assert "people.1.age" in message


def test_ghost_list_iter_yields_two_ghost_sub_configs():
    """Iterating a ghost GhostConfig yields exactly two ghost sub-configs."""
    config = GhostConfig.create()
    items = list(config["people"])
    assert len(items) == 2
    for item in items:
        assert isinstance(item, GhostConfig)

def test_get_with_list_default_records_key_as_missing():
    """get("people", []) when people is absent records the key itself as missing."""
    config = GhostConfig.create()
    result = config.get("people", [])
    assert result == []

    with pytest.raises(MissingConfigError) as exc_info:
        config.check()
    message = str(exc_info.value)
    assert "people" in message


def test_ghost_list_iter_records_missing_sub_fields():
    """Iterating a ghost with a for-loop records people.0.age and people.1.age."""
    config = GhostConfig.create()
    for person in config["people"]:
        assert isinstance(person, GhostConfig)
        age = person.get("age", 42)
        assert age == 42

    with pytest.raises(MissingConfigError) as exc_info:
        config.check()
    message = str(exc_info.value)
    assert "people.0.age" in message
    assert "people.1.age" in message

# -------------------------------------------------------------------------
# Unused keys
# -------------------------------------------------------------------------

def test_get_with_non_leaf():
    config = GhostConfig.create({"model": {"layers": 4}})
    model = config.get("model", {})
    assert model == {"layers": 4}
    assert isinstance(model, dict)
    assert config._flattened.unused_input_paths == set()

def test_unused_keys():
    """Test that only leafs are reported as unused."""
    config = GhostConfig.create({"model": {"layers": 4}, "optimizer": {"learning_rate": 0.001}})
    _ = config.get("model", {})
    assert config._flattened.unused_input_paths == {"optimizer.learning_rate"}

# ---------------------------------------------------------------------------
# Public API surface
# ---------------------------------------------------------------------------


def test_module_exports_ghost_config():
    assert hasattr(ghostconfig, "GhostConfig")


def test_module_exports_missing_config_error():
    assert hasattr(ghostconfig, "MissingConfigError")
