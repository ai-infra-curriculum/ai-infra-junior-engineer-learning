# Exercise 03: Creating Reusable ML Utility Functions and Modules

## Overview

This exercise teaches you how to design, implement, and organize reusable Python functions and modules for machine learning infrastructure. You'll learn to create utility libraries, implement proper function signatures, use type hints, handle default arguments, and structure code into maintainable modules.

## Learning Objectives

By completing this exercise, you will:
- Write clean, reusable functions with proper signatures and documentation
- Use type hints for better code quality and IDE support
- Implement default arguments and keyword arguments effectively
- Create modules and packages for ML utilities
- Use *args and **kwargs for flexible function interfaces
- Implement decorators for common ML patterns (timing, logging, caching)
- Apply functional programming concepts (map, filter, lambda)
- Build a comprehensive ML utility library

## Prerequisites

- Completed Exercise 01: Environment Setup
- Completed Exercise 02: Data Structures
- Completed Lectures 01 and 02
- Understanding of ML workflows and common operations

## Time Required

- Estimated: 100-120 minutes
- Difficulty: Intermediate

## Part 1: Function Basics and Best Practices

### Step 1: Writing Clean Functions with Type Hints

```python
# Create a script: function_basics.py

from typing import List, Dict, Tuple, Optional, Union
import numpy as np

def calculate_accuracy(predictions: List[int],
                      labels: List[int]) -> float:
    """
    Calculate classification accuracy.

    Args:
        predictions: Model predictions as class indices
        labels: Ground truth labels as class indices

    Returns:
        Accuracy as a float between 0 and 1

    Raises:
        ValueError: If predictions and labels have different lengths
    """
    if len(predictions) != len(labels):
        raise ValueError("Predictions and labels must have same length")

    if len(predictions) == 0:
        return 0.0

    correct = sum(p == l for p, l in zip(predictions, labels))
    accuracy = correct / len(predictions)

    return accuracy

def normalize_features(data: List[float],
                      method: str = "minmax",
                      feature_range: Tuple[float, float] = (0.0, 1.0)
                      ) -> List[float]:
    """
    Normalize feature values.

    Args:
        data: List of feature values
        method: Normalization method ("minmax" or "zscore")
        feature_range: Target range for minmax normalization

    Returns:
        Normalized feature values

    Raises:
        ValueError: If method is not supported
    """
    if not data:
        return []

    if method == "minmax":
        min_val = min(data)
        max_val = max(data)

        if min_val == max_val:
            # All values are the same
            return [feature_range[0]] * len(data)

        # Scale to feature_range
        range_min, range_max = feature_range
        scale = (range_max - range_min) / (max_val - min_val)

        normalized = [
            range_min + (x - min_val) * scale
            for x in data
        ]

        return normalized

    elif method == "zscore":
        mean = sum(data) / len(data)
        variance = sum((x - mean) ** 2 for x in data) / len(data)
        std_dev = variance ** 0.5

        if std_dev == 0:
            return [0.0] * len(data)

        normalized = [(x - mean) / std_dev for x in data]
        return normalized

    else:
        raise ValueError(f"Unknown normalization method: {method}")

def split_data(data: List,
               train_ratio: float = 0.7,
               val_ratio: float = 0.15,
               shuffle: bool = True,
               random_seed: Optional[int] = None
               ) -> Tuple[List, List, List]:
    """
    Split data into train, validation, and test sets.

    Args:
        data: Input data to split
        train_ratio: Proportion of data for training
        val_ratio: Proportion of data for validation
        shuffle: Whether to shuffle data before splitting
        random_seed: Random seed for reproducibility

    Returns:
        Tuple of (train_data, val_data, test_data)

    Raises:
        ValueError: If ratios don't sum to <= 1.0
    """
    import random

    if train_ratio + val_ratio > 1.0:
        raise ValueError("train_ratio + val_ratio must be <= 1.0")

    data_copy = data.copy()

    if shuffle:
        if random_seed is not None:
            random.seed(random_seed)
        random.shuffle(data_copy)

    n = len(data_copy)
    train_end = int(n * train_ratio)
    val_end = train_end + int(n * val_ratio)

    train_data = data_copy[:train_end]
    val_data = data_copy[train_end:val_end]
    test_data = data_copy[val_end:]

    return train_data, val_data, test_data

# Example usage and testing
if __name__ == "__main__":
    # Test accuracy calculation
    preds = [1, 0, 1, 1, 0, 1, 0, 0]
    labels = [1, 0, 1, 0, 0, 1, 0, 1]
    acc = calculate_accuracy(preds, labels)
    print(f"Accuracy: {acc:.2%}")

    # Test normalization
    features = [1.0, 2.0, 3.0, 4.0, 5.0]
    normalized_minmax = normalize_features(features, method="minmax")
    print(f"MinMax normalized: {normalized_minmax}")

    normalized_zscore = normalize_features(features, method="zscore")
    print(f"Z-score normalized: {[f'{x:.2f}' for x in normalized_zscore]}")

    # Test data splitting
    dataset = list(range(100))
    train, val, test = split_data(dataset, random_seed=42)
    print(f"Split sizes - Train: {len(train)}, Val: {len(val)}, Test: {len(test)}")
```

