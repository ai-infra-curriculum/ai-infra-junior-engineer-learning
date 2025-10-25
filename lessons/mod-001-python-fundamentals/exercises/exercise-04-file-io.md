# Exercise 04: Reading and Writing ML Data Files

## Overview

This exercise teaches you how to effectively read and write various file formats commonly used in machine learning workflows: CSV, JSON, YAML, pickle, and configuration files. You'll learn proper file handling, error management, and best practices for data persistence in ML applications.

## Learning Objectives

By completing this exercise, you will:
- Master file I/O operations with context managers
- Read and write CSV files for dataset storage
- Handle JSON for model metadata and configurations
- Work with YAML for human-readable configs
- Use pickle for Python object serialization
- Implement safe file operations with error handling
- Process large files efficiently with streaming
- Manage file paths across different operating systems

## Prerequisites

- Completed Exercise 01-03
- Understanding of Python data structures
- Basic knowledge of file systems

## Time Required

- Estimated: 90-120 minutes
- Difficulty: Intermediate

## Part 1: CSV Files for Datasets

### Step 1: Reading CSV Files

```python
# Create a script: csv_operations.py

import csv
from typing import List, Dict, Tuple

def read_csv_basic(filepath: str) -> List[List[str]]:
    """Read CSV file into list of rows"""
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        rows = list(reader)
    return rows

def read_csv_with_headers(filepath: str) -> Tuple[List[str], List[List[str]]]:
    """Read CSV with separate headers and data"""
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        headers = next(reader)  # First row as headers
        data = list(reader)
    return headers, data

def read_csv_as_dicts(filepath: str) -> List[Dict[str, str]]:
    """Read CSV as list of dictionaries"""
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        data = list(reader)
    return data

def read_csv_filtered(filepath: str, condition: callable) -> List[Dict]:
    """Read CSV with filtering"""
    results = []
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if condition(row):
                results.append(row)
    return results

# Example: Create sample dataset
def create_sample_dataset(filepath: str):
    """Create sample ML dataset"""
    with open(filepath, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # Write header
        writer.writerow(['id', 'feature1', 'feature2', 'feature3', 'label'])

        # Write data
        for i in range(100):
            writer.writerow([
                i,
                round(i * 0.5, 2),
                round(i * 1.2, 2),
                round(i * 0.8, 2),
                i % 2  # Binary label
            ])

    print(f"Created dataset: {filepath}")

# Example usage
if __name__ == "__main__":
    # Create sample data
    create_sample_dataset("training_data.csv")

    # Read different ways
    print("=== Basic Read ===")
    rows = read_csv_basic("training_data.csv")
    print(f"Total rows: {len(rows)}")
    print(f"First 3 rows: {rows[:3]}")

    print("\n=== Read with Headers ===")
    headers, data = read_csv_with_headers("training_data.csv")
    print(f"Headers: {headers}")
    print(f"First data row: {data[0]}")

    print("\n=== Read as Dicts ===")
    dict_data = read_csv_as_dicts("training_data.csv")
    print(f"First record: {dict_data[0]}")

    print("\n=== Filtered Read ===")
    # Filter positive labels only
    positive_samples = read_csv_filtered(
        "training_data.csv",
        lambda row: row['label'] == '1'
    )
    print(f"Positive samples: {len(positive_samples)}")
```

### Step 2: Writing CSV Files

