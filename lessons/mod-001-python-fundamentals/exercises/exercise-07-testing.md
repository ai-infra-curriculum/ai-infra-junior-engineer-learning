# Exercise 07: Unit Testing ML Utility Functions with Pytest

## Overview

This exercise teaches you how to write comprehensive unit tests for ML utility functions using pytest. You'll learn testing best practices, fixtures, mocking, parameterized tests, and how to build a robust test suite that ensures your ML infrastructure code is reliable and maintainable.

## Learning Objectives

By completing this exercise, you will:
- Write effective unit tests with pytest
- Use fixtures for test setup and teardown
- Implement parameterized tests for multiple scenarios
- Mock external dependencies and file I/O
- Test error handling and edge cases
- Measure test coverage
- Write tests for async functions
- Follow testing best practices for ML code
- Build a CI-ready test suite

## Prerequisites

- Completed Exercises 01-06
- Understanding of ML utility functions
- Installed pytest and pytest-cov

## Time Required

- Estimated: 100-120 minutes
- Difficulty: Intermediate

## Part 1: Pytest Basics

### Step 1: Your First Tests

```python
# Create a file: tests/test_basics.py

import pytest

# Simple function to test
def calculate_accuracy(predictions: list, labels: list) -> float:
    """Calculate classification accuracy"""
    if len(predictions) != len(labels):
        raise ValueError("Predictions and labels must have same length")

    if not predictions:
        return 0.0

    correct = sum(p == l for p, l in zip(predictions, labels))
    return correct / len(predictions)

# Tests
def test_accuracy_perfect():
    """Test perfect accuracy"""
    preds = [1, 0, 1, 1]
    labels = [1, 0, 1, 1]
    assert calculate_accuracy(preds, labels) == 1.0

def test_accuracy_zero():
    """Test zero accuracy"""
    preds = [1, 1, 1, 1]
    labels = [0, 0, 0, 0]
    assert calculate_accuracy(preds, labels) == 0.0

def test_accuracy_half():
    """Test 50% accuracy"""
    preds = [1, 0, 1, 0]
    labels = [1, 1, 0, 0]
    assert calculate_accuracy(preds, labels) == 0.5

def test_accuracy_empty():
    """Test empty inputs"""
    assert calculate_accuracy([], []) == 0.0

def test_accuracy_length_mismatch():
    """Test mismatched lengths"""
    with pytest.raises(ValueError, match="same length"):
        calculate_accuracy([1, 0], [1])

# Run tests: pytest tests/test_basics.py -v
```

### Step 2: Using Fixtures

```python
# Create a file: tests/test_fixtures.py

import pytest
from typing import List, Dict

# Sample data fixtures
@pytest.fixture
def sample_predictions():
    """Fixture providing sample predictions"""
    return [1, 0, 1, 1, 0, 1, 0, 0]

@pytest.fixture
def sample_labels():
    """Fixture providing sample labels"""
    return [1, 0, 1, 0, 0, 1, 0, 1]

@pytest.fixture
def sample_dataset():
    """Fixture providing sample dataset"""
    return [
        {"id": 1, "features": [1.0, 2.0], "label": 0},
        {"id": 2, "features": [2.0, 3.0], "label": 1},
        {"id": 3, "features": [3.0, 4.0], "label": 0},
    ]

@pytest.fixture
def temp_model_file(tmp_path):
    """Fixture providing temporary model file"""
    model_file = tmp_path / "model.txt"
    model_file.write_text("model_weights")
    return model_file

# Tests using fixtures
def test_with_fixtures(sample_predictions, sample_labels):
    """Test using fixtures"""
    from test_basics import calculate_accuracy

    accuracy = calculate_accuracy(sample_predictions, sample_labels)
    assert 0.0 <= accuracy <= 1.0

def test_dataset_size(sample_dataset):
    """Test dataset fixture"""
    assert len(sample_dataset) == 3
    assert all("features" in item for item in sample_dataset)

def test_temp_file(temp_model_file):
    """Test temporary file fixture"""
    assert temp_model_file.exists()
    assert temp_model_file.read_text() == "model_weights"

# Parametrized fixtures
@pytest.fixture(params=[16, 32, 64])
def batch_sizes(request):
    """Fixture providing different batch sizes"""
    return request.param

def test_batch_processing(batch_sizes):
    """Test with different batch sizes"""
    assert batch_sizes in [16, 32, 64]
    # Test your batch processing logic here
```

### Step 3: Parametrized Tests