**Tasks**:
1. Run the script and verify outputs
2. Add type hints to return complex types (Dict[str, float])
3. Implement input validation for all functions
4. Add comprehensive docstrings following NumPy or Google style

### Step 2: Functions with Flexible Arguments

```python
# Create a script: flexible_functions.py

from typing import Any, Dict, List, Optional, Tuple
import time

def log_metrics(*args, **kwargs) -> None:
    """
    Log any number of metrics with flexible arguments.

    Args:
        *args: Positional metrics to log
        **kwargs: Named metrics to log

    Examples:
        log_metrics(0.92, 0.15, 0.89)
        log_metrics(accuracy=0.92, loss=0.15, f1=0.89)
        log_metrics(0.92, loss=0.15, f1=0.89)
    """
    print("=== Metrics Log ===")

    if args:
        print("Positional metrics:")
        for i, value in enumerate(args):
            print(f"  Metric {i+1}: {value}")

    if kwargs:
        print("Named metrics:")
        for name, value in kwargs.items():
            print(f"  {name}: {value}")

def create_model(model_type: str,
                *layers: int,
                activation: str = "relu",
                dropout: float = 0.0,
                **config: Any) -> Dict[str, Any]:
    """
    Create a model configuration with flexible layer specification.

    Args:
        model_type: Type of model (e.g., "cnn", "mlp")
        *layers: Variable number of layer sizes
        activation: Activation function
        dropout: Dropout rate
        **config: Additional configuration parameters

    Returns:
        Model configuration dictionary
    """
    model_config = {
        "type": model_type,
        "layers": list(layers),
        "activation": activation,
        "dropout": dropout,
    }

    # Add any additional config
    model_config.update(config)

    return model_config

def batch_process(data: List[Any],
                 processor_func: callable,
                 batch_size: int = 32,
                 *processor_args,
                 **processor_kwargs) -> List[Any]:
    """
    Process data in batches using a processor function.

    Args:
        data: Data to process
        processor_func: Function to apply to each batch
        batch_size: Size of each batch
        *processor_args: Additional positional args for processor
        **processor_kwargs: Additional keyword args for processor

    Returns:
        List of processed results
    """
    results = []

    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        # Call processor with batch and additional arguments
        result = processor_func(batch, *processor_args, **processor_kwargs)
        results.append(result)

    return results

def augment_image(image: Any,
                 flip_horizontal: bool = False,
                 flip_vertical: bool = False,
                 rotate: Optional[int] = None,
                 brightness: float = 1.0,
                 **transforms: Any) -> Dict[str, Any]:
    """
    Apply image augmentations with flexible transformation options.

    Args:
        image: Input image
        flip_horizontal: Whether to flip horizontally
        flip_vertical: Whether to flip vertically
        rotate: Rotation angle in degrees
        brightness: Brightness adjustment factor
        **transforms: Additional transformations

    Returns:
        Dictionary with augmentation info
    """
    augmentations = {
        "original": image,
        "transforms_applied": []
    }

    if flip_horizontal:
        augmentations["transforms_applied"].append("flip_h")

    if flip_vertical:
        augmentations["transforms_applied"].append("flip_v")

    if rotate is not None:
        augmentations["transforms_applied"].append(f"rotate_{rotate}")

    if brightness != 1.0:
        augmentations["transforms_applied"].append(f"brightness_{brightness}")

    # Apply any custom transforms
    for transform_name, transform_value in transforms.items():
        augmentations["transforms_applied"].append(
            f"{transform_name}_{transform_value}"
        )

    return augmentations

# Example usage
if __name__ == "__main__":
    # Test flexible logging
    print("Example 1: Flexible logging")
    log_metrics(0.92, 0.15, 0.89)
    print()
    log_metrics(accuracy=0.92, loss=0.15, f1_score=0.89)
    print()
    log_metrics(0.92, loss=0.15, f1_score=0.89, learning_rate=0.001)
    print()

    # Test model creation
    print("Example 2: Model creation")
    model1 = create_model("mlp", 128, 64, 32, dropout=0.3)
    print(f"Model 1: {model1}")

    model2 = create_model("cnn", 64, 128, 256, activation="relu",
                         dropout=0.5, batch_norm=True, pool_size=2)
    print(f"Model 2: {model2}")
    print()

    # Test batch processing
    print("Example 3: Batch processing")
    def simple_processor(batch, multiplier=1):
        return sum(batch) * multiplier

    data = list(range(1, 21))
    results = batch_process(data, simple_processor, batch_size=5, multiplier=2)
    print(f"Batch results: {results}")
    print()

    # Test image augmentation
    print("Example 4: Image augmentation")
    aug_result = augment_image(
        "image.jpg",
        flip_horizontal=True,
        rotate=90,
        brightness=1.2,
        contrast=1.5,
        saturation=0.8
    )
    print(f"Augmentations: {aug_result['transforms_applied']}")
```

