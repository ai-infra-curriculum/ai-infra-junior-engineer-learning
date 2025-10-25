# Exercise 05: Exception Handling for Robust ML Applications

## Overview

This exercise teaches you how to write robust, fault-tolerant Python code for machine learning infrastructure. You'll learn to handle errors gracefully, implement proper exception handling, create custom exceptions, and build resilient ML applications that can recover from failures.

## Learning Objectives

By completing this exercise, you will:
- Understand Python's exception hierarchy and handling mechanisms
- Implement try-except-finally blocks for error handling
- Create custom exceptions for domain-specific errors
- Use context managers for resource management
- Implement retry logic for transient failures
- Log errors effectively for debugging
- Build fault-tolerant ML pipelines
- Handle common ML-specific errors (GPU OOM, data corruption, etc.)

## Prerequisites

- Completed Exercises 01-04
- Understanding of ML workflows and common failure points
- Basic knowledge of logging

## Time Required

- Estimated: 90-120 minutes
- Difficulty: Intermediate

## Part 1: Understanding Python Exceptions

### Step 1: Common Exception Types

```python
# Create a script: exception_basics.py

def demonstrate_exceptions():
    """Demonstrate common exception types in ML workflows"""

    # ValueError: Invalid value
    try:
        batch_size = int("invalid")
    except ValueError as e:
        print(f"ValueError: {e}")

    # TypeError: Wrong type
    try:
        result = "text" + 123
    except TypeError as e:
        print(f"TypeError: {e}")

    # KeyError: Missing dictionary key
    try:
        config = {"learning_rate": 0.001}
        batch_size = config["batch_size"]
    except KeyError as e:
        print(f"KeyError: Missing {e}")

    # IndexError: Invalid index
    try:
        data = [1, 2, 3]
        value = data[10]
    except IndexError as e:
        print(f"IndexError: {e}")

    # FileNotFoundError: Missing file
    try:
        with open("nonexistent.txt", 'r') as f:
            content = f.read()
    except FileNotFoundError as e:
        print(f"FileNotFoundError: {e}")

    # ZeroDivisionError: Division by zero
    try:
        accuracy = correct_predictions / 0
    except ZeroDivisionError as e:
        print(f"ZeroDivisionError: {e}")

    # AttributeError: Missing attribute
    try:
        model = None
        model.predict([1, 2, 3])
    except AttributeError as e:
        print(f"AttributeError: {e}")

if __name__ == "__main__":
    demonstrate_exceptions()
```

### Step 2: Try-Except-Else-Finally

```python
# Create a script: exception_handling.py

from typing import List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def safe_divide(a: float, b: float) -> Optional[float]:
    """Safely divide two numbers"""
    try:
        result = a / b
    except ZeroDivisionError:
        logger.error(f"Cannot divide {a} by zero")
        return None
    except TypeError as e:
        logger.error(f"Invalid types for division: {e}")
        return None
    else:
        logger.info(f"Division successful: {a} / {b} = {result}")
        return result
    finally:
        logger.debug("Division operation completed")

def load_model_with_fallback(primary_path: str,
                             backup_path: str) -> Optional[dict]:
    """Load model with fallback to backup"""
    try:
        # Try primary path
        logger.info(f"Loading model from {primary_path}")
        with open(primary_path, 'r') as f:
            model = {"path": primary_path, "data": f.read()}
            return model
    except FileNotFoundError:
        logger.warning(f"Primary model not found, trying backup")

        try:
            # Try backup path
            with open(backup_path, 'r') as f:
                model = {"path": backup_path, "data": f.read()}
                return model
        except FileNotFoundError:
            logger.error("Both primary and backup models not found")
            return None
    finally:
        logger.info("Model loading attempt completed")

def process_batch_safe(batch: List[float]) -> dict:
    """Process batch with comprehensive error handling"""
    results = {
        "processed": [],
        "errors": [],
        "stats": {}
    }

    try:
        if not batch:
            raise ValueError("Empty batch provided")

        for i, value in enumerate(batch):
            try:
                # Simulate processing
                processed = value * 2
                results["processed"].append(processed)
            except TypeError:
                results["errors"].append(f"Index {i}: Invalid type {type(value)}")
                results["processed"].append(None)

        # Calculate stats
        valid_values = [v for v in results["processed"] if v is not None]
        if valid_values:
            results["stats"] = {
                "mean": sum(valid_values) / len(valid_values),
                "count": len(valid_values)
            }

    except ValueError as e:
        logger.error(f"Batch processing failed: {e}")
        results["errors"].append(str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        results["errors"].append(f"Unexpected: {str(e)}")
    finally:
        logger.info(f"Processed {len(results['processed'])} items, "
                   f"{len(results['errors'])} errors")

    return results

# Example usage
if __name__ == "__main__":
    # Test safe division
    print("=== Safe Division ===")
    print(safe_divide(10, 2))
    print(safe_divide(10, 0))
    print(safe_divide("10", 2))
    print()

    # Test batch processing
    print("=== Batch Processing ===")
    batch = [1.0, 2.0, "invalid", 4.0, 5.0]
    results = process_batch_safe(batch)
    print(f"Results: {results}")
```