```python
# Create a script: csv_writer.py

import csv
from typing import List, Dict

def write_csv_from_lists(filepath: str,
                        headers: List[str],
                        data: List[List]) -> None:
    """Write CSV from list of lists"""
    with open(filepath, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(data)

def write_csv_from_dicts(filepath: str,
                        data: List[Dict],
                        fieldnames: List[str] = None) -> None:
    """Write CSV from list of dictionaries"""
    if not data:
        return

    if fieldnames is None:
        fieldnames = list(data[0].keys())

    with open(filepath, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def append_to_csv(filepath: str, row: Dict) -> None:
    """Append single row to existing CSV"""
    # Check if file exists to determine if header is needed
    import os
    file_exists = os.path.isfile(filepath)

    with open(filepath, 'a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=row.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

def write_predictions(filepath: str,
                     sample_ids: List[int],
                     predictions: List[float],
                     labels: List[int] = None) -> None:
    """Write model predictions to CSV"""
    with open(filepath, 'w', newline='', encoding='utf-8') as file:
        headers = ['sample_id', 'prediction']
        if labels is not None:
            headers.append('true_label')

        writer = csv.writer(file)
        writer.writerow(headers)

        for i, (sid, pred) in enumerate(zip(sample_ids, predictions)):
            row = [sid, pred]
            if labels is not None:
                row.append(labels[i])
            writer.writerow(row)

# Example usage
if __name__ == "__main__":
    # Write from lists
    headers = ['epoch', 'train_loss', 'val_loss', 'accuracy']
    training_history = [
        [1, 0.45, 0.52, 0.85],
        [2, 0.32, 0.38, 0.88],
        [3, 0.25, 0.30, 0.91],
    ]

    write_csv_from_lists("training_history.csv", headers, training_history)
    print("✓ Written training_history.csv")

    # Write from dicts
    experiments = [
        {'exp_id': 'exp001', 'model': 'resnet', 'accuracy': 0.92, 'runtime': 3600},
        {'exp_id': 'exp002', 'model': 'vgg', 'accuracy': 0.88, 'runtime': 4200},
        {'exp_id': 'exp003', 'model': 'mobilenet', 'accuracy': 0.85, 'runtime': 1800},
    ]

    write_csv_from_dicts("experiments.csv", experiments)
    print("✓ Written experiments.csv")

    # Append new experiment
    new_exp = {'exp_id': 'exp004', 'model': 'efficientnet', 'accuracy': 0.94, 'runtime': 2400}
    append_to_csv("experiments.csv", new_exp)
    print("✓ Appended to experiments.csv")

    # Write predictions
    write_predictions(
        "predictions.csv",
        sample_ids=[1, 2, 3, 4, 5],
        predictions=[0.92, 0.15, 0.88, 0.65, 0.95],
        labels=[1, 0, 1, 1, 1]
    )
    print("✓ Written predictions.csv")
```

## Part 2: JSON for Configuration and Metadata

### Step 3: Working with JSON