```python
# Create a file: tests/test_parametrized.py

import pytest

def normalize_value(value: float, min_val: float, max_val: float) -> float:
    """Normalize value to [0, 1] range"""
    if max_val == min_val:
        return 0.0
    return (value - min_val) / (max_val - min_val)

# Parametrize with test cases
@pytest.mark.parametrize("value,min_val,max_val,expected", [
    (5, 0, 10, 0.5),      # Middle value
    (0, 0, 10, 0.0),      # Min value
    (10, 0, 10, 1.0),     # Max value
    (7.5, 0, 10, 0.75),   # Three quarters
    (2.5, 0, 10, 0.25),   # One quarter
])
def test_normalize(value, min_val, max_val, expected):
    """Test normalization with various inputs"""
    result = normalize_value(value, min_val, max_val)
    assert abs(result - expected) < 1e-6

@pytest.mark.parametrize("value,min_val,max_val", [
    (5, 5, 5),   # All same
    (0, 0, 0),   # All zeros
])
def test_normalize_edge_cases(value, min_val, max_val):
    """Test edge cases"""
    result = normalize_value(value, min_val, max_val)
    assert result == 0.0

# Multiple parameters
@pytest.mark.parametrize("batch_size", [16, 32, 64])
@pytest.mark.parametrize("num_samples", [100, 500, 1000])
def test_batch_combinations(batch_size, num_samples):
    """Test all combinations of batch size and samples"""
    num_batches = (num_samples + batch_size - 1) // batch_size
    assert num_batches > 0
    assert num_batches <= (num_samples // batch_size) + 1
```

## Part 2: Testing ML Functions

### Step 4: Testing Data Processing

```python
# Create a file: src/preprocessing.py (if not exists)

from typing import List, Optional

def remove_outliers(data: List[float], threshold: float = 1.5) -> List[float]:
    """Remove outliers using IQR method"""
    if len(data) < 4:
        return data

    sorted_data = sorted(data)
    q1_idx = len(sorted_data) // 4
    q3_idx = 3 * len(sorted_data) // 4

    q1 = sorted_data[q1_idx]
    q3 = sorted_data[q3_idx]
    iqr = q3 - q1

    lower = q1 - threshold * iqr
    upper = q3 + threshold * iqr

    return [x for x in data if lower <= x <= upper]

def fill_missing(data: List[Optional[float]], strategy: str = "mean") -> List[float]:
    """Fill missing values"""
    valid = [x for x in data if x is not None]

    if not valid:
        return [0.0] * len(data)

    if strategy == "mean":
        fill_value = sum(valid) / len(valid)
    elif strategy == "median":
        sorted_valid = sorted(valid)
        mid = len(sorted_valid) // 2
        fill_value = sorted_valid[mid]
    else:
        raise ValueError(f"Unknown strategy: {strategy}")

    return [x if x is not None else fill_value for x in data]

# Create a file: tests/test_preprocessing.py

import pytest
from src.preprocessing import remove_outliers, fill_missing

class TestRemoveOutliers:
    """Test suite for outlier removal"""

    def test_no_outliers(self):
        """Test data without outliers"""
        data = [1, 2, 3, 4, 5]
        result = remove_outliers(data)
        assert len(result) == len(data)

    def test_with_outliers(self):
        """Test data with outliers"""
        data = [1, 2, 3, 4, 5, 100]
        result = remove_outliers(data)
        assert 100 not in result
        assert len(result) < len(data)

    def test_small_dataset(self):
        """Test dataset smaller than required"""
        data = [1, 2, 3]
        result = remove_outliers(data)
        assert result == data

    def test_empty_dataset(self):
        """Test empty dataset"""
        result = remove_outliers([])
        assert result == []

    @pytest.mark.parametrize("threshold", [1.0, 1.5, 2.0, 3.0])
    def test_different_thresholds(self, threshold):
        """Test various thresholds"""
        data = [1, 2, 3, 4, 5, 100]
        result = remove_outliers(data, threshold=threshold)
        assert len(result) <= len(data)

class TestFillMissing:
    """Test suite for missing value handling"""

    def test_fill_with_mean(self):
        """Test mean strategy"""
        data = [1.0, 2.0, None, 4.0]
        result = fill_missing(data, strategy="mean")
        assert len(result) == len(data)
        assert None not in result

    def test_fill_with_median(self):
        """Test median strategy"""
        data = [1.0, 2.0, None, 4.0, 5.0]
        result = fill_missing(data, strategy="median")
        assert len(result) == len(data)
        assert result[2] == 3.0  # Median of [1,2,4,5]

    def test_all_missing(self):
        """Test all values missing"""
        data = [None, None, None]
        result = fill_missing(data)
        assert result == [0.0, 0.0, 0.0]

    def test_no_missing(self):
        """Test no missing values"""
        data = [1.0, 2.0, 3.0]
        result = fill_missing(data)
        assert result == data

    def test_invalid_strategy(self):
        """Test invalid strategy"""
        with pytest.raises(ValueError, match="Unknown strategy"):
            fill_missing([1.0, None], strategy="invalid")
```

