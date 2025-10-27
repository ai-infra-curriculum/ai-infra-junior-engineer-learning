# Lecture 05: Testing with pytest & Code Quality

## Table of Contents
1. [Introduction](#introduction)
2. [Testing with pytest](#testing-with-pytest)
3. [Code Quality & Tooling](#code-quality--tooling)
4. [Summary](#summary)

---

## Introduction

This lecture covers two critical topics for professional Python development in AI infrastructure:

1. **Testing**: Building comprehensive test suites using pytest to ensure code reliability
2. **Code Quality**: Using linters, formatters, and type checkers to maintain professional standards

These skills are essential for building production-grade AI infrastructure systems that are reliable, maintainable, and performant.

### Why These Topics Matter

**In AI Infrastructure**:
- **Testing**: Ensure infrastructure code works correctly before deploying to production
- **Code Quality**: Maintain codebases that multiple engineers can work on effectively
- **Reliability**: Catch bugs early in the development cycle
- **Maintainability**: Keep code readable and consistent across the team

### Learning Objectives

By the end of this lecture, you will:
- Write comprehensive unit tests using pytest
- Use fixtures for reusable test data and setup
- Test async functions with pytest-asyncio
- Mock external dependencies to isolate tests
- Use code formatters (Black), linters (Ruff), and type checkers (mypy)
- Set up pre-commit hooks to automate quality checks
- Understand code coverage and quality metrics

This lecture builds on everything you've learned in Lectures 1-4, helping you maintain professional standards in your Python code.

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

1. **Test Everything**:
   - Model deployment logic
   - Configuration parsing
   - API endpoints
   - Error handling
   - Edge cases

2. **Maintain Quality**:
   - Use formatters (no debates about style)
   - Run linters (catch bugs early)
   - Type check (document interfaces)
   - Automate with pre-commit hooks

3. **Coverage Goals**:
   - Aim for >80% test coverage
   - Focus on critical paths first
   - Test error conditions
   - Mock external dependencies

### Completing Module 001

Congratulations! You've completed all five lectures in Module 001: Python Fundamentals for AI Infrastructure.

**You've learned**:
- Environment and dependency management (Lecture 01)
- Advanced Python patterns (Lecture 02)
- Python for DevOps operations (Lecture 03)
- Asynchronous programming (Lecture 04)
- Testing and code quality (Lecture 05)

**Next Steps**:
- Complete **Exercise 06: Async Programming** - Build concurrent model monitoring
- Complete **Exercise 07: Testing** - Write comprehensive test suites
- Practice using code quality tools in your projects
- Set up pre-commit hooks in all your repositories
- Move on to **Module 002: Linux Essentials for AI Infrastructure**

### Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Black Documentation](https://black.readthedocs.io/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [mypy Documentation](https://mypy.readthedocs.io/)
- [Real Python: Testing in Python](https://realpython.com/python-testing/)
- [Pre-commit Framework](https://pre-commit.com/)

---

**Module 001, Lecture 05 Complete!**

You now have the skills to:
- Write efficient async code for concurrent operations
- Build comprehensive test suites with pytest
- Maintain professional code quality standards
- Use modern Python tooling effectively

These skills form the foundation for professional AI infrastructure development.

**Lecture Version**: 1.0
**Last Updated**: October 2025
**Estimated Duration**: 8-10 hours