```python
# Create a script: json_operations.py

import json
from typing import Dict, Any, List
from pathlib import Path

def save_model_metadata(filepath: str, metadata: Dict[str, Any]) -> None:
    """Save model metadata to JSON"""
    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(metadata, file, indent=2)

def load_model_metadata(filepath: str) -> Dict[str, Any]:
    """Load model metadata from JSON"""
    with open(filepath, 'r', encoding='utf-8') as file:
        metadata = json.load(file)
    return metadata

def save_training_config(filepath: str, config: Dict) -> None:
    """Save training configuration"""
    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(config, file, indent=2, sort_keys=True)
    print(f"✓ Saved config to {filepath}")

def load_training_config(filepath: str) -> Dict:
    """Load training configuration"""
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            config = json.load(file)
        return config
    except FileNotFoundError:
        print(f"Config file not found: {filepath}")
        return {}
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in {filepath}: {e}")
        return {}

def update_experiment_log(filepath: str, experiment: Dict) -> None:
    """Append experiment to log file"""
    # Load existing log
    if Path(filepath).exists():
        with open(filepath, 'r', encoding='utf-8') as file:
            log = json.load(file)
    else:
        log = {'experiments': []}

    # Add new experiment
    log['experiments'].append(experiment)

    # Save updated log
    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(log, file, indent=2)

def save_metrics_history(filepath: str, history: Dict[str, List[float]]) -> None:
    """Save training metrics history"""
    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(history, file, indent=2)

# Example usage
if __name__ == "__main__":
    # Model metadata
    metadata = {
        "model_name": "ResNet50",
        "version": "1.0.0",
        "framework": "pytorch",
        "input_shape": [3, 224, 224],
        "num_classes": 1000,
        "accuracy": 0.92,
        "trained_on": "2024-10-18",
        "hyperparameters": {
            "learning_rate": 0.001,
            "batch_size": 32,
            "epochs": 100
        }
    }

    save_model_metadata("model_metadata.json", metadata)
    print("✓ Saved model metadata")

    loaded_metadata = load_model_metadata("model_metadata.json")
    print(f"Loaded accuracy: {loaded_metadata['accuracy']}")

    # Training config
    config = {
        "model": {
            "type": "resnet50",
            "pretrained": True
        },
        "training": {
            "epochs": 100,
            "batch_size": 32,
            "learning_rate": 0.001,
            "optimizer": "adam"
        },
        "data": {
            "train_path": "/data/train",
            "val_path": "/data/val",
            "augmentation": True
        }
    }

    save_training_config("config.json", config)

    # Experiment logging
    experiment = {
        "id": "exp001",
        "timestamp": "2024-10-18T10:30:00",
        "model": "resnet50",
        "accuracy": 0.92,
        "loss": 0.15
    }

    update_experiment_log("experiments.json", experiment)
    print("✓ Logged experiment")

    # Metrics history
    history = {
        "epoch": [1, 2, 3, 4, 5],
        "train_loss": [0.45, 0.32, 0.25, 0.20, 0.18],
        "val_loss": [0.52, 0.38, 0.30, 0.28, 0.26],
        "accuracy": [0.85, 0.88, 0.91, 0.92, 0.93]
    }

    save_metrics_history("metrics_history.json", history)
    print("✓ Saved metrics history")
```

## Part 3: YAML for Human-Readable Configs

### Step 4: Working with YAML

```python
# Create a script: yaml_operations.py

import yaml
from typing import Dict, Any
from pathlib import Path

def save_yaml_config(filepath: str, config: Dict[str, Any]) -> None:
    """Save configuration to YAML"""
    with open(filepath, 'w', encoding='utf-8') as file:
        yaml.dump(config, file, default_flow_style=False, sort_keys=False)

def load_yaml_config(filepath: str) -> Dict[str, Any]:
    """Load configuration from YAML"""
    with open(filepath, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    return config

def merge_configs(default_config: Dict, user_config: Dict) -> Dict:
    """Merge user config with defaults"""
    merged = default_config.copy()
    merged.update(user_config)
    return merged

# Example usage
if __name__ == "__main__":
    # Create ML pipeline config
    pipeline_config = {
        'model': {
            'name': 'ResNet50',
            'pretrained': True,
            'freeze_layers': 10
        },
        'training': {
            'epochs': 100,
            'batch_size': 32,
            'learning_rate': 0.001,
            'optimizer': {
                'type': 'adam',
                'betas': [0.9, 0.999],
                'weight_decay': 0.0001
            }
        },
        'data': {
            'train_path': '/data/train',
            'val_path': '/data/val',
            'test_path': '/data/test',
            'augmentation': {
                'horizontal_flip': True,
                'rotation': 15,
                'brightness': 0.2
            }
        },
        'logging': {
            'level': 'INFO',
            'save_dir': './logs',
            'tensorboard': True
        }
    }

    save_yaml_config("pipeline_config.yaml", pipeline_config)
    print("✓ Saved YAML config")

    loaded_config = load_yaml_config("pipeline_config.yaml")
    print(f"Loaded model: {loaded_config['model']['name']}")
    print(f"Batch size: {loaded_config['training']['batch_size']}")
```

## Part 4: Pickle for Python Objects

### Step 5: Serializing Python Objects