### Step 5: Testing with Mocks

```python
# Create a file: tests/test_mocking.py

import pytest
from unittest.mock import Mock, patch, mock_open
import json

# Function to test
def load_model_config(filepath: str) -> dict:
    """Load model configuration from file"""
    with open(filepath, 'r') as f:
        config = json.load(f)
    return config

def download_model(url: str) -> dict:
    """Download model from URL"""
    import requests
    response = requests.get(url)
    return response.json()

# Tests with mocking
def test_load_config_mock():
    """Test config loading with mock"""
    mock_config = {"model": "resnet", "lr": 0.001}
    mock_data = json.dumps(mock_config)

    with patch("builtins.open", mock_open(read_data=mock_data)):
        config = load_model_config("config.json")
        assert config == mock_config

def test_download_model_mock():
    """Test model download with mock"""
    mock_response = Mock()
    mock_response.json.return_value = {"model": "downloaded"}

    with patch("requests.get", return_value=mock_response):
        result = download_model("https://example.com/model")
        assert result == {"model": "downloaded"}

@patch("os.path.exists")
def test_file_exists_mock(mock_exists):
    """Test file existence check with mock"""
    mock_exists.return_value = True

    import os
    assert os.path.exists("/fake/path")
    mock_exists.assert_called_once_with("/fake/path")

# Mock class
class MockModel:
    """Mock model for testing"""

    def predict(self, data):
        return [0.9] * len(data)

    def save(self, path):
        pass

def test_with_mock_model():
    """Test using mock model"""
    model = MockModel()
    predictions = model.predict([1, 2, 3])
    assert len(predictions) == 3
    assert all(p == 0.9 for p in predictions)
```

### Step 6: Testing Error Handling

```python
# Create a file: tests/test_error_handling.py

import pytest
from src.preprocessing import fill_missing, remove_outliers

def validate_batch_size(batch_size: int) -> None:
    """Validate batch size"""
    if not isinstance(batch_size, int):
        raise TypeError("Batch size must be integer")

    if batch_size <= 0:
        raise ValueError("Batch size must be positive")

    if batch_size > 1024:
        raise ValueError("Batch size too large")

class TestErrorHandling:
    """Test error handling"""

    def test_type_error(self):
        """Test TypeError is raised"""
        with pytest.raises(TypeError, match="must be integer"):
            validate_batch_size("32")

    def test_value_error_negative(self):
        """Test ValueError for negative value"""
        with pytest.raises(ValueError, match="must be positive"):
            validate_batch_size(-1)

    def test_value_error_too_large(self):
        """Test ValueError for large value"""
        with pytest.raises(ValueError, match="too large"):
            validate_batch_size(2048)

    def test_valid_batch_size(self):
        """Test valid batch size"""
        validate_batch_size(32)  # Should not raise

    @pytest.mark.parametrize("invalid_value", [-1, 0, 2048, "32", 32.5, None])
    def test_invalid_values(self, invalid_value):
        """Test various invalid values"""
        with pytest.raises((TypeError, ValueError)):
            validate_batch_size(invalid_value)

    @pytest.mark.parametrize("valid_value", [1, 16, 32, 64, 128, 256, 512, 1024])
    def test_valid_values(self, valid_value):
        """Test various valid values"""
        validate_batch_size(valid_value)  # Should not raise
```

## Part 3: Testing Async Code

### Step 7: Async Tests

