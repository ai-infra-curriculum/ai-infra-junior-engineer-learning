# Exercise 06: Git for ML Workflows - DVC and Model Versioning

## Overview

**Difficulty**: Intermediate to Advanced
**Estimated Time**: 90-120 minutes
**Prerequisites**: Exercise 05 - Collaboration, Lecture 04 - Advanced Git for ML

In this exercise, you'll learn ML-specific Git workflows including data versioning with DVC (Data Version Control), managing large model files with Git LFS, experiment tracking, and maintaining reproducibility in ML projects.

## Learning Objectives

By completing this exercise, you will:

- Set up and use DVC for data versioning
- Track large model files with Git LFS
- Version control ML experiments
- Maintain reproducibility with Git
- Manage model artifacts and datasets
- Create reproducible ML pipelines
- Track model lineage and provenance
- Implement ML-specific Git hooks

## Scenario

You're building a production ML system that needs to track:
- Training datasets (multiple versions)
- Model weights and checkpoints
- Experiment configurations
- Training scripts and hyperparameters
- Model evaluation metrics

You need version control for both code AND data, ensuring reproducibility and traceability.

## Prerequisites

```bash
# Install DVC
pip install dvc dvc-s3  # Or dvc-gs for Google Cloud, dvc-azure for Azure

# Install Git LFS
# Mac:
brew install git-lfs

# Linux:
# sudo apt-get install git-lfs

# Windows:
# Download from https://git-lfs.github.com/

# Initialize Git LFS
git lfs install

# Verify installations
dvc version
git lfs version

# Create project
mkdir ml-classification-project
cd ml-classification-project
git init
git config init.defaultBranch main
```

---

## Part 1: Setting Up DVC for Data Versioning

### Task 1.1: Initialize DVC

Set up DVC for tracking data.

**Instructions:**

```bash
# Initialize DVC in your Git repo
dvc init

# This creates .dvc directory and .dvcignore
ls -la

# Commit DVC initialization
git status
git add .dvc .dvcignore
git commit -m "init: initialize DVC for data versioning"

# Configure DVC remote storage (local for now)
mkdir -p /tmp/dvc-storage
dvc remote add -d local /tmp/dvc-storage

# Commit remote configuration
git add .dvc/config
git commit -m "config: add DVC remote storage"

# View DVC configuration
cat .dvc/config
```

**Output:**
```
['remote "local"']
    url = /tmp/dvc-storage
[core]
    remote = local
```

---

### Task 1.2: Track Dataset with DVC

Version control your training data.

**Instructions:**

```bash
# Create a sample dataset
mkdir -p data/raw

# Generate sample training data
cat > data/raw/train.csv << 'EOF'
id,feature1,feature2,label
1,0.5,0.3,0
2,0.8,0.6,1
3,0.2,0.4,0
4,0.9,0.7,1
5,0.3,0.2,0
EOF

cat > data/raw/test.csv << 'EOF'
id,feature1,feature2,label
101,0.6,0.4,1
102,0.7,0.5,1
103,0.3,0.3,0
EOF

# Add dataset to DVC tracking
dvc add data/raw/train.csv
dvc add data/raw/test.csv

# This creates .dvc files
ls data/raw/

# Output: train.csv  train.csv.dvc  test.csv  test.csv.dvc

# The .dvc file contains metadata about the data
cat data/raw/train.csv.dvc
```

**Output:**
```yaml
outs:
- md5: abc123def456...
  size: 145
  path: train.csv
```

```bash
# Add .dvc files to Git (not the actual data!)
git add data/raw/*.dvc data/.gitignore
git commit -m "data: add initial training and test datasets

Datasets:
- train.csv: 5 samples
- test.csv: 3 samples

Tracked with DVC for version control."

# Push data to DVC remote
dvc push

# The actual CSV files are in DVC storage, not Git!
```

---

### Task 1.3: Version Dataset Changes

Track dataset evolution.

**Instructions:**

