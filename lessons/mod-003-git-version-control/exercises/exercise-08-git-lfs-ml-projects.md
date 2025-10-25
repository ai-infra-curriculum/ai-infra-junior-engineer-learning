# Exercise 08: Git LFS and Managing Large ML Projects

## Overview

This hands-on exercise focuses on using Git LFS (Large File Storage) for managing ML artifacts, implementing proper .gitignore patterns for ML projects, versioning models alongside code, and integrating with DVC (Data Version Control) for complete ML reproducibility.

## Learning Objectives

By completing this exercise, you will:
- Install and configure Git LFS for ML artifacts
- Track models, datasets, and checkpoints with LFS
- Create comprehensive .gitignore for ML projects
- Version models with semantic versioning
- Integrate Git with DVC for data versioning
- Implement model lineage tracking
- Clone and work with LFS repositories efficiently
- Migrate existing projects to Git LFS

## Prerequisites

- Completed exercises 01-07 in this module
- Lecture 05 (Git for Large-Scale ML Projects)
- Understanding of ML workflows and artifacts
- Git fundamentals

## Time Required

- Estimated: 90-120 minutes
- Difficulty: Intermediate

---

## Part 1: Setting Up Git LFS

### Task 1.1: Install Git LFS

```bash
# Ubuntu/Debian
sudo apt-get install git-lfs

# macOS
brew install git-lfs

# RHEL/CentOS
sudo yum install git-lfs

# Initialize Git LFS (one-time setup)
git lfs install

# Verify installation
git lfs version
# Output: git-lfs/3.x.x
```

### Task 1.2: Create ML Project with LFS

```bash
# Create new project
mkdir ml-model-repository
cd ml-model-repository
git init
git config init.defaultBranch main

# Configure LFS tracking
git lfs track "*.pt"           # PyTorch models
git lfs track "*.pth"          # PyTorch checkpoints
git lfs track "*.onnx"         # ONNX models
git lfs track "*.h5"           # Keras models
git lfs track "*.pb"           # TensorFlow models
git lfs track "*.safetensors"  # SafeTensors format
git lfs track "models/**"      # Everything in models/
git lfs track "*.parquet"      # Dataset files
git lfs track "*.pkl"          # Pickle files

# IMPORTANT: Always commit .gitattributes!
git add .gitattributes
git commit -m "Configure Git LFS for ML artifacts"

# View LFS tracking
cat .gitattributes
```

---

## Part 2: Versioning ML Models

### Task 2.1: Add Models to Repository

```bash
# Create project structure
mkdir -p models/production models/experiments
mkdir -p configs data/sample src tests

# Create sample model file (simulate trained model)
dd if=/dev/urandom of=models/production/bert-classifier-v1.0.0.onnx bs=1M count=100
# Creates a 100MB dummy model file

# Create model metadata
cat > models/production/bert-classifier-v1.0.0.yaml << 'EOF'
model:
  name: bert-classifier
  version: 1.0.0
  format: onnx
  architecture: BERT-base

training:
  dataset: sentiment-analysis-v2
  framework: pytorch
  framework_version: 2.0.1
  git_commit: abc123def456
  trained_date: 2024-01-15
  training_time_hours: 8.5

hyperparameters:
  learning_rate: 0.00002
  batch_size: 32
  epochs: 10
  max_seq_length: 512

performance:
  accuracy: 0.945
  f1_score: 0.938
  precision: 0.942
  recall: 0.934
  inference_latency_p50_ms: 12
  inference_latency_p99_ms: 45

artifacts:
  model_path: models/production/bert-classifier-v1.0.0.onnx
  config_path: configs/bert-classifier-production.yaml
  training_logs: s3://ml-artifacts/logs/exp_12345/
EOF

# Add to Git
git add models/production/bert-classifier-v1.0.0.*

# Commit model
git commit -m "model: add BERT classifier v1.0.0

- Accuracy: 94.5%
- F1 Score: 93.8%
- Inference latency (p99): 45ms
- Trained on sentiment-analysis-v2 dataset"

# Tag the model version
git tag -a model-bert-v1.0.0 -m "BERT Classifier v1.0.0 - Production Release"

# Verify LFS is tracking the model
git lfs ls-files
```

### Task 2.2: Create Comprehensive .gitignore

