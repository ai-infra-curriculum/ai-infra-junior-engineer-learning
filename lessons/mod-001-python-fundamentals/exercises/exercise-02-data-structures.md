# Exercise 02: Python Data Structures for ML Data Processing

## Overview

This exercise teaches you how to effectively use Python's built-in data structures (lists, dictionaries, sets, tuples) for machine learning data processing tasks. You'll work with real ML scenarios including dataset manipulation, feature engineering, batch processing, and model metadata management.

## Learning Objectives

By completing this exercise, you will:
- Master list operations for batch processing and data pipelines
- Use dictionaries for configuration management and feature storage
- Apply sets for deduplication and dataset operations
- Utilize tuples for immutable data and function returns
- Implement list comprehensions and dict comprehensions for efficient data processing
- Understand when to use each data structure in ML contexts
- Process nested data structures common in ML configurations

## Prerequisites

- Completed Exercise 01: Environment Setup
- Completed Lecture 01: Python Environment
- Basic Python syntax knowledge
- Understanding of ML concepts (datasets, batches, features)

## Time Required

- Estimated: 90-120 minutes
- Difficulty: Beginner to Intermediate

## Part 1: Lists for Batch Processing

### Step 1: Basic List Operations with ML Data

```python
# Create a script: list_operations.py

# Sample dataset: image file paths for training
training_images = [
    "img_0001.jpg",
    "img_0002.jpg",
    "img_0003.jpg",
    "img_0004.jpg",
    "img_0005.jpg"
]

# Print dataset information
print(f"Total training images: {len(training_images)}")
print(f"First image: {training_images[0]}")
print(f"Last image: {training_images[-1]}")

# Add new images
training_images.append("img_0006.jpg")
training_images.extend(["img_0007.jpg", "img_0008.jpg"])
print(f"After adding: {len(training_images)} images")

# Insert image at specific position
training_images.insert(0, "img_0000.jpg")
print(f"First image now: {training_images[0]}")

# Remove images
removed = training_images.pop()  # Remove last
print(f"Removed: {removed}")

training_images.remove("img_0000.jpg")  # Remove by value
print(f"Final count: {len(training_images)}")

# Check if image exists
if "img_0003.jpg" in training_images:
    index = training_images.index("img_0003.jpg")
    print(f"Found img_0003.jpg at index {index}")

# Slice operations (get batches)
batch_size = 3
batch_1 = training_images[0:batch_size]
batch_2 = training_images[batch_size:batch_size*2]
print(f"Batch 1: {batch_1}")
print(f"Batch 2: {batch_2}")

# Reverse and sort
training_images_sorted = sorted(training_images)
print(f"Sorted: {training_images_sorted}")

training_images_reversed = list(reversed(training_images))
print(f"Reversed: {training_images_reversed}")
```

**Expected Output**:
```
Total training images: 5
First image: img_0001.jpg
Last image: img_0005.jpg
After adding: 7 images
First image now: img_0000.jpg
Removed: img_0008.jpg
Final count: 6
Found img_0003.jpg at index 2
Batch 1: ['img_0001.jpg', 'img_0002.jpg', 'img_0003.jpg']
Batch 2: ['img_0004.jpg', 'img_0005.jpg', 'img_0006.jpg']
...
```

**Tasks**:
1. Run the script and verify output
2. Add 10 more images to the list
3. Create batches of size 4
4. Find all images with "000" in their name

### Step 2: List Comprehensions for Data Processing