**Tasks**:
1. Implement a function that accepts both *args and **kwargs
2. Create a configuration merger that combines default and custom configs
3. Build a metrics aggregator that handles variable metric types
4. Implement a flexible data loader with customizable preprocessing

## Part 2: Decorators for Common ML Patterns

### Step 3: Timing and Logging Decorators

```python
# Create a script: decorators.py

import time
import functools
from typing import Any, Callable
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def timing_decorator(func: Callable) -> Callable:
    """Decorator to measure function execution time"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        execution_time = end_time - start_time
        logger.info(f"{func.__name__} took {execution_time:.4f} seconds")

        return result
    return wrapper

def log_calls(func: Callable) -> Callable:
    """Decorator to log function calls with arguments"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)

        logger.info(f"Calling {func.__name__}({signature})")

        result = func(*args, **kwargs)

        logger.info(f"{func.__name__} returned {result!r}")

        return result
    return wrapper

def retry(max_attempts: int = 3, delay: float = 1.0):
    """
    Decorator to retry function on failure.

    Args:
        max_attempts: Maximum number of retry attempts
        delay: Delay between retries in seconds
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0

            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts >= max_attempts:
                        logger.error(
                            f"{func.__name__} failed after {max_attempts} attempts"
                        )
                        raise

                    logger.warning(
                        f"{func.__name__} failed (attempt {attempts}/{max_attempts}). "
                        f"Retrying in {delay}s... Error: {e}"
                    )
                    time.sleep(delay)

        return wrapper
    return decorator

def cache_results(func: Callable) -> Callable:
    """Decorator to cache function results (memoization)"""
    cache = {}

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Create cache key from args and kwargs
        cache_key = str(args) + str(sorted(kwargs.items()))

        if cache_key in cache:
            logger.info(f"Cache hit for {func.__name__}")
            return cache[cache_key]

        logger.info(f"Cache miss for {func.__name__}, computing...")
        result = func(*args, **kwargs)
        cache[cache_key] = result

        return result

    return wrapper

def validate_inputs(**validators):
    """
    Decorator to validate function inputs.

    Example:
        @validate_inputs(x=lambda x: x > 0, y=lambda y: isinstance(y, str))
        def my_func(x, y):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get function signature
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # Validate each argument
            for param_name, validator in validators.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]
                    if not validator(value):
                        raise ValueError(
                            f"Validation failed for parameter '{param_name}' "
                            f"with value {value}"
                        )

            return func(*args, **kwargs)

        return wrapper
    return decorator

# Example usage
@timing_decorator
@log_calls
def train_model(epochs: int, batch_size: int) -> float:
    """Simulate model training"""
    time.sleep(0.5)  # Simulate training time
    return 0.92

@retry(max_attempts=3, delay=0.5)
def load_model_from_storage(model_path: str) -> str:
    """Simulate loading model from storage (might fail)"""
    import random

    if random.random() < 0.5:
        raise IOError(f"Failed to load model from {model_path}")

    return f"Model loaded from {model_path}"

@cache_results
@timing_decorator
def compute_expensive_metric(data_size: int) -> float:
    """Simulate expensive computation"""
    time.sleep(1.0)
    return data_size * 0.001

@validate_inputs(
    learning_rate=lambda x: 0 < x < 1,
    batch_size=lambda x: isinstance(x, int) and x > 0
)
def configure_training(learning_rate: float, batch_size: int) -> dict:
    """Configure training with validation"""
    return {
        "learning_rate": learning_rate,
        "batch_size": batch_size
    }

if __name__ == "__main__":
    # Test timing and logging
    print("=== Testing timing and logging ===")
    accuracy = train_model(epochs=10, batch_size=32)
    print(f"Training accuracy: {accuracy}\n")

    # Test retry
    print("=== Testing retry ===")
    try:
        model = load_model_from_storage("/models/resnet50.h5")
        print(f"Success: {model}\n")
    except IOError as e:
        print(f"Failed: {e}\n")

    # Test caching
    print("=== Testing caching ===")
    result1 = compute_expensive_metric(1000)  # Cache miss
    result2 = compute_expensive_metric(1000)  # Cache hit
    result3 = compute_expensive_metric(2000)  # Cache miss
    print(f"Results: {result1}, {result2}, {result3}\n")

    # Test validation
    print("=== Testing validation ===")
    try:
        config1 = configure_training(learning_rate=0.001, batch_size=32)
        print(f"Valid config: {config1}")

        config2 = configure_training(learning_rate=1.5, batch_size=32)
        print(f"Invalid config: {config2}")
    except ValueError as e:
        print(f"Validation error: {e}")
```

