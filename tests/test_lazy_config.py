import lazy_config


def test_instantiate():
    config = lazy_config.LazyConfig()
    assert isinstance(config, lazy_config.LazyConfig)