```python
# Create a script: list_comprehensions.py

# Sample data: model training losses
losses = [2.5, 2.1, 1.8, 1.5, 1.3, 1.2, 1.1, 1.05, 1.02, 1.01]

# Square all losses
squared_losses = [loss ** 2 for loss in losses]
print(f"Squared losses: {squared_losses}")

# Filter losses below threshold
low_losses = [loss for loss in losses if loss < 1.5]
print(f"Losses below 1.5: {low_losses}")

# Transform and filter
normalized_losses = [(loss - min(losses)) / (max(losses) - min(losses))
                     for loss in losses if loss < 2.0]
print(f"Normalized losses: {normalized_losses}")

# Nested list comprehension: create batches
data_points = list(range(1, 21))  # 20 data points
batch_size = 5
batches = [data_points[i:i+batch_size]
           for i in range(0, len(data_points), batch_size)]
print(f"Batches: {batches}")

# Process image dimensions
image_sizes = [(224, 224), (256, 256), (512, 512), (1024, 1024)]
total_pixels = [width * height for width, height in image_sizes]
print(f"Total pixels: {total_pixels}")

# Create one-hot encoding
classes = ["cat", "dog", "bird", "fish"]
target_class = "dog"
one_hot = [1 if cls == target_class else 0 for cls in classes]
print(f"One-hot for '{target_class}': {one_hot}")

# Parse model filenames
model_files = [
    "model_v1_acc_0.85.h5",
    "model_v2_acc_0.92.h5",
    "model_v3_acc_0.88.h5"
]

# Extract accuracies
accuracies = [float(f.split("_acc_")[1].replace(".h5", ""))
              for f in model_files]
print(f"Accuracies: {accuracies}")

# Find best model
best_idx = accuracies.index(max(accuracies))
best_model = model_files[best_idx]
print(f"Best model: {best_model} (acc: {max(accuracies)})")

# Conditional list building
training_config = {
    "epochs": 100,
    "batch_size": 32,
    "learning_rate": 0.001,
    "use_gpu": True,
    "augmentation": True
}

enabled_features = [key for key, value in training_config.items()
                   if isinstance(value, bool) and value]
print(f"Enabled features: {enabled_features}")
```

**Tasks**:
1. Create a list comprehension that filters models with accuracy > 0.90
2. Generate batches with overlapping windows (stride < batch_size)
3. Create a list of tuples (filename, accuracy) sorted by accuracy
4. Use nested comprehension to flatten a 2D list of features

### Step 3: Real-World Batch Processing

```python
# Create a script: batch_processor.py

import random
from typing import List, Tuple

class DataBatchProcessor:
    """Process data in batches for ML training"""

    def __init__(self, data: List, batch_size: int, shuffle: bool = True):
        self.data = data.copy()
        self.batch_size = batch_size
        self.shuffle = shuffle

    def get_batches(self) -> List[List]:
        """Generate batches from data"""
        if self.shuffle:
            random.shuffle(self.data)

        batches = []
        for i in range(0, len(self.data), self.batch_size):
            batch = self.data[i:i + self.batch_size]
            batches.append(batch)

        return batches

    def get_batch_statistics(self) -> dict:
        """Calculate batch statistics"""
        num_batches = (len(self.data) + self.batch_size - 1) // self.batch_size
        last_batch_size = len(self.data) % self.batch_size or self.batch_size

        return {
            "total_samples": len(self.data),
            "batch_size": self.batch_size,
            "num_batches": num_batches,
            "last_batch_size": last_batch_size
        }

# Example usage
sample_ids = list(range(1, 101))  # 100 samples

processor = DataBatchProcessor(sample_ids, batch_size=16)
batches = processor.get_batches()

print(f"Generated {len(batches)} batches")
print(f"First batch: {batches[0]}")
print(f"Last batch size: {len(batches[-1])}")

stats = processor.get_batch_statistics()
print(f"Statistics: {stats}")

# TODO: Extend this class to support:
# 1. Stratified sampling for classification
# 2. Weighted sampling
# 3. Custom batch padding for uneven batches
```

**Challenge Tasks**:
1. Implement stratified batching that ensures each batch has balanced classes
2. Add a method to drop the last incomplete batch
3. Create a method that returns batch indices instead of batch data
4. Implement a circular batch generator for infinite training loops

## Part 2: Dictionaries for Configuration and Metadata

### Step 4: Dictionary Operations for ML Configs

```python
# Create a script: dict_operations.py

# Model configuration
model_config = {
    "name": "ResNet50",
    "version": "1.0.0",
    "input_shape": (224, 224, 3),
    "num_classes": 1000,
    "pretrained": True,
    "freeze_layers": 10
}

# Access values
print(f"Model: {model_config['name']}")
print(f"Version: {model_config['version']}")

# Safe access with get()
optimizer = model_config.get("optimizer", "adam")  # Default to adam
print(f"Optimizer: {optimizer}")

# Update config
model_config["learning_rate"] = 0.001
model_config.update({
    "optimizer": "adam",
    "weight_decay": 0.0001
})

print(f"Updated config: {model_config}")

# Check key existence
if "dropout" not in model_config:
    model_config["dropout"] = 0.5
    print("Added dropout configuration")

# Iterate over config
print("\nConfiguration summary:")
for key, value in model_config.items():
    print(f"  {key}: {value}")

# Get all keys and values
config_keys = list(model_config.keys())
config_values = list(model_config.values())
print(f"\nConfig keys: {config_keys}")

# Remove keys
removed_value = model_config.pop("freeze_layers", None)
print(f"Removed freeze_layers: {removed_value}")

# Clear specific keys
temp_config = model_config.copy()
temp_config.clear()
print(f"Cleared config: {temp_config}")
print(f"Original still intact: {len(model_config)} keys")
```