```bash
# Update the dataset (simulate data collection)
cat >> data/raw/train.csv << 'EOF'
6,0.4,0.5,1
7,0.6,0.3,1
8,0.1,0.2,0
EOF

# Update DVC tracking
dvc add data/raw/train.csv

# The .dvc file changes (new MD5 hash)
git diff data/raw/train.csv.dvc

# Commit the change
git add data/raw/train.csv.dvc
git commit -m "data: expand training set to 8 samples

Added 3 more training examples for better model coverage."

# Push new version to DVC storage
dvc push

# Now you have versioned datasets!
git log --oneline -- data/raw/train.csv.dvc
```

---

### Task 1.4: Retrieve Old Dataset Versions

Time-travel your data.

**Instructions:**

```bash
# Check out old version of dataset
git checkout HEAD~1 data/raw/train.csv.dvc

# Pull the old data
dvc checkout data/raw/train.csv.dvc

# View the data (should be 5 rows again)
wc -l data/raw/train.csv

# Return to latest
git checkout main data/raw/train.csv.dvc
dvc checkout
```

---

## Part 2: Git LFS for Large Model Files

### Task 2.1: Set Up Git LFS

Configure LFS for model files.

**Instructions:**

```bash
# Track model files with LFS
git lfs track "*.h5"
git lfs track "*.pkl"
git lfs track "*.pth"
git lfs track "*.onnx"
git lfs track "*.pb"

# This creates .gitattributes
cat .gitattributes

# Commit LFS configuration
git add .gitattributes
git commit -m "config: track model files with Git LFS

Configure LFS for:
- PyTorch (.pth)
- Keras (.h5)
- Pickle (.pkl)
- ONNX (.onnx)
- TensorFlow (.pb)"
```

---

### Task 2.2: Version Model Checkpoints

Track model weights with LFS.

**Instructions:**

```bash
# Create models directory
mkdir -p models/resnet50

# Simulate model training and saving
cat > models/resnet50/model_v1.0.0.pth << 'EOF'
# This would be actual PyTorch weights
# Simulating with dummy file for exercise
model_checkpoint_v1.0.0
EOF

# Create model metadata
cat > models/resnet50/model_v1.0.0.json << 'EOF'
{
  "model_name": "resnet50",
  "version": "1.0.0",
  "architecture": "ResNet-50",
  "framework": "pytorch",
  "created_at": "2024-01-15T10:00:00Z",
  "training_config": {
    "dataset": "imagenet",
    "epochs": 90,
    "batch_size": 256,
    "learning_rate": 0.1,
    "optimizer": "sgd"
  },
  "metrics": {
    "train_accuracy": 0.876,
    "val_accuracy": 0.852,
    "test_accuracy": 0.848
  },
  "data_version": "imagenet_v2023.1",
  "git_commit": "abc123def456"
}
EOF

# Add to Git (LFS will handle the .pth file)
git add models/
git commit -m "model: add ResNet-50 v1.0.0

Initial model checkpoint:
- Architecture: ResNet-50
- Test accuracy: 84.8%
- Trained on ImageNet v2023.1

Model weights tracked with Git LFS."

# LFS automatically pushes large files to LFS storage
git push  # (if you have remote configured)
```

---

### Task 2.3: Tag Model Releases

Create tagged releases for models.

**Instructions:**

```bash
# Tag the model version
git tag -a model-v1.0.0 -m "Model Release v1.0.0

ResNet-50 image classifier
- Test accuracy: 84.8%
- Production-ready

Training details:
- Dataset: ImageNet v2023.1
- 90 epochs, batch size 256
- SGD optimizer, LR 0.1

Deployment:
- Compatible with PyTorch 2.0+
- Input: 224x224 RGB images
- Output: 1000-class predictions"

# View tag
git show model-v1.0.0

# List all model tags
git tag -l "model-*"
```

---

## Part 3: Experiment Tracking with Git

### Task 3.1: Version Experiment Configurations

Track ML experiments.

**Instructions:**