```python
# Create a file: tests/test_async.py

import pytest
import asyncio

# Async functions to test
async def async_process_sample(sample_id: int) -> dict:
    """Process sample asynchronously"""
    await asyncio.sleep(0.01)
    return {"id": sample_id, "processed": True}

async def async_batch_process(batch: list) -> list:
    """Process batch asynchronously"""
    tasks = [async_process_sample(sid) for sid in batch]
    return await asyncio.gather(*tasks)

# Async tests
@pytest.mark.asyncio
async def test_async_single_sample():
    """Test async single sample processing"""
    result = await async_process_sample(1)
    assert result["id"] == 1
    assert result["processed"] is True

@pytest.mark.asyncio
async def test_async_batch():
    """Test async batch processing"""
    batch = [1, 2, 3, 4, 5]
    results = await async_batch_process(batch)

    assert len(results) == len(batch)
    assert all(r["processed"] for r in results)
    assert [r["id"] for r in results] == batch

@pytest.mark.asyncio
async def test_async_error_handling():
    """Test async error handling"""
    async def failing_function():
        await asyncio.sleep(0.01)
        raise ValueError("Test error")

    with pytest.raises(ValueError, match="Test error"):
        await failing_function()

# Fixtures for async tests
@pytest.fixture
async def async_sample_data():
    """Async fixture"""
    await asyncio.sleep(0.01)
    return {"samples": [1, 2, 3]}

@pytest.mark.asyncio
async def test_with_async_fixture(async_sample_data):
    """Test using async fixture"""
    assert "samples" in async_sample_data
    assert len(async_sample_data["samples"]) == 3
```

## Part 4: Test Coverage

### Step 8: Measuring Coverage

```python
# Create a file: tests/test_coverage_example.py

import pytest

def complex_function(x: int) -> str:
    """Function with multiple branches"""
    if x < 0:
        return "negative"
    elif x == 0:
        return "zero"
    elif x < 10:
        return "small"
    elif x < 100:
        return "medium"
    else:
        return "large"

# Tests covering all branches
@pytest.mark.parametrize("value,expected", [
    (-5, "negative"),
    (0, "zero"),
    (5, "small"),
    (50, "medium"),
    (150, "large"),
])
def test_complex_function(value, expected):
    """Test all branches"""
    assert complex_function(value) == expected

# Run with coverage:
# pytest tests/test_coverage_example.py --cov=. --cov-report=html
# pytest tests/test_coverage_example.py --cov=. --cov-report=term-missing
```

## Part 5: Integration Tests

### Step 9: Testing Complete Workflows

```python
# Create a file: tests/test_integration.py

import pytest
from typing import List, Dict

class DataPipeline:
    """Simple data pipeline for testing"""

    def __init__(self):
        self.data = []

    def load(self, samples: List[dict]) -> None:
        """Load data"""
        if not samples:
            raise ValueError("No samples provided")
        self.data = samples

    def preprocess(self) -> None:
        """Preprocess data"""
        if not self.data:
            raise RuntimeError("No data loaded")

        for sample in self.data:
            sample['preprocessed'] = True

    def validate(self) -> bool:
        """Validate data"""
        return all(s.get('preprocessed', False) for s in self.data)

    def get_summary(self) -> dict:
        """Get pipeline summary"""
        return {
            "total_samples": len(self.data),
            "preprocessed": sum(1 for s in self.data if s.get('preprocessed')),
        }

class TestDataPipelineIntegration:
    """Integration tests for data pipeline"""

    @pytest.fixture
    def pipeline(self):
        """Pipeline fixture"""
        return DataPipeline()

    @pytest.fixture
    def sample_data(self):
        """Sample data fixture"""
        return [
            {"id": 1, "value": 10},
            {"id": 2, "value": 20},
            {"id": 3, "value": 30},
        ]

    def test_complete_workflow(self, pipeline, sample_data):
        """Test complete pipeline workflow"""
        # Load
        pipeline.load(sample_data)
        assert len(pipeline.data) == 3

        # Preprocess
        pipeline.preprocess()
        assert pipeline.validate()

        # Summary
        summary = pipeline.get_summary()
        assert summary["total_samples"] == 3
        assert summary["preprocessed"] == 3

    def test_empty_load(self, pipeline):
        """Test loading empty data"""
        with pytest.raises(ValueError, match="No samples"):
            pipeline.load([])

    def test_preprocess_without_load(self, pipeline):
        """Test preprocessing without loading"""
        with pytest.raises(RuntimeError, match="No data loaded"):
            pipeline.preprocess()

    def test_validation_fails(self, pipeline, sample_data):
        """Test validation without preprocessing"""
        pipeline.load(sample_data)
        assert not pipeline.validate()
```

## Part 6: Test Organization

### Step 10: Organizing Your Test Suite

