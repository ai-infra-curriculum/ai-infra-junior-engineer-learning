# Lecture 04: Testing, Async Programming & Code Quality

## Table of Contents
1. [Introduction](#introduction)
2. [Asynchronous Programming in Python](#asynchronous-programming-in-python)
3. [Testing with pytest](#testing-with-pytest)
4. [Code Quality & Tooling](#code-quality--tooling)
5. [Summary](#summary)

---

## Introduction

This lecture covers three critical topics for professional Python development in AI infrastructure:

1. **Asynchronous Programming**: Writing concurrent code using `async`/`await` for handling I/O-bound operations efficiently
2. **Testing**: Building comprehensive test suites using pytest to ensure code reliability
3. **Code Quality**: Using linters, formatters, and type checkers to maintain professional standards

These skills are essential for building production-grade AI infrastructure systems that are reliable, maintainable, and performant.

### Why These Topics Matter

**In AI Infrastructure**:
- **Async Programming**: Handle multiple API requests, database queries, or model serving calls concurrently
- **Testing**: Ensure infrastructure code works correctly before deploying to production
- **Code Quality**: Maintain codebases that multiple engineers can work on effectively

---

## Asynchronous Programming in Python

### Understanding Async/Await

**Asynchronous programming** allows you to write concurrent code that can handle multiple operations without blocking. This is crucial for I/O-bound operations like:
- Making HTTP API calls
- Reading/writing to databases
- File I/O operations
- Network communication

### When to Use Async

✅ **Use Async For**:
- I/O-bound operations (network calls, file operations, database queries)
- Handling many concurrent connections (web servers, API gateways)
- Long-running operations that wait on external systems

❌ **Don't Use Async For**:
- CPU-bound operations (use multiprocessing instead)
- Simple scripts without concurrent operations
- Code that doesn't involve waiting

### Basic Async Syntax

```python
import asyncio

# Define an async function with 'async def'
async def fetch_data(url: str) -> dict:
    """Async function to fetch data from URL"""
    await asyncio.sleep(1)  # Simulate network delay
    return {"url": url, "data": "sample data"}

# Run async function
async def main():
    result = await fetch_data("https://api.example.com/data")
    print(result)

# Execute the async code
if __name__ == "__main__":
    asyncio.run(main())
```

**Key Concepts**:
- `async def`: Defines a coroutine function
- `await`: Pauses execution until the awaited operation completes
- `asyncio.run()`: Entry point for running async code

### Running Multiple Tasks Concurrently

The power of async is running multiple operations at once:

```python
import asyncio
from typing import List

async def fetch_model_metadata(model_id: str) -> dict:
    """Fetch metadata for a single model"""
    await asyncio.sleep(0.5)  # Simulate API call
    return {
        "model_id": model_id,
        "version": "1.0",
        "accuracy": 0.95
    }

async def fetch_all_models(model_ids: List[str]) -> List[dict]:
    """Fetch metadata for multiple models concurrently"""
    # Create tasks for all models
    tasks = [fetch_model_metadata(mid) for mid in model_ids]

    # Run all tasks concurrently
    results = await asyncio.gather(*tasks)
    return results

async def main():
    model_ids = [f"model-{i}" for i in range(5)]

    # Sequential execution (slow)
    print("Sequential execution:")
    import time
    start = time.time()
    results = []
    for mid in model_ids:
        result = await fetch_model_metadata(mid)
        results.append(result)
    print(f"Time: {time.time() - start:.2f}s")  # ~2.5 seconds

    # Concurrent execution (fast)
    print("\nConcurrent execution:")
    start = time.time()
    results = await fetch_all_models(model_ids)
    print(f"Time: {time.time() - start:.2f}s")  # ~0.5 seconds

if __name__ == "__main__":
    asyncio.run(main())
```

### Async with HTTP Requests

Using `httpx` for async HTTP calls:

```python
import asyncio
import httpx
from typing import List, Dict

async def check_model_health(endpoint: str) -> Dict[str, str]:
    """Check if a model serving endpoint is healthy"""
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.get(f"{endpoint}/health")
            return {
                "endpoint": endpoint,
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_time": response.elapsed.total_seconds()
            }
        except Exception as e:
            return {
                "endpoint": endpoint,
                "status": "error",
                "error": str(e)
            }

async def monitor_models(endpoints: List[str]) -> List[Dict]:
    """Monitor multiple model endpoints concurrently"""
    tasks = [check_model_health(ep) for ep in endpoints]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results

# Usage
async def main():
    endpoints = [
        "http://model1.example.com",
        "http://model2.example.com",
        "http://model3.example.com"
    ]

    health_status = await monitor_models(endpoints)
    for status in health_status:
        print(f"{status['endpoint']}: {status['status']}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Error Handling in Async Code

```python
import asyncio
from typing import Optional

async def fetch_with_retry(url: str, max_retries: int = 3) -> Optional[dict]:
    """Fetch data with retry logic"""
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException:
            print(f"Timeout on attempt {attempt + 1}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        except httpx.HTTPError as e:
            print(f"HTTP error: {e}")
            return None

    return None  # All retries failed
```

### Async Context Managers

```python
import asyncio
from typing import AsyncGenerator

class AsyncModelClient:
    """Async client for ML model serving"""

    async def __aenter__(self):
        """Setup when entering context"""
        self.client = httpx.AsyncClient()
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup when exiting context"""
        await self.disconnect()
        await self.client.aclose()

    async def connect(self):
        """Establish connection"""
        await asyncio.sleep(0.1)  # Simulate connection
        print("Connected to model server")

    async def disconnect(self):
        """Close connection"""
        await asyncio.sleep(0.1)
        print("Disconnected from model server")

    async def predict(self, data: dict) -> dict:
        """Make prediction"""
        response = await self.client.post(
            "http://model.example.com/predict",
            json=data
        )
        return response.json()

# Usage
async def main():
    async with AsyncModelClient() as client:
        result = await client.predict({"features": [1, 2, 3]})
        print(result)
```

### Async Generators

```python
import asyncio
from typing import AsyncGenerator

async def stream_training_logs(job_id: str) -> AsyncGenerator[str, None]:
    """Stream training logs asynchronously"""
    for i in range(10):
        await asyncio.sleep(0.5)
        yield f"[{job_id}] Epoch {i+1}/10 - loss: {1.0/(i+1):.4f}"

async def monitor_training():
    """Monitor training job logs"""
    async for log_line in stream_training_logs("job-123"):
        print(log_line)

if __name__ == "__main__":
    asyncio.run(monitor_training())
```

### Common Async Patterns for AI Infrastructure

#### Pattern 1: Concurrent Model Deployment

```python
import asyncio
from typing import List

async def deploy_model(model_id: str, environment: str) -> dict:
    """Deploy a single model"""
    print(f"Deploying {model_id} to {environment}...")
    await asyncio.sleep(2)  # Simulate deployment time
    return {
        "model_id": model_id,
        "environment": environment,
        "status": "deployed"
    }

async def deploy_multiple_models(
    models: List[str],
    environment: str
) -> List[dict]:
    """Deploy multiple models concurrently"""
    tasks = [deploy_model(mid, environment) for mid in models]
    return await asyncio.gather(*tasks)
```

#### Pattern 2: Async Data Pipeline

```python
import asyncio
from typing import List, Dict

async def fetch_training_data(source: str) -> List[Dict]:
    """Fetch training data from source"""
    await asyncio.sleep(1)
    return [{"id": i, "features": [i]*10} for i in range(100)]

async def preprocess_batch(batch: List[Dict]) -> List[Dict]:
    """Preprocess a batch of data"""
    await asyncio.sleep(0.5)
    return [{"id": item["id"], "processed": True} for item in batch]

async def save_to_storage(data: List[Dict]) -> None:
    """Save processed data to storage"""
    await asyncio.sleep(0.3)
    print(f"Saved {len(data)} records")

async def data_pipeline():
    """Execute data pipeline with async operations"""
    # Fetch data
    raw_data = await fetch_training_data("s3://bucket/data")

    # Preprocess in batches concurrently
    batch_size = 25
    batches = [raw_data[i:i+batch_size] for i in range(0, len(raw_data), batch_size)]
    processed_batches = await asyncio.gather(*[preprocess_batch(b) for b in batches])

    # Flatten results
    processed_data = [item for batch in processed_batches for item in batch]

    # Save
    await save_to_storage(processed_data)
```

---

## Testing with pytest

### Why Testing Matters

**Testing in AI Infrastructure**:
- Catch bugs before deployment
- Ensure infrastructure changes don't break existing functionality
- Provide documentation through test cases
- Enable confident refactoring

### Setting Up pytest

```bash
# Install pytest and plugins
pip install pytest pytest-cov pytest-asyncio pytest-mock

# Project structure
my_project/
├── src/
│   ├── __init__.py
│   ├── models.py
│   └── deployment.py
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   └── test_deployment.py
├── pytest.ini
└── requirements-dev.txt
```

### Writing Your First Test

```python
# src/calculator.py
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

def divide(a: float, b: float) -> float:
    """Divide two numbers"""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

# tests/test_calculator.py
import pytest
from src.calculator import add, divide

def test_add_positive_numbers():
    """Test adding positive numbers"""
    assert add(2, 3) == 5

def test_add_negative_numbers():
    """Test adding negative numbers"""
    assert add(-5, 3) == -2

def test_divide_normal():
    """Test normal division"""
    assert divide(10, 2) == 5.0

def test_divide_by_zero():
    """Test that dividing by zero raises ValueError"""
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(10, 0)
```

### Test Fixtures

Fixtures provide reusable test data and setup:

```python
import pytest
from typing import Dict, List

@pytest.fixture
def sample_model_config() -> Dict:
    """Provide sample model configuration"""
    return {
        "model_name": "fraud_detector",
        "version": "1.0.0",
        "framework": "sklearn",
        "parameters": {
            "n_estimators": 100,
            "max_depth": 10
        }
    }

@pytest.fixture
def sample_training_data() -> List[Dict]:
    """Provide sample training data"""
    return [
        {"features": [1, 2, 3], "label": 0},
        {"features": [4, 5, 6], "label": 1},
        {"features": [7, 8, 9], "label": 0}
    ]

def test_model_initialization(sample_model_config):
    """Test model initialization with config"""
    from src.models import MLModel

    model = MLModel(sample_model_config)
    assert model.name == "fraud_detector"
    assert model.version == "1.0.0"

def test_model_training(sample_model_config, sample_training_data):
    """Test model training"""
    from src.models import MLModel

    model = MLModel(sample_model_config)
    result = model.train(sample_training_data)
    assert result["status"] == "success"
    assert "accuracy" in result
```

### Parametrized Tests

Test multiple scenarios with one test function:

```python
import pytest

@pytest.mark.parametrize("input_value,expected", [
    (0, "zero"),
    (1, "positive"),
    (-1, "negative"),
    (100, "positive"),
    (-50, "negative")
])
def test_classify_number(input_value, expected):
    """Test number classification"""
    from src.utils import classify_number
    assert classify_number(input_value) == expected

@pytest.mark.parametrize("model_type,framework", [
    ("classification", "sklearn"),
    ("regression", "sklearn"),
    ("neural_network", "pytorch"),
    ("ensemble", "xgboost")
])
def test_model_creation(model_type, framework):
    """Test creating different model types"""
    from src.models import create_model
    model = create_model(model_type, framework)
    assert model is not None
    assert model.model_type == model_type
```

### Testing Async Functions

```python
import pytest
import asyncio

# Mark async tests with @pytest.mark.asyncio
@pytest.mark.asyncio
async def test_async_model_prediction():
    """Test async model prediction"""
    from src.async_model import AsyncModelClient

    async with AsyncModelClient() as client:
        result = await client.predict({"features": [1, 2, 3]})
        assert "prediction" in result
        assert isinstance(result["prediction"], (int, float))

@pytest.mark.asyncio
async def test_concurrent_predictions():
    """Test multiple concurrent predictions"""
    from src.async_model import AsyncModelClient

    async with AsyncModelClient() as client:
        tasks = [
            client.predict({"features": [i, i+1, i+2]})
            for i in range(5)
        ]
        results = await asyncio.gather(*tasks)
        assert len(results) == 5
        assert all("prediction" in r for r in results)
```

### Mocking and Patching

Mock external dependencies:

```python
import pytest
from unittest.mock import Mock, patch, AsyncMock

def test_with_mock_database():
    """Test with mocked database"""
    from src.storage import DataStore

    # Create mock database connection
    mock_db = Mock()
    mock_db.query.return_value = [{"id": 1, "value": "test"}]

    store = DataStore(mock_db)
    result = store.get_all()

    assert len(result) == 1
    mock_db.query.assert_called_once()

@pytest.mark.asyncio
async def test_with_mock_api():
    """Test with mocked async API"""
    from src.api_client import ModelAPIClient

    # Create mock for async function
    mock_response = AsyncMock()
    mock_response.return_value = {"status": "success", "prediction": 0.95}

    with patch("httpx.AsyncClient.post", mock_response):
        client = ModelAPIClient()
        result = await client.predict({"features": [1, 2, 3]})
        assert result["status"] == "success"
```

### Testing Exceptions and Errors

```python
import pytest

def test_invalid_model_config():
    """Test that invalid config raises ValueError"""
    from src.models import MLModel

    invalid_config = {"model_name": ""}  # Empty name

    with pytest.raises(ValueError, match="model_name cannot be empty"):
        MLModel(invalid_config)

def test_model_prediction_with_invalid_input():
    """Test prediction with invalid input shape"""
    from src.models import MLModel

    model = MLModel({"model_name": "test", "input_dim": 10})

    # Input has wrong dimension
    with pytest.raises(ValueError, match="Expected 10 features"):
        model.predict([1, 2, 3])  # Only 3 features
```

### Test Coverage

```bash
# Run tests with coverage
pytest --cov=src --cov-report=html --cov-report=term

# View coverage report
# Coverage report will be in htmlcov/index.html

# Set minimum coverage requirement
pytest --cov=src --cov-fail-under=80
```

### pytest Configuration

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    asyncio: marks async tests

addopts =
    -v
    --strict-markers
    --tb=short
    --cov=src
    --cov-report=term-missing
    --cov-fail-under=70

asyncio_mode = auto
```

---

## Code Quality & Tooling

### Code Formatting with Black

**Black** is the uncompromising Python code formatter:

```bash
# Install
pip install black

# Format all Python files
black src/ tests/

# Check without modifying
black --check src/

# Format with line length limit
black --line-length 100 src/
```

**Configuration**:
```toml
# pyproject.toml
[tool.black]
line-length = 100
target-version = ['py311']
include = '\.pyi?$'
exclude = '''
/(
    \.git
  | \.venv
  | build
  | dist
)/
'''
```

### Import Sorting with isort

```bash
# Install
pip install isort

# Sort imports
isort src/ tests/

# Check without modifying
isort --check-only src/
```

**Configuration**:
```toml
# pyproject.toml
[tool.isort]
profile = "black"
line_length = 100
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
```

### Linting with Ruff

**Ruff** is a fast Python linter:

```bash
# Install
pip install ruff

# Lint code
ruff check src/ tests/

# Auto-fix issues
ruff check --fix src/

# Watch mode
ruff check --watch src/
```

**Configuration**:
```toml
# pyproject.toml
[tool.ruff]
line-length = 100
target-version = "py311"

select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]

ignore = [
    "E501",  # line too long (handled by black)
]

[tool.ruff.per-file-ignores]
"tests/*" = ["S101"]  # Allow assert in tests
```

### Type Checking with mypy

```bash
# Install
pip install mypy

# Type check code
mypy src/

# Strict mode
mypy --strict src/

# Check specific files
mypy src/models.py src/deployment.py
```

**Configuration**:
```ini
# mypy.ini
[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_any_generics = True
check_untyped_defs = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
warn_unreachable = True
strict_equality = True

[mypy-tests.*]
disallow_untyped_defs = False
```

### Pre-commit Hooks

Automate code quality checks:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### Complete Development Workflow

```bash
# 1. Format code
black src/ tests/
isort src/ tests/

# 2. Lint code
ruff check src/ tests/

# 3. Type check
mypy src/

# 4. Run tests
pytest tests/ -v --cov=src

# 5. Check coverage
pytest --cov=src --cov-report=html

# Or use Makefile
make format lint typecheck test
```

**Makefile**:
```makefile
.PHONY: format lint typecheck test quality

format:
	black src/ tests/
	isort src/ tests/

lint:
	ruff check src/ tests/

typecheck:
	mypy src/

test:
	pytest tests/ -v --cov=src

quality: format lint typecheck test
	@echo "All quality checks passed!"
```

---

## Summary

### Key Takeaways

#### Async Programming
- Use `async`/`await` for I/O-bound concurrent operations
- `asyncio.gather()` runs multiple tasks concurrently
- Async is essential for efficient API calls and database queries
- Always use `asyncio.run()` as the entry point

#### Testing
- Write tests using pytest for reliability
- Use fixtures for reusable test data
- Parametrize tests to cover multiple scenarios
- Mock external dependencies to isolate tests
- Aim for >80% code coverage
- Test async functions with `@pytest.mark.asyncio`

#### Code Quality
- **Black**: Automatic code formatting
- **isort**: Import statement organization
- **Ruff**: Fast linting with auto-fix
- **mypy**: Static type checking
- **Pre-commit hooks**: Automate quality checks

### Best Practices for AI Infrastructure

1. **Write Async Code for**:
   - Model serving APIs (multiple concurrent requests)
   - Batch inference with multiple model calls
   - Health check monitoring across services
   - Data pipeline operations

2. **Test Everything**:
   - Model deployment logic
   - Configuration parsing
   - API endpoints
   - Error handling
   - Edge cases

3. **Maintain Quality**:
   - Use formatters (no debates about style)
   - Run linters (catch bugs early)
   - Type check (document interfaces)
   - Automate with pre-commit hooks

### Next Steps

- Complete **Exercise 06: Async Programming** - Build concurrent model monitoring
- Complete **Exercise 07: Testing** - Write comprehensive test suites
- Practice using code quality tools in your projects
- Set up pre-commit hooks in all your repositories

### Additional Resources

- [asyncio Documentation](https://docs.python.org/3/library/asyncio.html)
- [pytest Documentation](https://docs.pytest.org/)
- [Real Python: Async IO](https://realpython.com/async-io-python/)
- [Black Documentation](https://black.readthedocs.io/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [mypy Documentation](https://mypy.readthedocs.io/)

---

**Module 001, Lecture 04 Complete!**

You now have the skills to:
- Write efficient async code for concurrent operations
- Build comprehensive test suites with pytest
- Maintain professional code quality standards
- Use modern Python tooling effectively

These skills form the foundation for professional AI infrastructure development.