### Step 5: Dict Comprehensions and Nested Structures

```python
# Create a script: dict_comprehensions.py

# Create metric dictionary from lists
metric_names = ["accuracy", "precision", "recall", "f1_score"]
metric_values = [0.92, 0.89, 0.94, 0.91]

metrics = {name: value for name, value in zip(metric_names, metric_values)}
print(f"Metrics: {metrics}")

# Filter metrics above threshold
high_metrics = {k: v for k, v in metrics.items() if v > 0.90}
print(f"High metrics (>0.90): {high_metrics}")

# Transform values
metrics_percentage = {k: f"{v*100:.1f}%" for k, v in metrics.items()}
print(f"Metrics as %: {metrics_percentage}")

# Nested dictionary: experiment results
experiments = {
    "exp_001": {
        "model": "resnet50",
        "accuracy": 0.92,
        "loss": 0.15,
        "epoch": 50,
        "status": "completed"
    },
    "exp_002": {
        "model": "vgg16",
        "accuracy": 0.88,
        "loss": 0.22,
        "epoch": 45,
        "status": "completed"
    },
    "exp_003": {
        "model": "mobilenet",
        "accuracy": 0.85,
        "loss": 0.28,
        "epoch": 30,
        "status": "failed"
    }
}

# Find best experiment by accuracy
completed_exps = {k: v for k, v in experiments.items()
                  if v["status"] == "completed"}
best_exp = max(completed_exps.items(), key=lambda x: x["accuracy"])
print(f"Best experiment: {best_exp[0]} with accuracy {best_exp[1]['accuracy']}")

# Extract specific field from all experiments
accuracies = {exp_id: data["accuracy"]
              for exp_id, data in experiments.items()
              if data["status"] == "completed"}
print(f"All accuracies: {accuracies}")

# Group experiments by model
by_model = {}
for exp_id, data in experiments.items():
    model = data["model"]
    if model not in by_model:
        by_model[model] = []
    by_model[model].append(exp_id)

print(f"Experiments by model: {by_model}")

# Create summary statistics
summary = {
    "total_experiments": len(experiments),
    "completed": sum(1 for v in experiments.values() if v["status"] == "completed"),
    "failed": sum(1 for v in experiments.values() if v["status"] == "failed"),
    "avg_accuracy": sum(v["accuracy"] for v in experiments.values()
                       if v["status"] == "completed") / len(completed_exps)
}
print(f"Summary: {summary}")
```

### Step 6: Feature Dictionary Management

```python
# Create a script: feature_manager.py

from typing import Dict, List, Any
import json

class FeatureManager:
    """Manage ML features and their metadata"""

    def __init__(self):
        self.features: Dict[str, Dict[str, Any]] = {}

    def add_feature(self, name: str, dtype: str,
                   importance: float = 0.0, description: str = ""):
        """Add a feature with metadata"""
        self.features[name] = {
            "dtype": dtype,
            "importance": importance,
            "description": description,
            "used_count": 0
        }

    def get_feature(self, name: str) -> Dict[str, Any]:
        """Get feature metadata"""
        return self.features.get(name, {})

    def update_importance(self, name: str, importance: float):
        """Update feature importance"""
        if name in self.features:
            self.features[name]["importance"] = importance

    def increment_usage(self, name: str):
        """Track feature usage"""
        if name in self.features:
            self.features[name]["used_count"] += 1

    def get_top_features(self, n: int = 5) -> List[tuple]:
        """Get top N features by importance"""
        sorted_features = sorted(
            self.features.items(),
            key=lambda x: x[1]["importance"],
            reverse=True
        )
        return sorted_features[:n]

    def filter_by_dtype(self, dtype: str) -> Dict[str, Dict]:
        """Get all features of specific data type"""
        return {
            name: meta for name, meta in self.features.items()
            if meta["dtype"] == dtype
        }

    def export_config(self, filepath: str):
        """Export features to JSON"""
        with open(filepath, 'w') as f:
            json.dump(self.features, f, indent=2)

    def import_config(self, filepath: str):
        """Import features from JSON"""
        with open(filepath, 'r') as f:
            self.features = json.load(f)

# Example usage
manager = FeatureManager()

# Add features
manager.add_feature("age", "int", 0.85, "User age in years")
manager.add_feature("income", "float", 0.92, "Annual income")
manager.add_feature("location", "str", 0.65, "City name")
manager.add_feature("clicks", "int", 0.78, "Number of clicks")
manager.add_feature("conversion", "bool", 0.95, "Converted or not")

# Update and use features
manager.update_importance("age", 0.88)
manager.increment_usage("age")
manager.increment_usage("income")

# Get top features
top_features = manager.get_top_features(3)
print("Top 3 features:")
for name, meta in top_features:
    print(f"  {name}: importance={meta['importance']}")

# Filter by type
numeric_features = manager.filter_by_dtype("int")
print(f"\nNumeric features: {list(numeric_features.keys())}")

# Export/import
manager.export_config("features.json")
print("Features exported to features.json")

# TODO: Extend this class to support:
# 1. Feature engineering transformations
# 2. Feature version tracking
# 3. Feature validation rules
# 4. Feature correlation analysis
```

