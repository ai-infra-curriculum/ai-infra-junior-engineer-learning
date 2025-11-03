# Exercise 01: Python Environment Setup and Management

## Overview

Set up a complete Python development environment for an ML training project with proper dependency management, reproducible configuration, and automation scripts.

## Learning Objectives

By completing this exercise, you will:
- Create and manage virtual environments
- Write comprehensive requirements files
- Set up project structure following best practices
- Create automation scripts for environment setup
- Document setup process for team members

## Prerequisites

- Python 3.11+ installed
- Basic command-line knowledge
- Text editor or IDE

## Project Scenario

You're joining an AI infrastructure team. Your first task is to set up a reproducible development environment for a new machine learning training pipeline project called "sentiment-classifier".

## Part 1: Project Structure Setup (15 minutes)

### Task 1.1: Create Project Directory Structure

Create the following directory structure:

```
sentiment-classifier/
├── .gitignore
├── README.md
├── requirements.txt
├── requirements-dev.txt
├── setup.sh
├── .env.example
├── src/
│   ├── __init__.py
│   ├── train.py
│   ├── evaluate.py
│   └── utils/
│       ├── __init__.py
│       ├── data_loader.py
│       └── metrics.py
├── tests/
│   ├── __init__.py
│   ├── test_data_loader.py
│   └── test_metrics.py
├── data/
│   └── .gitkeep
├── models/
│   └── .gitkeep
└── configs/
    ├── training_config.yaml
    └── model_config.yaml
```

**TODO**: Create this directory structure. Use `mkdir -p` and `touch` commands or write a Python script.

**Questions to consider:**
- Why do we include `__init__.py` files?
- What is the purpose of `.gitkeep` files?
- Why separate `src/` from `tests/`?

### Task 1.2: Create .gitignore File

Create a `.gitignore` file with appropriate patterns for Python ML projects:

```gitignore
# TODO: Add patterns to ignore:
# - Virtual environments (venv, .venv, env, virtualenv)
# - Python cache files (__pycache__, *.pyc, *.pyo, *.pyd)
# - IDE files (.vscode/, .idea/, *.swp)
# - Environment files (.env, .env.local)
# - Model files (*.pt, *.pth, *.h5, *.ckpt)
# - Data files (data/*.csv, data/*.json, but keep .gitkeep)
# - Log files (*.log, logs/)
# - Distribution files (dist/, build/, *.egg-info/)
```

**TODO**: Complete the `.gitignore` file with proper patterns.

## Part 2: Virtual Environment Management (20 minutes)

### Task 2.1: Create Virtual Environment

**TODO**: Create a virtual environment using venv:

```bash
# Command to create virtual environment
# TODO: Complete this command
python -m venv _____
```

**Questions:**
- What directories are created inside the virtual environment?
- Where are packages installed when the environment is active?

### Task 2.2: Activation Script Testing

**TODO**:
1. Activate the virtual environment
2. Verify activation by checking `which python` (Linux/Mac) or `where python` (Windows)
3. Check Python version: `python --version`
4. Verify pip location: `which pip` or `where pip`

Document your findings:
```
Before activation:
  Python location: _____
  Pip location: _____

After activation:
  Python location: _____
  Pip location: _____
```

### Task 2.3: Multiple Environment Testing

Create two separate virtual environments to understand isolation:

```bash
# Environment 1: For development with Python 3.11
# TODO: Create venv-py311

# Environment 2: For testing with Python 3.10
# TODO: Create venv-py310 (if you have Python 3.10 installed)
```

**TODO**: Install different package versions in each:
- venv-py311: Install `numpy==1.24.0`
- venv-py310: Install `numpy==1.23.0`

Verify isolation by activating each and running:
```python
import numpy
print(numpy.__version__)
```

## Part 3: Dependency Management (30 minutes)

### Task 3.1: Create requirements.txt

The project needs these production dependencies:

**TODO**: Create `requirements.txt` with pinned versions:

```txt
# Core ML frameworks
# TODO: Add torch 2.1.0
# TODO: Add torchvision 0.16.0
# TODO: Add transformers 4.35.0

# Data processing
# TODO: Add pandas 2.1.0
# TODO: Add numpy 1.24.0
# TODO: Add scikit-learn 1.3.0

# Configuration and utilities
# TODO: Add pyyaml 6.0.1
# TODO: Add python-dotenv 1.0.0
# TODO: Add tqdm 4.66.1

# API and serving (for future modules)
# TODO: Add fastapi 0.104.1
# TODO: Add uvicorn 0.24.0

# Logging and monitoring
# TODO: Add loguru 0.7.2
```

**Questions:**
- Why do we pin exact versions (==) instead of using >= or ~=?
- What happens if we don't pin versions?

### Task 3.2: Create requirements-dev.txt

**TODO**: Create `requirements-dev.txt` with development tools:

```txt
# Include production requirements
-r requirements.txt

# Testing
# TODO: Add pytest 7.4.3
# TODO: Add pytest-cov 4.1.0
# TODO: Add pytest-mock 3.12.0

# Code quality
# TODO: Add black 23.11.0
# TODO: Add flake8 6.1.0
# TODO: Add mypy 1.7.0
# TODO: Add isort 5.12.0

# Development tools
# TODO: Add ipython 8.17.0
# TODO: Add jupyter 1.0.0
```