## Part 2: Custom Exceptions

### Step 3: Creating Domain-Specific Exceptions

```python
# Create a script: custom_exceptions.py

class MLException(Exception):
    """Base exception for ML operations"""
    pass

class ModelNotFoundError(MLException):
    """Raised when model file is not found"""
    def __init__(self, model_path: str):
        self.model_path = model_path
        super().__init__(f"Model not found: {model_path}")

class InvalidDataError(MLException):
    """Raised when data validation fails"""
    def __init__(self, message: str, data_info: dict = None):
        self.data_info = data_info
        super().__init__(message)

class GPUOutOfMemoryError(MLException):
    """Raised when GPU runs out of memory"""
    def __init__(self, batch_size: int, model_size: int):
        self.batch_size = batch_size
        self.model_size = model_size
        super().__init__(
            f"GPU OOM: batch_size={batch_size}, model_size={model_size}MB"
        )

class TrainingFailedError(MLException):
    """Raised when training fails"""
    def __init__(self, epoch: int, reason: str):
        self.epoch = epoch
        self.reason = reason
        super().__init__(f"Training failed at epoch {epoch}: {reason}")

class ConfigurationError(MLException):
    """Raised when configuration is invalid"""
    def __init__(self, param: str, value, expected: str):
        self.param = param
        self.value = value
        self.expected = expected
        super().__init__(
            f"Invalid config: {param}={value}, expected {expected}"
        )

# Example usage
def load_model(model_path: str) -> dict:
    """Load model or raise custom exception"""
    import os

    if not os.path.exists(model_path):
        raise ModelNotFoundError(model_path)

    # Simulate loading
    return {"path": model_path, "loaded": True}

def validate_data(data: list) -> None:
    """Validate data or raise exception"""
    if not data:
        raise InvalidDataError(
            "Dataset is empty",
            data_info={"size": 0, "type": type(data)}
        )

    if len(data) < 10:
        raise InvalidDataError(
            "Dataset too small",
            data_info={"size": len(data), "minimum": 10}
        )

def validate_config(config: dict) -> None:
    """Validate configuration"""
    required_params = ["learning_rate", "batch_size", "epochs"]

    for param in required_params:
        if param not in config:
            raise ConfigurationError(param, None, "required parameter")

    if not 0 < config["learning_rate"] < 1:
        raise ConfigurationError(
            "learning_rate",
            config["learning_rate"],
            "0 < lr < 1"
        )

    if config["batch_size"] <= 0:
        raise ConfigurationError(
            "batch_size",
            config["batch_size"],
            "positive integer"
        )

# Test custom exceptions
if __name__ == "__main__":
    print("=== Testing Custom Exceptions ===\n")

    # Test ModelNotFoundError
    try:
        model = load_model("/nonexistent/model.h5")
    except ModelNotFoundError as e:
        print(f"Caught: {e}")
        print(f"Model path: {e.model_path}\n")

    # Test InvalidDataError
    try:
        validate_data([])
    except InvalidDataError as e:
        print(f"Caught: {e}")
        print(f"Data info: {e.data_info}\n")

    # Test ConfigurationError
    try:
        config = {"learning_rate": 1.5, "batch_size": 32}
        validate_config(config)
    except ConfigurationError as e:
        print(f"Caught: {e}")
        print(f"Parameter: {e.param}, Value: {e.value}\n")
```