## Part 3: Sets for Deduplication and Operations

### Step 7: Set Operations for Dataset Management

```python
# Create a script: set_operations.py

# Training and validation dataset IDs
train_ids = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}
val_ids = {9, 10, 11, 12, 13}
test_ids = {13, 14, 15, 16, 17}

print(f"Training samples: {len(train_ids)}")
print(f"Validation samples: {len(val_ids)}")
print(f"Test samples: {len(test_ids)}")

# Find overlapping samples (data leakage check)
train_val_overlap = train_ids & val_ids  # Intersection
print(f"Train-Val overlap: {train_val_overlap}")

train_test_overlap = train_ids & test_ids
print(f"Train-Test overlap: {train_test_overlap}")

val_test_overlap = val_ids & test_ids
print(f"Val-Test overlap: {val_test_overlap}")

# Union: all unique samples
all_samples = train_ids | val_ids | test_ids
print(f"Total unique samples: {len(all_samples)}")
print(f"All sample IDs: {sorted(all_samples)}")

# Difference: samples only in training
train_only = train_ids - val_ids - test_ids
print(f"Samples only in training: {train_only}")

# Symmetric difference: samples in either but not both
train_val_exclusive = train_ids ^ val_ids
print(f"Exclusive to train or val: {train_val_exclusive}")

# Check if sets are disjoint (no overlap)
is_clean_split = train_ids.isdisjoint(test_ids)
print(f"Clean train-test split: {is_clean_split}")

# Add and remove samples
new_samples = {18, 19, 20}
test_ids_updated = test_ids | new_samples  # Union
print(f"Updated test set: {test_ids_updated}")

# Remove outliers
outliers = {5, 10}
train_cleaned = train_ids - outliers
print(f"Training after removing outliers: {train_cleaned}")

# Subset check
small_set = {1, 2, 3}
is_subset = small_set.issubset(train_ids)
print(f"Is {small_set} subset of training? {is_subset}")

is_superset = train_ids.issuperset(small_set)
print(f"Is training superset of {small_set}? {is_superset}")
```

### Step 8: Deduplication and Data Cleaning