```bash
cat > .gitignore << 'EOF'
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

# Jupyter Notebooks
.ipynb_checkpoints/
*.ipynb  # Optional: version notebooks in separate repo

# ML Frameworks - Training Artifacts (DON'T version these)
checkpoints/
experiments/*/checkpoints/
lightning_logs/
wandb/
mlruns/
runs/
outputs/
snapshots/

# Data - Use DVC or S3 instead
data/raw/
data/processed/
data/interim/
datasets/
*.csv
*.json
*.jsonl
*.tfrecord
# Exception: Keep small sample data for tests
!data/sample/*.csv

# Large model files during development (use LFS for production models only)
*.pt
*.pth
*.ckpt
# Exception: Production models tracked with LFS
!models/production/*.pt
!models/production/*.onnx
!models/production/*.h5

# Logs
*.log
logs/
*.out
*.err

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Docker
*.tar
*.tar.gz
# Exception: Keep Dockerfiles
!Dockerfile
!docker-compose.yml

# Secrets
.env
.env.local
*.key
*.pem
credentials.json
secrets/
config/secrets.yaml

# OS
Thumbs.db
.DS_Store

# Build
build/
dist/
*.egg-info/

# Temporary files
*.tmp
*.temp
.cache/
EOF

git add .gitignore
git commit -m "chore: add comprehensive .gitignore for ML projects"
```

---

## Part 3: Working with LFS Repositories

### Task 3.1: Clone LFS Repository

```bash
# Create remote repository (simulate GitHub)
cd ..
git clone --bare ml-model-repository ml-model-repository.git

# Clone with LFS (downloads all LFS files)
git clone ml-model-repository.git ml-model-clone
cd ml-model-clone

# Verify model was downloaded
ls -lh models/production/
# Should show 100MB model file

# Check LFS status
git lfs ls-files
```

### Task 3.2: Clone Without LFS Files (Save Bandwidth)

```bash
# Clone without downloading LFS files
cd ..
GIT_LFS_SKIP_SMUDGE=1 git clone ml-model-repository.git ml-model-clone-minimal
cd ml-model-clone-minimal

# LFS files are pointers (tiny)
ls -lh models/production/
# Shows 133 bytes (pointer file, not 100MB)

# Download specific LFS files when needed
git lfs pull --include="models/production/bert-classifier-v1.0.0.onnx"

# Now file is 100MB
ls -lh models/production/
```

---

## Part 4: Model Versioning Workflow

### Task 4.1: Release New Model Version

```bash
cd ../ml-model-repository

# Simulate training a new model
dd if=/dev/urandom of=models/production/bert-classifier-v1.1.0.onnx bs=1M count=105

# Create metadata
cat > models/production/bert-classifier-v1.1.0.yaml << 'EOF'
model:
  name: bert-classifier
  version: 1.1.0  # Minor version bump (backward compatible improvement)
  format: onnx
  architecture: BERT-base

training:
  dataset: sentiment-analysis-v2.1  # Updated dataset
  improvements:
    - Added data augmentation
    - Improved preprocessing
  git_commit: def456abc789

performance:
  accuracy: 0.958  # +1.3% improvement
  f1_score: 0.951
  inference_latency_p99_ms: 42  # -3ms improvement
EOF

# Commit new version
git add models/production/bert-classifier-v1.1.0.*
git commit -m "model: release BERT classifier v1.1.0

Improvements:
- Accuracy: 95.8% (+1.3%)
- F1 Score: 95.1%
- Latency: 42ms (-3ms)

Changes:
- Updated dataset to v2.1
- Added data augmentation
- Improved preprocessing pipeline"

# Tag new version
git tag -a model-bert-v1.1.0 -m "BERT Classifier v1.1.0 - Accuracy Improvement"

# Push to remote (including tags and LFS)
git push origin main
git push origin --tags
git lfs push origin main
```

### Task 4.2: Model Lineage Tracking

```bash
# Create lineage tracking file
cat > MODELS.md << 'EOF'
# Model Registry

## Production Models

### BERT Classifier

| Version | Release Date | Accuracy | F1 Score | Latency (p99) | Git Tag | Status |
|---------|--------------|----------|----------|---------------|---------|--------|
| 1.1.0 | 2024-01-20 | 95.8% | 95.1% | 42ms | model-bert-v1.1.0 | **Production** |
| 1.0.0 | 2024-01-15 | 94.5% | 93.8% | 45ms | model-bert-v1.0.0 | Deprecated |

### Deployment Instructions

```bash
# Checkout specific model version
git checkout model-bert-v1.1.0

# Download model
git lfs pull --include="models/production/bert-classifier-v1.1.0.onnx"

# Deploy
kubectl apply -f deployment/bert-classifier-v1.1.0.yaml
```

### Rollback Procedure

```bash
# If v1.1.0 has issues, rollback to v1.0.0
git checkout model-bert-v1.0.0
git lfs pull --include="models/production/bert-classifier-v1.0.0.onnx"
```
EOF

git add MODELS.md
git commit -m "docs: add model registry and deployment guide"
```

