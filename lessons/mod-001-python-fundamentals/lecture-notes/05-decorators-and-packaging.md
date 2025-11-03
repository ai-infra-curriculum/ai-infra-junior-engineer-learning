# Lecture 05: Decorators and Python Packaging for Infrastructure

## Table of Contents
1. [Introduction](#introduction)
2. [Function Decorators Fundamentals](#function-decorators-fundamentals)
3. [Practical Decorators for ML Infrastructure](#practical-decorators-for-ml-infrastructure)
4. [Class Decorators](#class-decorators)
5. [Decorator Patterns and Best Practices](#decorator-patterns-and-best-practices)
6. [Python Modules and Packages](#python-modules-and-packages)
7. [Building Reusable ML Utilities](#building-reusable-ml-utilities)
8. [Package Distribution](#package-distribution)
9. [Summary and Best Practices](#summary-and-best-practices)

---

## Introduction

### Why Decorators and Packaging Matter

As you build ML infrastructure, you'll encounter repetitive patterns:
- **Timing** how long training takes
- **Logging** function calls for debugging
- **Validating** inputs before processing
- **Caching** expensive computations
- **Retrying** failed operations

Decorators let you extract these patterns into reusable, composable utilities. Packaging lets you share these utilities across projects and teams.

### Learning Objectives

By the end of this lecture, you will:
- Understand what decorators are and how they work
- Write custom decorators for ML infrastructure tasks
- Apply built-in decorators like `@property`, `@staticmethod`, `@lru_cache`
- Structure Python packages with proper module organization
- Create reusable utility libraries for AI infrastructure
- Package and distribute Python code

---

## Function Decorators Fundamentals

### What Is a Decorator?

A decorator is a **function that takes another function and extends its behavior** without modifying its source code directly.

```python
def my_decorator(func):
    """A simple decorator that wraps a function."""
    def wrapper():
        print("Before function call")
        result = func()
        print("After function call")
        return result
    return wrapper

# Apply decorator manually
def say_hello():
    print("Hello!")

say_hello = my_decorator(say_hello)

# Usage
say_hello()
# Output:
# Before function call
# Hello!
# After function call
```

### The @ Syntax

Python provides syntactic sugar for decorators:

```python
@my_decorator
def say_hello():
    print("Hello!")

# Equivalent to:
# say_hello = my_decorator(say_hello)
```

### How Decorators Work

```python
# Step-by-step breakdown

# 1. Define decorator function
def timing_decorator(func):
    """Decorator that times function execution."""

    # 2. Define wrapper function
    def wrapper(*args, **kwargs):
        import time
        start = time.time()

        # 3. Call original function
        result = func(*args, **kwargs)

        # 4. Add behavior
        elapsed = time.time() - start
        print(f"{func.__name__} took {elapsed:.4f} seconds")

        # 5. Return result
        return result

    # 6. Return wrapper
    return wrapper

# Apply decorator
@timing_decorator
def train_model():
    import time
    time.sleep(2)  # Simulate training
    return {"accuracy": 0.92}

# Usage
metrics = train_model()
# Output: train_model took 2.0023 seconds
```

### Preserving Function Metadata

Problem: Decorators replace the original function, losing its metadata.

```python
def simple_decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@simple_decorator
def my_function():
    """This is my function."""
    pass

print(my_function.__name__)  # "wrapper" (wrong!)
print(my_function.__doc__)   # None (lost!)
```

Solution: Use `functools.wraps`

```python
from functools import wraps

def simple_decorator(func):
    @wraps(func)  # Preserves metadata
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@simple_decorator
def my_function():
    """This is my function."""
    pass

print(my_function.__name__)  # "my_function" (correct!)
print(my_function.__doc__)   # "This is my function." (preserved!)
```

**Always use `@wraps` in your decorators!**

---

## Practical Decorators for ML Infrastructure

### 1. Timing Decorator

```python
import time
from functools import wraps
from typing import Callable, Any

def timer(func: Callable) -> Callable:
    """Measure and log function execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = time.time() - start_time

        print(f"[TIMER] {func.__name__} completed in {elapsed_time:.4f}s")
        return result
    return wrapper

# Usage
@timer
def load_dataset(path: str):
    time.sleep(1)  # Simulate loading
    return {"samples": 10000}

@timer
def train_epoch(model, data):
    time.sleep(2)  # Simulate training
    return {"loss": 0.45, "accuracy": 0.85}

# Calls automatically timed
dataset = load_dataset("/data/train")
# [TIMER] load_dataset completed in 1.0012s

metrics = train_epoch(model=None, data=dataset)
# [TIMER] train_epoch completed in 2.0018s
```

### 2. Logging Decorator

```python
import logging
from functools import wraps

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_calls(func: Callable) -> Callable:
    """Log function calls with arguments and results."""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        # Log function call
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)

        logger.info(f"Calling {func.__name__}({signature})")

        try:
            result = func(*args, **kwargs)
            logger.info(f"{func.__name__} returned {result!r}")
            return result
        except Exception as e:
            logger.exception(f"{func.__name__} raised {type(e).__name__}: {e}")
            raise

    return wrapper

# Usage
@log_calls
def load_model(model_name: str, checkpoint: int = None):
    if checkpoint is None:
        raise ValueError("Checkpoint required")
    return f"Loaded {model_name} checkpoint {checkpoint}"

# Test
try:
    model = load_model("resnet50", checkpoint=100)
    # INFO: Calling load_model('resnet50', checkpoint=100)
    # INFO: load_model returned 'Loaded resnet50 checkpoint 100'
except ValueError:
    pass

try:
    model = load_model("resnet50")
    # INFO: Calling load_model('resnet50')
    # ERROR: load_model raised ValueError: Checkpoint required
except ValueError:
    pass
```

### 3. Retry Decorator

```python
import time
from functools import wraps
from typing import Callable, Type, Tuple

def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
) -> Callable:
    """Retry function on failure with exponential backoff."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            attempt = 1
            current_delay = delay

            while attempt <= max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        print(f"[RETRY] {func.__name__} failed after {max_attempts} attempts")
                        raise

                    print(f"[RETRY] {func.__name__} failed (attempt {attempt}/{max_attempts}): {e}")
                    print(f"[RETRY] Retrying in {current_delay}s...")
                    time.sleep(current_delay)

                    attempt += 1
                    current_delay *= 2  # Exponential backoff

            return None  # Should never reach here

        return wrapper
    return decorator

# Usage
import random

@retry(max_attempts=5, delay=0.5, exceptions=(ConnectionError, TimeoutError))
def download_model(url: str):
    """Simulate unreliable model download."""
    if random.random() < 0.7:  # 70% chance of failure
        raise ConnectionError("Network error")
    return f"Downloaded from {url}"

# Test
result = download_model("https://models.ai/resnet50.pth")
# [RETRY] download_model failed (attempt 1/5): Network error
# [RETRY] Retrying in 0.5s...
# [RETRY] download_model failed (attempt 2/5): Network error
# [RETRY] Retrying in 1.0s...
# Downloaded from https://models.ai/resnet50.pth
```

### 4. Validation Decorator

```python
from functools import wraps
from typing import Callable, Any

def validate_types(**type_hints) -> Callable:
    """Validate function argument types at runtime."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Get function argument names
            import inspect
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()

            # Validate types
            for param_name, expected_type in type_hints.items():
                if param_name in bound.arguments:
                    value = bound.arguments[param_name]
                    if not isinstance(value, expected_type):
                        raise TypeError(
                            f"{func.__name__}() argument '{param_name}' must be "
                            f"{expected_type.__name__}, got {type(value).__name__}"
                        )

            return func(*args, **kwargs)
        return wrapper
    return decorator

# Usage
@validate_types(learning_rate=float, batch_size=int, epochs=int)
def train_model(learning_rate, batch_size, epochs):
    print(f"Training with lr={learning_rate}, bs={batch_size}, epochs={epochs}")

# Valid call
train_model(0.001, 32, 100)
# Training with lr=0.001, bs=32, epochs=100

# Invalid call
try:
    train_model("0.001", 32, 100)  # String instead of float
except TypeError as e:
    print(e)
    # train_model() argument 'learning_rate' must be float, got str
```

### 5. Caching Decorator

```python
from functools import wraps, lru_cache
from typing import Callable

def memoize(func: Callable) -> Callable:
    """Simple memoization decorator (cache all results)."""
    cache = {}

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create cache key from arguments
        key = (args, tuple(sorted(kwargs.items())))

        if key not in cache:
            print(f"[CACHE MISS] Computing {func.__name__}{args}")
            cache[key] = func(*args, **kwargs)
        else:
            print(f"[CACHE HIT] Returning cached {func.__name__}{args}")

        return cache[key]

    # Add cache inspection methods
    wrapper.cache = cache
    wrapper.cache_clear = cache.clear

    return wrapper

# Usage
@memoize
def load_model_weights(model_name: str, checkpoint: int):
    """Simulate expensive model loading."""
    time.sleep(2)
    return f"Weights for {model_name} checkpoint {checkpoint}"

# First call: cache miss
weights1 = load_model_weights("resnet50", 100)
# [CACHE MISS] Computing load_model_weights('resnet50', 100)

# Second call: cache hit
weights2 = load_model_weights("resnet50", 100)
# [CACHE HIT] Returning cached load_model_weights('resnet50', 100)

# Different arguments: cache miss
weights3 = load_model_weights("vgg16", 50)
# [CACHE MISS] Computing load_model_weights('vgg16', 50)

# Inspect cache
print(f"Cache size: {len(load_model_weights.cache)}")  # 2
```

**Python's Built-in LRU Cache** (better for production):

```python
from functools import lru_cache

@lru_cache(maxsize=128)  # Keep up to 128 most recent results
def compute_features(sample_id: int) -> dict:
    """Compute features with automatic caching."""
    # Expensive computation
    return {"feature1": sample_id * 2, "feature2": sample_id ** 2}

# First call: computed
result1 = compute_features(42)

# Second call: cached
result2 = compute_features(42)

# Cache info
print(compute_features.cache_info())
# CacheInfo(hits=1, misses=1, maxsize=128, currsize=1)

# Clear cache
compute_features.cache_clear()
```

---

## Class Decorators

### Method Decorators

```python
class ModelTrainer:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.training_time = 0

    @timer  # Reuse our timing decorator
    def train_epoch(self, data):
        """Train one epoch."""
        time.sleep(1)
        return {"loss": 0.5, "accuracy": 0.85}

    @log_calls  # Reuse our logging decorator
    def save_checkpoint(self, path: str):
        """Save model checkpoint."""
        print(f"Saving {self.model_name} to {path}")

# Usage
trainer = ModelTrainer("resnet50")
metrics = trainer.train_epoch(data=None)
# [TIMER] train_epoch completed in 1.0015s

trainer.save_checkpoint("/checkpoints/model.pth")
# INFO: Calling save_checkpoint('/checkpoints/model.pth')
# Saving resnet50 to /checkpoints/model.pth
# INFO: save_checkpoint returned None
```

### Built-in Decorators

#### @property: Computed Attributes

```python
class ModelMetrics:
    def __init__(self, true_positives: int, false_positives: int,
                 true_negatives: int, false_negatives: int):
        self.tp = true_positives
        self.fp = false_positives
        self.tn = true_negatives
        self.fn = false_negatives

    @property
    def accuracy(self) -> float:
        """Compute accuracy on demand."""
        total = self.tp + self.fp + self.tn + self.fn
        return (self.tp + self.tn) / total if total > 0 else 0.0

    @property
    def precision(self) -> float:
        """Compute precision on demand."""
        denominator = self.tp + self.fp
        return self.tp / denominator if denominator > 0 else 0.0

    @property
    def recall(self) -> float:
        """Compute recall on demand."""
        denominator = self.tp + self.fn
        return self.tp / denominator if denominator > 0 else 0.0

    @property
    def f1_score(self) -> float:
        """Compute F1 score on demand."""
        prec = self.precision
        rec = self.recall
        return 2 * (prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0

# Usage
metrics = ModelMetrics(tp=90, fp=10, tn=85, fn=15)

# Access like attributes (no parentheses!)
print(f"Accuracy: {metrics.accuracy:.2%}")    # 87.50%
print(f"Precision: {metrics.precision:.2%}")  # 90.00%
print(f"Recall: {metrics.recall:.2%}")        # 85.71%
print(f"F1 Score: {metrics.f1_score:.3f}")    # 0.878
```

#### @staticmethod and @classmethod

```python
class ModelUtils:
    """Utility functions for model operations."""

    MODEL_REGISTRY = {
        "resnet50": {"layers": 50, "params": "25.5M"},
        "vgg16": {"layers": 16, "params": "138M"}
    }

    @staticmethod
    def calculate_flops(input_size: tuple, layers: int) -> int:
        """Calculate FLOPs (doesn't need instance or class)."""
        h, w, c = input_size
        return h * w * c * layers * 1000  # Simplified

    @classmethod
    def get_model_info(cls, model_name: str) -> dict:
        """Get model info from registry (accesses class variable)."""
        return cls.MODEL_REGISTRY.get(model_name, {})

    @classmethod
    def register_model(cls, name: str, layers: int, params: str):
        """Add model to registry (modifies class variable)."""
        cls.MODEL_REGISTRY[name] = {"layers": layers, "params": params}

# Usage (no instance needed)
flops = ModelUtils.calculate_flops((224, 224, 3), 50)
print(f"FLOPs: {flops:,}")

info = ModelUtils.get_model_info("resnet50")
print(f"ResNet50: {info}")

ModelUtils.register_model("efficientnet", 7, "5.3M")
```

---

## Decorator Patterns and Best Practices

### Decorator Composition

Stack multiple decorators:

```python
@retry(max_attempts=3)
@timer
@log_calls
def train_model(config: dict):
    """Train model with retry, timing, and logging."""
    if random.random() < 0.3:
        raise RuntimeError("Training failed")
    return {"accuracy": 0.92}

# Execution order: retry -> timer -> log_calls -> function
# Equivalent to:
# train_model = retry(max_attempts=3)(timer(log_calls(train_model)))
```

### Parameterized Decorators

```python
def repeat(times: int) -> Callable:
    """Decorator that repeats function execution."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> list:
            results = []
            for i in range(times):
                print(f"Execution {i + 1}/{times}")
                result = func(*args, **kwargs)
                results.append(result)
            return results
        return wrapper
    return decorator

@repeat(times=3)
def augment_sample(image):
    """Apply random augmentation."""
    return {"image": image, "rotation": random.randint(0, 360)}

# Usage
augmented = augment_sample("cat.jpg")
# Execution 1/3
# Execution 2/3
# Execution 3/3
# Returns list of 3 augmented samples
```

### Real-World ML Decorator Library

```python
# ml_decorators.py
"""Reusable decorators for ML infrastructure."""

import time
import logging
from functools import wraps
from typing import Callable, Any

logger = logging.getLogger(__name__)

def track_metrics(metric_name: str):
    """Track execution time as a metric."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start

            # Log to metrics system (e.g., Prometheus, Weights & Biases)
            logger.info(f"METRIC: {metric_name}={elapsed:.4f}s")

            return result
        return wrapper
    return decorator

def require_gpu(func: Callable) -> Callable:
    """Ensure GPU is available before execution."""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        import torch
        if not torch.cuda.is_available():
            raise RuntimeError(f"{func.__name__} requires GPU but none available")
        return func(*args, **kwargs)
    return wrapper

def batch_process(batch_size: int):
    """Process data in batches."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(data: list, *args, **kwargs) -> list:
            results = []
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                batch_results = func(batch, *args, **kwargs)
                results.extend(batch_results)
            return results
        return wrapper
    return decorator

# Usage
@require_gpu
@track_metrics("training_time")
def train_on_gpu(model, data):
    """Train model on GPU."""
    # Training code
    return {"loss": 0.5}

@batch_process(batch_size=32)
def process_samples(batch: list) -> list:
    """Process batch of samples."""
    return [f"processed_{item}" for item in batch]

# Test
samples = list(range(100))
results = process_samples(samples)  # Automatically batched
# Returns 100 processed items (processed in batches of 32)
```

---

## Python Modules and Packages

### Module Basics

A **module** is a single `.py` file containing Python code.

```python
# ml_utils.py
"""Utility functions for ML infrastructure."""

def normalize(data: list) -> list:
    """Normalize data to [0, 1] range."""
    min_val, max_val = min(data), max(data)
    return [(x - min_val) / (max_val - min_val) for x in data]

def calculate_accuracy(predictions: list, labels: list) -> float:
    """Calculate classification accuracy."""
    correct = sum(p == l for p, l in zip(predictions, labels))
    return correct / len(labels)

# Module-level constant
DEFAULT_BATCH_SIZE = 32
```

**Using the module**:

```python
# In another file
import ml_utils

# Access functions and constants
normalized = ml_utils.normalize([1, 2, 3, 4, 5])
accuracy = ml_utils.calculate_accuracy([1, 0, 1], [1, 1, 1])
batch_size = ml_utils.DEFAULT_BATCH_SIZE
```

### Import Patterns

```python
# 1. Import entire module
import ml_utils
result = ml_utils.normalize([1, 2, 3])

# 2. Import specific items
from ml_utils import normalize, calculate_accuracy
result = normalize([1, 2, 3])

# 3. Import with alias
import ml_utils as utils
result = utils.normalize([1, 2, 3])

# 4. Import all (discouraged - pollutes namespace)
from ml_utils import *
result = normalize([1, 2, 3])  # Where did this come from?
```

**Best practice**: Be explicit about what you import.

---

## Building Reusable ML Utilities

### Package Structure

A **package** is a directory containing an `__init__.py` file.

```
ml_toolkit/
├── __init__.py          # Makes this a package
├── preprocessing/
│   ├── __init__.py
│   ├── normalization.py
│   ├── augmentation.py
│   └── validation.py
├── models/
│   ├── __init__.py
│   ├── registry.py
│   └── loaders.py
├── metrics/
│   ├── __init__.py
│   ├── classification.py
│   └── regression.py
└── utils/
    ├── __init__.py
    ├── decorators.py
    └── logging.py
```

### Creating a Package

#### Step 1: Create Directory Structure

```bash
mkdir -p ml_toolkit/preprocessing
mkdir -p ml_toolkit/models
mkdir -p ml_toolkit/metrics
mkdir -p ml_toolkit/utils
```

#### Step 2: Add `__init__.py` Files

```python
# ml_toolkit/__init__.py
"""ML infrastructure toolkit."""

__version__ = "0.1.0"
__author__ = "Your Name"

# Import commonly used items for convenience
from ml_toolkit.preprocessing import normalize, augment_image
from ml_toolkit.metrics import accuracy, precision, recall

# Define what's exported with "from ml_toolkit import *"
__all__ = ["normalize", "augment_image", "accuracy", "precision", "recall"]
```

```python
# ml_toolkit/preprocessing/__init__.py
"""Data preprocessing utilities."""

from ml_toolkit.preprocessing.normalization import normalize, standardize
from ml_toolkit.preprocessing.augmentation import augment_image

__all__ = ["normalize", "standardize", "augment_image"]
```

```python
# ml_toolkit/preprocessing/normalization.py
"""Normalization functions."""

from typing import List

def normalize(data: List[float]) -> List[float]:
    """Normalize to [0, 1] range."""
    min_val, max_val = min(data), max(data)
    range_val = max_val - min_val
    if range_val == 0:
        return [0.0] * len(data)
    return [(x - min_val) / range_val for x in data]

def standardize(data: List[float]) -> List[float]:
    """Standardize to mean=0, std=1."""
    mean = sum(data) / len(data)
    variance = sum((x - mean) ** 2 for x in data) / len(data)
    std = variance ** 0.5
    if std == 0:
        return [0.0] * len(data)
    return [(x - mean) / std for x in data]
```

```python
# ml_toolkit/metrics/__init__.py
"""Metric calculation utilities."""

from ml_toolkit.metrics.classification import accuracy, precision, recall, f1_score

__all__ = ["accuracy", "precision", "recall", "f1_score"]
```

```python
# ml_toolkit/metrics/classification.py
"""Classification metrics."""

from typing import List

def accuracy(predictions: List[int], labels: List[int]) -> float:
    """Calculate accuracy."""
    if not predictions or len(predictions) != len(labels):
        raise ValueError("Predictions and labels must have same length")
    correct = sum(p == l for p, l in zip(predictions, labels))
    return correct / len(labels)

def precision(predictions: List[int], labels: List[int], positive_class: int = 1) -> float:
    """Calculate precision for binary classification."""
    tp = sum((p == positive_class and l == positive_class)
             for p, l in zip(predictions, labels))
    fp = sum((p == positive_class and l != positive_class)
             for p, l in zip(predictions, labels))
    return tp / (tp + fp) if (tp + fp) > 0 else 0.0

def recall(predictions: List[int], labels: List[int], positive_class: int = 1) -> float:
    """Calculate recall for binary classification."""
    tp = sum((p == positive_class and l == positive_class)
             for p, l in zip(predictions, labels))
    fn = sum((p != positive_class and l == positive_class)
             for p, l in zip(predictions, labels))
    return tp / (tp + fn) if (tp + fn) > 0 else 0.0

def f1_score(predictions: List[int], labels: List[int], positive_class: int = 1) -> float:
    """Calculate F1 score."""
    prec = precision(predictions, labels, positive_class)
    rec = recall(predictions, labels, positive_class)
    return 2 * (prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
```

#### Step 3: Using Your Package

```python
# Option 1: Import from top level
from ml_toolkit import normalize, accuracy

data = [1, 2, 3, 4, 5]
normalized = normalize(data)

predictions = [1, 0, 1, 1, 0]
labels = [1, 0, 1, 0, 0]
acc = accuracy(predictions, labels)

# Option 2: Import submodules
from ml_toolkit.preprocessing import standardize
from ml_toolkit.metrics import precision, recall

standardized = standardize([10, 20, 30])
prec = precision(predictions, labels)
rec = recall(predictions, labels)

# Option 3: Import subpackages
import ml_toolkit.metrics as metrics

f1 = metrics.f1_score(predictions, labels)
```

### Relative Imports Within Package

```python
# ml_toolkit/utils/validation.py
"""Validation utilities."""

# Import from sibling module
from .decorators import timer, retry

# Import from parent package
from ..preprocessing import normalize

# Import from cousin module
from ..metrics.classification import accuracy

@timer
def validate_data(data: list) -> bool:
    """Validate data is normalized."""
    normalized = normalize(data)
    return all(0 <= x <= 1 for x in normalized)
```

**Relative import rules**:
- `.` = current package
- `..` = parent package
- `...` = grandparent package

---

## Package Distribution

### Creating `setup.py`

```python
# setup.py
"""Setup configuration for ml_toolkit package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="ml-toolkit",
    version="0.1.0",
    author="Your Name",
    author_email="you@example.com",
    description="Reusable ML infrastructure utilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ml-toolkit",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "torch>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "mypy>=1.0.0",
        ],
    },
)
```

### Modern `pyproject.toml` (Preferred)

```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "ml-toolkit"
version = "0.1.0"
description = "Reusable ML infrastructure utilities"
readme = "README.md"
authors = [{name = "Your Name", email = "you@example.com"}]
license = {text = "MIT"}
requires-python = ">=3.8"
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
    "Programming Language :: Python :: 3",
]
dependencies = [
    "numpy>=1.21.0",
    "torch>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "black>=22.0.0",
    "mypy>=1.0.0",
]

[project.urls]
Homepage = "https://github.com/yourusername/ml-toolkit"
Documentation = "https://ml-toolkit.readthedocs.io"
Repository = "https://github.com/yourusername/ml-toolkit.git"
```

### Installing Your Package

```bash
# Development installation (editable mode)
# Changes to source code are immediately reflected
pip install -e .

# With dev dependencies
pip install -e ".[dev]"

# Build distribution
python -m build

# This creates:
# dist/
#   ml_toolkit-0.1.0-py3-none-any.whl
#   ml_toolkit-0.1.0.tar.gz

# Install from wheel
pip install dist/ml_toolkit-0.1.0-py3-none-any.whl

# Upload to PyPI (requires account)
pip install twine
twine upload dist/*
```

### Package Best Practices

```python
# ml_toolkit/__init__.py

# 1. Define version
__version__ = "0.1.0"

# 2. Import frequently used items
from ml_toolkit.preprocessing import normalize
from ml_toolkit.metrics import accuracy

# 3. Define public API
__all__ = ["normalize", "accuracy", "__version__"]

# 4. Add module docstring
"""
ML Toolkit - Reusable ML Infrastructure Utilities
==================================================

This package provides common utilities for ML infrastructure:

- preprocessing: Data normalization and augmentation
- metrics: Classification and regression metrics
- utils: Decorators and logging utilities

Example usage:
    >>> from ml_toolkit import normalize, accuracy
    >>> data = normalize([1, 2, 3, 4, 5])
    >>> acc = accuracy([1, 0, 1], [1, 1, 1])
"""
```

---

## Summary and Best Practices

### Decorator Key Takeaways

1. **Use decorators** to extract cross-cutting concerns (timing, logging, retries)
2. **Always use `@wraps`** to preserve function metadata
3. **Stack decorators** for composition (order matters!)
4. **Create reusable decorator libraries** for your infrastructure
5. **Use built-in decorators**: `@property`, `@staticmethod`, `@classmethod`, `@lru_cache`

### Common Decorator Patterns

```python
# Timing
@timer
def slow_operation():
    pass

# Logging
@log_calls
def important_function():
    pass

# Retry with backoff
@retry(max_attempts=3, delay=1.0)
def flaky_network_call():
    pass

# Caching
@lru_cache(maxsize=128)
def expensive_computation():
    pass

# Validation
@validate_types(x=int, y=float)
def calculate(x, y):
    pass

# Composition
@retry(max_attempts=3)
@timer
@log_calls
def critical_operation():
    pass
```

### Packaging Key Takeaways

1. **Structure your code** into logical modules and packages
2. **Use `__init__.py`** to define package public APIs
3. **Use relative imports** within packages
4. **Create `pyproject.toml`** for modern package configuration
5. **Install in editable mode** (`pip install -e .`) during development
6. **Define clear dependencies** in your package configuration
7. **Version your package** semantically (major.minor.patch)

### Package Structure Example

```
my_ml_package/
├── pyproject.toml       # Package configuration
├── README.md           # Documentation
├── LICENSE             # License file
├── .gitignore          # Git ignore patterns
├── src/
│   └── my_ml_package/
│       ├── __init__.py      # Package entry point
│       ├── preprocessing/   # Subpackage
│       │   ├── __init__.py
│       │   └── transforms.py
│       ├── models/          # Subpackage
│       │   ├── __init__.py
│       │   └── registry.py
│       └── utils/           # Subpackage
│           ├── __init__.py
│           └── decorators.py
├── tests/
│   ├── __init__.py
│   ├── test_preprocessing.py
│   └── test_models.py
└── docs/
    └── index.md
```

### Real-World Workflow

```python
# 1. Create reusable utilities
# ml_infra_utils/decorators.py
from functools import wraps
import time

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__}: {time.time() - start:.4f}s")
        return result
    return wrapper

# 2. Package them
# ml_infra_utils/__init__.py
from ml_infra_utils.decorators import timer
__all__ = ["timer"]

# 3. Install in development
# pip install -e .

# 4. Use across projects
from ml_infra_utils import timer

@timer
def train_model():
    # Training code
    pass
```

### Next Steps

You now understand decorators and packaging! In the next lectures, we'll explore:
- Asynchronous programming patterns
- Testing strategies for ML infrastructure
- CLI tools and automation

Continue to **Exercise 03: Functions, Modules & Decorators** to practice these concepts!

---

**Word Count**: ~5,200 words
**Estimated Reading Time**: 25-30 minutes