**Tasks**:
1. Create a decorator that logs GPU memory usage
2. Implement a decorator for checkpointing function results to disk
3. Build a decorator that sends metrics to a monitoring service
4. Create a decorator that implements rate limiting for API calls

## Part 3: Building Reusable Modules

### Step 4: Creating a Metrics Module

```python
# Create a file: ml_utils/metrics.py
# Directory structure:
# ml_utils/
#   __init__.py
#   metrics.py
#   preprocessing.py
#   visualization.py

"""
Machine Learning Metrics Module

Provides common evaluation metrics for classification and regression tasks.
"""

from typing import List, Dict, Tuple
import math

def accuracy(predictions: List[int], labels: List[int]) -> float:
    """Calculate classification accuracy"""
    if len(predictions) != len(labels):
        raise ValueError("Predictions and labels must have same length")

    if not predictions:
        return 0.0

    correct = sum(p == l for p, l in zip(predictions, labels))
    return correct / len(predictions)

def precision(predictions: List[int],
             labels: List[int],
             positive_class: int = 1) -> float:
    """Calculate precision for binary classification"""
    true_positives = sum(
        1 for p, l in zip(predictions, labels)
        if p == positive_class and l == positive_class
    )

    predicted_positives = sum(1 for p in predictions if p == positive_class)

    if predicted_positives == 0:
        return 0.0

    return true_positives / predicted_positives

def recall(predictions: List[int],
          labels: List[int],
          positive_class: int = 1) -> float:
    """Calculate recall for binary classification"""
    true_positives = sum(
        1 for p, l in zip(predictions, labels)
        if p == positive_class and l == positive_class
    )

    actual_positives = sum(1 for l in labels if l == positive_class)

    if actual_positives == 0:
        return 0.0

    return true_positives / actual_positives

def f1_score(predictions: List[int],
            labels: List[int],
            positive_class: int = 1) -> float:
    """Calculate F1 score"""
    prec = precision(predictions, labels, positive_class)
    rec = recall(predictions, labels, positive_class)

    if prec + rec == 0:
        return 0.0

    return 2 * (prec * rec) / (prec + rec)

def confusion_matrix(predictions: List[int],
                    labels: List[int],
                    num_classes: int) -> List[List[int]]:
    """
    Calculate confusion matrix.

    Returns:
        Matrix where element [i][j] represents samples with true label i
        and predicted label j
    """
    matrix = [[0] * num_classes for _ in range(num_classes)]

    for pred, label in zip(predictions, labels):
        matrix[label][pred] += 1

    return matrix

def classification_report(predictions: List[int],
                         labels: List[int],
                         class_names: List[str] = None) -> Dict[str, Dict]:
    """
    Generate comprehensive classification report.

    Returns:
        Dictionary with per-class metrics
    """
    num_classes = max(max(predictions), max(labels)) + 1

    if class_names is None:
        class_names = [f"class_{i}" for i in range(num_classes)]

    report = {}

    for class_id, class_name in enumerate(class_names):
        report[class_name] = {
            "precision": precision(predictions, labels, class_id),
            "recall": recall(predictions, labels, class_id),
            "f1_score": f1_score(predictions, labels, class_id)
        }

    # Add overall accuracy
    report["accuracy"] = accuracy(predictions, labels)

    return report

def mean_squared_error(predictions: List[float],
                      labels: List[float]) -> float:
    """Calculate MSE for regression"""
    if len(predictions) != len(labels):
        raise ValueError("Predictions and labels must have same length")

    if not predictions:
        return 0.0

    squared_errors = [(p - l) ** 2 for p, l in zip(predictions, labels)]
    return sum(squared_errors) / len(squared_errors)

def mean_absolute_error(predictions: List[float],
                       labels: List[float]) -> float:
    """Calculate MAE for regression"""
    if len(predictions) != len(labels):
        raise ValueError("Predictions and labels must have same length")

    if not predictions:
        return 0.0

    absolute_errors = [abs(p - l) for p, l in zip(predictions, labels)]
    return sum(absolute_errors) / len(absolute_errors)

def r_squared(predictions: List[float],
             labels: List[float]) -> float:
    """Calculate R² score for regression"""
    if len(predictions) != len(labels):
        raise ValueError("Predictions and labels must have same length")

    if not predictions:
        return 0.0

    # Calculate mean of labels
    mean_label = sum(labels) / len(labels)

    # Total sum of squares
    ss_tot = sum((l - mean_label) ** 2 for l in labels)

    # Residual sum of squares
    ss_res = sum((l - p) ** 2 for l, p in zip(labels, predictions))

    if ss_tot == 0:
        return 0.0

    return 1 - (ss_res / ss_tot)

# Create ml_utils/__init__.py
"""
ML Utilities Package

Provides reusable utilities for machine learning workflows.
"""

from . import metrics
from . import preprocessing

__version__ = "0.1.0"
__all__ = ["metrics", "preprocessing"]
```

