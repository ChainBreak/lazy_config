# lazy_config

A config system that is lazily validated as parameters are used.

## Installation

```bash
pip install lazy_config
```

## Usage

```python
import lazy_config

config = lazy_config.LazyConfig()
```

## Development

### Setup

```bash
pip install -e ".[dev]"
```

Or install with test dependencies:

```bash
pip install pytest
pip install -e .
```

### Running Tests

```bash
pytest
```

To run with verbose output:

```bash
pytest -v
```

## Building and Publishing to PyPI

### Prerequisites

```bash
pip install build twine
```

### Build the distribution

```bash
python -m build
```

This creates a `dist/` directory containing a `.whl` and `.tar.gz` file.

### Upload to PyPI

First, upload to [TestPyPI](https://test.pypi.org/) to verify everything looks correct:

```bash
twine upload --repository testpypi dist/*
```

When ready, upload to the real PyPI:

```bash
twine upload dist/*
```

You will be prompted for your PyPI credentials. It is recommended to use an [API token](https://pypi.org/manage/account/token/) instead of your password.

To avoid entering credentials each time, create a `~/.pypirc` file:

```ini
[pypi]
  username = __token__
  password = pypi-your-api-token-here
```