```bash
# Create experiments directory
mkdir -p experiments

# Experiment 1: Baseline
cat > experiments/exp-001-baseline.yaml << 'EOF'
experiment:
  id: "exp-001"
  name: "baseline-resnet50"
  description: "Baseline ResNet-50 with default hyperparameters"
  created_at: "2024-01-15T10:00:00Z"

model:
  architecture: "resnet50"
  pretrained: false

data:
  dataset: "imagenet"
  version: "2023.1"
  train_split: 0.8
  val_split: 0.1
  test_split: 0.1

training:
  epochs: 90
  batch_size: 256
  learning_rate: 0.1
  optimizer: "sgd"
  momentum: 0.9
  weight_decay: 0.0001
  lr_scheduler: "step"
  lr_decay_epochs: [30, 60, 80]
  lr_decay_rate: 0.1

augmentation:
  random_crop: true
  random_flip: true
  normalize: true

hardware:
  gpus: 4
  distributed: true

results:
  train_accuracy: 0.876
  val_accuracy: 0.852
  test_accuracy: 0.848
  train_loss: 0.342
  val_loss: 0.389
  training_time_hours: 48.5
EOF

git add experiments/exp-001-baseline.yaml
git commit -m "experiment: add baseline ResNet-50 experiment

Experiment ID: exp-001
Test accuracy: 84.8%
Training time: 48.5 hours on 4 GPUs"

# Experiment 2: Increased learning rate
cat > experiments/exp-002-higher-lr.yaml << 'EOF'
experiment:
  id: "exp-002"
  name: "resnet50-higher-lr"
  description: "ResNet-50 with higher initial learning rate"
  parent_experiment: "exp-001"
  created_at: "2024-01-16T09:00:00Z"

model:
  architecture: "resnet50"
  pretrained: false

data:
  dataset: "imagenet"
  version: "2023.1"
  train_split: 0.8
  val_split: 0.1
  test_split: 0.1

training:
  epochs: 90
  batch_size: 256
  learning_rate: 0.3  # CHANGED: increased from 0.1
  optimizer: "sgd"
  momentum: 0.9
  weight_decay: 0.0001
  lr_scheduler: "step"
  lr_decay_epochs: [30, 60, 80]
  lr_decay_rate: 0.1

augmentation:
  random_crop: true
  random_flip: true
  normalize: true

hardware:
  gpus: 4
  distributed: true

results:
  train_accuracy: 0.891
  val_accuracy: 0.867
  test_accuracy: 0.862
  train_loss: 0.298
  val_loss: 0.356
  training_time_hours: 47.2
EOF

git add experiments/exp-002-higher-lr.yaml
git commit -m "experiment: higher learning rate improves accuracy

Experiment ID: exp-002
Test accuracy: 86.2% (+1.4% vs baseline)
Training time: 47.2 hours

Changed:
- Learning rate: 0.1 → 0.3

Result: Improved accuracy with faster convergence."

# View experiment history
git log --oneline -- experiments/
```

---

### Task 3.2: Branch Per Experiment

Use branches for experimental work.

**Instructions:**

