from __future__ import annotations

import json
import textwrap
import pathlib
import pytest
import yaml

import lazy_config
from lazy_config import LazyConfig, MissingConfigError


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
def test_from_dict_returns_lazy_config():
    config = LazyConfig.from_dict({"number": 42})
    assert isinstance(config, LazyConfig)

# Good
def test_from_dict_get_existing_leaf():
    config = LazyConfig.from_dict({"number": 42})
    assert config.get("number", 0) == 42

# Good
def test_from_dict_get_missing_leaf_returns_default():
    config = LazyConfig.from_dict({})
    assert config.get("learning_rate", 0.001) == 0.001

# Good
def test_from_dict_check_passes_when_nothing_missing():
    config = LazyConfig.from_dict({"number": 42})
    config.get("number", 0)
    config.check()  # should not raise

# Good
def test_from_dict_check_raises_with_dict_suggestion():
    config = LazyConfig.from_dict({})
    config.get("learning_rate", 0.001)
    with pytest.raises(MissingConfigError) as exc_info:
        config.check()
    message = str(exc_info.value)
    assert "learning_rate" in message
    assert "0.001" in message
    assert "dict" in message

# Good
def test_from_dict_empty_source_suggests_full_structure():
    config = LazyConfig.from_dict({})
    config.get("model").get("layers", 4)
    config.get("model").get("block", "resnet")
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
def test_from_yaml_returns_lazy_config(tmp_path):
    path = write_yaml(tmp_path, "number: 42\n")
    config = LazyConfig.from_yaml(path)
    assert isinstance(config, LazyConfig)

# Good
def test_from_yaml_get_existing_leaf(tmp_path):
    path = write_yaml(tmp_path, "layers: 4\n")
    config = LazyConfig.from_yaml(path)
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
    config = LazyConfig.from_yaml(path)

    model_config = config.get("model")
    assert isinstance(model_config, LazyConfig)
    assert model_config.get("layers", 1) == 4
    assert model_config.get("block", "vgg") == "resnet"

    dataset_config = config.get("dataset")
    assert dataset_config.get("path", "") == "my/data/"
    assert dataset_config.get("augmentations", []) == ["crop"]

# Good
def test_from_yaml_check_passes_when_all_present(tmp_path):
    path = write_yaml(tmp_path, "layers: 4\n")
    config = LazyConfig.from_yaml(path)
    config.get("layers", 1)
    config.check()  # should not raise

# Good
def test_from_yaml_check_raises_with_yaml_suggestion(tmp_path):
    path = write_yaml(tmp_path, "layers: 4\n")
    config = LazyConfig.from_yaml(path)
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
    config = LazyConfig.from_yaml(path)
    training_config = config.get("training")
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
def test_ghost_sub_config_returns_lazy_config(tmp_path):
    path = write_yaml(tmp_path, "layers: 4\n")
    config = LazyConfig.from_yaml(path)
    training_config = config.get("training")
    assert isinstance(training_config, LazyConfig)

# Good
def test_ghost_chain_returns_default_leaf():
    config = LazyConfig.from_dict({"layers": 4})
    result = config.get("training").get("learning_rate", 0.001)
    assert result == 0.001

# Good
def test_ghost_chain_records_full_dotted_path():
    config = LazyConfig.from_dict({})
    config.get("training").get("learning_rate", 0.001)
    with pytest.raises(MissingConfigError) as exc_info:
        config.check()
    message = str(exc_info.value)
    assert "training.learning_rate" in message or (
        "training" in message and "learning_rate" in message
    )

# Good
def test_ghost_chain_preserves_first_default_on_repeated_access():
    config = LazyConfig.from_dict({})
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
    config = LazyConfig.from_json(path)
    config.get("learning_rate", 0.001)
    with pytest.raises(MissingConfigError) as exc_info:
        config.check()
    message = str(exc_info.value)
    assert "json" in message
    assert "learning_rate" in message

# Good
def test_from_json_existing_leaf(tmp_path):
    path = write_json(tmp_path, {"layers": 4})
    config = LazyConfig.from_json(path)
    assert config.get("layers", 1) == 4


# ---------------------------------------------------------------------------
# Type preservation
# ---------------------------------------------------------------------------

# Good
def test_type_preservation_int():
    config = LazyConfig.from_dict({"count": 10})
    result = config.get("count", 0)
    assert result == 10
    assert isinstance(result, int)

# Good
def test_type_preservation_float():
    config = LazyConfig.from_dict({"ratio": 0.5})
    result = config.get("ratio", 1.0)
    assert result == 0.5
    assert isinstance(result, float)

# Good
def test_type_preservation_list():
    config = LazyConfig.from_dict({"items": [1, 2, 3]})
    result = config.get("items", [])
    assert result == [1, 2, 3]
    assert isinstance(result, list)

# Good
def test_type_preservation_bool():
    config = LazyConfig.from_dict({"enabled": True})
    result = config.get("enabled", False)
    assert result is True


# ---------------------------------------------------------------------------
# TypeError when get(key, default) lands on a sub-config
# ---------------------------------------------------------------------------

