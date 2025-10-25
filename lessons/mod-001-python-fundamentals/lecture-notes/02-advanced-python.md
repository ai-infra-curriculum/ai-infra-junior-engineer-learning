# Lecture 02: Advanced Python for Infrastructure - Type Hints, Logging, and Configuration

## Table of Contents
1. [Introduction](#introduction)
2. [Type Hints and Static Typing](#type-hints-and-static-typing)
3. [Production Logging Strategies](#production-logging-strategies)
4. [Configuration Management](#configuration-management)
5. [Working with Data Formats](#working-with-data-formats)
6. [Error Handling Patterns](#error-handling-patterns)
7. [Summary and Best Practices](#summary-and-best-practices)

---

## Introduction

### The Production Code Challenge

Writing code that works is easy. Writing code that:
- **Works reliably** in production
- **Can be debugged** when things go wrong
- **Is maintained** by other engineers
- **Handles** unexpected inputs gracefully
- **Scales** from development to enterprise

...is the challenge of infrastructure engineering.

This lecture covers three pillars of production-grade Python:

1. **Type Hints**: Make code self-documenting and catch errors before runtime
2. **Logging**: Understand what's happening in production systems
3. **Configuration Management**: Run the same code across multiple environments

### Why These Matter for AI Infrastructure

**Type Hints**: ML pipelines involve complex data structures (tensors, dataframes, model configs). Type hints prevent passing a `List[Dict]` where you expected `pd.DataFrame`.

**Logging**: When a model serving endpoint returns wrong predictions at 3 AM, logs are your only window into what happened.

**Configuration**: Training hyperparameters, model paths, API endpoints—all differ between dev, staging, and production. Configuration management keeps this maintainable.

### Learning Objectives

By the end of this lecture, you will:
- Write comprehensively type-hinted Python code
- Use mypy for static type checking
- Implement structured logging for production systems
- Design configuration systems for multiple environments
- Handle different data formats (JSON, YAML, TOML)
- Apply error handling patterns for infrastructure code

---

## Type Hints and Static Typing

### Why Type Hints?

Consider this function:

```python
def train_model(data, config, epochs):
    # What are these types?
    # data: DataFrame? List? numpy array?
    # config: dict? object? string path?
    # epochs: int? string?
    pass
```

Now with type hints:

```python
import pandas as pd
from typing import Dict, Any

def train_model(
    data: pd.DataFrame,
    config: Dict[str, Any],
    epochs: int
) -> Dict[str, float]:
    """Train ML model with given data and configuration.

    Returns metrics dict with training/validation loss.
    """
    pass
```

**Immediately clearer**:
- `data` must be a pandas DataFrame
- `config` is a dictionary with string keys
- `epochs` is an integer
- Returns a dict mapping metric names to float values

### Basic Type Annotations

#### Primitive Types

```python
# Basic types
name: str = "model-v1"
version: int = 42
learning_rate: float = 0.001
is_training: bool = True

# Function parameters and return
def get_batch_size(training: bool) -> int:
    return 32 if training else 64

# None type
def log_message(message: str) -> None:
    print(message)
```

#### Collection Types

```python
from typing import List, Dict, Set, Tuple

# List of strings
model_names: List[str] = ["bert", "gpt", "t5"]

# Dict mapping strings to integers
layer_sizes: Dict[str, int] = {
    "input": 768,
    "hidden": 1024,
    "output": 512
}

# Set of unique identifiers
seen_ids: Set[int] = {1, 2, 3}

# Tuple with fixed size and types
dimensions: Tuple[int, int, int] = (224, 224, 3)

# Tuple with variable length (all same type)
from typing import Tuple
scores: Tuple[float, ...] = (0.9, 0.85, 0.92, 0.88)
```

#### Optional and Union Types

```python
from typing import Optional, Union

# Optional means "could be None"
def load_checkpoint(path: Optional[str] = None) -> Dict[str, Any]:
    if path is None:
        return {}
    # load from path

# Modern syntax (Python 3.10+)
def load_checkpoint(path: str | None = None) -> Dict[str, Any]:
    pass

# Union of multiple types
from typing import Union
def process_input(data: Union[str, bytes, List[str]]) -> str:
    if isinstance(data, str):
        return data
    elif isinstance(data, bytes):
        return data.decode()
    else:
        return " ".join(data)

# Modern union syntax (Python 3.10+)
def process_input(data: str | bytes | List[str]) -> str:
    pass
```

#### Complex Types

```python
from typing import List, Dict, Any, Callable

# Nested structures
ModelConfig = Dict[str, Any]
TrainingConfigs = Dict[str, ModelConfig]

configs: TrainingConfigs = {
    "bert": {"layers": 12, "hidden_size": 768},
    "gpt": {"layers": 24, "hidden_size": 1024}
}

# Callable (function) types
ProcessingFunction = Callable[[str], str]

def apply_processing(text: str, func: ProcessingFunction) -> str:
    return func(text)

# More specific callable
from typing import Callable
MetricCalculator = Callable[[List[float], List[float]], float]

def evaluate(
    predictions: List[float],
    labels: List[float],
    metric_fn: MetricCalculator
) -> float:
    return metric_fn(predictions, labels)
```

### Type Aliases for Readability

```python
from typing import Dict, List, Tuple, Any

# Define once, reuse everywhere
ModelPath = str
Hyperparameters = Dict[str, Any]
TrainingData = List[Tuple[str, int]]
Metrics = Dict[str, float]

def train_model(
    model_path: ModelPath,
    hyperparams: Hyperparameters,
    data: TrainingData
) -> Metrics:
    """Much more readable than raw types"""
    pass

# For ML infrastructure
import pandas as pd
import torch

DataFrame = pd.DataFrame
Tensor = torch.Tensor
Device = torch.device

def prepare_batch(
    df: DataFrame,
    device: Device
) -> Tensor:
    pass
```

### Advanced Type Hints

#### Generic Types

```python
from typing import TypeVar, Generic, List

T = TypeVar('T')

class DataLoader(Generic[T]):
    """Generic data loader for any type"""

    def __init__(self, data: List[T]):
        self.data = data

    def get_batch(self, size: int) -> List[T]:
        return self.data[:size]

# Use with specific types
int_loader: DataLoader[int] = DataLoader([1, 2, 3])
str_loader: DataLoader[str] = DataLoader(["a", "b", "c"])
```

#### Protocol Types (Structural Subtyping)

```python
from typing import Protocol

class ModelProtocol(Protocol):
    """Any class with these methods is a "Model" """

    def train(self, data: Any) -> None: ...
    def predict(self, input: Any) -> Any: ...

def train_and_evaluate(model: ModelProtocol, data: Any) -> float:
    """Accepts any object with train() and predict() methods"""
    model.train(data)
    predictions = model.predict(data)
    return evaluate(predictions)

# Both work without inheritance!
class PyTorchModel:
    def train(self, data): pass
    def predict(self, input): pass

class TensorFlowModel:
    def train(self, data): pass
    def predict(self, input): pass
```

#### Literal Types

```python
from typing import Literal

ModelType = Literal["bert", "gpt", "t5"]

def load_model(model_type: ModelType) -> Any:
    """model_type must be exactly one of these strings"""
    if model_type == "bert":
        return BertModel()
    elif model_type == "gpt":
        return GPTModel()
    else:
        return T5Model()

# Type checker ensures only valid values
load_model("bert")     # ✓ OK
load_model("invalid")  # ✗ Type error
```

### Using mypy for Type Checking

Install mypy:
```bash
pip install mypy
```

**Example code** (`training.py`):
```python
from typing import List, Dict

def calculate_average(numbers: List[float]) -> float:
    return sum(numbers) / len(numbers)

def main() -> None:
    scores: List[float] = [0.9, 0.85, 0.92]
    avg: str = calculate_average(scores)  # Type error!
    print(avg)
```

**Run mypy**:
```bash
mypy training.py
```

**Output**:
```
training.py:8: error: Incompatible types in assignment (expression has type "float", variable has type "str")
Found 1 error in 1 file (checked 1 source file)
```

#### Mypy Configuration

Create `mypy.ini` or add to `pyproject.toml`:

```ini
# mypy.ini
[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True  # All functions must have types
disallow_incomplete_defs = True
check_untyped_defs = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_unreachable = True
strict_equality = True

# Per-module settings
[mypy-numpy.*]
ignore_missing_imports = True  # Numpy doesn't have complete type stubs

[mypy-pandas.*]
ignore_missing_imports = True
```

**Or in pyproject.toml**:
```toml
[tool.mypy]
python_version = "3.11"
disallow_untyped_defs = true
warn_return_any = true
no_implicit_optional = true
```

#### Gradual Typing Strategy

Don't type everything at once. Start with:

**Level 1: Type function signatures**
```python
def train_model(config: Dict, data: Any) -> Any:
    # Function body not typed yet
    pass
```

**Level 2: Type critical functions completely**
```python
def train_model(
    config: Dict[str, Any],
    data: pd.DataFrame
) -> Dict[str, float]:
    epochs: int = config["epochs"]
    batch_size: int = config["batch_size"]
    # ...
    return {"loss": 0.5, "accuracy": 0.95}
```

**Level 3: Enable strict mode**
```python
# Add to top of file
# mypy: strict

# or use --strict flag
# mypy --strict training.py
```

---

## Production Logging Strategies

### Why Logging Matters

**Scenario**: Model serving API returns incorrect predictions. Without logging:
- No idea what input caused the issue
- Don't know which code path executed
- Can't reproduce the error
- Can't see performance metrics

**With proper logging**:
- Trace exact request that failed
- See model version, input features, prediction
- Identify if it's data issue, model issue, or code bug
- Measure latency, throughput, error rates

### Python's Logging Module

```python
import logging

# Basic logging
logging.debug("Detailed information for debugging")
logging.info("General informational messages")
logging.warning("Warning: something unexpected happened")
logging.error("Error: something failed")
logging.critical("Critical: system is unusable")
```

**Log levels**:
```
DEBUG    (10): Detailed diagnostic information
INFO     (20): Confirmation things are working
WARNING  (30): Something unexpected but handled
ERROR    (40): Serious problem, function failed
CRITICAL (50): System-level failure
```

### Configuring Logging

#### Basic Configuration

```python
import logging

# Configure logging at application startup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

logger.info("Application started")
logger.warning("Configuration file not found, using defaults")
```

**Output**:
```
2025-10-18 10:30:45 - __main__ - INFO - Application started
2025-10-18 10:30:45 - __main__ - WARNING - Configuration file not found, using defaults
```

#### Logger Hierarchy

```python
# File: ml_pipeline/training/trainer.py
logger = logging.getLogger(__name__)  # Creates: ml_pipeline.training.trainer

# File: ml_pipeline/data/loader.py
logger = logging.getLogger(__name__)  # Creates: ml_pipeline.data.loader

# Configure root or parent loggers
logging.getLogger("ml_pipeline").setLevel(logging.INFO)
logging.getLogger("ml_pipeline.training").setLevel(logging.DEBUG)  # More verbose
```

### Advanced Logging Configuration

#### Multiple Handlers

```python
import logging
from logging.handlers import RotatingFileHandler
import sys

def setup_logging():
    # Create logger
    logger = logging.getLogger("ml_pipeline")
    logger.setLevel(logging.DEBUG)

    # Console handler (INFO and above)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_format)

    # File handler (DEBUG and above, with rotation)
    file_handler = RotatingFileHandler(
        'ml_pipeline.log',
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_format)

    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

logger = setup_logging()
logger.info("Logging configured")
```

#### Structured Logging (JSON)

For centralized logging systems (ELK, Datadog, CloudWatch):

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add custom fields
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id

        return json.dumps(log_data)

# Setup
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger("api")
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Use with extra context
logger.info(
    "Model prediction completed",
    extra={
        "user_id": "user123",
        "request_id": "req-456",
        "model_version": "v2.1",
        "latency_ms": 45
    }
)
```

**Output**:
```json
{
  "timestamp": "2025-10-18T10:30:45.123456",
  "level": "INFO",
  "logger": "api",
  "message": "Model prediction completed",
  "module": "serving",
  "function": "predict",
  "line": 42,
  "user_id": "user123",
  "request_id": "req-456",
  "model_version": "v2.1",
  "latency_ms": 45
}
```

### Logging Best Practices for ML Systems

#### 1. Log at Appropriate Levels

```python
logger = logging.getLogger(__name__)

# DEBUG: Detailed diagnostic info
logger.debug(f"Processing batch {batch_id}, shape: {data.shape}")
logger.debug(f"Model weights: {model.state_dict().keys()}")

# INFO: Major steps, milestones
logger.info("Training started for model v2.1")
logger.info(f"Epoch {epoch}/{total_epochs} completed, loss: {loss:.4f}")
logger.info("Model saved to /models/checkpoint-100.pt")

# WARNING: Unexpected but handled
logger.warning("GPU not available, falling back to CPU")
logger.warning(f"Validation loss increased: {prev_loss:.4f} -> {curr_loss:.4f}")

# ERROR: Operation failed
logger.error(f"Failed to load checkpoint: {checkpoint_path}")
logger.error("Model prediction failed", exc_info=True)  # Includes traceback

# CRITICAL: System failure
logger.critical("Out of memory, cannot continue training")
```

#### 2. Include Context

```python
# Bad: Not enough context
logger.info("Training complete")

# Good: Includes relevant details
logger.info(
    f"Training complete - model: {model_name}, "
    f"epochs: {epochs}, final_loss: {final_loss:.4f}, "
    f"duration: {duration:.2f}s"
)

# Bad: Just the error
logger.error("Prediction failed")

# Good: Includes context for debugging
logger.error(
    f"Prediction failed for input shape {input_shape}, "
    f"model_version: {model_version}, "
    f"error: {str(e)}"
)
```

#### 3. Use Structured Logging

```python
import logging
import structlog

# Configure structlog
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger()

# Log with structured context
logger.info(
    "model_prediction",
    model_id="bert-v2",
    input_length=512,
    prediction_confidence=0.95,
    latency_ms=23
)
```

#### 4. Context Managers for Request Tracing

```python
import logging
from contextlib import contextmanager
import uuid

logger = logging.getLogger(__name__)

@contextmanager
def request_context(request_id: str | None = None):
    """Add request ID to all logs within context"""
    if request_id is None:
        request_id = str(uuid.uuid4())

    # Create logger adapter that adds request_id
    adapter = logging.LoggerAdapter(
        logger,
        {"request_id": request_id}
    )

    try:
        yield adapter
    finally:
        pass

# Usage
def handle_prediction(input_data):
    with request_context() as log:
        log.info("Prediction request received")

        result = model.predict(input_data)
        log.info(f"Prediction completed: {result}")

        return result

# All logs include request_id automatically!
```

---

## Configuration Management

### The Configuration Challenge

Same code, different environments:

```
Development:
- Model: /local/models/dev-model.pt
- Database: localhost:5432
- Log level: DEBUG
- Batch size: 8 (small for quick testing)

Staging:
- Model: s3://staging-models/model-v2.pt
- Database: staging-db.internal:5432
- Log level: INFO
- Batch size: 32

Production:
- Model: s3://prod-models/model-v2.1.pt
- Database: prod-db-replica.internal:5432
- Log level: WARNING
- Batch size: 128
- TLS: Required
```

**Goal**: Single codebase, configuration drives behavior.

### Configuration Strategies

#### 1. Environment Variables

```python
import os

# Read from environment
MODEL_PATH = os.getenv("MODEL_PATH", "/default/model.pt")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "32"))
DEBUG_MODE = os.getenv("DEBUG", "false").lower() == "true"

# Validate required variables
DB_HOST = os.environ["DB_HOST"]  # Raises KeyError if missing
```

**Set environment variables**:
```bash
# Development
export MODEL_PATH=/local/models/dev-model.pt
export BATCH_SIZE=8
export DEBUG=true

# Or in one line
MODEL_PATH=/local/models/dev-model.pt python train.py
```

#### 2. .env Files

Install python-dotenv:
```bash
pip install python-dotenv
```

**`.env` file**:
```bash
# .env
MODEL_PATH=/local/models/model.pt
BATCH_SIZE=32
LEARNING_RATE=0.001
DB_HOST=localhost
DB_PORT=5432
DB_PASSWORD=secretpassword
```

**Load in Python**:
```python
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Now read from environment
model_path = os.getenv("MODEL_PATH")
batch_size = int(os.getenv("BATCH_SIZE"))
```

**Multiple environment files**:
```bash
.env                 # Default
.env.development     # Development overrides
.env.staging         # Staging overrides
.env.production      # Production overrides
```

```python
from dotenv import load_dotenv
import os

# Load based on environment
env = os.getenv("ENVIRONMENT", "development")
load_dotenv(f".env.{env}")
```

#### 3. Configuration Files (YAML)

**config.yaml**:
```yaml
# config.yaml
application:
  name: ml-training-pipeline
  version: 2.1.0

model:
  path: /models/bert-base
  type: bert
  max_length: 512

training:
  batch_size: 32
  learning_rate: 0.001
  epochs: 10
  device: cuda

database:
  host: localhost
  port: 5432
  name: ml_data
  pool_size: 10

logging:
  level: INFO
  format: json
  handlers:
    - type: console
    - type: file
      path: /var/log/ml-training.log
```

**Load YAML config**:
```python
import yaml
from typing import Dict, Any

def load_config(path: str) -> Dict[str, Any]:
    with open(path, 'r') as f:
        return yaml.safe_load(f)

config = load_config('config.yaml')

batch_size = config['training']['batch_size']
model_path = config['model']['path']
db_host = config['database']['host']
```

#### 4. Validated Configuration with Pydantic

```python
from pydantic import BaseModel, Field, validator
from typing import Literal
import yaml

class ModelConfig(BaseModel):
    path: str
    type: Literal["bert", "gpt", "t5"]
    max_length: int = Field(gt=0, le=2048)

class TrainingConfig(BaseModel):
    batch_size: int = Field(gt=0)
    learning_rate: float = Field(gt=0, lt=1)
    epochs: int = Field(gt=0)
    device: Literal["cuda", "cpu"] = "cuda"

    @validator("batch_size")
    def validate_batch_size(cls, v):
        if v % 8 != 0:
            raise ValueError("batch_size must be multiple of 8")
        return v

class DatabaseConfig(BaseModel):
    host: str
    port: int = Field(ge=1, le=65535)
    name: str
    pool_size: int = Field(default=10, ge=1)

class AppConfig(BaseModel):
    model: ModelConfig
    training: TrainingConfig
    database: DatabaseConfig

# Load and validate
with open('config.yaml') as f:
    config_dict = yaml.safe_load(f)

config = AppConfig(**config_dict)  # Validates all fields!

# Type-safe access
batch_size: int = config.training.batch_size
model_path: str = config.model.path
```

**Benefits**:
- Type safety
- Automatic validation
- Clear error messages
- IDE autocomplete
- Documentation via field descriptions

#### 5. Hierarchical Configuration

```python
from pathlib import Path
import yaml
from typing import Dict, Any

class Config:
    def __init__(self, environment: str = "development"):
        self.environment = environment
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load base config + environment overrides"""
        # Load base configuration
        base_config = self._load_yaml("config.yaml")

        # Load environment-specific overrides
        env_config_path = f"config.{self.environment}.yaml"
        if Path(env_config_path).exists():
            env_config = self._load_yaml(env_config_path)
            base_config = self._deep_merge(base_config, env_config)

        # Override with environment variables
        self._apply_env_overrides(base_config)

        return base_config

    def _load_yaml(self, path: str) -> Dict[str, Any]:
        with open(path) as f:
            return yaml.safe_load(f)

    def _deep_merge(
        self,
        base: Dict[str, Any],
        override: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Recursively merge override into base"""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def _apply_env_overrides(self, config: Dict[str, Any]) -> None:
        """Override config from environment variables"""
        import os

        # ML_TRAINING_BATCH_SIZE -> config['training']['batch_size']
        # ML_MODEL_PATH -> config['model']['path']
        for key, value in os.environ.items():
            if key.startswith("ML_"):
                self._set_nested(config, key[3:].lower().split('_'), value)

    def _set_nested(self, d: Dict, keys: list, value: str) -> None:
        """Set nested dict value from key path"""
        for key in keys[:-1]:
            d = d.setdefault(key, {})
        # Try to convert to appropriate type
        try:
            d[keys[-1]] = int(value)
        except ValueError:
            try:
                d[keys[-1]] = float(value)
            except ValueError:
                d[keys[-1]] = value

# Usage
config = Config(environment="production")
```

**Configuration precedence** (highest to lowest):
1. Environment variables (highest priority)
2. Environment-specific config file (config.production.yaml)
3. Base config file (config.yaml)
4. Code defaults (lowest priority)

---

## Working with Data Formats

### JSON

```python
import json
from typing import Dict, Any

# Write JSON
config: Dict[str, Any] = {
    "model": "bert-base",
    "batch_size": 32,
    "learning_rate": 0.001
}

with open("config.json", "w") as f:
    json.dump(config, f, indent=2)

# Read JSON
with open("config.json", "r") as f:
    loaded_config = json.load(f)

# JSON string
json_string = json.dumps(config)
parsed = json.loads(json_string)
```

### YAML

```python
import yaml

# Write YAML
config = {
    "model": {
        "name": "bert-base",
        "params": {
            "hidden_size": 768,
            "num_layers": 12
        }
    }
}

with open("config.yaml", "w") as f:
    yaml.dump(config, f, default_flow_style=False)

# Read YAML
with open("config.yaml", "r") as f:
    loaded = yaml.safe_load(f)  # Use safe_load!
```

### TOML

```python
import tomli  # Python 3.11+ has tomllib in stdlib
import tomli_w

# Write TOML
config = {
    "model": {
        "name": "bert-base",
        "hidden_size": 768
    },
    "training": {
        "batch_size": 32,
        "epochs": 10
    }
}

with open("config.toml", "wb") as f:
    tomli_w.dump(config, f)

# Read TOML
with open("config.toml", "rb") as f:
    loaded = tomli.load(f)
```

---

## Error Handling Patterns

### Specific Exception Handling

```python
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def load_model(path: str) -> Optional[Any]:
    try:
        model = torch.load(path)
        logger.info(f"Model loaded from {path}")
        return model
    except FileNotFoundError:
        logger.error(f"Model file not found: {path}")
        return None
    except torch.serialization.SerializationError:
        logger.error(f"Corrupted model file: {path}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error loading model: {e}", exc_info=True)
        raise
```

### Retry Logic for Infrastructure

```python
import time
import logging
from typing import Callable, TypeVar, Any

logger = logging.getLogger(__name__)
T = TypeVar('T')

def retry(
    func: Callable[..., T],
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0
) -> T:
    """Retry function with exponential backoff"""
    attempt = 0
    current_delay = delay

    while attempt < max_attempts:
        try:
            return func()
        except Exception as e:
            attempt += 1
            if attempt >= max_attempts:
                logger.error(f"Failed after {max_attempts} attempts")
                raise

            logger.warning(
                f"Attempt {attempt} failed: {e}. "
                f"Retrying in {current_delay}s..."
            )
            time.sleep(current_delay)
            current_delay *= backoff

# Usage
def fetch_data():
    # Might fail due to network issues
    response = requests.get("https://api.example.com/data")
    response.raise_for_status()
    return response.json()

data = retry(fetch_data, max_attempts=5, delay=2.0)
```

---

## Summary and Best Practices

### Type Hints Checklist

✅ Annotate all function signatures
✅ Use type aliases for complex types
✅ Enable mypy in CI/CD
✅ Use `Optional[T]` for nullable values
✅ Leverage `Protocol` for flexible interfaces
✅ Use `Literal` for fixed string choices

### Logging Checklist

✅ Configure logging at application startup
✅ Use appropriate log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
✅ Include context in log messages
✅ Use structured logging (JSON) for production
✅ Implement log rotation for file handlers
✅ Never log sensitive data (passwords, tokens)

### Configuration Checklist

✅ Never hardcode configuration
✅ Use environment variables for deployment-specific config
✅ Use `.env` files for development
✅ Validate configuration on startup
✅ Document all configuration options
✅ Provide sensible defaults
✅ Use configuration hierarchies (base + overrides)

---

**Lecture Version**: 1.0
**Last Updated**: October 2025
**Word Count**: ~4,200 words
**Estimated Reading Time**: 50-70 minutes

**Next**: Continue to `03-python-devops.md` for subprocess management, file operations, and CLI development.