```bash
# Create experiment branch
git switch -c experiment/data-augmentation

# Add new augmentation strategy
cat > experiments/exp-003-augmentation.yaml << 'EOF'
experiment:
  id: "exp-003"
  name: "resnet50-advanced-augmentation"
  description: "ResNet-50 with advanced augmentation techniques"
  parent_experiment: "exp-002"
  created_at: "2024-01-17T08:00:00Z"

model:
  architecture: "resnet50"
  pretrained: false

data:
  dataset: "imagenet"
  version: "2023.1"
  train_split: 0.8
  val_split: 0.1
  test_split: 0.1

training:
  epochs: 90
  batch_size: 256
  learning_rate: 0.3
  optimizer: "sgd"
  momentum: 0.9
  weight_decay: 0.0001
  lr_scheduler: "step"
  lr_decay_epochs: [30, 60, 80]
  lr_decay_rate: 0.1

augmentation:
  random_crop: true
  random_flip: true
  normalize: true
  # NEW augmentations:
  random_rotation: true
  rotation_degrees: 15
  color_jitter: true
  jitter_brightness: 0.2
  jitter_contrast: 0.2
  cutout: true
  cutout_size: 16

hardware:
  gpus: 4
  distributed: true

results:
  train_accuracy: 0.903
  val_accuracy: 0.881
  test_accuracy: 0.876
  train_loss: 0.267
  val_loss: 0.324
  training_time_hours: 52.3
EOF

git add experiments/exp-003-augmentation.yaml
git commit -m "experiment: advanced augmentation improves accuracy

Experiment ID: exp-003
Test accuracy: 87.6% (+1.4% vs exp-002)

Added augmentations:
- Random rotation (±15°)
- Color jitter
- Cutout regularization

Trade-off: +5 hours training time but better accuracy."

# If experiment succeeds, merge to main
git switch main
git merge experiment/data-augmentation --no-edit

# Tag successful experiment
git tag -a exp-003-success -m "Successful experiment: advanced augmentation"
```

---

## Part 4: Reproducibility

### Task 4.1: Lock Dependencies

Ensure reproducible environments.

**Instructions:**

```bash
# Create comprehensive requirements
cat > requirements.txt << 'EOF'
# Core ML Framework
torch==2.1.0
torchvision==0.16.0

# Data Processing
numpy==1.26.0
pandas==2.1.1
pillow==10.1.0

# Experiment Tracking
mlflow==2.8.0
wandb==0.15.12

# Version Control
dvc==3.30.0
dvc-s3==3.0.0

# Utilities
pyyaml==6.0.1
python-dotenv==1.0.0
tqdm==4.66.1
EOF

# Lock exact versions with pip freeze
pip install -r requirements.txt
pip freeze > requirements.lock

git add requirements.txt requirements.lock
git commit -m "deps: lock dependency versions for reproducibility

Added requirements.lock with exact versions to ensure
identical environments across training runs."

# Create environment.yaml for conda users
cat > environment.yaml << 'EOF'
name: ml-classification
channels:
  - pytorch
  - conda-forge
  - defaults
dependencies:
  - python=3.11
  - pytorch=2.1.0
  - torchvision=0.16.0
  - numpy=1.26.0
  - pandas=2.1.1
  - pillow=10.1.0
  - pip
  - pip:
    - mlflow==2.8.0
    - wandb==0.15.12
    - dvc==3.30.0
EOF

git add environment.yaml
git commit -m "deps: add conda environment specification"
```

---

### Task 4.2: Document Training Process

Create reproducible training documentation.

**Instructions:**

```bash
# Create training README
cat > experiments/README.md << 'EOF'
# Experiment Tracking

## Reproducing Experiments

### Prerequisites
```bash
# Install dependencies
pip install -r requirements.lock

# Setup DVC
dvc pull
```

### Running Experiments

#### Experiment 001: Baseline
```bash
# Checkout experiment commit
git checkout <commit-hash>

# Get data
dvc pull

# Run training
python train.py --config experiments/exp-001-baseline.yaml

# Expected results:
# - Test accuracy: ~84.8%
# - Training time: ~48.5 hours on 4x V100
```

#### Experiment 002: Higher Learning Rate
```bash
git checkout <commit-hash>
dvc pull
python train.py --config experiments/exp-002-higher-lr.yaml

# Expected results:
# - Test accuracy: ~86.2%
```

## Experiment Naming Convention
```
exp-<number>-<description>.yaml

Examples:
- exp-001-baseline.yaml
- exp-002-higher-lr.yaml
- exp-003-augmentation.yaml
```

## Experiment Fields
Each experiment YAML must contain:
- `experiment.id`: Unique identifier
- `experiment.name`: Human-readable name
- `experiment.description`: What is being tested
- `model.*`: Model architecture and config
- `data.*`: Dataset version and splits
- `training.*`: Hyperparameters
- `results.*`: Metrics achieved

## Data Versioning
All experiments reference specific data versions:
```yaml
data:
  dataset: "imagenet"
  version: "2023.1"  # Tracked with DVC
