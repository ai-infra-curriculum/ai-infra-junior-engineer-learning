# Exercise 01: Creating Your First ML Project Repository

## Overview

**Difficulty**: Beginner
**Estimated Time**: 60-90 minutes
**Prerequisites**: Lecture 01 - Git Fundamentals

In this exercise, you'll create your first Git repository for a machine learning project from scratch. You'll learn proper repository initialization, file organization, `.gitignore` configuration, and making your first commits. This exercise simulates starting a new ML inference API project.

## Learning Objectives

By completing this exercise, you will:

- Initialize a Git repository correctly
- Configure Git with appropriate settings for ML projects
- Create a proper `.gitignore` file for Python and ML projects
- Organize a repository structure for an ML project
- Make atomic, well-documented commits
- Understand the three-state Git workflow in practice
- Use `git status` and `git diff` effectively
- Write professional commit messages

## Scenario

You've been tasked with creating a new machine learning inference API that will serve predictions from a pre-trained image classification model. The project is starting from scratch, and you need to set up the repository properly from day one.

The API will:
- Accept image uploads via REST API
- Run inference using a PyTorch model
- Return classification results with confidence scores
- Log predictions for monitoring
- Support multiple model versions

## Prerequisites

Before starting, ensure you have:

```bash
# Git installed
git --version
# Should show: git version 2.x.x or higher

# Python 3.11+ installed
python3 --version

# A text editor (VS Code, vim, nano, etc.)
```

---

## Part 1: Initial Setup and Configuration

### Task 1.1: Configure Git Identity

Before creating your first repository, configure your Git identity.

**Instructions:**

```bash
# Set your name (use your real name or GitHub username)
git config --global user.name "Your Name"

# Set your email (use your email)
git config --global user.email "your.email@example.com"

# Verify configuration
git config --list --show-origin
```

**Expected Output:**
```
file:/home/user/.gitconfig    user.name=Your Name
file:/home/user/.gitconfig    user.email=your.email@example.com
```

**Checkpoint Question:**
- Why is it important to set user.name and user.email before making commits?

---

### Task 1.2: Create Project Directory and Initialize Repository

Create the project directory and initialize it as a Git repository.

**Instructions:**

```bash
# Create project directory
mkdir ml-inference-api
cd ml-inference-api

# Initialize Git repository
git init

# Verify repository was created
ls -la
```

**Expected Output:**
```
Initialized empty Git repository in /path/to/ml-inference-api/.git/
```