## Part 3: Retry Logic and Resilience

### Step 4: Implementing Retry Mechanisms

```python
# Create a script: retry_logic.py

import time
import random
from typing import Callable, Any, Optional
from functools import wraps
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def retry_with_backoff(max_retries: int = 3,
                      initial_delay: float = 1.0,
                      backoff_factor: float = 2.0,
                      exceptions: tuple = (Exception,)):
    """
    Decorator for retry with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        backoff_factor: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch and retry
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            delay = initial_delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt == max_retries:
                        logger.error(
                            f"{func.__name__} failed after {max_retries} retries"
                        )
                        raise

                    logger.warning(
                        f"{func.__name__} failed (attempt {attempt + 1}/{max_retries}). "
                        f"Retrying in {delay}s... Error: {e}"
                    )

                    time.sleep(delay)
                    delay *= backoff_factor

            # Should not reach here, but just in case
            raise last_exception

        return wrapper
    return decorator

@retry_with_backoff(max_retries=3, initial_delay=0.5)
def download_model(model_url: str) -> dict:
    """Simulate model download with potential failures"""
    if random.random() < 0.7:  # 70% failure rate
        raise ConnectionError(f"Failed to download from {model_url}")

    logger.info(f"Successfully downloaded model from {model_url}")
    return {"url": model_url, "status": "downloaded"}

@retry_with_backoff(max_retries=5, initial_delay=1.0, backoff_factor=1.5)
def load_from_storage(file_path: str) -> dict:
    """Load file with retry logic"""
    if random.random() < 0.5:  # 50% failure rate
        raise IOError(f"Storage temporarily unavailable: {file_path}")

    return {"path": file_path, "data": "model_weights"}

class ResilientDataLoader:
    """Data loader with automatic retry and fallback"""

    def __init__(self, primary_source: str, backup_sources: list):
        self.primary_source = primary_source
        self.backup_sources = backup_sources

    def load_data(self) -> Optional[dict]:
        """Load data with fallback to backup sources"""
        sources = [self.primary_source] + self.backup_sources

        for i, source in enumerate(sources):
            try:
                logger.info(f"Attempting to load from source {i + 1}: {source}")
                data = self._load_from_source(source)
                logger.info(f"Successfully loaded from {source}")
                return data
            except Exception as e:
                logger.warning(f"Failed to load from {source}: {e}")

                if i == len(sources) - 1:
                    logger.error("All data sources failed")
                    return None

        return None

    @retry_with_backoff(max_retries=2, initial_delay=0.5)
    def _load_from_source(self, source: str) -> dict:
        """Load from specific source"""
        if random.random() < 0.6:  # 60% failure rate
            raise IOError(f"Source unavailable: {source}")

        return {"source": source, "data": [1, 2, 3, 4, 5]}

# Example usage
if __name__ == "__main__":
    print("=== Testing Retry Logic ===\n")

    # Test download with retries
    try:
        result = download_model("https://example.com/model.h5")
        print(f"Download result: {result}\n")
    except ConnectionError as e:
        print(f"Download failed: {e}\n")

    # Test storage loading
    try:
        data = load_from_storage("/storage/model.pkl")
        print(f"Loaded: {data}\n")
    except IOError as e:
        print(f"Load failed: {e}\n")

    # Test resilient loader
    loader = ResilientDataLoader(
        primary_source="s3://primary/data",
        backup_sources=["s3://backup1/data", "s3://backup2/data"]
    )

    data = loader.load_data()
    if data:
        print(f"Data loaded: {data}")
    else:
        print("Failed to load from all sources")
```

## Part 4: Context Managers

### Step 5: Safe Resource Management