### Step 5: Creating a Preprocessing Module

```python
# Create a file: ml_utils/preprocessing.py

"""
Data Preprocessing Module

Provides utilities for data cleaning and preprocessing.
"""

from typing import List, Tuple, Optional, Dict, Any
import statistics

def normalize_minmax(data: List[float],
                    feature_range: Tuple[float, float] = (0.0, 1.0)
                    ) -> List[float]:
    """Normalize data to specified range"""
    if not data:
        return []

    min_val = min(data)
    max_val = max(data)

    if min_val == max_val:
        return [feature_range[0]] * len(data)

    range_min, range_max = feature_range
    scale = (range_max - range_min) / (max_val - min_val)

    return [range_min + (x - min_val) * scale for x in data]

def normalize_zscore(data: List[float]) -> List[float]:
    """Normalize data using z-score standardization"""
    if not data:
        return []

    mean = statistics.mean(data)
    std_dev = statistics.stdev(data) if len(data) > 1 else 0

    if std_dev == 0:
        return [0.0] * len(data)

    return [(x - mean) / std_dev for x in data]

def remove_outliers(data: List[float],
                   method: str = "iqr",
                   threshold: float = 1.5) -> List[float]:
    """
    Remove outliers from data.

    Args:
        data: Input data
        method: Method to use ("iqr" or "zscore")
        threshold: Threshold for outlier detection

    Returns:
        Data with outliers removed
    """
    if not data or len(data) < 4:
        return data

    if method == "iqr":
        sorted_data = sorted(data)
        q1_idx = len(sorted_data) // 4
        q3_idx = 3 * len(sorted_data) // 4

        q1 = sorted_data[q1_idx]
        q3 = sorted_data[q3_idx]
        iqr = q3 - q1

        lower_bound = q1 - threshold * iqr
        upper_bound = q3 + threshold * iqr

        return [x for x in data if lower_bound <= x <= upper_bound]

    elif method == "zscore":
        mean = statistics.mean(data)
        std_dev = statistics.stdev(data)

        z_scores = [abs((x - mean) / std_dev) for x in data]
        return [x for x, z in zip(data, z_scores) if z <= threshold]

    else:
        raise ValueError(f"Unknown method: {method}")

def fill_missing_values(data: List[Optional[float]],
                       strategy: str = "mean") -> List[float]:
    """
    Fill missing values in data.

    Args:
        data: Input data with possible None values
        strategy: Strategy to use ("mean", "median", "mode", "forward", "backward")

    Returns:
        Data with missing values filled
    """
    if not data:
        return []

    # Get non-missing values
    valid_values = [x for x in data if x is not None]

    if not valid_values:
        return [0.0] * len(data)

    if strategy == "mean":
        fill_value = statistics.mean(valid_values)
        return [x if x is not None else fill_value for x in data]

    elif strategy == "median":
        fill_value = statistics.median(valid_values)
        return [x if x is not None else fill_value for x in data]

    elif strategy == "mode":
        fill_value = statistics.mode(valid_values)
        return [x if x is not None else fill_value for x in data]

    elif strategy == "forward":
        result = []
        last_valid = valid_values[0]
        for x in data:
            if x is not None:
                last_valid = x
                result.append(x)
            else:
                result.append(last_valid)
        return result

    elif strategy == "backward":
        result = []
        data_reversed = list(reversed(data))
        valid_reversed = [x for x in data_reversed if x is not None]
        last_valid = valid_reversed[0]

        for x in data_reversed:
            if x is not None:
                last_valid = x
                result.append(x)
            else:
                result.append(last_valid)

        return list(reversed(result))

    else:
        raise ValueError(f"Unknown strategy: {strategy}")

def one_hot_encode(labels: List[int], num_classes: int) -> List[List[int]]:
    """Convert class labels to one-hot encoding"""
    encoded = []

    for label in labels:
        one_hot = [0] * num_classes
        if 0 <= label < num_classes:
            one_hot[label] = 1
        encoded.append(one_hot)

    return encoded

def train_test_split(data: List[Any],
                    test_size: float = 0.2,
                    shuffle: bool = True,
                    random_seed: Optional[int] = None
                    ) -> Tuple[List[Any], List[Any]]:
    """Split data into training and test sets"""
    import random

    if not 0 < test_size < 1:
        raise ValueError("test_size must be between 0 and 1")

    data_copy = data.copy()

    if shuffle:
        if random_seed is not None:
            random.seed(random_seed)
        random.shuffle(data_copy)

    split_idx = int(len(data_copy) * (1 - test_size))
    train_data = data_copy[:split_idx]
    test_data = data_copy[split_idx:]

    return train_data, test_data
```