---

## Part 5: DVC Integration (Data Version Control)

### Task 5.1: Install and Setup DVC

```bash
# Install DVC
pip install dvc dvc-s3

# Initialize DVC in your Git repo
dvc init

# This creates:
# - .dvc/ directory
# - .dvc/.gitignore
# - .dvc/config

# Commit DVC configuration
git add .dvc .dvcignore
git commit -m "chore: initialize DVC for data versioning"
```

### Task 5.2: Track Dataset with DVC

```bash
# Create sample dataset
mkdir -p data/raw
echo "Sample training data" > data/raw/train.csv
for i in {1..1000}; do
    echo "sample_id_$i,feature1,feature2,label" >> data/raw/train.csv
done

# Track dataset with DVC
dvc add data/raw/train.csv

# This creates data/raw/train.csv.dvc (metadata file)
# And adds data/raw/train.csv to .gitignore

# Commit DVC metadata (NOT the actual data)
git add data/raw/train.csv.dvc data/raw/.gitignore
git commit -m "data: add training dataset v1 (tracked with DVC)"

# Configure remote storage (use S3, GCS, or local for this exercise)
dvc remote add -d storage /tmp/dvc-storage
dvc remote modify storage type local

# Push data to DVC remote
dvc push
```

### Task 5.3: Version Data Updates

```bash
# Update dataset
echo "New sample data" >> data/raw/train.csv

# Track new version
dvc add data/raw/train.csv

# Commit metadata
git add data/raw/train.csv.dvc
git commit -m "data: update training dataset to v2"
git tag -a data-v2 -m "Training dataset v2"

# Push data
dvc push

# Push Git
git push origin main
git push origin --tags
```

---

## Part 6: LFS Maintenance and Optimization

### Task 6.1: Check LFS Storage Usage

```bash
# View LFS file list
git lfs ls-files

# Check LFS storage stats
git lfs ls-files --size

# Show LFS bandwidth usage
git lfs env

# Find large files
git lfs ls-files --size | sort -k2 -hr | head -10
```

### Task 6.2: Prune Old LFS Files

```bash
# Remove LFS files not needed for current checkout
git lfs prune

# Dry run to see what would be removed
git lfs prune --dry-run

# Verify LFS objects
git lfs fsck

# Fetch only LFS files for specific commits
git lfs fetch --recent  # Last 10 commits
```

---

## Part 7: Migrating Existing Project to LFS

### Task 7.1: Convert Existing Repository

```bash
# If you accidentally committed large files without LFS

# 1. Install BFG Repo-Cleaner
wget https://repo1.maven.org/maven2/com/madgag/bfg/1.14.0/bfg-1.14.0.jar

# 2. Configure LFS tracking
git lfs track "*.onnx"
git lfs track "*.pt"

# 3. Migrate existing large files
git lfs migrate import --include="*.onnx,*.pt" --everything

# 4. Verify migration
git lfs ls-files

# 5. Force push (WARNING: rewrites history)
git push --force origin main
```

---

## Deliverables

Submit the following:

1. **Git Repository**:
   - Configured .gitattributes for LFS
   - Comprehensive .gitignore
   - At least 2 model versions with metadata
   - MODELS.md registry file

2. **DVC Setup**:
   - Initialized DVC
   - At least one dataset tracked with DVC
   - DVC remote configured

3. **Documentation**:
   - README explaining project structure
   - Model deployment guide
   - Data versioning workflow

4. **Evidence**:
   - `git lfs ls-files` output
   - `git log --oneline --graph` output
   - `dvc status` output

---

## Challenge Questions

1. **Storage Costs**: If your model is 500MB and you release 100 versions per year, how much LFS storage will you need? How can you reduce this?

2. **Bandwidth**: Your CI/CD pipeline clones the repo 1000 times/day. How can you minimize LFS bandwidth costs?

3. **Monorepo**: You have 50 models in one repository. How do you allow teams to clone only their model's files?

4. **Disaster Recovery**: If GitHub LFS goes down, how do you ensure models are still accessible?

5. **Compliance**: How do you track which model version is deployed in which environment for audit purposes?

---

## Additional Resources

- [Git LFS Documentation](https://git-lfs.github.com/)
- [DVC Documentation](https://dvc.org/doc)
- [Model Versioning Best Practices](https://neptune.ai/blog/version-control-for-ml-models)
- [MLflow Model Registry](https://www.mlflow.org/docs/latest/model-registry.html)
- [Semantic Versioning](https://semver.org/)

---

**Congratulations!** You can now manage large ML projects with Git LFS, version models alongside code, and integrate with DVC for complete reproducibility.