# Good
def test_get_with_default_on_sub_config_raises():
    config = LazyConfig.from_dict({"model": {"layers": 4}})
    with pytest.raises(TypeError):
        config.get("model", {})


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
    config = LazyConfig.from_yaml(path)
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
    config = LazyConfig.from_yaml(path)
    assert config.get(0).get("name") == "Alice"
    assert config.get(1).get("name") == "Bob"
    assert config.get(2).get("city") == "Sydney"


def test_top_level_list_integer_index_returns_lazy_config(tmp_path):
    path = write_yaml(tmp_path, PEOPLE_YAML)
    config = LazyConfig.from_yaml(path)
    alice = config.get(0)
    assert isinstance(alice, LazyConfig)


def test_top_level_list_leaf_values(tmp_path):
    path = write_yaml(tmp_path, PEOPLE_YAML)
    config = LazyConfig.from_yaml(path)
    assert config.get(0).get("age") == 30
    assert isinstance(config.get(0).get("age"), int)


def test_top_level_list_out_of_bounds_returns_ghost(tmp_path):
    path = write_yaml(tmp_path, PEOPLE_YAML)
    config = LazyConfig.from_yaml(path)
    ghost = config.get(99)
    assert isinstance(ghost, LazyConfig)
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


def test_iteration_yields_lazy_config_for_dict_elements(tmp_path):
    path = write_yaml(tmp_path, LAYERS_YAML)
    config = LazyConfig.from_yaml(path)
    for layer_config in config.get("layers"):
        assert isinstance(layer_config, LazyConfig)
        assert layer_config.get("norm") in ("BatchNorm", "LayerNorm")


def test_iteration_correct_values(tmp_path):
    path = write_yaml(tmp_path, LAYERS_YAML)
    config = LazyConfig.from_yaml(path)
    sizes = [layer.get("size") for layer in config.get("layers")]
    assert sizes == [64, 128, 256]


def test_iteration_length(tmp_path):
    path = write_yaml(tmp_path, LAYERS_YAML)
    config = LazyConfig.from_yaml(path)
    assert len(list(config.get("layers"))) == 3


def test_iteration_over_scalar_list_yields_plain_values():
    config = LazyConfig.from_dict({"tags": ["a", "b", "c"]})
    assert list(config.get("tags")) == ["a", "b", "c"]


def test_iteration_over_non_list_raises():
    config = LazyConfig.from_dict({"model": {"layers": 4}})
    with pytest.raises(TypeError):
        list(config.get("model"))


def test_get_no_default_on_scalar_returns_value():
    config = LazyConfig.from_dict({"learning_rate": 0.001})
    assert config.get("learning_rate") == 0.001


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
    config = LazyConfig.from_yaml(path)

    for person in config.get("people"):
        assert isinstance(person, LazyConfig)
        age = person.get("age", 42)
        assert age == 42

    with pytest.raises(MissingConfigError) as exc_info:
        config.check()
    message = str(exc_info.value)
    assert "people.0.age" in message
    assert "people.1.age" in message


def test_ghost_list_index_access_records_correct_paths():
    """'people' key is entirely absent; index access into the ghost records paths."""
    config = LazyConfig.from_dict({})
    people = config.get("people")
    assert isinstance(people, LazyConfig)

    for index in range(2):
        person = people.get(index)
        assert isinstance(person, LazyConfig)
        age = person.get("age", 42)
        assert age == 42

    with pytest.raises(MissingConfigError) as exc_info:
        config.check()
    message = str(exc_info.value)
    assert "people.0.age" in message
    assert "people.1.age" in message


def test_ghost_list_iter_yields_two_ghost_sub_configs():
    """Iterating a ghost LazyConfig yields exactly two ghost sub-configs."""
    config = LazyConfig.from_dict({})
    items = list(config.get("people"))
    assert len(items) == 2
    for item in items:
        assert isinstance(item, LazyConfig)

def test_get_with_list_default_records_key_as_missing():
    """get("people", []) when people is absent records the key itself as missing."""
    config = LazyConfig.from_dict({})
    result = config.get("people", [])
    assert result == []

    with pytest.raises(MissingConfigError) as exc_info:
        config.check()
    message = str(exc_info.value)
    assert "people" in message


def test_ghost_list_iter_records_missing_sub_fields():
    """Iterating a ghost with a for-loop records people.0.age and people.1.age."""
    config = LazyConfig.from_dict({})
    for person in config.get("people"):
        assert isinstance(person, LazyConfig)
        age = person.get("age", 42)
        assert age == 42

    with pytest.raises(MissingConfigError) as exc_info:
        config.check()
    message = str(exc_info.value)
    assert "people.0.age" in message
    assert "people.1.age" in message
    

# ---------------------------------------------------------------------------
# Public API surface
# ---------------------------------------------------------------------------


def test_module_exports_lazy_config():
    assert hasattr(lazy_config, "LazyConfig")


def test_module_exports_missing_config_error():
    assert hasattr(lazy_config, "MissingConfigError")
