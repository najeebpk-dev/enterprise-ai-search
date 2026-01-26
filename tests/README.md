# Tests

This directory contains unit and integration tests for the Enterprise AI Search project.

## Running Tests

### Install Development Dependencies

```bash
pip install -r requirements-dev.txt
```

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=src --cov-report=html
```

### Run Specific Test File

```bash
pytest tests/test_basic.py -v
```

## Test Structure

- `test_basic.py` - Basic unit tests for core functionality
- Integration tests are marked with `@pytest.mark.integration` and skipped by default

## Adding Tests

When adding new features, please include:
1. Unit tests for individual functions
2. Integration tests for end-to-end workflows (mark with `@pytest.mark.integration`)
3. Mock external dependencies (Azure APIs) in unit tests
