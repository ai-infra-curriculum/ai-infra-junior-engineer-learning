# Lecture 04: Python Data Structures & Comprehensions for AI Infrastructure

## Table of Contents
1. [Introduction](#introduction)
2. [Lists: Ordered Data Management](#lists-ordered-data-management)
3. [Dictionaries: Key-Value Mappings](#dictionaries-key-value-mappings)
4. [Sets: Unique Collections](#sets-unique-collections)
5. [Tuples: Immutable Data](#tuples-immutable-data)
6. [Comprehensions: Efficient Data Transformation](#comprehensions-efficient-data-transformation)
7. [Data Structure Selection Guide](#data-structure-selection-guide)
8. [Performance Considerations](#performance-considerations)
9. [Summary and Best Practices](#summary-and-best-practices)

---

## Introduction

### Why Data Structures Matter in AI Infrastructure

Every AI infrastructure engineer spends significant time manipulating data:
- **Processing batches** of training examples
- **Managing configurations** for experiments
- **Tracking metrics** from model runs
- **Deduplicating datasets** to avoid train/test leakage
- **Returning multiple values** from functions

Python's built-in data structures—lists, dictionaries, sets, and tuples—are the foundation for efficient data manipulation. Understanding when to use each structure, and how to transform data efficiently with comprehensions, is essential for writing performant infrastructure code.

### Learning Objectives

By the end of this lecture, you will:
- Understand the characteristics and use cases for each core Python data structure
- Apply lists, dictionaries, sets, and tuples to ML infrastructure scenarios
- Write efficient comprehensions for data transformation
- Select the appropriate data structure based on performance requirements
- Use advanced techniques like nested comprehensions and generator expressions

---

## Lists: Ordered Data Management

### What Are Lists?

Lists are **ordered, mutable sequences** that can contain any Python objects. They maintain insertion order and allow duplicate elements.

```python
# Creating lists
training_samples = [1, 2, 3, 4, 5]
model_names = ["resnet50", "vgg16", "efficientnet"]
mixed_data = [42, "text", 3.14, True, None]

# Empty list
experiments = []
```

### Essential List Operations

#### Adding Elements

```python
# Append: add to end (O(1) - constant time)
models = []
models.append("bert-base")
models.append("gpt2")
# Result: ["bert-base", "gpt2"]

# Extend: add multiple items
models.extend(["t5-small", "roberta"])
# Result: ["bert-base", "gpt2", "t5-small", "roberta"]

# Insert: add at specific position (O(n) - linear time)
models.insert(1, "distilbert")
# Result: ["bert-base", "distilbert", "gpt2", "t5-small", "roberta"]

# Concatenation: create new list
new_models = models + ["xlnet", "albert"]
```

#### Accessing Elements

```python
model_names = ["resnet50", "vgg16", "efficientnet", "mobilenet"]

# Indexing (O(1))
first_model = model_names[0]           # "resnet50"
last_model = model_names[-1]           # "mobilenet"
second_last = model_names[-2]          # "efficientnet"

# Slicing (creates new list)
first_two = model_names[0:2]           # ["resnet50", "vgg16"]
skip_first = model_names[1:]           # ["vgg16", "efficientnet", "mobilenet"]
last_two = model_names[-2:]            # ["efficientnet", "mobilenet"]
every_other = model_names[::2]         # ["resnet50", "efficientnet"]
reversed_list = model_names[::-1]      # ["mobilenet", "efficientnet", "vgg16", "resnet50"]
```

#### Modifying Lists

```python
metrics = [0.85, 0.90, 0.78, 0.92]

# Update single element
metrics[2] = 0.88  # [0.85, 0.90, 0.88, 0.92]

# Delete elements
del metrics[1]     # [0.85, 0.88, 0.92]
metrics.remove(0.88)  # [0.85, 0.92] - removes first occurrence
popped = metrics.pop()  # returns 0.92, metrics = [0.85]
metrics.clear()    # []
```

#### Searching and Counting

```python
batch_sizes = [32, 64, 32, 128, 32, 256]

# Check membership (O(n))
has_64 = 64 in batch_sizes  # True

# Count occurrences
count_32 = batch_sizes.count(32)  # 3

# Find index (raises ValueError if not found)
idx = batch_sizes.index(128)  # 3

# Length
total = len(batch_sizes)  # 6
```

### ML Infrastructure Use Cases for Lists

#### 1. Managing Training Batches

```python
from typing import List, Tuple
import numpy as np

def create_batches(
    data: List[np.ndarray],
    batch_size: int
) -> List[List[np.ndarray]]:
    """Split dataset into batches for training."""
    batches = []
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        batches.append(batch)
    return batches

# Usage
samples = [np.array([1, 2, 3]) for _ in range(100)]
training_batches = create_batches(samples, batch_size=32)
print(f"Created {len(training_batches)} batches")  # 4 batches
```

#### 2. Tracking Experiment History

```python
class ExperimentTracker:
    def __init__(self):
        self.experiments: List[dict] = []

    def log_experiment(self, model: str, accuracy: float, loss: float):
        """Record experiment results in order."""
        experiment = {
            "model": model,
            "accuracy": accuracy,
            "loss": loss,
            "timestamp": time.time()
        }
        self.experiments.append(experiment)

    def get_best_accuracy(self) -> Tuple[str, float]:
        """Find experiment with highest accuracy."""
        best = max(self.experiments, key=lambda x: x["accuracy"])
        return best["model"], best["accuracy"]
```

#### 3. Layer Configuration Sequences

```python
# Neural network layer configurations maintain order
layer_configs = [
    {"type": "conv2d", "filters": 64, "kernel": 3},
    {"type": "relu"},
    {"type": "maxpool", "size": 2},
    {"type": "conv2d", "filters": 128, "kernel": 3},
    {"type": "relu"},
    {"type": "dense", "units": 10}
]

# Process layers in sequence
def build_model(configs: List[dict]):
    for i, config in enumerate(configs):
        print(f"Layer {i}: {config['type']}")
```

### List Sorting and Ordering

```python
accuracies = [0.85, 0.92, 0.78, 0.90]

# Sort in place
accuracies.sort()  # [0.78, 0.85, 0.90, 0.92]
accuracies.sort(reverse=True)  # [0.92, 0.90, 0.85, 0.78]

# Return new sorted list (original unchanged)
metrics = [0.85, 0.92, 0.78, 0.90]
sorted_metrics = sorted(metrics)  # [0.78, 0.85, 0.90, 0.92]

# Sort by custom key
experiments = [
    {"name": "exp1", "accuracy": 0.85},
    {"name": "exp2", "accuracy": 0.92},
    {"name": "exp3", "accuracy": 0.78}
]
sorted_exps = sorted(experiments, key=lambda x: x["accuracy"], reverse=True)
# exp2 (0.92), exp1 (0.85), exp3 (0.78)
```

---

## Dictionaries: Key-Value Mappings

### What Are Dictionaries?

Dictionaries are **unordered collections of key-value pairs** (ordered by insertion in Python 3.7+). They provide fast lookups by key.

```python
# Creating dictionaries
model_config = {
    "learning_rate": 0.001,
    "batch_size": 32,
    "epochs": 100
}

# Alternative syntax
hyperparams = dict(lr=0.001, momentum=0.9)

# Empty dictionary
metrics = {}
```

### Essential Dictionary Operations

#### Accessing and Modifying

```python
config = {"model": "resnet50", "layers": 50, "pretrained": True}

# Access by key (raises KeyError if missing)
model_name = config["model"]  # "resnet50"

# Safe access with default
optimizer = config.get("optimizer", "adam")  # "adam" (key doesn't exist)

# Add or update
config["batch_size"] = 32
config["layers"] = 101  # Update existing

# Multiple updates
config.update({"dropout": 0.5, "learning_rate": 0.001})

# Delete keys
del config["pretrained"]
removed = config.pop("dropout", None)  # Returns value or default
```

#### Dictionary Methods

```python
training_config = {
    "epochs": 100,
    "batch_size": 32,
    "learning_rate": 0.001
}

# Get all keys, values, items
keys = training_config.keys()      # dict_keys(['epochs', 'batch_size', 'learning_rate'])
values = training_config.values()  # dict_values([100, 32, 0.001])
items = training_config.items()    # dict_items([('epochs', 100), ...])

# Membership testing (checks keys only)
has_epochs = "epochs" in training_config  # True
has_dropout = "dropout" in training_config  # False

# Length
num_params = len(training_config)  # 3

# Copy (shallow)
config_copy = training_config.copy()

# Clear all items
training_config.clear()  # {}
```

### ML Infrastructure Use Cases for Dictionaries

#### 1. Model Configuration Management

```python
from typing import Dict, Any

class ModelConfig:
    """Type-safe model configuration using dictionaries."""

    DEFAULT_CONFIG: Dict[str, Any] = {
        "model_name": "resnet50",
        "num_classes": 1000,
        "pretrained": True,
        "dropout": 0.5,
        "learning_rate": 0.001,
        "batch_size": 32
    }

    @classmethod
    def create(cls, overrides: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create config by merging defaults with overrides."""
        config = cls.DEFAULT_CONFIG.copy()
        if overrides:
            config.update(overrides)
        return config

# Usage
dev_config = ModelConfig.create({"batch_size": 16, "learning_rate": 0.0001})
prod_config = ModelConfig.create({"batch_size": 128})
```

#### 2. Feature Dictionaries

```python
def extract_features(data: dict) -> Dict[str, float]:
    """Extract ML features from raw data dictionary."""
    features = {
        "text_length": len(data.get("text", "")),
        "has_image": 1.0 if data.get("image") else 0.0,
        "user_age": data.get("user", {}).get("age", 0),
        "timestamp": data.get("created_at", 0)
    }
    return features

# Process batch of records
raw_data = [
    {"text": "Hello world", "user": {"age": 25}},
    {"text": "ML is fun", "image": "img.jpg", "user": {"age": 30}}
]

feature_batch = [extract_features(record) for record in raw_data]
```

#### 3. Metrics Tracking

```python
class MetricsAggregator:
    def __init__(self):
        self.metrics: Dict[str, List[float]] = {}

    def record(self, name: str, value: float):
        """Record a metric value."""
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append(value)

    def get_summary(self) -> Dict[str, Dict[str, float]]:
        """Calculate summary statistics for each metric."""
        summary = {}
        for name, values in self.metrics.items():
            summary[name] = {
                "mean": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "count": len(values)
            }
        return summary

# Usage
tracker = MetricsAggregator()
for epoch in range(10):
    tracker.record("loss", 0.5 - epoch * 0.04)
    tracker.record("accuracy", 0.7 + epoch * 0.02)

print(tracker.get_summary())
# {
#   "loss": {"mean": 0.32, "min": 0.14, "max": 0.5, "count": 10},
#   "accuracy": {"mean": 0.79, "min": 0.7, "max": 0.88, "count": 10}
# }
```

### Dictionary Iteration Patterns

```python
model_metrics = {
    "accuracy": 0.92,
    "precision": 0.89,
    "recall": 0.91,
    "f1_score": 0.90
}

# Iterate over keys
for metric_name in model_metrics:
    print(metric_name)

# Iterate over values
for value in model_metrics.values():
    print(f"{value:.2%}")

# Iterate over key-value pairs (most common)
for name, value in model_metrics.items():
    print(f"{name}: {value:.3f}")

# Dictionary unpacking (Python 3.5+)
base_config = {"epochs": 100, "batch_size": 32}
full_config = {**base_config, "learning_rate": 0.001, "dropout": 0.5}
```

---

## Sets: Unique Collections

### What Are Sets?

Sets are **unordered collections of unique elements**. They automatically eliminate duplicates and provide fast membership testing.

```python
# Creating sets
unique_tags = {"computer-vision", "nlp", "reinforcement-learning"}
numbers = {1, 2, 3, 4, 5}

# From list (removes duplicates)
samples = [1, 2, 2, 3, 3, 3, 4]
unique_samples = set(samples)  # {1, 2, 3, 4}

# Empty set (must use set(), not {})
empty = set()
```

### Essential Set Operations

#### Adding and Removing Elements

```python
model_types = {"cnn", "rnn"}

# Add single element
model_types.add("transformer")  # {"cnn", "rnn", "transformer"}
model_types.add("cnn")  # Still {"cnn", "rnn", "transformer"} - no duplicate

# Add multiple elements
model_types.update(["lstm", "gru", "bert"])

# Remove element (raises KeyError if missing)
model_types.remove("rnn")

# Safe remove (no error if missing)
model_types.discard("nonexistent")  # No error

# Remove and return arbitrary element
removed = model_types.pop()
```

#### Set Mathematics

```python
# Training and validation dataset IDs
train_ids = {1, 2, 3, 4, 5, 6}
val_ids = {5, 6, 7, 8}

# Union: all unique IDs
all_ids = train_ids | val_ids  # {1, 2, 3, 4, 5, 6, 7, 8}
all_ids = train_ids.union(val_ids)  # Same result

# Intersection: overlapping IDs (potential data leakage!)
overlap = train_ids & val_ids  # {5, 6}
overlap = train_ids.intersection(val_ids)  # Same result

# Difference: elements in first but not second
train_only = train_ids - val_ids  # {1, 2, 3, 4}
train_only = train_ids.difference(val_ids)  # Same result

# Symmetric difference: elements in either but not both
exclusive = train_ids ^ val_ids  # {1, 2, 3, 4, 7, 8}
exclusive = train_ids.symmetric_difference(val_ids)  # Same result

# Subset and superset checks
small_set = {1, 2}
is_subset = small_set <= train_ids  # True
is_superset = train_ids >= small_set  # True
```

### ML Infrastructure Use Cases for Sets

#### 1. Detecting Data Leakage

```python
from typing import Set

def check_data_leakage(
    train_ids: Set[str],
    val_ids: Set[str],
    test_ids: Set[str]
) -> dict:
    """Verify no overlap between train/val/test splits."""
    train_val_overlap = train_ids & val_ids
    train_test_overlap = train_ids & test_ids
    val_test_overlap = val_ids & test_ids

    return {
        "has_leakage": bool(train_val_overlap or train_test_overlap or val_test_overlap),
        "train_val_overlap": len(train_val_overlap),
        "train_test_overlap": len(train_test_overlap),
        "val_test_overlap": len(val_test_overlap)
    }

# Usage
train = set(range(0, 8000))
val = set(range(8000, 9000))
test = set(range(9000, 10000))

result = check_data_leakage(train, val, test)
print(f"Data leakage detected: {result['has_leakage']}")  # False
```

#### 2. Feature Deduplication

```python
def deduplicate_features(samples: list) -> list:
    """Remove duplicate samples based on feature hash."""
    seen_hashes = set()
    unique_samples = []

    for sample in samples:
        # Create hashable representation
        feature_hash = tuple(sorted(sample.items()))

        if feature_hash not in seen_hashes:
            seen_hashes.add(feature_hash)
            unique_samples.append(sample)

    return unique_samples

# Usage
data = [
    {"x": 1, "y": 2},
    {"x": 3, "y": 4},
    {"x": 1, "y": 2},  # Duplicate
    {"x": 5, "y": 6}
]

unique_data = deduplicate_features(data)
print(f"Reduced from {len(data)} to {len(unique_data)} samples")  # 4 to 3
```

#### 3. Required vs Available Resources

```python
class ResourceValidator:
    """Check if required resources are available."""

    @staticmethod
    def validate_dependencies(
        required: Set[str],
        available: Set[str]
    ) -> dict:
        """Check which dependencies are missing."""
        missing = required - available
        extra = available - required

        return {
            "valid": len(missing) == 0,
            "missing": missing,
            "extra": extra
        }

# Check GPU dependencies
required_packages = {"torch", "torchvision", "cuda-toolkit", "cudnn"}
installed_packages = {"torch", "torchvision", "numpy", "pandas"}

validation = ResourceValidator.validate_dependencies(
    required_packages,
    installed_packages
)

if not validation["valid"]:
    print(f"Missing packages: {validation['missing']}")
    # Missing packages: {'cuda-toolkit', 'cudnn'}
```

---

## Tuples: Immutable Data

### What Are Tuples?

Tuples are **ordered, immutable sequences**. Once created, they cannot be modified. They're perfect for fixed collections or function return values.

```python
# Creating tuples
coordinates = (10.5, 20.3)
model_info = ("resnet50", 50, 25.5)  # name, layers, size_mb
single_element = (42,)  # Note the comma!

# Tuple unpacking
x, y = coordinates
name, layers, size = model_info

# Without parentheses (still a tuple)
dimensions = 224, 224, 3
```

### Why Use Tuples?

1. **Immutability guarantees**: Can't accidentally modify
2. **Hashable**: Can be dictionary keys or set elements
3. **Memory efficient**: Slightly smaller than lists
4. **Semantic clarity**: Signals "this shouldn't change"

### Essential Tuple Operations

```python
model_shape = (224, 224, 3)

# Indexing and slicing (like lists)
height = model_shape[0]  # 224
spatial = model_shape[:2]  # (224, 224)

# Concatenation creates new tuple
extended = model_shape + (32,)  # (224, 224, 3, 32)

# Repetition
repeated = (0,) * 5  # (0, 0, 0, 0, 0)

# Membership and counting
has_3 = 3 in model_shape  # True
count_224 = model_shape.count(224)  # 2

# Length
dims = len(model_shape)  # 3

# Cannot modify (raises TypeError)
# model_shape[0] = 256  # ERROR!
```

### ML Infrastructure Use Cases for Tuples

#### 1. Fixed Configuration Values

```python
# Image preprocessing constants (shouldn't change)
IMAGE_MEAN = (0.485, 0.456, 0.406)
IMAGE_STD = (0.229, 0.224, 0.225)
INPUT_SHAPE = (224, 224, 3)

def normalize_image(image: np.ndarray) -> np.ndarray:
    """Normalize image using fixed statistics."""
    return (image - IMAGE_MEAN) / IMAGE_STD
```

#### 2. Multiple Return Values

```python
from typing import Tuple

def train_epoch(
    model,
    train_loader,
    val_loader
) -> Tuple[float, float, float, float]:
    """Train one epoch and return metrics.

    Returns:
        (train_loss, train_acc, val_loss, val_acc)
    """
    train_loss = 0.45
    train_acc = 0.85
    val_loss = 0.52
    val_acc = 0.82

    return train_loss, train_acc, val_loss, val_acc  # Tuple packing

# Usage with unpacking
tr_loss, tr_acc, val_loss, val_acc = train_epoch(model, train_dl, val_dl)
print(f"Train: {tr_loss:.3f} / {tr_acc:.2%}")
print(f"Val: {val_loss:.3f} / {val_acc:.2%}")
```

#### 3. Dictionary Keys for Caching

```python
from typing import Tuple, Dict

class ModelCache:
    """Cache model predictions using immutable keys."""

    def __init__(self):
        self.cache: Dict[Tuple, np.ndarray] = {}

    def get_prediction(
        self,
        model_name: str,
        input_shape: Tuple[int, ...],
        batch_size: int
    ) -> np.ndarray:
        """Get cached prediction or compute new one."""
        # Tuple as cache key
        cache_key = (model_name, input_shape, batch_size)

        if cache_key not in self.cache:
            print(f"Computing prediction for {cache_key}")
            # Simulate prediction
            self.cache[cache_key] = np.random.rand(batch_size, 10)

        return self.cache[cache_key]

# Usage
cache = ModelCache()
pred1 = cache.get_prediction("resnet50", (224, 224, 3), 32)
pred2 = cache.get_prediction("resnet50", (224, 224, 3), 32)  # Cached!
```

### Named Tuples for Clarity

```python
from typing import NamedTuple

class ModelMetrics(NamedTuple):
    """Type-safe model metrics with named fields."""
    accuracy: float
    precision: float
    recall: float
    f1_score: float

    def summary(self) -> str:
        return f"Acc: {self.accuracy:.2%}, F1: {self.f1_score:.3f}"

# Usage
metrics = ModelMetrics(
    accuracy=0.92,
    precision=0.89,
    recall=0.91,
    f1_score=0.90
)

# Access by name (clearer than index)
print(f"Accuracy: {metrics.accuracy}")
print(f"F1: {metrics.f1_score}")

# Still works like regular tuple
acc, prec, rec, f1 = metrics
```

---

## Comprehensions: Efficient Data Transformation

### List Comprehensions

**Syntax**: `[expression for item in iterable if condition]`

#### Basic Examples

```python
# Traditional loop
squares = []
for x in range(10):
    squares.append(x ** 2)

# List comprehension (more concise)
squares = [x ** 2 for x in range(10)]
# [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

# With condition
even_squares = [x ** 2 for x in range(10) if x % 2 == 0]
# [0, 4, 16, 36, 64]

# Transform strings
model_names = ["ResNet50", "VGG16", "EfficientNet"]
lowercase = [name.lower() for name in model_names]
# ["resnet50", "vgg16", "efficientnet"]
```

#### ML Infrastructure Examples

```python
# 1. Process batch of predictions
predictions = [0.8, 0.3, 0.9, 0.4, 0.7]
binary_preds = [1 if p > 0.5 else 0 for p in predictions]
# [1, 0, 1, 0, 1]

# 2. Extract specific fields from experiments
experiments = [
    {"id": 1, "accuracy": 0.85, "model": "resnet"},
    {"id": 2, "accuracy": 0.92, "model": "vgg"},
    {"id": 3, "accuracy": 0.78, "model": "mobilenet"}
]
accuracies = [exp["accuracy"] for exp in experiments]
high_performing = [exp["model"] for exp in experiments if exp["accuracy"] > 0.8]
# ["resnet", "vgg"]

# 3. Create training file paths
image_ids = [1, 2, 3, 4, 5]
train_paths = [f"/data/train/image_{id:04d}.jpg" for id in image_ids]
# ["/data/train/image_0001.jpg", "/data/train/image_0002.jpg", ...]

# 4. Normalize features
features = [10, 20, 30, 40, 50]
mean = sum(features) / len(features)  # 30
normalized = [(f - mean) / 10 for f in features]
# [-2.0, -1.0, 0.0, 1.0, 2.0]
```

### Dictionary Comprehensions

**Syntax**: `{key_expr: value_expr for item in iterable if condition}`

```python
# Basic examples
squares_dict = {x: x ** 2 for x in range(5)}
# {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

# Invert dictionary
model_versions = {"resnet": "v1", "vgg": "v2", "efficientnet": "v1"}
version_models = {v: k for k, v in model_versions.items()}
# {"v1": "efficientnet", "v2": "vgg"}  # Note: last occurrence wins

# Filter dictionary
metrics = {"accuracy": 0.92, "loss": 0.15, "precision": 0.89, "recall": 0.91}
high_metrics = {k: v for k, v in metrics.items() if v > 0.9}
# {"accuracy": 0.92, "recall": 0.91}
```

#### ML Infrastructure Examples

```python
# 1. Create config from lists
param_names = ["learning_rate", "batch_size", "epochs"]
param_values = [0.001, 32, 100]
config = {name: value for name, value in zip(param_names, param_values)}
# {"learning_rate": 0.001, "batch_size": 32, "epochs": 100}

# 2. Convert metric lists to dict
metric_names = ["accuracy", "precision", "recall", "f1"]
metric_values = [0.92, 0.89, 0.91, 0.90]
metrics = {name: value for name, value in zip(metric_names, metric_values)}

# 3. Transform values in existing dict
train_losses = {"epoch_1": 2.3, "epoch_2": 1.8, "epoch_3": 1.5}
log_losses = {k: round(v, 2) for k, v in train_losses.items()}

# 4. Feature scaling dictionary
raw_features = {"age": 45, "income": 75000, "credit_score": 720}
feature_ranges = {"age": (0, 100), "income": (0, 200000), "credit_score": (300, 850)}

normalized_features = {
    feature: (value - feature_ranges[feature][0]) /
             (feature_ranges[feature][1] - feature_ranges[feature][0])
    for feature, value in raw_features.items()
}
```

### Set Comprehensions

**Syntax**: `{expression for item in iterable if condition}`

```python
# Find unique file extensions
filenames = ["model.pth", "data.csv", "config.json", "weights.pth", "test.csv"]
extensions = {name.split('.')[-1] for name in filenames}
# {"pth", "csv", "json"}

# Unique model types from experiments
experiments = [
    {"model": "resnet50"},
    {"model": "vgg16"},
    {"model": "resnet50"},  # Duplicate
    {"model": "efficientnet"}
]
unique_models = {exp["model"] for exp in experiments}
# {"resnet50", "vgg16", "efficientnet"}

# Unique labels in dataset
data_samples = [
    {"label": "cat"}, {"label": "dog"}, {"label": "cat"},
    {"label": "bird"}, {"label": "dog"}
]
unique_labels = {sample["label"] for sample in data_samples}
# {"cat", "dog", "bird"}
```

### Nested Comprehensions

```python
# 2D matrix creation
matrix = [[i * j for j in range(4)] for i in range(3)]
# [[0, 0, 0, 0],
#  [0, 1, 2, 3],
#  [0, 2, 4, 6]]

# Flatten nested list
nested = [[1, 2], [3, 4], [5, 6]]
flattened = [item for sublist in nested for item in sublist]
# [1, 2, 3, 4, 5, 6]

# ML example: create all hyperparameter combinations
learning_rates = [0.001, 0.01, 0.1]
batch_sizes = [16, 32, 64]

configs = [
    {"lr": lr, "batch_size": bs}
    for lr in learning_rates
    for bs in batch_sizes
]
# Results in 9 configurations (3 * 3)

# Filter nested structures
experiments = [
    [{"acc": 0.8}, {"acc": 0.9}],
    [{"acc": 0.7}, {"acc": 0.95}],
]
high_acc = [
    exp for exp_group in experiments
    for exp in exp_group
    if exp["acc"] > 0.85
]
# [{"acc": 0.9}, {"acc": 0.95}]
```

### Generator Expressions

Generator expressions look like comprehensions but use parentheses. They generate values **on-demand** instead of creating the full list in memory.

```python
# List comprehension: creates full list in memory
squares_list = [x ** 2 for x in range(1000000)]  # Uses ~8MB

# Generator expression: creates values on demand
squares_gen = (x ** 2 for x in range(1000000))   # Uses ~128 bytes!

# Consume generator
for square in squares_gen:
    if square > 100:
        break  # Most values never computed!

# Use in functions that accept iterables
total = sum(x ** 2 for x in range(1000))  # No brackets needed
max_val = max(x * 2 for x in range(100) if x % 2 == 0)
```

#### ML Infrastructure Generator Examples

```python
# 1. Process large datasets without loading all into memory
def load_batch_data(batch_size: int):
    """Generator that yields batches without loading full dataset."""
    for batch_id in range(100):  # 100 batches
        # Yield generated batch (not stored in memory)
        yield {
            "batch_id": batch_id,
            "data": [i for i in range(batch_size)]
        }

# Process one batch at a time
for batch in load_batch_data(32):
    # Process batch
    print(f"Processing batch {batch['batch_id']}")
    # Previous batches are garbage collected

# 2. Calculate metrics without storing all values
def calculate_running_average(values):
    """Calculate average using generator (memory efficient)."""
    total = sum(values)  # Generator consumed once
    count = sum(1 for _ in values)  # Need to recreate generator!
    # Better approach:
    # total, count = 0, 0
    # for v in values:
    #     total += v
    #     count += 1
    return total / count if count > 0 else 0
```

---

## Data Structure Selection Guide

### Quick Decision Tree

```
Need to store multiple values?
├─ Need to preserve order?
│  ├─ Need to modify after creation?
│  │  ├─ Need fast lookup by key?
│  │  │  └─ Use: DICTIONARY
│  │  └─ Sequential access?
│  │     └─ Use: LIST
│  └─ Fixed values (immutable)?
│     └─ Use: TUPLE
└─ Only need unique values?
   └─ Use: SET
```

### Use Case Matrix

| Data Structure | When to Use | ML/AI Infrastructure Examples |
|---------------|-------------|-------------------------------|
| **List** | Ordered collection, may have duplicates | Training batches, layer configs, time-series metrics |
| **Dictionary** | Key-value mapping, fast lookups | Model configs, feature dicts, hyperparameters |
| **Set** | Unique values, membership testing | Deduplication, data split validation, required dependencies |
| **Tuple** | Immutable sequence, function returns | Image shapes, normalization constants, cache keys |

### Common Anti-Patterns

```python
# ❌ BAD: Using list for uniqueness check
def has_duplicates_slow(ids: list) -> bool:
    """Slow O(n²) approach."""
    for i, id1 in enumerate(ids):
        for id2 in ids[i+1:]:
            if id1 == id2:
                return True
    return False

# ✅ GOOD: Use set for uniqueness
def has_duplicates_fast(ids: list) -> bool:
    """Fast O(n) approach."""
    return len(ids) != len(set(ids))

# ❌ BAD: Using list for config (should be dict)
config = ["resnet50", 50, 0.001, 32]  # What does each value mean?

# ✅ GOOD: Use dict for config
config = {
    "model": "resnet50",
    "layers": 50,
    "learning_rate": 0.001,
    "batch_size": 32
}

# ❌ BAD: Using mutable list as default argument
def process_batch(samples, results=[]):  # BUG!
    results.append(len(samples))
    return results

# ✅ GOOD: Use None and create new list
def process_batch(samples, results=None):
    if results is None:
        results = []
    results.append(len(samples))
    return results
```

---

## Performance Considerations

### Time Complexity Summary

| Operation | List | Dictionary | Set | Tuple |
|-----------|------|------------|-----|-------|
| Access by index | O(1) | N/A | N/A | O(1) |
| Access by key | N/A | O(1) avg | N/A | N/A |
| Search | O(n) | O(1) avg | O(1) avg | O(n) |
| Insert/Delete at end | O(1) | O(1) avg | O(1) avg | N/A (immutable) |
| Insert/Delete at beginning | O(n) | O(1) avg | O(1) avg | N/A |
| Iteration | O(n) | O(n) | O(n) | O(n) |

### Memory Usage

```python
import sys

# Compare memory usage
list_data = [i for i in range(1000)]
tuple_data = tuple(range(1000))
set_data = {i for i in range(1000)}
dict_data = {i: i for i in range(1000)}

print(f"List:  {sys.getsizeof(list_data)} bytes")   # ~9024 bytes
print(f"Tuple: {sys.getsizeof(tuple_data)} bytes")  # ~8024 bytes (smaller!)
print(f"Set:   {sys.getsizeof(set_data)} bytes")    # ~32992 bytes (larger!)
print(f"Dict:  {sys.getsizeof(dict_data)} bytes")   # ~41072 bytes (largest)
```

### Performance Tips

```python
# 1. Membership testing: use set, not list
# ❌ SLOW: O(n) for each lookup
valid_ids = [1, 2, 3, 4, 5] * 1000  # 5000 items
if 4999 in valid_ids:  # Scans through list
    pass

# ✅ FAST: O(1) for each lookup
valid_ids_set = set(valid_ids)
if 4999 in valid_ids_set:  # Instant hash lookup
    pass

# 2. Building lists: append is usually fine
# ❌ SLOW: Creates new list each time
result = []
for i in range(1000):
    result = result + [i]  # O(n) operation each time!

# ✅ FAST: Append in place
result = []
for i in range(1000):
    result.append(i)  # O(1) amortized

# 3. Pre-allocate if size known (rare in Python)
# For massive datasets with known size
size = 1000000
result = [None] * size  # Pre-allocate
for i in range(size):
    result[i] = i ** 2

# 4. Use generator for large data
# ❌ Memory intensive
squares = [x ** 2 for x in range(10000000)]

# ✅ Memory efficient
squares_gen = (x ** 2 for x in range(10000000))
```

---

## Summary and Best Practices

### Key Takeaways

1. **Lists**: Ordered, mutable sequences
   - Use for: Batches, sequences, time-series data
   - When order matters and you need to modify

2. **Dictionaries**: Key-value mappings
   - Use for: Configs, features, metrics
   - Fast O(1) lookups by key

3. **Sets**: Unique, unordered collections
   - Use for: Deduplication, membership testing, set operations
   - Best for uniqueness guarantees and fast lookups

4. **Tuples**: Immutable sequences
   - Use for: Fixed values, multiple returns, hashable keys
   - When data shouldn't change

5. **Comprehensions**: Concise data transformation
   - More readable than loops for simple transformations
   - Generator expressions for memory efficiency

### Best Practices for AI Infrastructure

```python
# 1. Type hints for clarity
from typing import List, Dict, Set, Tuple

def process_batch(
    samples: List[Dict[str, float]],
    config: Dict[str, int]
) -> Tuple[float, float]:
    """Type hints make interfaces clear."""
    pass

# 2. Use sets for uniqueness guarantees
def validate_no_duplicates(train_ids: List[int], val_ids: List[int]):
    """Detect data leakage."""
    train_set = set(train_ids)
    val_set = set(val_ids)
    overlap = train_set & val_set

    if overlap:
        raise ValueError(f"Found {len(overlap)} duplicate IDs")

# 3. Named tuples for complex returns
from typing import NamedTuple

class BatchMetrics(NamedTuple):
    loss: float
    accuracy: float
    batch_time: float

def train_batch() -> BatchMetrics:
    return BatchMetrics(loss=0.5, accuracy=0.85, batch_time=0.2)

# 4. Comprehensions for transformations
configs = [
    {"lr": 0.001, "bs": 32},
    {"lr": 0.01, "bs": 64}
]

# Extract learning rates
learning_rates = [cfg["lr"] for cfg in configs]

# 5. Use appropriate data structure for problem
# Set for deduplication
unique_labels = set(sample["label"] for sample in dataset)

# Dict for configs
hyperparams = {"learning_rate": 0.001, "batch_size": 32}

# List for sequences
training_losses = [2.3, 1.8, 1.5, 1.2, 0.9]

# Tuple for constants
IMAGE_SIZE = (224, 224, 3)
```

### Common Pitfalls to Avoid

1. ❌ Using mutable defaults in functions
2. ❌ Using lists for membership testing (use sets)
3. ❌ Modifying list while iterating
4. ❌ Using dict keys that aren't hashable
5. ❌ Creating huge lists when generators would work

### Next Steps

You now have a solid foundation in Python's core data structures. In the next lecture, we'll explore:
- Advanced function patterns and decorators
- Building reusable modules and packages
- Writing functional utilities for ML infrastructure

Continue to **Exercise 02: Data Structures** to practice these concepts with hands-on ML infrastructure scenarios!

---

**Word Count**: ~4,750 words
**Estimated Reading Time**: 20-25 minutes