### Task 3.3: Install Dependencies

**TODO**:
1. Activate your virtual environment
2. Upgrade pip: `python -m pip install --upgrade pip`
3. Install development dependencies: `pip install -r requirements-dev.txt`
4. Verify installation: `pip list`

**Expected outcome**: All packages from requirements.txt and requirements-dev.txt should be installed.

### Task 3.4: Freeze Current Environment

**TODO**: Generate a complete dependency freeze:

```bash
pip freeze > requirements-frozen.txt
```

**Compare**:
- Open `requirements.txt` and `requirements-frozen.txt`
- How many packages are in each file?
- What's the difference?

**Answer these questions:**
- Why does `requirements-frozen.txt` have more packages?
- What are transitive dependencies?
- When should you use frozen vs. unpinned requirements?

## Part 4: Environment Variables and Configuration (25 minutes)

### Task 4.1: Create .env.example Template

**TODO**: Create `.env.example` with configuration templates:

```bash
# .env.example
# Copy this to .env and fill in actual values

# Model Configuration
MODEL_NAME=bert-base-uncased
MODEL_CACHE_DIR=/path/to/model/cache
MAX_SEQUENCE_LENGTH=512

# Training Configuration
BATCH_SIZE=32
LEARNING_RATE=0.001
NUM_EPOCHS=10
DEVICE=cuda
# Alternatively: cpu

# Data Configuration
DATA_DIR=/path/to/data
TRAIN_FILE=train.csv
VAL_FILE=val.csv
TEST_FILE=test.csv

# Logging
LOG_LEVEL=INFO
# Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE=training.log

# Weights & Biases (optional)
WANDB_API_KEY=your-wandb-api-key-here
WANDB_PROJECT=sentiment-classifier
WANDB_ENTITY=your-username

# Database (for future use)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ml_experiments
DB_USER=mluser
DB_PASSWORD=changeme
```

### Task 4.2: Create Actual .env File

**TODO**:
1. Copy `.env.example` to `.env`
2. Fill in reasonable values for your local development
3. Verify `.env` is in `.gitignore`

**CRITICAL**: Never commit `.env` to git!

### Task 4.3: Test Environment Loading

Create `test_env.py`:

```python
# test_env.py
import os
from dotenv import load_dotenv

# TODO: Load .env file
# Hint: use load_dotenv()

# TODO: Read and print environment variables
model_name = os.getenv("MODEL_NAME")
batch_size = os.getenv("BATCH_SIZE")
device = os.getenv("DEVICE")

print(f"Model: {model_name}")
print(f"Batch Size: {batch_size}")
print(f"Device: {device}")

# TODO: Handle missing variables
db_password = os.getenv("DB_PASSWORD")
if db_password == "changeme":
    print("WARNING: Using default database password. Change in production!")

# TODO: Type conversion
batch_size_int = int(os.getenv("BATCH_SIZE", "32"))
print(f"Batch size as integer: {batch_size_int}")
```

**Run and verify**: `python test_env.py`

## Part 5: Automation Scripts (30 minutes)

### Task 5.1: Create setup.sh Script

**TODO**: Create `setup.sh` to automate environment setup:

```bash
#!/bin/bash
# setup.sh - Automated environment setup script

set -e  # Exit on error

echo "========================================="
echo "Setting up Sentiment Classifier Project"
echo "========================================="

# TODO: Check Python version
echo "Checking Python version..."
# Hint: Use python --version

# TODO: Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Virtual environment already exists."
    read -p "Recreate it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing existing virtual environment..."
        rm -rf venv
    fi
fi

# TODO: Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    # Hint: python -m venv venv
fi

# TODO: Activate virtual environment
echo "Activating virtual environment..."
# Hint: source venv/bin/activate

# TODO: Upgrade pip
echo "Upgrading pip..."
# Hint: python -m pip install --upgrade pip

# TODO: Install dependencies
echo "Installing dependencies..."
# Hint: pip install -r requirements-dev.txt

# TODO: Create .env from template if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env from template..."
    cp .env.example .env
    echo "WARNING: .env created from template. Please update with actual values!"
fi

# TODO: Run verification
echo ""
echo "========================================="
echo "Setup complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Activate environment: source venv/bin/activate"
echo "2. Update .env with your configuration"
echo "3. Run tests: pytest tests/"
echo ""
```

**TODO**:
1. Complete the TODOs in setup.sh
2. Make it executable: `chmod +x setup.sh`
3. Test it: `./setup.sh`

### Task 5.2: Create verify_setup.py Script

**TODO**: Create `verify_setup.py` to validate the setup:

```python
#!/usr/bin/env python3
"""
verify_setup.py - Verify development environment setup
"""

import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Verify Python version is 3.11+"""
    # TODO: Check sys.version_info
    # Should be at least 3.11
    pass

def check_virtual_environment():
    """Verify running in virtual environment"""
    # TODO: Check if sys.prefix != sys.base_prefix
    # This indicates virtual environment is active
    pass

def check_required_packages():
    """Verify all required packages are installed"""
    required_packages = [
        "torch",
        "transformers",
        "pandas",
        "pytest",
        "black",
        "mypy"
    ]

    # TODO: Try importing each package
    # Report which are missing
    pass

def check_project_structure():
    """Verify project directories exist"""
    required_dirs = [
        "src",
        "tests",
        "data",
        "models",
        "configs"
    ]

    required_files = [
        "requirements.txt",
        "requirements-dev.txt",
        ".gitignore",
        ".env.example"
    ]

    # TODO: Check each directory and file exists
    # Report any missing
    pass

def check_git_setup():
    """Verify git configuration"""
    # TODO: Check if .git directory exists
    # Verify .gitignore includes venv/
    pass

def main():
    print("Verifying Development Environment Setup")
    print("=" * 50)

    checks = [
        ("Python Version", check_python_version),
        ("Virtual Environment", check_virtual_environment),
        ("Required Packages", check_required_packages),
        ("Project Structure", check_project_structure),
        ("Git Configuration", check_git_setup)
    ]

    all_passed = True

    for check_name, check_func in checks:
        try:
            check_func()
            print(f"✓ {check_name}")
        except Exception as e:
            print(f"✗ {check_name}: {e}")
            all_passed = False

    print("=" * 50)

    if all_passed:
        print("All checks passed! Environment is ready.")
        return 0
    else:
        print("Some checks failed. Please fix issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

**TODO**:
1. Complete the implementation of each check function
2. Run: `python verify_setup.py`
3. Fix any issues reported

## Part 6: Documentation (20 minutes)

### Task 6.1: Create Comprehensive README.md

**TODO**: Create `README.md` with setup instructions:

```markdown
# Sentiment Classifier

ML training pipeline for sentiment classification using transformer models.

## Prerequisites

- Python 3.11+
- Git
- 8GB+ RAM
- (Optional) NVIDIA GPU with CUDA 11.8+

## Quick Setup

# TODO: Add step-by-step setup instructions
# Include:
# 1. Clone repository
# 2. Run setup script
# 3. Configure .env
# 4. Verify setup

## Development

# TODO: Add common development tasks
# - Running training
# - Running tests
# - Code formatting
# - Type checking

## Project Structure

# TODO: Document directory structure
# Explain purpose of each directory

## Configuration

# TODO: Explain configuration system
# - Environment variables
# - Config files
# - Precedence order

## Troubleshooting

# TODO: Add common issues and solutions
```

### Task 6.2: Document Your Learnings

Create `SETUP_NOTES.md` documenting:
- Challenges you encountered
- How you solved them
- Tips for team members
- Common errors and fixes

## Verification Checklist

Before submitting, verify:

- [ ] Virtual environment created and working
- [ ] All dependencies installed successfully
- [ ] `requirements.txt` has all production dependencies with pinned versions
- [ ] `requirements-dev.txt` has all development tools
- [ ] `.env.example` created with all configuration options
- [ ] `.env` created (but not committed to git!)
- [ ] `.gitignore` properly excludes sensitive and generated files
- [ ] `setup.sh` successfully automates full setup
- [ ] `verify_setup.py` passes all checks
- [ ] `README.md` has clear setup instructions
- [ ] Project structure matches specification
- [ ] Can activate venv and run `python` successfully
- [ ] Can run `pip list` and see all packages
- [ ] Can import core packages: `import torch`, `import transformers`

## Submission

Create a document answering:

1. **Environment Isolation**: Explain how virtual environments provide isolation. What happens when you install a package in one venv vs globally?

2. **Dependency Pinning**: Why do we pin exact versions in production but might use `>=` during development?

3. **Transitive Dependencies**: What are they? How does `pip freeze` differ from your original requirements.txt?

4. **Configuration Strategy**: Why separate `.env.example` (committed) from `.env` (not committed)?

5. **Automation**: What are the benefits of `setup.sh` vs manual setup instructions?

6. **Challenges**: What was the most challenging part of this exercise? How did you overcome it?

## Extension Challenges (Optional)

For additional practice:

1. **Multiple Environments**: Create separate environments for Python 3.10, 3.11, and 3.12. Test package compatibility.

2. **Pip-tools Integration**: Install `pip-tools` and create `requirements.in` instead of `requirements.txt`. Use `pip-compile` to generate locked requirements.

3. **Docker Integration**: Create a `Dockerfile` that sets up this environment in a container.

4. **Pre-commit Hooks**: Set up pre-commit hooks to run `black`, `flake8`, and `mypy` before commits.

5. **CI/CD Configuration**: Create a GitHub Actions workflow that sets up the environment and runs tests.

## Resources

- [Python venv documentation](https://docs.python.org/3/library/venv.html)
- [pip documentation](https://pip.pypa.io/)
- [pip-tools](https://github.com/jazzband/pip-tools)
- [python-dotenv](https://github.com/theskumar/python-dotenv)

---

**Exercise Version**: 1.0
**Estimated Time**: 2-3 hours
**Difficulty**: Beginner