```

To get specific data version:
```bash
git checkout <commit> data/
dvc checkout
```

## Model Versioning
Trained models are tagged:
```bash
git tag -l "model-*"
```

Get specific model:
```bash
git checkout model-v1.0.0
git lfs pull
```
EOF

git add experiments/README.md
git commit -m "docs: add experiment reproduction guide"
```

---

## Part 5: ML-Specific Git Hooks

### Task 5.1: Pre-Commit Validation

Prevent common ML mistakes.

**Instructions:**

```bash
# Install pre-commit framework
pip install pre-commit

# Create pre-commit configuration
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=1000']  # Prevent large files in Git
      - id: check-json
      - id: check-merge-conflict
      - id: detect-private-key

  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/PyCQA/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
        args: ['--max-line-length=88']

  # ML-specific checks
  - repo: local
    hooks:
      - id: check-model-metadata
        name: Check model metadata
        entry: python scripts/check_model_metadata.py
        language: python
        files: models/.*\.json$

      - id: validate-experiment-config
        name: Validate experiment configs
        entry: python scripts/validate_experiment.py
        language: python
        files: experiments/.*\.yaml$
EOF

# Create validation scripts
mkdir -p scripts

cat > scripts/check_model_metadata.py << 'EOF'
#!/usr/bin/env python3
"""Validate model metadata files."""

import json
import sys
from pathlib import Path

REQUIRED_FIELDS = [
    "model_name",
    "version",
    "architecture",
    "framework",
    "created_at",
    "training_config",
    "metrics"
]

def validate_metadata(filepath):
    """Validate model metadata JSON."""
    with open(filepath) as f:
        metadata = json.load(f)

    missing = [field for field in REQUIRED_FIELDS if field not in metadata]

    if missing:
        print(f"Error in {filepath}: Missing fields: {missing}")
        return False

    # Check version format
    version = metadata.get("version", "")
    if not version or len(version.split(".")) != 3:
        print(f"Error in {filepath}: Invalid version format. Use X.Y.Z")
        return False

    return True

if __name__ == "__main__":
    files = sys.argv[1:]
    all_valid = all(validate_metadata(f) for f in files)
    sys.exit(0 if all_valid else 1)
EOF

cat > scripts/validate_experiment.py << 'EOF'
#!/usr/bin/env python3
"""Validate experiment configuration files."""

import yaml
import sys

REQUIRED_SECTIONS = ["experiment", "model", "data", "training"]

def validate_experiment(filepath):
    """Validate experiment YAML."""
    with open(filepath) as f:
        config = yaml.safe_load(f)

    missing = [s for s in REQUIRED_SECTIONS if s not in config]

    if missing:
        print(f"Error in {filepath}: Missing sections: {missing}")
        return False

    # Check experiment ID format
    exp_id = config.get("experiment", {}).get("id")
    if not exp_id or not exp_id.startswith("exp-"):
        print(f"Error in {filepath}: Invalid experiment ID format. Use exp-XXX")
        return False

    return True

if __name__ == "__main__":
    files = sys.argv[1:]
    all_valid = all(validate_experiment(f) for f in files)
    sys.exit(0 if all_valid else 1)
EOF

chmod +x scripts/*.py

# Install pre-commit hooks
pre-commit install

git add .pre-commit-config.yaml scripts/
git commit -m "ci: add pre-commit hooks for ML workflows

Hooks:
- Code formatting (Black)
- Linting (Flake8)
- YAML/JSON validation
- Model metadata validation
- Experiment config validation
- Prevent large files in Git"

# Test pre-commit
# pre-commit run --all-files
```

---

## Part 6: DVC Pipelines

### Task 6.1: Define ML Pipeline

Create reproducible ML pipeline with DVC.

**Instructions:**