You should see a `.git` directory (it's hidden, hence `ls -la`).

**Checkpoint Questions:**
- What does the `.git` directory contain?
- What command shows you the current status of the repository?

Run `git status` now. What does it say?

---

### Task 1.3: Configure Repository-Specific Settings

Set up ML project-specific Git configurations.

**Instructions:**

```bash
# Set default branch name to 'main' (modern convention)
git config init.defaultBranch main

# Configure line endings (important for cross-platform teams)
# Linux/Mac:
git config core.autocrlf input
# Windows:
# git config core.autocrlf true

# Increase buffer size for large files
git config http.postBuffer 524288000

# Create useful aliases
git config alias.st status
git config alias.co checkout
git config alias.br branch
git config alias.ci commit
git config alias.unstage 'reset HEAD --'
git config alias.last 'log -1 HEAD --stat'

# Verify repository configuration
git config --local --list
```

**Checkpoint:**
Test an alias:
```bash
git st
# Should show: On branch main, No commits yet, nothing to commit
```

---

## Part 2: Creating Project Structure

### Task 2.1: Create Directory Structure

Create a professional directory structure for the ML project.

**Instructions:**

```bash
# Create directory structure
mkdir -p src/{api,models,preprocessing,utils}
mkdir -p tests/{unit,integration}
mkdir -p configs
mkdir -p scripts
mkdir -p docs

# Create initial files
touch README.md
touch requirements.txt
touch requirements-dev.txt
touch setup.py
touch .env.example
touch .gitignore
touch .gitattributes

# Create source code files
touch src/__init__.py
touch src/api/__init__.py
touch src/api/app.py
touch src/models/__init__.py
touch src/models/classifier.py
touch src/preprocessing/__init__.py
touch src/preprocessing/image.py
touch src/utils/__init__.py
touch src/utils/logging.py

# Create test files
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/unit/test_classifier.py
touch tests/integration/__init__.py

# Create configuration files
touch configs/default.yaml
touch configs/production.yaml

# Create scripts
touch scripts/download_model.sh
touch scripts/run_server.sh

# Verify structure
tree -L 2
```

**Expected Structure:**
```
ml-inference-api/
├── .env.example
├── .gitattributes
├── .gitignore
├── README.md
├── requirements-dev.txt
├── requirements.txt
├── setup.py
├── configs/
│   ├── default.yaml
│   └── production.yaml
├── docs/
├── scripts/
│   ├── download_model.sh
│   └── run_server.sh
├── src/
│   ├── __init__.py
│   ├── api/
│   ├── models/
│   ├── preprocessing/
│   └── utils/
└── tests/
    ├── __init__.py
    ├── integration/
    └── unit/
```

**Checkpoint:**
Run `git status`. What files does it show?

---

### Task 2.2: Create .gitignore File

Create a comprehensive `.gitignore` file for ML projects.

**Instructions:**

Create `.gitignore` with this content:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
env.bak/
venv.bak/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environments
.env
.venv
ENV/
env/
venv/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Jupyter Notebooks
.ipynb_checkpoints
*.ipynb_checkpoints/

# Machine Learning
*.h5
*.hdf5
*.pkl
*.pickle
*.pt
*.pth
*.onnx
*.pb
saved_models/
checkpoints/
models/
*.model
*.weights

# Data
data/
datasets/
*.csv
*.tsv
*.dat
*.json
!configs/*.json
!configs/*.yaml
*.parquet
*.feather

# Logs and Experiment Tracking
logs/
*.log
mlruns/
.mlflow/
wandb/
runs/
tensorboard/

# Credentials and Secrets
.env
.env.local
.env.*.local
secrets/
*.key
*.pem
credentials.json
service-account.json
.aws/
.gcloud/

# Testing
.coverage
.pytest_cache/
.tox/
htmlcov/
.hypothesis/

# Documentation
docs/_build/
site/

# Compiled files
*.com
*.class
*.dll
*.exe
*.o

# Archives
*.zip
*.tar
*.tar.gz
*.rar
*.7z

# Temporary files
*.tmp
*.bak
*.swp
.cache/
```

**Save the file.**

**Checkpoint:**
```bash
git status
```

Notice that `data/`, `models/`, and other ignored directories don't appear in the status.

---

### Task 2.3: Create .gitattributes File

Configure file handling for ML projects.

**Instructions:**

Create `.gitattributes` with this content:

```
# Auto detect text files and perform LF normalization
* text=auto

# Python files
*.py text eol=lf
*.pyi text eol=lf
*.pyx text eol=lf

# YAML files
*.yml text eol=lf
*.yaml text eol=lf

# Markdown
*.md text eol=lf

# Shell scripts
*.sh text eol=lf

# Binary files (don't attempt to diff)
*.pkl binary
*.pickle binary
*.h5 binary
*.hdf5 binary
*.pt binary
*.pth binary
*.onnx binary
*.pb binary
*.parquet binary
*.feather binary

# Images
*.jpg binary
*.jpeg binary
*.png binary
*.gif binary
*.ico binary
*.svg text

# Archives
*.zip binary
*.tar binary
*.gz binary
*.7z binary
*.rar binary
```

**Save the file.**

---

## Part 3: Creating Initial Content

### Task 3.1: Create README.md

Create a professional README for the project.

**Instructions:**

Edit `README.md`:

```markdown
# ML Inference API

A production-ready REST API for serving image classification predictions using PyTorch.

## Overview

This API provides endpoints for:
- Image classification with confidence scores
- Model version management
- Prediction logging and monitoring
- Health checks and metrics

## Tech Stack

- **Framework**: FastAPI
- **ML Framework**: PyTorch
- **Model**: ResNet-50 (pre-trained on ImageNet)
- **Containerization**: Docker
- **Deployment**: Kubernetes

## Project Status

🚧 **In Development**

Current version: 0.1.0

## Getting Started

### Prerequisites

- Python 3.11+
- pip
- Virtual environment tool (venv, conda, etc.)

### Installation

```bash
# Clone repository
git clone <repository-url>
cd ml-inference-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download model weights
bash scripts/download_model.sh
```

### Running Locally

```bash
# Start development server
bash scripts/run_server.sh
```

API will be available at `http://localhost:8000`

### Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src
```

## API Endpoints

- `POST /predict` - Upload image for classification
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics
- `GET /models` - List available model versions

## Configuration

Configuration files in `configs/`:
- `default.yaml` - Default settings
- `production.yaml` - Production overrides

## Project Structure

```
ml-inference-api/
├── src/           # Source code
├── tests/         # Test suite
├── configs/       # Configuration files
├── scripts/       # Utility scripts
└── docs/          # Documentation
```

## Contributing

1. Create feature branch: `git checkout -b feature/new-feature`
2. Make changes and commit: `git commit -m "Add new feature"`
3. Push to branch: `git push origin feature/new-feature`
4. Create Pull Request

## License

MIT License - see LICENSE file for details

## Authors

- Your Name <your.email@example.com>

## Acknowledgments

- PyTorch team for the pre-trained models
- FastAPI for the excellent web framework
```

**Save the file.**

---

### Task 3.2: Create requirements.txt

Create dependency file for the project.

**Instructions:**

Edit `requirements.txt`:

```
# Web Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0

# Machine Learning
torch==2.1.0
torchvision==0.16.0
numpy==1.26.0
pillow==10.1.0

# Utilities
pyyaml==6.0.1
python-dotenv==1.0.0
python-multipart==0.0.6

# Logging and Monitoring
structlog==23.2.0
prometheus-client==0.19.0

# HTTP Client
httpx==0.25.1
```

Edit `requirements-dev.txt`:

```
-r requirements.txt

# Testing
pytest==7.4.3
pytest-cov==4.1.0
pytest-asyncio==0.21.1

# Linting and Formatting
black==23.11.0
flake8==6.1.0
mypy==1.7.0
isort==5.12.0

# Pre-commit hooks
pre-commit==3.5.0
```

**Save both files.**

---

### Task 3.3: Create Configuration Files

Create initial configuration files.

**Instructions:**

Edit `configs/default.yaml`:

```yaml
# Default Configuration for ML Inference API

server:
  host: "0.0.0.0"
  port: 8000
  workers: 4
  reload: false

model:
  name: "resnet50"
  version: "1.0.0"
  weights_path: "models/resnet50_weights.pth"
  device: "cpu"  # Options: cpu, cuda
  batch_size: 32

preprocessing:
  image_size: [224, 224]
  normalize_mean: [0.485, 0.456, 0.406]
  normalize_std: [0.229, 0.224, 0.225]

api:
  max_upload_size: 10485760  # 10 MB
  allowed_extensions:
    - jpg
    - jpeg
    - png
  rate_limit: 100  # requests per minute

logging:
  level: "INFO"
  format: "json"
  output: "stdout"

monitoring:
  enable_metrics: true
  metrics_port: 9090
```

Edit `configs/production.yaml`:

```yaml
# Production Configuration Overrides

server:
  reload: false
  workers: 8

model:
  device: "cuda"
  batch_size: 64

logging:
  level: "WARNING"
  output: "file"
  file_path: "/var/log/ml-api/app.log"

monitoring:
  enable_metrics: true
```

**Save both files.**

---

### Task 3.4: Create .env.example

Create template for environment variables.

**Instructions:**

Edit `.env.example`:

```bash
# Environment Variables Template
# Copy this file to .env and fill in actual values
# NEVER commit .env to Git!

# Application
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=your-secret-key-here

# Model Storage
MODEL_STORAGE_PATH=./models
MODEL_CACHE_SIZE=1000

# AWS Credentials (if using S3 for model storage)
# AWS_ACCESS_KEY_ID=your-access-key
# AWS_SECRET_ACCESS_KEY=your-secret-key
# AWS_REGION=us-west-2
# S3_BUCKET=ml-models

# Database (if needed)
# DATABASE_URL=postgresql://user:password@localhost:5432/mlapi

# Redis (if using for caching)
# REDIS_URL=redis://localhost:6379/0

# Monitoring
# SENTRY_DSN=your-sentry-dsn
```

**Save the file.**

**Important:** Never create an actual `.env` file in this exercise. The `.gitignore` will prevent it from being tracked.

---

## Part 4: Making Your First Commits

### Task 4.1: Stage and Review Changes

Now that we have content, let's prepare our first commit.

**Instructions:**

```bash
# Check status
git status

# You should see many "Untracked files"

# Add all files to staging area
git add .

# Check status again
git status

# Review what's been staged
git diff --staged
```

**Expected Output:**
```
On branch main

No commits yet

Changes to be committed:
  (use "git rm --cached <file>..." to unstage)
        new file:   .env.example
        new file:   .gitattributes
        new file:   .gitignore
        new file:   README.md
        ... (many more files)
```

**Checkpoint Questions:**
- What's the difference between `git diff` and `git diff --staged`?
- Why don't we see `data/` or `models/` directories in the staging area?

---

### Task 4.2: Make First Commit

Create your first commit with a proper message.

**Instructions:**

```bash
# Commit with a descriptive message
git commit -m "Initial project structure

Set up ML inference API project with:
- Directory structure for source code, tests, and configs
- Python package structure with __init__.py files
- Comprehensive .gitignore for ML projects
- .gitattributes for proper file handling
- README with project overview
- Requirements files for dependencies
- Configuration templates (default and production)
- Environment variable template

This establishes the foundation for the image classification API."

# View commit
git log

# View commit with details
git show

# View commit statistics
git show --stat
```

**Expected Output:**
```
[main (root-commit) abc123] Initial project structure
 25 files changed, 350 insertions(+)
 create mode 100644 .env.example
 create mode 100644 .gitattributes
 ... (list of files)
```

**Checkpoint:**
Your repository now has one commit! Run `git log --oneline` to see it.

---

### Task 4.3: Add Source Code Files

Now let's add some actual code to the project.

**Instructions:**

Edit `src/api/app.py`:

```python
"""
ML Inference API - Main Application

FastAPI application for serving ML model predictions.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import structlog
from typing import Dict, List

from src.models.classifier import ImageClassifier
from src.preprocessing.image import preprocess_image

# Configure logging
logger = structlog.get_logger()

# Initialize FastAPI app
app = FastAPI(
    title="ML Inference API",
    description="REST API for image classification",
    version="0.1.0"
)

# Initialize classifier (will be loaded on startup)
classifier = None


@app.on_event("startup")
async def startup_event():
    """Load model on application startup."""
    global classifier
    logger.info("Loading model...")
    classifier = ImageClassifier()
    await classifier.load_model()
    logger.info("Model loaded successfully")


@app.get("/")
async def root():
    """Root endpoint - API information."""
    return {
        "name": "ML Inference API",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    if classifier is None or not classifier.is_loaded():
        raise HTTPException(status_code=503, detail="Model not loaded")

    return {
        "status": "healthy",
        "model_loaded": True
    }


@app.post("/predict")
async def predict(file: UploadFile = File(...)) -> JSONResponse:
    """
    Predict image classification.

    Args:
        file: Uploaded image file

    Returns:
        JSON response with predictions
    """
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="File must be an image"
        )

    try:
        # Read and preprocess image
        image_bytes = await file.read()
        processed_image = await preprocess_image(image_bytes)

        # Get predictions
        predictions = await classifier.predict(processed_image)

        logger.info(
            "Prediction made",
            filename=file.filename,
            top_class=predictions[0]["class"]
        )

        return JSONResponse(content={
            "success": True,
            "predictions": predictions
        })

    except Exception as e:
        logger.error("Prediction failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )


@app.get("/models")
async def list_models() -> Dict[str, str]:
    """List available models."""
    if classifier is None:
        return {"models": []}

    return {
        "current_model": classifier.model_name,
        "version": classifier.version
    }
```

**Save the file.**

Edit `src/models/classifier.py`:

```python
"""
Image Classifier Module

Handles loading and inference for image classification models.
"""

import torch
import torchvision.models as models
from typing import List, Dict
import structlog

logger = structlog.get_logger()


class ImageClassifier:
    """Image classification model wrapper."""

    def __init__(self, model_name: str = "resnet50", device: str = "cpu"):
        """
        Initialize classifier.

        Args:
            model_name: Name of the model architecture
            device: Device to run inference on (cpu or cuda)
        """
        self.model_name = model_name
        self.device = device
        self.model = None
        self.version = "1.0.0"

    async def load_model(self):
        """Load pre-trained model."""
        logger.info(f"Loading {self.model_name} model...")

        # Load pre-trained ResNet50
        self.model = models.resnet50(pretrained=True)
        self.model.eval()
        self.model.to(self.device)

        logger.info(f"Model loaded on {self.device}")

    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self.model is not None

    async def predict(self, image_tensor: torch.Tensor) -> List[Dict]:
        """
        Make prediction on preprocessed image.

        Args:
            image_tensor: Preprocessed image tensor

        Returns:
            List of predictions with class and confidence
        """
        if self.model is None:
            raise RuntimeError("Model not loaded")

        # Move to device
        image_tensor = image_tensor.to(self.device)

        # Inference
        with torch.no_grad():
            outputs = self.model(image_tensor)
            probabilities = torch.nn.functional.softmax(outputs[0], dim=0)

        # Get top 5 predictions
        top5_prob, top5_catid = torch.topk(probabilities, 5)

        predictions = []
        for i in range(5):
            predictions.append({
                "class_id": int(top5_catid[i]),
                "class": f"class_{top5_catid[i]}",  # Placeholder
                "confidence": float(top5_prob[i])
            })

        return predictions
```

**Save the file.**

---

### Task 4.4: Commit Code Changes

Make a separate commit for the code.

**Instructions:**

```bash
# Check what changed
git status

# Stage the files
git add src/api/app.py src/models/classifier.py

# Review changes before committing
git diff --staged

# Commit
git commit -m "Add FastAPI app and image classifier

Implemented:
- FastAPI application with predict endpoint
- ImageClassifier class for model inference
- Health check and model info endpoints
- Structured logging throughout
- Error handling for invalid inputs

The API can now accept image uploads and return
classification predictions using ResNet-50."

# View log
git log --oneline
```

**Expected Output:**
```
abc123 Add FastAPI app and image classifier
def456 Initial project structure
```

---

### Task 4.5: Add More Files and Practice Selective Staging

Add preprocessing code, but stage files selectively.

**Instructions:**

Edit `src/preprocessing/image.py`:

```python
"""
Image Preprocessing Module

Handles image loading and preprocessing for model inference.
"""

import torch
from torchvision import transforms
from PIL import Image
import io
from typing import Union


# Standard ImageNet normalization
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


def get_preprocessing_transform():
    """
    Get image preprocessing transform.

    Returns:
        Composed transform for preprocessing
    """
    return transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
    ])


async def preprocess_image(image_bytes: bytes) -> torch.Tensor:
    """
    Preprocess image bytes for model input.

    Args:
        image_bytes: Raw image bytes

    Returns:
        Preprocessed image tensor
    """
    # Load image
    image = Image.open(io.BytesIO(image_bytes))

    # Convert to RGB if needed
    if image.mode != "RGB":
        image = image.convert("RGB")

    # Apply preprocessing
    transform = get_preprocessing_transform()
    image_tensor = transform(image)

    # Add batch dimension
    image_tensor = image_tensor.unsqueeze(0)

    return image_tensor


def validate_image(image_bytes: bytes) -> bool:
    """
    Validate that bytes represent a valid image.

    Args:
        image_bytes: Raw bytes

    Returns:
        True if valid image, False otherwise
    """
    try:
        Image.open(io.BytesIO(image_bytes))
        return True
    except Exception:
        return False
```

Edit `src/utils/logging.py`:

```python
"""
Logging Configuration

Structured logging setup for the application.
"""

import structlog
import logging
import sys


def configure_logging(level: str = "INFO", format_type: str = "json"):
    """
    Configure structured logging.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        format_type: Output format (json or console)
    """
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper())
    )

    # Configure structlog
    if format_type == "json":
        processors = [
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ]
    else:
        processors = [
            structlog.dev.ConsoleRenderer()
        ]

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
```

**Now practice selective staging:**

```bash
# Check status
git status

# Stage only the preprocessing file
git add src/preprocessing/image.py

# Check status - logging.py should still be unstaged
git status

# Commit preprocessing
git commit -m "Add image preprocessing module

Implemented preprocessing pipeline:
- Image loading from bytes
- Resize and center crop to 224x224
- ImageNet normalization
- Tensor conversion
- Image validation

Preprocessing follows standard ImageNet transform pipeline
for compatibility with pre-trained models."

# Now stage and commit logging
git add src/utils/logging.py

git commit -m "Add structured logging configuration

Implemented logging setup with:
- Structured logging using structlog
- JSON and console output formats
- Configurable log levels
- Timestamp inclusion

This provides consistent, parseable logs for production
monitoring and debugging."

# View log
git log --oneline
```

**Expected Output:**
```
ghi789 Add structured logging configuration
abc123 Add image preprocessing module
def456 Add FastAPI app and image classifier
jkl012 Initial project structure
```

---

## Part 5: Working with Git History

### Task 5.1: Explore Your Commits

Learn to navigate your commit history.

**Instructions:**

```bash
# View commit history (full)
git log

# View commit history (one line per commit)
git log --oneline

# View last commit with details
git show

# View specific commit
git show def456  # Use actual hash from your log

# View only commit message
git log --oneline -1

# View commits with statistics
git log --stat

# View commits with actual changes
git log -p

# View last 2 commits
git log -2
```

**Checkpoint Question:**
What information does each commit contain?

---

### Task 5.2: Check Repository Status

Practice using `git status` at different stages.

**Instructions:**

```bash
# Current status (should be clean)
git status

# Create a new file
echo "# TODO: Add deployment documentation" > docs/deployment.md

# Check status - untracked file
git status

# Add the file
git add docs/deployment.md

# Check status - staged file
git status

# Modify the file
echo "## Prerequisites" >> docs/deployment.md

# Check status - modified staged file
git status

# See the difference
git diff
git diff --staged
```

**Checkpoint Questions:**
- What's the difference between what `git diff` and `git diff --staged` show?
- How do you unstage a file?

---

### Task 5.3: Practice Unstaging

Learn to unstage files if you change your mind.

**Instructions:**

```bash
# File is currently staged
git status

# Unstage it
git restore --staged docs/deployment.md

# Check status
git status

# File should be in working directory, not staged
```

---

### Task 5.4: Discard Changes

Practice discarding unwanted changes.

**Instructions:**

```bash
# File has unstaged changes
git status

# Discard changes (BE CAREFUL - this is permanent!)
git restore docs/deployment.md

# Check status
git status

# File should be gone (was untracked after unstaging)
```

**Warning:** `git restore` discards changes permanently. There's no undo!

---

## Part 6: Viewing Differences

### Task 6.1: Make Changes and Compare

Practice using `git diff` effectively.

**Instructions:**

Create a test script:

```bash
# Create new file
cat > scripts/test_api.sh << 'EOF'
#!/bin/bash
# Test script for ML Inference API

echo "Starting API tests..."

# Test health endpoint
curl http://localhost:8000/health

# Test root endpoint
curl http://localhost:8000/

echo "Tests complete"
EOF

# Make it executable
chmod +x scripts/test_api.sh

# Add and commit
git add scripts/test_api.sh
git commit -m "Add API testing script"
```

Now modify it:

```bash
# Modify the file
cat >> scripts/test_api.sh << 'EOF'

# Test models endpoint
curl http://localhost:8000/models
EOF

# View changes
git diff

# View with color highlighting
git diff --color-words

# Stage the changes
git add scripts/test_api.sh

# View staged changes
git diff --staged

# Commit
git commit -m "Add models endpoint test to testing script"
```

---

## Validation and Testing

### Task 7.1: Verify Repository State

Run these commands to verify your repository is correct:

**Instructions:**

```bash
# Should show clean working tree
git status

# Should show ~6 commits
git log --oneline

# Verify .gitignore is working
mkdir data
echo "test" > data/test.csv
git status
# data/test.csv should NOT appear

# Verify directory structure
tree -L 2

# Verify files exist
ls -la src/api/
ls -la src/models/
ls -la configs/
```

**Expected Results:**
- Clean working directory
- Multiple commits in history
- Proper directory structure
- `.gitignore` preventing unwanted files from being tracked

---

## Challenge Tasks (Optional)

Ready for more? Try these additional challenges:

### Challenge 1: Add Tests

Create test files and commit them:

```bash
# Create test file
cat > tests/unit/test_classifier.py << 'EOF'
import pytest
from src.models.classifier import ImageClassifier

def test_classifier_initialization():
    """Test classifier can be initialized."""
    classifier = ImageClassifier()
    assert classifier.model_name == "resnet50"
    assert classifier.device == "cpu"
    assert not classifier.is_loaded()

def test_classifier_device():
    """Test classifier device setting."""
    classifier = ImageClassifier(device="cuda")
    assert classifier.device == "cuda"
EOF

git add tests/unit/test_classifier.py
git commit -m "Add unit tests for classifier initialization"
```

### Challenge 2: Fix a "Bug"

Simulate finding and fixing a bug:

```bash
# Create a "bug" by modifying a file
echo "# FIXME: Handle CUDA out of memory errors" >> src/models/classifier.py

# Stage and commit
git add src/models/classifier.py
git commit -m "Add FIXME note for CUDA OOM handling"

# Now "fix" it
# Edit the file to add proper error handling
# Then commit the fix
git add src/models/classifier.py
git commit -m "Fix: Add CUDA OOM error handling

Handle torch.cuda.OutOfMemoryError by automatically
falling back to CPU inference when GPU memory is exhausted.

Fixes #1"
```

### Challenge 3: Write Better Commit Messages

Practice writing detailed commit messages:

```bash
# Make a change
echo "strict = true" >> setup.cfg

git add setup.cfg
git commit
# Editor opens - write a detailed message following the format from lecture
```

---

## Reflection Questions

Answer these questions to solidify your understanding:

1. **Why is `.gitignore` important for ML projects?**
   - What happens if you accidentally commit a 5GB model file?

2. **What's the difference between tracked and untracked files?**
   - How does Git treat them differently?

3. **Why make multiple small commits instead of one large commit?**
   - What are the benefits?

4. **What does "atomic commit" mean?**
   - Give an example from this exercise.

5. **What information should a good commit message contain?**
   - Review the commit message guidelines from Lecture 01.

6. **Why stage files before committing?**
   - Why not commit directly from the working directory?

7. **How would you undo the last commit if you made a mistake?**
   - (Hint: This is covered in Lecture 04, but think about what might work)

---

## Summary

Congratulations! You've completed Exercise 01. You learned:

- ✅ How to initialize a Git repository properly
- ✅ Configure Git for ML projects
- ✅ Create proper directory structures
- ✅ Write comprehensive `.gitignore` files
- ✅ Make atomic, well-documented commits
- ✅ Use the three-state Git workflow
- ✅ Navigate commit history
- ✅ Stage and unstage files selectively
- ✅ Use `git status` and `git diff` effectively

### Key Commands Learned

```bash
git init                    # Initialize repository
git config                  # Configure Git
git status                  # Check repository status
git add                     # Stage changes
git commit                  # Create commit
git log                     # View history
git show                    # Show commit details
git diff                    # View unstaged changes
git diff --staged           # View staged changes
git restore                 # Discard or unstage changes
```

### Next Steps

- Complete Exercise 02 to learn more about commits and history
- Review Lecture 01 if any concepts are unclear
- Practice creating repositories for other projects

**Great job!** You've taken your first steps into version control for ML projects.