```python
# Create a script: deduplication.py

from typing import List, Set, Dict

def remove_duplicate_samples(sample_ids: List[int]) -> List[int]:
    """Remove duplicates while preserving order"""
    seen = set()
    unique_samples = []

    for sample_id in sample_ids:
        if sample_id not in seen:
            seen.add(sample_id)
            unique_samples.append(sample_id)

    return unique_samples

def find_duplicate_files(filepaths: List[str]) -> Dict[str, List[str]]:
    """Find duplicate files by basename"""
    from collections import defaultdict
    import os

    basename_map = defaultdict(list)

    for filepath in filepaths:
        basename = os.path.basename(filepath)
        basename_map[basename].append(filepath)

    # Return only duplicates
    duplicates = {k: v for k, v in basename_map.items() if len(v) > 1}
    return duplicates

def validate_unique_classes(dataset: List[tuple]) -> bool:
    """Validate that all class labels are unique per sample"""
    sample_ids = [item[0] for item in dataset]
    unique_ids = set(sample_ids)

    if len(sample_ids) != len(unique_ids):
        print(f"Warning: {len(sample_ids) - len(unique_ids)} duplicate sample IDs found")
        return False
    return True

# Example: dataset with duplicates
raw_dataset = [
    (1, "cat", "img1.jpg"),
    (2, "dog", "img2.jpg"),
    (3, "cat", "img3.jpg"),
    (1, "cat", "img1_copy.jpg"),  # Duplicate ID
    (4, "bird", "img4.jpg"),
    (2, "dog", "img2_v2.jpg"),    # Duplicate ID
]

print("Original dataset size:", len(raw_dataset))

# Extract unique IDs
sample_ids = [item[0] for item in raw_dataset]
unique_ids = list(set(sample_ids))
print(f"Unique sample IDs: {len(unique_ids)} (from {len(sample_ids)} total)")

# Remove duplicates preserving first occurrence
cleaned_ids = remove_duplicate_samples(sample_ids)
print(f"Cleaned IDs: {cleaned_ids}")

# Find duplicate entries
seen_ids = set()
duplicates = []
for item in raw_dataset:
    if item[0] in seen_ids:
        duplicates.append(item)
    seen_ids.add(item[0])

print(f"Duplicate entries: {duplicates}")

# Validate uniqueness
is_valid = validate_unique_classes(raw_dataset)
print(f"Dataset has unique IDs: {is_valid}")

# Example: find duplicate filenames
image_files = [
    "/data/train/img001.jpg",
    "/data/train/img002.jpg",
    "/data/val/img001.jpg",      # Same basename
    "/data/test/img002.jpg",     # Same basename
    "/data/train/img003.jpg"
]

duplicate_files = find_duplicate_files(image_files)
print(f"\nDuplicate filenames: {duplicate_files}")

# Set operations for class distribution
class_labels = ["cat", "dog", "cat", "bird", "dog", "cat", "fish", "dog"]
unique_classes = set(class_labels)
print(f"\nUnique classes: {unique_classes}")
print(f"Number of classes: {len(unique_classes)}")

# Count occurrences
from collections import Counter
class_counts = Counter(class_labels)
print(f"Class distribution: {dict(class_counts)}")
```

## Part 4: Tuples for Immutable Data

### Step 9: Using Tuples for Fixed Data

```python
# Create a script: tuple_operations.py

# Model metadata (immutable)
model_metadata = ("ResNet50", "1.0.0", "2024-10-18", 0.92)
model_name, version, date, accuracy = model_metadata  # Unpacking

print(f"Model: {model_name}")
print(f"Version: {version}")
print(f"Released: {date}")
print(f"Accuracy: {accuracy}")

# Tuple of tuples: training history
training_history = (
    (1, 0.85, 0.45),   # (epoch, accuracy, loss)
    (2, 0.88, 0.32),
    (3, 0.91, 0.25),
    (4, 0.92, 0.20),
    (5, 0.93, 0.18)
)

print("\nTraining History:")
for epoch, acc, loss in training_history:
    print(f"Epoch {epoch}: Accuracy={acc:.2f}, Loss={loss:.2f}")

# Find best epoch
best_epoch = max(training_history, key=lambda x: x[1])
print(f"Best epoch: {best_epoch[0]} with accuracy {best_epoch[1]}")

# Named tuples for better readability
from collections import namedtuple

ModelConfig = namedtuple('ModelConfig',
                        ['name', 'layers', 'params', 'memory_mb'])

resnet_config = ModelConfig('ResNet50', 50, 25_500_000, 98)
vgg_config = ModelConfig('VGG16', 16, 138_000_000, 528)

print(f"\n{resnet_config.name}: {resnet_config.params:,} parameters")
print(f"{vgg_config.name}: {vgg_config.params:,} parameters")

# Compare memory
if resnet_config.memory_mb < vgg_config.memory_mb:
    print(f"{resnet_config.name} is more memory efficient")

# Tuple as dictionary key (immutable)
model_performance = {
    ('ResNet50', 'ImageNet'): 0.92,
    ('VGG16', 'ImageNet'): 0.88,
    ('ResNet50', 'CIFAR10'): 0.95,
}

key = ('ResNet50', 'ImageNet')
accuracy = model_performance[key]
print(f"\n{key[0]} on {key[1]}: {accuracy}")

# Return multiple values from function
def train_model(epochs: int) -> tuple:
    """Simulate training, return multiple metrics"""
    final_accuracy = 0.92
    final_loss = 0.15
    training_time = 3600  # seconds
    num_params = 25_500_000

    return final_accuracy, final_loss, training_time, num_params

# Unpack return values
acc, loss, time, params = train_model(50)
print(f"\nTraining complete:")
print(f"  Accuracy: {acc}")
print(f"  Loss: {loss}")
print(f"  Time: {time}s")
print(f"  Parameters: {params:,}")
```