### Step 6: Using Your Custom Module

```python
# Create a script: test_ml_utils.py

# Make sure ml_utils/ is in your Python path
import sys
sys.path.insert(0, '.')

from ml_utils import metrics, preprocessing

def test_metrics():
    """Test metrics module"""
    print("=== Testing Metrics Module ===")

    # Test data
    predictions = [1, 0, 1, 1, 0, 1, 0, 0, 1, 1]
    labels = [1, 0, 1, 0, 0, 1, 0, 1, 1, 0]

    # Calculate metrics
    acc = metrics.accuracy(predictions, labels)
    prec = metrics.precision(predictions, labels)
    rec = metrics.recall(predictions, labels)
    f1 = metrics.f1_score(predictions, labels)

    print(f"Accuracy: {acc:.2%}")
    print(f"Precision: {prec:.2%}")
    print(f"Recall: {rec:.2%}")
    print(f"F1 Score: {f1:.2%}")

    # Generate report
    report = metrics.classification_report(
        predictions, labels,
        class_names=["negative", "positive"]
    )
    print(f"\nClassification Report:")
    for class_name, metrics_dict in report.items():
        if class_name != "accuracy":
            print(f"  {class_name}: {metrics_dict}")

    print(f"  Overall Accuracy: {report['accuracy']:.2%}\n")

def test_preprocessing():
    """Test preprocessing module"""
    print("=== Testing Preprocessing Module ===")

    # Test normalization
    data = [1.0, 2.0, 3.0, 4.0, 5.0]
    normalized = preprocessing.normalize_minmax(data)
    print(f"Original: {data}")
    print(f"Normalized: {[f'{x:.2f}' for x in normalized]}")

    # Test outlier removal
    data_with_outliers = [1, 2, 3, 4, 5, 100, 2, 3, 4, 5]
    cleaned = preprocessing.remove_outliers(data_with_outliers)
    print(f"\nWith outliers: {data_with_outliers}")
    print(f"Cleaned: {cleaned}")

    # Test missing value handling
    data_with_missing = [1.0, 2.0, None, 4.0, None, 6.0]
    filled = preprocessing.fill_missing_values(data_with_missing, strategy="mean")
    print(f"\nWith missing: {data_with_missing}")
    print(f"Filled (mean): {[f'{x:.2f}' for x in filled]}")

    # Test one-hot encoding
    labels = [0, 1, 2, 1, 0, 2]
    one_hot = preprocessing.one_hot_encode(labels, num_classes=3)
    print(f"\nLabels: {labels}")
    print(f"One-hot: {one_hot}\n")

if __name__ == "__main__":
    test_metrics()
    test_preprocessing()

    print("✓ All tests passed!")
```