```python
# Create a script: context_managers.py

from typing import Optional
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GPUContext:
    """Context manager for GPU operations"""

    def __init__(self, device_id: int = 0):
        self.device_id = device_id
        self.previous_device = None

    def __enter__(self):
        logger.info(f"Allocating GPU {self.device_id}")
        # Simulate GPU allocation
        self.previous_device = 0
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.info(f"Releasing GPU {self.device_id}")

        if exc_type is not None:
            logger.error(f"GPU operation failed: {exc_val}")

        # Clean up GPU memory
        # Return False to propagate exceptions
        return False

class ModelCheckpoint:
    """Context manager for model checkpointing"""

    def __init__(self, checkpoint_path: str):
        self.checkpoint_path = checkpoint_path
        self.temp_path = f"{checkpoint_path}.tmp"

    def __enter__(self):
        logger.info(f"Starting checkpoint to {self.checkpoint_path}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            # Success: rename temp to final
            logger.info("Checkpoint successful")
            # os.rename(self.temp_path, self.checkpoint_path)
        else:
            # Failure: remove temp file
            logger.error(f"Checkpoint failed: {exc_val}")
            # os.remove(self.temp_path)

        return False

class TimerContext:
    """Context manager for timing code blocks"""

    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        logger.info(f"Starting: {self.name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.time() - self.start_time
        logger.info(f"{self.name} took {elapsed:.4f} seconds")
        return False

# Example usage
def train_with_context():
    """Train model using context managers"""

    with GPUContext(device_id=0):
        logger.info("Training on GPU...")

        with TimerContext("Training epoch"):
            # Simulate training
            time.sleep(0.5)

        with ModelCheckpoint("model_checkpoint.h5"):
            logger.info("Saving checkpoint...")
            # Simulate saving
            time.sleep(0.2)

if __name__ == "__main__":
    print("=== Context Manager Examples ===\n")
    train_with_context()
```

## Part 5: Comprehensive Error Handling System

### Step 6: Building a Robust ML Pipeline

```python
# Create a script: ml_pipeline_robust.py

from typing import Optional, Dict, Any, List
import logging
from dataclasses import dataclass
from enum import Enum

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PipelineStatus(Enum):
    """Pipeline execution status"""
    SUCCESS = "success"
    PARTIAL_FAILURE = "partial_failure"
    COMPLETE_FAILURE = "failure"
    RETRYING = "retrying"

@dataclass
class PipelineResult:
    """Result of pipeline execution"""
    status: PipelineStatus
    data: Optional[Any]
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]

class RobustMLPipeline:
    """ML pipeline with comprehensive error handling"""

    def __init__(self, config: dict):
        self.config = config
        self.errors = []
        self.warnings = []

    def run(self) -> PipelineResult:
        """Execute pipeline with error handling"""
        logger.info("Starting ML pipeline")
        data = None

        try:
            # Step 1: Load data
            data = self._load_data_safe()
            if data is None:
                return self._create_failure_result("Data loading failed")

            # Step 2: Validate data
            if not self._validate_data_safe(data):
                return self._create_failure_result("Data validation failed")

            # Step 3: Preprocess
            data = self._preprocess_safe(data)
            if data is None:
                return self._create_failure_result("Preprocessing failed")

            # Step 4: Train model
            model = self._train_safe(data)
            if model is None:
                return self._create_failure_result("Training failed")

            # Step 5: Evaluate
            metrics = self._evaluate_safe(model, data)

            # Success
            return PipelineResult(
                status=PipelineStatus.SUCCESS,
                data={"model": model, "metrics": metrics},
                errors=self.errors,
                warnings=self.warnings,
                metadata={"steps_completed": 5}
            )

        except Exception as e:
            logger.error(f"Unexpected pipeline error: {e}")
            return self._create_failure_result(f"Unexpected error: {str(e)}")

    def _load_data_safe(self) -> Optional[dict]:
        """Load data with error handling"""
        try:
            logger.info("Loading data...")
            # Simulate data loading
            data = {"samples": 1000, "features": 10}
            return data
        except FileNotFoundError as e:
            self.errors.append(f"Data file not found: {e}")
            logger.error(f"Data loading failed: {e}")
            return None
        except Exception as e:
            self.errors.append(f"Data loading error: {e}")
            logger.error(f"Unexpected data loading error: {e}")
            return None

    def _validate_data_safe(self, data: dict) -> bool:
        """Validate data with error handling"""
        try:
            logger.info("Validating data...")

            if data.get("samples", 0) < 10:
                self.errors.append("Insufficient samples")
                return False

            if data.get("features", 0) < 1:
                self.errors.append("No features found")
                return False

            return True

        except Exception as e:
            self.errors.append(f"Validation error: {e}")
            logger.error(f"Validation failed: {e}")
            return False

    def _preprocess_safe(self, data: dict) -> Optional[dict]:
        """Preprocess data with error handling"""
        try:
            logger.info("Preprocessing data...")
            # Simulate preprocessing
            processed = {**data, "preprocessed": True}
            return processed
        except Exception as e:
            self.errors.append(f"Preprocessing error: {e}")
            logger.error(f"Preprocessing failed: {e}")
            return None

    def _train_safe(self, data: dict) -> Optional[dict]:
        """Train model with error handling"""
        try:
            logger.info("Training model...")
            # Simulate training
            model = {"trained": True, "accuracy": 0.92}
            return model
        except MemoryError as e:
            self.errors.append("Out of memory during training")
            logger.error(f"Training failed: OOM")
            return None
        except Exception as e:
            self.errors.append(f"Training error: {e}")
            logger.error(f"Training failed: {e}")
            return None

    def _evaluate_safe(self, model: dict, data: dict) -> dict:
        """Evaluate model with error handling"""
        try:
            logger.info("Evaluating model...")
            metrics = {"accuracy": 0.92, "loss": 0.15}
            return metrics
        except Exception as e:
            self.warnings.append(f"Evaluation error: {e}")
            logger.warning(f"Evaluation failed: {e}")
            return {}

    def _create_failure_result(self, error_msg: str) -> PipelineResult:
        """Create failure result"""
        self.errors.append(error_msg)
        return PipelineResult(
            status=PipelineStatus.COMPLETE_FAILURE,
            data=None,
            errors=self.errors,
            warnings=self.warnings,
            metadata={}
        )

# Example usage
if __name__ == "__main__":
    print("=== Robust ML Pipeline ===\n")

    config = {
        "data_path": "/data/train.csv",
        "model_type": "resnet",
        "epochs": 100
    }

    pipeline = RobustMLPipeline(config)
    result = pipeline.run()

    print(f"Status: {result.status.value}")
    print(f"Errors: {result.errors}")
    print(f"Warnings: {result.warnings}")
    print(f"Metadata: {result.metadata}")

    if result.status == PipelineStatus.SUCCESS:
        print(f"Model trained successfully!")
        print(f"Metrics: {result.data['metrics']}")
```