## Part 5: Comprehensive Data Structure Challenge

### Step 10: Build a Dataset Manager

```python
# Create a script: dataset_manager.py

from typing import Dict, List, Set, Tuple
from collections import defaultdict
import random

class MLDatasetManager:
    """Comprehensive dataset manager using all data structures"""

    def __init__(self):
        # Dictionary: sample_id -> sample data
        self.samples: Dict[int, Dict] = {}

        # Sets: track dataset splits
        self.train_ids: Set[int] = set()
        self.val_ids: Set[int] = set()
        self.test_ids: Set[int] = set()

        # List: maintain order for class labels
        self.class_names: List[str] = []

        # Dictionary: class -> list of sample IDs
        self.class_to_samples: Dict[str, List[int]] = defaultdict(list)

    def add_sample(self, sample_id: int, filepath: str,
                   class_label: str, metadata: Dict = None):
        """Add a sample to the dataset"""
        if sample_id in self.samples:
            raise ValueError(f"Sample {sample_id} already exists")

        self.samples[sample_id] = {
            'filepath': filepath,
            'class': class_label,
            'metadata': metadata or {}
        }

        # Update class tracking
        if class_label not in self.class_names:
            self.class_names.append(class_label)

        self.class_to_samples[class_label].append(sample_id)

    def split_dataset(self, train_ratio: float = 0.7,
                     val_ratio: float = 0.15, seed: int = 42):
        """Split dataset into train/val/test"""
        random.seed(seed)

        all_ids = list(self.samples.keys())
        random.shuffle(all_ids)

        n = len(all_ids)
        train_end = int(n * train_ratio)
        val_end = train_end + int(n * val_ratio)

        self.train_ids = set(all_ids[:train_end])
        self.val_ids = set(all_ids[train_end:val_end])
        self.test_ids = set(all_ids[val_end:])

    def validate_splits(self) -> Tuple[bool, List[str]]:
        """Validate dataset splits have no overlap"""
        issues = []

        # Check overlaps
        train_val = self.train_ids & self.val_ids
        if train_val:
            issues.append(f"Train-Val overlap: {len(train_val)} samples")

        train_test = self.train_ids & self.test_ids
        if train_test:
            issues.append(f"Train-Test overlap: {len(train_test)} samples")

        val_test = self.val_ids & self.test_ids
        if val_test:
            issues.append(f"Val-Test overlap: {len(val_test)} samples")

        # Check all samples assigned
        all_split_ids = self.train_ids | self.val_ids | self.test_ids
        if len(all_split_ids) != len(self.samples):
            issues.append("Not all samples assigned to splits")

        return len(issues) == 0, issues

    def get_class_distribution(self, split: str = 'train') -> Dict[str, int]:
        """Get class distribution for a split"""
        if split == 'train':
            split_ids = self.train_ids
        elif split == 'val':
            split_ids = self.val_ids
        elif split == 'test':
            split_ids = self.test_ids
        else:
            raise ValueError("Split must be 'train', 'val', or 'test'")

        distribution = {}
        for class_name in self.class_names:
            class_samples = set(self.class_to_samples[class_name])
            count = len(class_samples & split_ids)
            distribution[class_name] = count

        return distribution

    def get_summary(self) -> Dict:
        """Get dataset summary statistics"""
        return {
            'total_samples': len(self.samples),
            'num_classes': len(self.class_names),
            'classes': self.class_names,
            'train_samples': len(self.train_ids),
            'val_samples': len(self.val_ids),
            'test_samples': len(self.test_ids),
            'class_distribution': {
                cls: len(samples)
                for cls, samples in self.class_to_samples.items()
            }
        }

# Example usage
manager = MLDatasetManager()

# Add samples
samples_data = [
    (1, "/data/cat_001.jpg", "cat"),
    (2, "/data/dog_001.jpg", "dog"),
    (3, "/data/cat_002.jpg", "cat"),
    (4, "/data/bird_001.jpg", "bird"),
    (5, "/data/dog_002.jpg", "dog"),
    (6, "/data/cat_003.jpg", "cat"),
    (7, "/data/bird_002.jpg", "bird"),
    (8, "/data/dog_003.jpg", "dog"),
    (9, "/data/cat_004.jpg", "cat"),
    (10, "/data/bird_003.jpg", "bird"),
]

for sample_id, filepath, class_label in samples_data:
    manager.add_sample(sample_id, filepath, class_label)

# Split dataset
manager.split_dataset(train_ratio=0.6, val_ratio=0.2, seed=42)

# Validate
is_valid, issues = manager.validate_splits()
print(f"Splits valid: {is_valid}")
if issues:
    for issue in issues:
        print(f"  - {issue}")

# Get summary
summary = manager.get_summary()
print(f"\nDataset Summary:")
for key, value in summary.items():
    print(f"  {key}: {value}")

# Check distributions
print("\nClass Distribution per Split:")
for split in ['train', 'val', 'test']:
    dist = manager.get_class_distribution(split)
    print(f"  {split}: {dist}")
```