```python
# Create a script: pickle_operations.py

import pickle
from typing import Any, Dict, List

def save_object(filepath: str, obj: Any) -> None:
    """Save Python object to pickle file"""
    with open(filepath, 'wb') as file:
        pickle.dump(obj, file)

def load_object(filepath: str) -> Any:
    """Load Python object from pickle file"""
    with open(filepath, 'rb') as file:
        obj = pickle.load(file)
    return obj

class ModelCheckpoint:
    """Example class for model checkpointing"""

    def __init__(self, model_state: Dict, optimizer_state: Dict,
                 epoch: int, metrics: Dict):
        self.model_state = model_state
        self.optimizer_state = optimizer_state
        self.epoch = epoch
        self.metrics = metrics
        self.timestamp = "2024-10-18"

    def __repr__(self):
        return f"Checkpoint(epoch={self.epoch}, metrics={self.metrics})"

# Example usage
if __name__ == "__main__":
    # Save simple objects
    data = {'accuracy': 0.92, 'loss': 0.15}
    save_object("metrics.pkl", data)
    print("✓ Saved metrics pickle")

    loaded_data = load_object("metrics.pkl")
    print(f"Loaded: {loaded_data}")

    # Save complex object
    checkpoint = ModelCheckpoint(
        model_state={'layer1.weight': [0.1, 0.2, 0.3]},
        optimizer_state={'lr': 0.001},
        epoch=50,
        metrics={'accuracy': 0.92, 'loss': 0.15}
    )

    save_object("checkpoint.pkl", checkpoint)
    print("✓ Saved checkpoint")

    loaded_checkpoint = load_object("checkpoint.pkl")
    print(f"Loaded: {loaded_checkpoint}")
```

## Part 5: Large File Processing

### Step 6: Streaming Large Files

```python
# Create a script: large_file_processing.py

from typing import Iterator, List, Dict
import csv

def read_csv_chunks(filepath: str,
                   chunk_size: int = 1000) -> Iterator[List[Dict]]:
    """Read large CSV in chunks"""
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        chunk = []
        for row in reader:
            chunk.append(row)

            if len(chunk) >= chunk_size:
                yield chunk
                chunk = []

        # Yield remaining rows
        if chunk:
            yield chunk

def process_large_dataset(filepath: str) -> Dict[str, float]:
    """Process large dataset in chunks"""
    total_samples = 0
    total_positive = 0

    for chunk in read_csv_chunks(filepath, chunk_size=100):
        total_samples += len(chunk)
        total_positive += sum(1 for row in chunk if row['label'] == '1')

    return {
        'total_samples': total_samples,
        'positive_ratio': total_positive / total_samples if total_samples > 0 else 0
    }

def read_file_lines(filepath: str) -> Iterator[str]:
    """Read file line by line (memory efficient)"""
    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            yield line.strip()

# Example usage
if __name__ == "__main__":
    # Process in chunks
    stats = process_large_dataset("training_data.csv")
    print(f"Dataset stats: {stats}")
```

## Part 6: Comprehensive File Manager

### Step 7: Build a Complete File Manager