## Part 4: Functional Programming Patterns

### Step 7: Using map, filter, and lambda

```python
# Create a script: functional_patterns.py

from typing import List, Callable, Any
from functools import reduce

# Lambda functions for common operations
square = lambda x: x ** 2
is_even = lambda x: x % 2 == 0
normalize = lambda x, min_val, max_val: (x - min_val) / (max_val - min_val)

def example_map():
    """Demonstrate map for transformations"""
    print("=== Map Examples ===")

    # Square all numbers
    numbers = [1, 2, 3, 4, 5]
    squared = list(map(square, numbers))
    print(f"Original: {numbers}")
    print(f"Squared: {squared}")

    # Convert predictions to class labels
    probabilities = [0.2, 0.8, 0.6, 0.3, 0.9]
    predictions = list(map(lambda p: 1 if p > 0.5 else 0, probabilities))
    print(f"Probabilities: {probabilities}")
    print(f"Predictions: {predictions}")

    # Parse filenames
    files = ["model_v1.h5", "model_v2.h5", "model_v3.h5"]
    versions = list(map(lambda f: f.split("_v")[1].split(".")[0], files))
    print(f"Files: {files}")
    print(f"Versions: {versions}\n")

def example_filter():
    """Demonstrate filter for selection"""
    print("=== Filter Examples ===")

    # Filter even numbers
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    evens = list(filter(is_even, numbers))
    print(f"Numbers: {numbers}")
    print(f"Evens: {evens}")

    # Filter high-accuracy models
    models = [
        {"name": "model1", "accuracy": 0.85},
        {"name": "model2", "accuracy": 0.92},
        {"name": "model3", "accuracy": 0.88},
        {"name": "model4", "accuracy": 0.95},
    ]

    high_accuracy = list(filter(lambda m: m["accuracy"] > 0.90, models))
    print(f"High accuracy models: {[m['name'] for m in high_accuracy]}")

    # Filter completed experiments
    experiments = [
        ("exp1", "completed"),
        ("exp2", "running"),
        ("exp3", "completed"),
        ("exp4", "failed"),
    ]

    completed = list(filter(lambda e: e[1] == "completed", experiments))
    print(f"Completed: {[e[0] for e in completed]}\n")

def example_reduce():
    """Demonstrate reduce for aggregation"""
    print("=== Reduce Examples ===")

    # Sum all numbers
    numbers = [1, 2, 3, 4, 5]
    total = reduce(lambda acc, x: acc + x, numbers, 0)
    print(f"Numbers: {numbers}")
    print(f"Sum: {total}")

    # Find maximum accuracy
    accuracies = [0.85, 0.92, 0.88, 0.95, 0.90]
    max_acc = reduce(lambda acc, x: max(acc, x), accuracies, 0)
    print(f"Accuracies: {accuracies}")
    print(f"Max: {max_acc}")

    # Merge configurations
    configs = [
        {"learning_rate": 0.001},
        {"batch_size": 32},
        {"epochs": 100},
    ]

    merged = reduce(lambda acc, d: {**acc, **d}, configs, {})
    print(f"Configs: {configs}")
    print(f"Merged: {merged}\n")

def example_composition():
    """Demonstrate function composition"""
    print("=== Function Composition ===")

    # Compose data processing pipeline
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    # Pipeline: filter evens, square, sum
    result = reduce(
        lambda acc, x: acc + x,
        map(square, filter(is_even, data)),
        0
    )

    print(f"Original: {data}")
    print(f"Evens squared and summed: {result}")

    # Process model metrics
    metrics = [
        {"model": "m1", "acc": 0.85, "loss": 0.25},
        {"model": "m2", "acc": 0.92, "loss": 0.15},
        {"model": "m3", "acc": 0.88, "loss": 0.20},
    ]

    # Filter high accuracy, extract names
    best_models = list(map(
        lambda m: m["model"],
        filter(lambda m: m["acc"] > 0.87, metrics)
    ))

    print(f"Best models: {best_models}\n")

if __name__ == "__main__":
    example_map()
    example_filter()
    example_reduce()
    example_composition()
```