## Validation and Testing

```python
# Create a script: validate_exercise.py

def test_list_operations():
    """Test list comprehensions"""
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    # Test filtering
    evens = [n for n in numbers if n % 2 == 0]
    assert evens == [2, 4, 6, 8, 10], "Even filter failed"

    # Test transformation
    squared = [n**2 for n in numbers]
    assert squared[0] == 1 and squared[-1] == 100, "Squaring failed"

    print("✓ List operations tests passed")

def test_dict_operations():
    """Test dictionary operations"""
    metrics = {"acc": 0.92, "loss": 0.15, "f1": 0.89}

    # Test filtering
    high_metrics = {k: v for k, v in metrics.items() if v > 0.20}
    assert "loss" not in high_metrics, "Dict filtering failed"

    # Test get with default
    lr = metrics.get("learning_rate", 0.001)
    assert lr == 0.001, "Dict get with default failed"

    print("✓ Dict operations tests passed")

def test_set_operations():
    """Test set operations"""
    set_a = {1, 2, 3, 4, 5}
    set_b = {4, 5, 6, 7, 8}

    # Test intersection
    overlap = set_a & set_b
    assert overlap == {4, 5}, "Set intersection failed"

    # Test union
    combined = set_a | set_b
    assert len(combined) == 8, "Set union failed"

    # Test difference
    only_a = set_a - set_b
    assert only_a == {1, 2, 3}, "Set difference failed"

    print("✓ Set operations tests passed")

def test_tuple_operations():
    """Test tuple immutability and usage"""
    config = ("model", "v1", 0.92)

    # Test unpacking
    name, version, acc = config
    assert name == "model", "Tuple unpacking failed"

    # Test immutability
    try:
        config[0] = "new_model"
        assert False, "Tuple should be immutable"
    except TypeError:
        pass  # Expected

    print("✓ Tuple operations tests passed")

if __name__ == "__main__":
    test_list_operations()
    test_dict_operations()
    test_set_operations()
    test_tuple_operations()
    print("\n✓ All validation tests passed!")
```

## Reflection Questions

1. When should you use a list vs. a tuple for ML data?
2. Why are dictionaries useful for storing configuration?
3. How can sets help prevent data leakage in train/test splits?
4. What are the performance implications of list comprehensions vs. for loops?
5. How would you handle a dataset with millions of samples efficiently?
6. When should you use a named tuple instead of a dictionary?
7. How can you ensure data structure choices don't impact model performance?

## Next Steps

After completing this exercise:
- **Exercise 03**: Functions and Modules - Build reusable ML utilities
- **Exercise 04**: File I/O - Read and write ML data files
- **Lecture 02**: Advanced Python Concepts

## Additional Resources

- Python Data Structures: https://docs.python.org/3/tutorial/datastructures.html
- List Comprehensions Guide: https://realpython.com/list-comprehension-python/
- Collections Module: https://docs.python.org/3/library/collections.html
- Performance Tips: https://wiki.python.org/moin/PythonSpeed/PerformanceTips

---

**Congratulations!** You've mastered Python data structures for ML data processing. These skills are fundamental for efficient ML pipeline development.
