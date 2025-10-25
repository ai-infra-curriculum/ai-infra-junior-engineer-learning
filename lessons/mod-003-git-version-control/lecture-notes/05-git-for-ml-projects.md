# Lecture 05: Git for Large-Scale ML Projects

## Table of Contents
1. [Introduction](#introduction)
2. [Git Large File Storage (LFS)](#git-large-file-storage-lfs)
3. [Managing ML Artifacts](#managing-ml-artifacts)
4. [Monorepo Strategies](#monorepo-strategies)
5. [Git Workflows for ML Teams](#git-workflows-for-ml-teams)
6. [Performance Optimization](#performance-optimization)
7. [ML-Specific Best Practices](#ml-specific-best-practices)
8. [Summary and Key Takeaways](#summary-and-key-takeaways)

## Introduction

Machine learning projects present unique challenges for version control:
- **Large binary files**: Models, datasets, Docker images
- **Experiment tracking**: Managing hundreds of training runs
- **Complex dependencies**: ML frameworks, data pipelines, infrastructure code
- **Team collaboration**: Data scientists, ML engineers, infrastructure engineers
- **Reproducibility**: Ensuring experiments can be recreated

This lecture addresses these challenges with Git strategies specifically designed for ML infrastructure.

### Learning Objectives

By the end of this lecture, you will:
- Use Git LFS to manage large ML artifacts efficiently
- Organize ML projects for scalability and team collaboration
- Implement effective branching strategies for ML workflows
- Optimize Git performance for large repositories
- Apply ML-specific best practices to maintain clean, reproducible projects
- Handle common pitfalls in ML version control

### Prerequisites
- Completion of Lectures 01-04 in this module
- Understanding of ML workflows (training, evaluation, deployment)
- Familiarity with ML artifacts (models, datasets, checkpoints)

**Duration**: 90 minutes
**Difficulty**: Intermediate to Advanced

---

## 1. Git Large File Storage (LFS)

### The Problem with Large Files in Git

Git was designed for source code (text files), not large binary files. When you commit a large file:

```
Bad: Regular Git commit of model.pt (500MB)
┌────────────────────────────────────┐
│  .git/ directory                   │
│  ├── model_v1.pt (500MB)          │
│  ├── model_v2.pt (500MB)          │
│  ├── model_v3.pt (500MB)          │
│  └── model_v4.pt (500MB)          │
│  Total: 2GB for 4 versions!        │
└────────────────────────────────────┘

Result:
✗ Slow clones (download all versions)
✗ Slow pushes/pulls
✗ Repository bloat
✗ Network bandwidth waste
```

### Git LFS Solution

Git LFS (Large File Storage) stores large files outside the Git repository:

```
Good: Git LFS for model.pt
┌────────────────────────────────────┐
│  .git/ directory                   │
│  ├── model.pt → pointer (123 bytes)│
└────────────────────────────────────┘
        ↓
┌────────────────────────────────────┐
│  LFS Storage (separate)            │
│  └── model_v4.pt (500MB)          │
│      Only current version!         │
└────────────────────────────────────┘

Result:
✓ Fast clones (download only needed versions)
✓ Small repository size
✓ Efficient bandwidth usage
```

### Installing Git LFS

```bash
# Ubuntu/Debian
sudo apt-get install git-lfs

# macOS
brew install git-lfs

# RHEL/CentOS
sudo yum install git-lfs

# Initialize Git LFS (once per user)
git lfs install
```

### Using Git LFS

**1. Track file types with LFS:**

```bash
# Track all PyTorch models
git lfs track "*.pt"
git lfs track "*.pth"

# Track TensorFlow models
git lfs track "*.pb"
git lfs track "*.h5"

# Track ONNX models
git lfs track "*.onnx"

# Track model checkpoints
git lfs track "checkpoints/**"

# Track datasets
git lfs track "*.parquet"
git lfs track "*.csv.gz"

# Track Docker images (not recommended, use registry instead)
# git lfs track "*.tar"

# Verify tracking
cat .gitattributes
```

**2. The `.gitattributes` file:**

After running `git lfs track`, Git creates/updates `.gitattributes`:

```
*.pt filter=lfs diff=lfs merge=lfs -text
*.pth filter=lfs diff=lfs merge=lfs -text
*.onnx filter=lfs diff=lfs merge=lfs -text
checkpoints/** filter=lfs diff=lfs merge=lfs -text
```

**Always commit `.gitattributes`:**

```bash
git add .gitattributes
git commit -m "Configure Git LFS for ML artifacts"
```

**3. Add and commit LFS files:**

```bash
# Add model file
git add models/bert-base.pt

# Verify it's tracked by LFS
git lfs ls-files

# Commit
git commit -m "Add BERT base model"

# Push (uploads to LFS storage)
git push origin main
```

### Advanced LFS Operations

**View LFS files:**

```bash
# List all LFS files
git lfs ls-files

# Show LFS file info
git lfs ls-files -l

# Check LFS status
git lfs status
```

**Fetch LFS files:**

```bash
# Fetch all LFS files for current commit
git lfs fetch

# Fetch LFS files for all branches
git lfs fetch --all

# Fetch specific file
git lfs fetch origin main models/bert.pt
```

**Pull without LFS files (save bandwidth):**

```bash
# Clone without downloading LFS files
GIT_LFS_SKIP_SMUDGE=1 git clone <repo>

# Later, download specific LFS files
git lfs pull --include="models/bert-base.pt"
```

**Prune old LFS files:**

```bash
# Remove old LFS files not needed
git lfs prune

# Dry run to see what would be removed
git lfs prune --dry-run

# Verify LFS objects
git lfs fsck
```

### LFS Best Practices

1. **Don't track everything** - Be selective
   ```bash
   # ✓ Good: Track only final models
   git lfs track "models/production/*.onnx"

   # ✗ Bad: Track all intermediate checkpoints
   # git lfs track "experiments/**/*.pt"  # Could be 100GB+
   ```

2. **Use .gitignore for large experimental data**
   ```bash
   # .gitignore
   experiments/*/checkpoints/  # Don't version intermediate checkpoints
   data/raw/                   # Don't version raw data (store in S3/GCS)
   *.log                       # Don't version logs
   wandb/                      # Don't version W&B artifacts
   ```

3. **Set up LFS server** for team use
   - Use GitHub, GitLab, or Bitbucket (includes LFS storage)
   - Or self-host LFS server for sensitive models

4. **Monitor LFS quota**
   ```bash
   # Check LFS storage usage (GitHub)
   # Settings → Billing → Git LFS data
   ```

---

## 2. Managing ML Artifacts

### What to Version Control

```
ML Project Structure - What Goes in Git?

✓ Version Control:
├── src/                       # Python code
│   ├── training/
│   ├── inference/
│   └── preprocessing/
├── configs/                   # Training configs (YAML, JSON)
│   ├── bert-base.yaml
│   └── production.yaml
├── models/
│   └── production/            # Final models only (with LFS)
│       └── model_v1.0.0.onnx
├── tests/                     # Unit/integration tests
├── docker/                    # Dockerfiles
├── kubernetes/                # K8s manifests
├── .github/workflows/         # CI/CD pipelines
├── requirements.txt           # Dependencies
├── README.md                  # Documentation
└── .gitattributes            # LFS configuration

✗ Do NOT Version Control:
├── data/raw/                  # Raw datasets (use S3/GCS)
├── data/processed/            # Processed data (regenerate from raw)
├── experiments/               # Experiment outputs (use MLflow/W&B)
│   ├── checkpoints/           # Training checkpoints
│   ├── logs/                  # Training logs
│   └── tensorboard/           # TensorBoard logs
├── .venv/                     # Virtual environments
├── __pycache__/               # Python cache
└── *.pyc                      # Compiled Python
```

### Comprehensive `.gitignore` for ML Projects

```bash
# .gitignore for ML projects

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
ENV/
env/
pip-log.txt
pip-delete-this-directory.txt

# Jupyter Notebooks
.ipynb_checkpoints/
*.ipynb

# ML Frameworks
# PyTorch
*.pt
*.pth
*.ckpt
# (unless in models/production/ with LFS)

# TensorFlow
*.pb
*.h5
saved_model/
# (unless in models/production/ with LFS)

# Data
data/raw/
data/processed/
data/interim/
datasets/
*.csv
*.parquet
*.tfrecord
# Exception: small sample data for tests

# Experiment Tracking
experiments/
runs/
outputs/
mlruns/
wandb/
tensorboard/
lightning_logs/

# Model Artifacts
checkpoints/
snapshots/
*.safetensors
# Exception: models/production/ with LFS

# Logs
*.log
logs/
*.out

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Docker
*.tar
*.tar.gz
# (Docker images go in registry, not Git)

# Secrets
.env
.env.local
*.key
*.pem
credentials.json
secrets/
```

### Tracking Experiments

**Don't use Git for experiment tracking.** Use specialized tools:

```python
# ✗ Bad: Committing every experiment
# Leads to 1000s of commits, repository bloat

# ✓ Good: Use MLflow
import mlflow

mlflow.start_run()
mlflow.log_param("learning_rate", 0.001)
mlflow.log_param("batch_size", 32)
mlflow.log_metric("accuracy", 0.95)
mlflow.log_artifact("model.pt")
mlflow.end_run()

# Or Weights & Biases
import wandb

wandb.init(project="my-ml-project")
wandb.config.update({"learning_rate": 0.001})
wandb.log({"accuracy": 0.95})
wandb.save("model.pt")
```

**Git is for code versions, MLflow/W&B for experiment versions.**

---

## 3. Monorepo Strategies

### Monorepo vs Multi-Repo

**Multi-Repo (Poly-Repo)**
```
ml-training/          # Separate repos
ml-inference/
ml-data-pipeline/
ml-infrastructure/
```

**Pros**: Clear ownership, independent versioning
**Cons**: Dependency hell, code duplication, difficult refactoring

**Monorepo**
```
ml-platform/
├── training/
├── inference/
├── data-pipeline/
└── infrastructure/
```

**Pros**: Easy code sharing, atomic changes, simplified dependencies
**Cons**: Larger repo, requires discipline

### When to Use Monorepo for ML

✓ **Use Monorepo when:**
- Multiple services share code (e.g., feature engineering, utilities)
- You need atomic changes across services
- Team is small to medium (<50 engineers)
- Strong CI/CD to handle complexity

✗ **Avoid Monorepo when:**
- Teams are very large and independent
- Services are in different languages with no shared code
- Strict access control needed per service

### Organizing an ML Monorepo

```
ml-platform/
├── libs/                      # Shared libraries
│   ├── feature-engineering/
│   ├── model-utils/
│   └── monitoring/
├── services/
│   ├── training-service/
│   ├── inference-api/
│   ├── data-ingestion/
│   └── model-registry/
├── models/                    # Model definitions
│   ├── bert-classifier/
│   └── resnet-detector/
├── infrastructure/            # IaC
│   ├── terraform/
│   └── kubernetes/
├── tools/                     # Developer tools
│   └── scripts/
├── docs/                      # Documentation
└── .github/
    └── workflows/             # CI/CD
```

### Monorepo Tools

**Bazel** - Google's build system

```python
# BUILD file
py_library(
    name = "feature_engineering",
    srcs = ["feature_eng.py"],
    deps = ["//libs/utils:data_utils"],
)

py_binary(
    name = "train",
    srcs = ["train.py"],
    deps = [
        ":feature_engineering",
        "//libs/model-utils:training",
    ],
)
```

**Benefits**:
- Only builds/tests changed code
- Caches build artifacts
- Enforces dependency graph

**Nx (for Node.js/Python)**
**Pants (for Python)**
**Turborepo (for JavaScript)**

---

## 4. Git Workflows for ML Teams

### Feature Branch Workflow (Recommended)

```
main (production)
  │
  ├── feature/new-model-architecture
  │
  ├── feature/data-pipeline-optimization
  │
  └── feature/inference-performance
```

**Process:**

```bash
# 1. Create feature branch
git checkout -b feature/transformer-model

# 2. Develop
# ... make changes ...

# 3. Commit regularly
git add src/models/transformer.py
git commit -m "Add transformer model architecture"

# 4. Push to remote
git push origin feature/transformer-model

# 5. Create Pull Request
# ... code review ...

# 6. Merge to main
git checkout main
git merge feature/transformer-model
git push origin main

# 7. Delete feature branch
git branch -d feature/transformer-model
git push origin --delete feature/transformer-model
```

### Git Flow for ML Projects

```
main (production models)
  │
  ├── develop (integration branch)
  │   │
  │   ├── feature/bert-fine-tuning
  │   ├── feature/data-augmentation
  │   └── feature/model-compression
  │
  ├── release/v1.2.0 (preparing release)
  │
  └── hotfix/inference-bug (emergency fix)
```

**When to use Git Flow:**
- Multiple versions in production simultaneously
- Strict release cycles
- Need for hotfixes without affecting development

### Trunk-Based Development

```
main (always deployable)
  │
  ├── short-lived feature branches (<1 day)
  └── direct commits (for small changes)
```

**Best for:**
- Fast-paced ML experimentation
- Strong CI/CD pipeline
- Feature flags for incomplete features

---

## 5. Performance Optimization

### Large Repository Problems

ML repositories can grow large:
- Many commits (daily experiments)
- Large files (even with LFS, history grows)
- Deep history (years of development)

**Symptoms:**
- Slow `git clone`
- Slow `git status` / `git log`
- Large `.git` folder

### Shallow Clones

**Clone only recent history:**

```bash
# Clone only last 10 commits
git clone --depth 10 <repo-url>

# Clone only last commit
git clone --depth 1 <repo-url>

# Later, fetch more history if needed
git fetch --deepen=100
```

**Use case:** CI/CD pipelines that don't need full history

### Sparse Checkout

**Clone only specific directories:**

```bash
# Clone repository
git clone --filter=blob:none --sparse <repo-url>
cd repo

# Checkout only specific paths
git sparse-checkout init --cone
git sparse-checkout set services/inference-api

# Add more paths later
git sparse-checkout add infrastructure/kubernetes
```

**Use case:** Large monorepos where you only work on one service

### Partial Clones

**Clone without downloading all blobs:**

```bash
# Clone without file contents
git clone --filter=blob:none <repo-url>

# Git downloads files as needed

# Or exclude large files
git clone --filter=blob:limit=1m <repo-url>  # Skip files >1MB
```

### Git Maintenance

```bash
# Optimize repository
git gc --aggressive --prune=now

# Verify repository integrity
git fsck

# Show repository size
du -sh .git

# Repack objects efficiently
git repack -ad

# Prune unreachable objects
git prune
```

---

## 6. ML-Specific Best Practices

### 1. Semantic Versioning for Models

```
model_v{MAJOR}.{MINOR}.{PATCH}.onnx

Example:
model_v1.0.0.onnx  # Initial production model
model_v1.1.0.onnx  # Improved accuracy (backward compatible)
model_v2.0.0.onnx  # New architecture (breaking change)
```

**Git tags for model versions:**

```bash
# Tag production model
git tag -a model-v1.0.0 -m "BERT classifier - 95% accuracy"
git push origin model-v1.0.0

# List model versions
git tag -l "model-v*"

# Checkout specific model version
git checkout model-v1.0.0
```

### 2. Commit Message Convention

**Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature or model
- `fix`: Bug fix
- `perf`: Performance improvement
- `data`: Data pipeline change
- `model`: Model architecture change
- `exp`: Experiment (not for main branch)
- `docs`: Documentation
- `test`: Tests
- `ci`: CI/CD changes

**Examples:**

```bash
feat(training): add data augmentation pipeline

- Implement random crop and rotation
- Add color jittering
- Improves validation accuracy by 2%

Closes #123

---

fix(inference): correct batch size handling

TensorRT inference was failing for batch_size=1
due to dimension mismatch.

Fixes #456

---

perf(model): quantize model to int8

- Reduces model size from 500MB to 125MB
- Improves inference latency from 100ms to 25ms
- Accuracy drop: 95.2% → 94.8% (acceptable)
```

### 3. Branch Naming Conventions

```
<type>/<description>

Examples:
feature/add-transformer-model
fix/data-loading-bug
experiment/bert-vs-roberta
hotfix/inference-memory-leak
release/v2.0.0
```

### 4. Model Lineage Tracking

**Use Git to track model provenance:**

```yaml
# models/production/model_v1.0.0.yaml
model:
  name: bert-classifier
  version: 1.0.0
  architecture: BERT-base

training:
  commit: abc123def456  # Git commit that trained this model
  date: 2024-01-15
  dataset: training-data-v2.1
  config: configs/bert-base.yaml

performance:
  accuracy: 0.952
  f1_score: 0.948
  latency_p99: 45ms
```

**Commit this metadata with the model:**

```bash
git add models/production/model_v1.0.0.onnx
git add models/production/model_v1.0.0.yaml
git commit -m "model: release BERT classifier v1.0.0"
git tag -a model-v1.0.0 -m "BERT classifier production release"
```

### 5. Data Versioning (DVC)

**Git doesn't handle large datasets well.** Use **DVC (Data Version Control)**:

```bash
# Install DVC
pip install dvc

# Initialize DVC
dvc init

# Track dataset
dvc add data/train.csv

# This creates data/train.csv.dvc (small text file)
git add data/train.csv.dvc .gitignore
git commit -m "data: add training dataset v1"

# Push data to remote storage (S3, GCS, etc.)
dvc remote add -d storage s3://my-bucket/dvc-storage
dvc push

# Pull data on another machine
dvc pull
```

**DVC integrates with Git but stores data separately.**

### 6. Reproducible Environments

**Pin all dependencies:**

```txt
# requirements.txt
torch==2.0.1
transformers==4.30.0
numpy==1.24.3
scikit-learn==1.3.0

# Generated with: pip freeze > requirements.txt
```

**Or use Poetry/Pipenv for better dependency management:**

```toml
# pyproject.toml (Poetry)
[tool.poetry.dependencies]
python = "^3.9"
torch = "2.0.1"
transformers = "4.30.0"
```

**Commit lock files:**

```bash
git add requirements.txt poetry.lock Pipfile.lock
git commit -m "deps: pin dependencies for reproducibility"
```

---

## 7. Summary and Key Takeaways

### Core Concepts

1. **Git LFS** manages large ML artifacts
   - Track models, checkpoints with `git lfs track`
   - Keeps repository size small
   - Essential for binary files >50MB

2. **Selective versioning** reduces repository bloat
   - Version code, configs, final models
   - Don't version raw data, experiments, logs
   - Use `.gitignore` liberally

3. **Monorepos** can work for ML platforms
   - Share code easily across services
   - Requires discipline and good tooling
   - Consider for teams <50 engineers

4. **ML-specific workflows** improve collaboration
   - Use feature branches for experiments
   - Tag production models with versions
   - Commit model metadata for lineage

5. **Performance optimization** keeps Git fast
   - Shallow clones for CI/CD
   - Sparse checkout for large monorepos
   - Regular maintenance with `git gc`

6. **Reproducibility** is paramount
   - Pin dependencies
   - Version configs and code together
   - Tag production releases
   - Use DVC for datasets

### Practical Skills Gained

✅ Configure and use Git LFS for ML artifacts
✅ Structure ML projects for team collaboration
✅ Choose appropriate Git workflow for ML teams
✅ Optimize Git performance for large repositories
✅ Apply versioning best practices to models and data
✅ Ensure reproducibility across team and time

### Common Pitfalls to Avoid

❌ Committing large files without LFS (bloats repo)
❌ Versioning raw data in Git (use S3/GCS + DVC)
❌ Versioning virtual environments (use requirements.txt)
❌ Not pinning dependencies (breaks reproducibility)
❌ Creating long-lived feature branches (causes merge conflicts)
❌ Not tagging production model versions

### Next Steps

- **Practice**: Set up Git LFS for a model training project
- **Experiment**: Compare monorepo vs multi-repo for your team
- **Implement**: Apply commit conventions to your projects
- **Explore**: Try DVC for dataset versioning

### Additional Resources

- [Git LFS Documentation](https://git-lfs.github.com/)
- [DVC - Data Version Control](https://dvc.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [MLflow Model Registry](https://www.mlflow.org/docs/latest/model-registry.html)
- [Monorepo Tools Comparison](https://monorepo.tools/)
- [Git Performance Best Practices](https://github.blog/2021-11-10-git-performance/)

---

**Congratulations!** You now understand how to use Git effectively for large-scale ML projects, from managing large files with LFS to organizing complex ML repositories and workflows.

**Next Module**: Module 004 - ML Basics