## Validation and Reflection

```python
# Create a script: validate_module.py

def validate_exercise():
    """Validate all exercise components"""
    print("=== Exercise 03 Validation ===\n")

    # Check 1: Type hints
    from ml_utils import metrics
    import inspect

    sig = inspect.signature(metrics.accuracy)
    print(f"✓ Type hints present in metrics.accuracy: {sig}")

    # Check 2: Decorators work
    from decorators import timing_decorator

    @timing_decorator
    def test_func():
        import time
        time.sleep(0.1)
        return "done"

    result = test_func()
    print(f"✓ Decorator executed: {result}")

    # Check 3: Module imports
    try:
        from ml_utils import metrics, preprocessing
        print(f"✓ Module imports successful")
    except ImportError as e:
        print(f"✗ Module import failed: {e}")

    # Check 4: Functions work correctly
    preds = [1, 0, 1, 1]
    labels = [1, 0, 0, 1]
    acc = metrics.accuracy(preds, labels)
    expected = 0.75
    assert abs(acc - expected) < 0.01, f"Expected {expected}, got {acc}"
    print(f"✓ Metrics calculation correct: {acc}")

    print("\n✓ All validations passed!")

if __name__ == "__main__":
    validate_exercise()
```

## Reflection Questions

1. When should you use type hints in production code?
2. How do decorators help make code more maintainable?
3. What are the benefits of organizing code into modules?
4. When should you use *args and **kwargs?
5. How does functional programming improve code readability?
6. What testing strategies should you use for utility functions?
7. How do you balance flexibility vs. simplicity in function design?

## Next Steps

After completing this exercise:
- **Exercise 04**: File I/O - Read and write ML data files
- **Exercise 05**: Error Handling - Build robust ML applications
- **Lecture 03**: Python DevOps Integration

## Additional Resources

- Type Hints: https://docs.python.org/3/library/typing.html
- Decorators Guide: https://realpython.com/primer-on-python-decorators/
- Python Modules: https://docs.python.org/3/tutorial/modules.html
- Functional Programming: https://docs.python.org/3/howto/functional.html

---

**Congratulations!** You've learned to create reusable, well-structured Python code for ML infrastructure. These patterns will serve you throughout your career in AI engineering.