```python
# Create a script: file_manager.py

import json
import csv
import yaml
import pickle
from pathlib import Path
from typing import Any, Dict, List, Union

class MLFileManager:
    """Comprehensive file manager for ML workflows"""

    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, data: Any, filename: str, format: str = 'auto') -> None:
        """
        Save data in specified format.

        Args:
            data: Data to save
            filename: Output filename
            format: Format ('json', 'yaml', 'csv', 'pickle', or 'auto')
        """
        filepath = self.base_dir / filename

        # Auto-detect format from extension
        if format == 'auto':
            format = filepath.suffix[1:]  # Remove dot

        if format == 'json':
            self._save_json(filepath, data)
        elif format == 'yaml' or format == 'yml':
            self._save_yaml(filepath, data)
        elif format == 'csv':
            self._save_csv(filepath, data)
        elif format == 'pkl' or format == 'pickle':
            self._save_pickle(filepath, data)
        else:
            raise ValueError(f"Unsupported format: {format}")

        print(f"✓ Saved {filename}")

    def load(self, filename: str, format: str = 'auto') -> Any:
        """Load data from file"""
        filepath = self.base_dir / filename

        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        if format == 'auto':
            format = filepath.suffix[1:]

        if format == 'json':
            return self._load_json(filepath)
        elif format == 'yaml' or format == 'yml':
            return self._load_yaml(filepath)
        elif format == 'csv':
            return self._load_csv(filepath)
        elif format == 'pkl' or format == 'pickle':
            return self._load_pickle(filepath)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _save_json(self, filepath: Path, data: Any) -> None:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def _load_json(self, filepath: Path) -> Any:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_yaml(self, filepath: Path, data: Any) -> None:
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False)

    def _load_yaml(self, filepath: Path) -> Any:
        with open(filepath, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _save_csv(self, filepath: Path, data: List[Dict]) -> None:
        if not data:
            return

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)

    def _load_csv(self, filepath: Path) -> List[Dict]:
        with open(filepath, 'r', encoding='utf-8') as f:
            return list(csv.DictReader(f))

    def _save_pickle(self, filepath: Path, data: Any) -> None:
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)

    def _load_pickle(self, filepath: Path) -> Any:
        with open(filepath, 'rb') as f:
            return pickle.load(f)

    def list_files(self, pattern: str = '*') -> List[str]:
        """List files matching pattern"""
        return [f.name for f in self.base_dir.glob(pattern)]

# Example usage
if __name__ == "__main__":
    manager = MLFileManager(base_dir="ml_data")

    # Save different formats
    config = {'model': 'resnet', 'lr': 0.001}
    manager.save(config, 'config.json')
    manager.save(config, 'config.yaml')

    # Save CSV
    data = [
        {'id': 1, 'accuracy': 0.92, 'loss': 0.15},
        {'id': 2, 'accuracy': 0.88, 'loss': 0.22}
    ]
    manager.save(data, 'results.csv')

    # Load back
    loaded_config = manager.load('config.json')
    print(f"Loaded config: {loaded_config}")

    # List files
    files = manager.list_files('*.json')
    print(f"JSON files: {files}")
```

## Validation

```python
# Create a script: validate_file_io.py

def validate_exercise():
    """Validate file I/O exercise"""
    print("=== File I/O Validation ===\n")

    # Test CSV
    import csv
    with open('test.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['a', 'b', 'c'])

    with open('test.csv', 'r') as f:
        reader = csv.reader(f)
        rows = list(reader)

    assert rows[0] == ['a', 'b', 'c'], "CSV test failed"
    print("✓ CSV operations work")

    # Test JSON
    import json
    data = {'test': 123}

    with open('test.json', 'w') as f:
        json.dump(data, f)

    with open('test.json', 'r') as f:
        loaded = json.load(f)

    assert loaded == data, "JSON test failed"
    print("✓ JSON operations work")

    print("\n✓ All validations passed!")

    # Cleanup
    import os
    os.remove('test.csv')
    os.remove('test.json')

if __name__ == "__main__":
    validate_exercise()
```

## Reflection Questions

1. When should you use CSV vs JSON for data storage?
2. What are the security implications of using pickle?
3. How do you handle file operations across different operating systems?
4. When is it necessary to process files in chunks?
5. What are the advantages of YAML over JSON for configuration?
6. How do you ensure file operations are atomic and safe?

## Next Steps

- **Exercise 05**: Error Handling for robust file operations
- **Exercise 06**: Async Programming for concurrent I/O
- **Lecture 03**: Python DevOps Integration

## Additional Resources

- CSV Module: https://docs.python.org/3/library/csv.html
- JSON Module: https://docs.python.org/3/library/json.html
- PyYAML: https://pyyaml.org/wiki/PyYAMLDocumentation
- Pickle Security: https://docs.python.org/3/library/pickle.html#module-pickle

---

**Congratulations!** You've mastered file I/O operations for ML workflows. You can now persist and load data efficiently across various formats.