## Validation

```python
# Create a script: validate_error_handling.py

def test_exception_handling():
    """Test exception handling works correctly"""
    try:
        value = 10 / 0
    except ZeroDivisionError:
        print("✓ Caught ZeroDivisionError")

    try:
        data = {"a": 1}
        _ = data["b"]
    except KeyError:
        print("✓ Caught KeyError")

def test_custom_exceptions():
    """Test custom exceptions"""
    from custom_exceptions import ConfigurationError

    try:
        raise ConfigurationError("test_param", 123, "string")
    except ConfigurationError as e:
        assert e.param == "test_param"
        print("✓ Custom exception works")

def test_retry_logic():
    """Test retry decorator"""
    from retry_logic import retry_with_backoff

    @retry_with_backoff(max_retries=2, initial_delay=0.1)
    def flaky_function():
        import random
        if random.random() < 0.5:
            raise ValueError("Random failure")
        return "success"

    try:
        result = flaky_function()
        print(f"✓ Retry logic works: {result}")
    except ValueError:
        print("✓ Retry logic attempted retries")

if __name__ == "__main__":
    print("=== Error Handling Validation ===\n")
    test_exception_handling()
    test_custom_exceptions()
    test_retry_logic()
    print("\n✓ All tests passed!")
```

## Reflection Questions

1. When should you catch broad vs. specific exceptions?
2. How do custom exceptions improve code maintainability?
3. What retry strategies work best for different failure types?
4. How do context managers ensure proper resource cleanup?
5. What information should be logged when exceptions occur?
6. How do you balance error handling with code readability?
7. When should exceptions be raised vs. returned as error codes?

## Next Steps

- **Exercise 06**: Async Programming for concurrent operations
- **Exercise 07**: Testing your error handling code
- **Module 002**: Linux Essentials

## Additional Resources

- Python Exceptions: https://docs.python.org/3/tutorial/errors.html
- Logging HOWTO: https://docs.python.org/3/howto/logging.html
- Context Managers: https://docs.python.org/3/reference/datamodel.html#context-managers

---

**Congratulations!** You've learned to build robust, fault-tolerant ML applications that handle errors gracefully and recover from failures effectively.