```bash
# Create pipeline stages
dvc stage add -n prepare \
    -d data/raw \
    -o data/processed \
    python scripts/prepare_data.py

dvc stage add -n train \
    -d data/processed \
    -d experiments/exp-001-baseline.yaml \
    -o models/resnet50/model_v1.0.0.pth \
    -M metrics.json \
    python train.py --config experiments/exp-001-baseline.yaml

dvc stage add -n evaluate \
    -d models/resnet50/model_v1.0.0.pth \
    -d data/processed/test \
    -M evaluation.json \
    python evaluate.py

# This creates dvc.yaml
cat dvc.yaml
```

**Output:**
```yaml
stages:
  prepare:
    cmd: python scripts/prepare_data.py
    deps:
      - data/raw
    outs:
      - data/processed

  train:
    cmd: python train.py --config experiments/exp-001-baseline.yaml
    deps:
      - data/processed
      - experiments/exp-001-baseline.yaml
    outs:
      - models/resnet50/model_v1.0.0.pth
    metrics:
      - metrics.json

  evaluate:
    cmd: python evaluate.py
    deps:
      - models/resnet50/model_v1.0.0.pth
      - data/processed/test
    metrics:
      - evaluation.json
```

```bash
# Run pipeline
# dvc repro

git add dvc.yaml dvc.lock
git commit -m "pipeline: define ML training pipeline with DVC

Pipeline stages:
1. prepare: Data preprocessing
2. train: Model training
3. evaluate: Model evaluation

Fully reproducible with 'dvc repro'"
```

---

## Validation

### Verify Your Setup

```bash
# Check DVC configuration
dvc status
dvc dag  # View pipeline DAG

# Check Git LFS
git lfs ls-files

# Check pre-commit
pre-commit run --all-files

# View experiment history
git log --oneline -- experiments/

# View model tags
git tag -l "model-*"

# Check data versioning
git log --oneline -- data/
```

---

## Challenge Tasks

### Challenge 1: Implement Model Registry

Create a model registry with metadata:

```bash
# models/registry.json
{
  "models": [
    {
      "id": "model-001",
      "name": "resnet50_v1.0.0",
      "git_tag": "model-v1.0.0",
      "accuracy": 0.848,
      "deployed": true
    }
  ]
}
```

### Challenge 2: Automate Experiment Tracking

Create script to automatically log experiments to MLflow/W&B with Git commit info.

### Challenge 3: Data Quality Checks

Add DVC pipeline stage for data validation before training.

---

## Troubleshooting

**Issue**: "DVC remote storage full"
```bash
# Clean up old data versions
dvc gc -w  # Garbage collect
```

**Issue**: "Git LFS quota exceeded"
```bash
# Prune old LFS objects
git lfs prune
```

**Issue**: "Cannot reproduce experiment"
```bash
# Ensure exact commit and data version
git checkout <commit>
dvc checkout
pip install -r requirements.lock
```

---

## Reflection Questions

1. **Why use DVC instead of committing data to Git?**
2. **When should you use Git LFS vs. DVC?**
3. **How does versioning experiments help ML development?**
4. **What makes an ML experiment reproducible?**
5. **How do you track model lineage from data to deployment?**

---

## Summary

Congratulations! You've mastered ML-specific Git workflows:

- ✅ Data versioning with DVC
- ✅ Model tracking with Git LFS
- ✅ Experiment versioning and tracking
- ✅ Reproducibility with locked dependencies
- ✅ ML pipelines with DVC
- ✅ Pre-commit hooks for ML
- ✅ Model and data provenance

### Key Commands

```bash
dvc init                      # Initialize DVC
dvc add <file>                # Track file with DVC
dvc push/pull                 # Sync DVC storage
git lfs track <pattern>       # Track with LFS
git tag model-v1.0.0          # Tag model versions
dvc repro                     # Reproduce pipeline
pre-commit install            # Setup hooks
```

### Next Steps

- Exercise 07: Advanced Git techniques
- Apply to your ML projects

**Outstanding work!** You can now manage ML projects with proper version control.