```python
# Create a file: conftest.py (pytest configuration)

import pytest
import os

# Session-scoped fixtures
@pytest.fixture(scope="session")
def test_data_dir(tmp_path_factory):
    """Create temporary test data directory"""
    data_dir = tmp_path_factory.mktemp("test_data")
    return data_dir

@pytest.fixture(scope="session")
def sample_config():
    """Provide test configuration"""
    return {
        "batch_size": 32,
        "learning_rate": 0.001,
        "epochs": 10,
    }

# Module-scoped fixtures
@pytest.fixture(scope="module")
def large_dataset():
    """Generate large dataset (expensive operation)"""
    return [{"id": i, "value": i * 2} for i in range(10000)]

# Pytest markers
def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow"
    )
    config.addinivalue_line(
        "markers", "integration: marks integration tests"
    )
    config.addinivalue_line(
        "markers", "gpu: marks tests requiring GPU"
    )

# Run slow tests: pytest -m slow
# Skip slow tests: pytest -m "not slow"
# Run integration tests: pytest -m integration
```

```python
# Create a file: tests/test_markers.py

import pytest
import time

@pytest.mark.slow
def test_slow_operation():
    """Slow test example"""
    time.sleep(2)
    assert True

@pytest.mark.integration
def test_integration():
    """Integration test example"""
    # Test that combines multiple components
    assert True

@pytest.mark.gpu
@pytest.mark.skipif(not os.path.exists("/dev/nvidia0"),
                   reason="GPU not available")
def test_gpu_operation():
    """Test requiring GPU"""
    # GPU-specific test
    pass

@pytest.mark.parametrize("size", [100, 1000, 10000])
@pytest.mark.slow
def test_large_dataset(size):
    """Test with various dataset sizes"""
    data = list(range(size))
    assert len(data) == size
```

## Validation

```python
# Create a file: tests/test_validation.py

def test_all_tests_run():
    """Meta-test to ensure test discovery works"""
    assert True

def test_fixtures_available(sample_config):
    """Test that fixtures are available"""
    assert "batch_size" in sample_config

def test_parametrize_works():
    """Test parametrize decorator"""
    @pytest.mark.parametrize("x", [1, 2, 3])
    def inner_test(x):
        assert x > 0

    # Pytest will discover and run this
    assert True

# Run all tests: pytest tests/ -v
# Run with coverage: pytest tests/ --cov=src --cov-report=html
# Run only fast tests: pytest -m "not slow"
# Run specific file: pytest tests/test_basics.py
```

## Best Practices Summary

```python
# Create a file: TESTING_GUIDELINES.md

"""
# ML Testing Best Practices

## Test Structure
- Arrange: Set up test data and conditions
- Act: Execute the function being tested
- Assert: Verify the results

## Naming Conventions
- test_<function>_<scenario>
- Example: test_normalize_empty_list()

## What to Test
✓ Happy path (normal operation)
✓ Edge cases (empty, None, extremes)
✓ Error conditions
✓ Boundary values
✓ Different data types

## Fixtures
- Use for common test data
- Scope appropriately (function, module, session)
- Keep fixtures simple and focused

## Parametrization
- Test multiple scenarios efficiently
- Good for testing ranges of values
- Reduces code duplication

## Mocking
- Mock external dependencies (APIs, files, databases)
- Mock expensive operations (model training)
- Don't mock what you're testing

## Coverage
- Aim for >80% coverage
- 100% coverage doesn't guarantee correctness
- Focus on critical paths

## Test Organization
tests/
  conftest.py              # Shared fixtures
  test_preprocessing.py    # Unit tests
  test_integration.py      # Integration tests
  test_e2e.py             # End-to-end tests

## CI Integration
- Run tests on every commit
- Run slow tests nightly
- Fail builds on test failures
- Track coverage trends
"""
```

## Reflection Questions

1. What makes a good unit test?
2. When should you use mocks vs real objects?
3. How much test coverage is enough?
4. What's the difference between unit and integration tests?
5. How do you test ML model predictions?
6. When should tests be skipped vs fixed?
7. How do you maintain tests as code evolves?

## Next Steps

- **Module 002**: Linux Essentials
- **Project 01**: Build tested ML pipeline
- Set up CI/CD with automated testing

## Additional Resources

- Pytest Documentation: https://docs.pytest.org/
- Test-Driven Development: https://testdriven.io/
- Coverage.py: https://coverage.readthedocs.io/
- Mock Documentation: https://docs.python.org/3/library/unittest.mock.html

---

**Congratulations!** You've mastered unit testing for ML utilities. You can now write comprehensive test suites that ensure your ML infrastructure code is reliable and maintainable.
