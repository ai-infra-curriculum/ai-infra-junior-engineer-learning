# Lecture 01: Python Environment & Dependency Management

## Table of Contents
1. [Introduction](#introduction)
2. [Understanding Python Environments](#understanding-python-environments)
3. [Virtual Environments Deep Dive](#virtual-environments-deep-dive)
4. [Package Management with pip](#package-management-with-pip)
5. [Requirements Files](#requirements-files)
6. [Python Version Management](#python-version-management)
7. [Best Practices for AI Infrastructure](#best-practices-for-ai-infrastructure)
8. [Common Issues and Troubleshooting](#common-issues-and-troubleshooting)
9. [Summary and Key Takeaways](#summary-and-key-takeaways)

---

## Introduction

### Why Environment Management Matters

Imagine this scenario: You've spent weeks developing an ML model training pipeline. It works perfectly on your laptop. You deploy it to production, and suddenly, cryptic errors appear. The model won't load. Libraries throw version incompatibility warnings. Your carefully tuned pipeline crashes.

What happened? **Environment mismatch**.

In AI infrastructure engineering, environment management isn't just best practice—it's survival. The ML ecosystem involves hundreds of dependencies, many with complex version requirements. PyTorch needs specific CUDA versions. TensorFlow has strict numpy version requirements. One mismatched package can cascade into system-wide failures.

This lecture teaches you to prevent these disasters through rigorous environment and dependency management.

### Learning Objectives

By the end of this lecture, you will:

- Understand how Python finds and loads packages
- Create isolated virtual environments using multiple tools
- Manage dependencies with pip effectively
- Write bulletproof requirements files
- Handle multiple Python versions on one system
- Apply environment management to AI/ML workflows
- Troubleshoot common environment issues

### The AI Infrastructure Context

AI infrastructure engineers work at the intersection of:
- **Data Science**: Managing environments for data scientists and ML engineers
- **Software Engineering**: Building production-grade Python applications
- **DevOps**: Deploying and maintaining services across multiple environments

You'll need to ensure that:
- Training jobs run with correct library versions
- Model serving APIs load the right ML framework version
- Development environments match production exactly
- Team members can reproduce each other's work
- CI/CD pipelines use consistent dependencies

---

## Understanding Python Environments

### How Python Finds Packages

When you write `import tensorflow`, Python searches for the package through a specific process:

```
1. Check sys.modules (already imported packages)
2. Search through directories in sys.path:
   - Current directory
   - PYTHONPATH environment variable
   - Standard library directories
   - Site-packages directories (3rd party packages)
```

You can inspect this yourself:

```python
import sys
print(sys.path)
```

Output might look like:
```
[
    '/home/user/my-project',  # Current directory
    '/usr/lib/python3.11',    # Standard library
    '/usr/lib/python3.11/site-packages',  # System packages
    '/home/user/.local/lib/python3.11/site-packages'  # User packages
]
```

### The Global vs Local Package Problem

**Global Installation** (problematic):
```bash
pip install tensorflow  # Installs to system Python
```

Issues with global installation:
- Every project uses the same package versions
- Upgrading for one project breaks others
- Can't test with different versions
- Risk of system Python corruption
- Requires admin/sudo on many systems
- Conflicts between project requirements

**Local Installation** (isolated):
```bash
python -m venv my-project-env
source my-project-env/bin/activate
pip install tensorflow  # Installs only for this environment
```

Benefits of isolation:
- Each project has independent dependencies
- Safe to experiment with versions
- No admin privileges needed
- Reproducible across machines
- Clear dependency manifest per project

### Site-Packages Directory Structure

Understanding where packages live helps debug import issues:

```
my-venv/
├── bin/               # Executables (python, pip, scripts)
│   ├── python -> python3.11
│   ├── pip
│   └── activate       # Activation script
├── include/           # C headers for compiled extensions
├── lib/
│   └── python3.11/
│       └── site-packages/    # ALL installed packages go here
│           ├── tensorflow/
│           ├── numpy/
│           ├── requests/
│           └── ...
└── pyvenv.cfg         # Environment configuration
```

When you activate a virtual environment, it modifies:
- `PATH`: Prepends `my-venv/bin/` so its python runs first
- `PYTHONPATH`: Points to `my-venv/lib/python3.11/site-packages`

---

## Virtual Environments Deep Dive

### Using venv (Built-in, Recommended)

The `venv` module comes with Python 3.3+. It's the standard, official solution.

#### Creating an Environment

```bash
# Basic creation
python3 -m venv myenv

# Specify Python version explicitly
python3.11 -m venv myenv

# Create in a specific location
python3 -m venv /path/to/my/project/venv
```

**What happens during creation?**
1. Creates directory structure (bin, lib, include)
2. Copies or symlinks Python interpreter
3. Installs pip and setuptools
4. Creates activation scripts for various shells

#### Activating the Environment

**Linux/macOS (bash/zsh)**:
```bash
source myenv/bin/activate
```

**Windows (Command Prompt)**:
```cmd
myenv\Scripts\activate.bat
```

**Windows (PowerShell)**:
```powershell
myenv\Scripts\Activate.ps1
```

**What activation does**:
```bash
# Before activation
which python
# /usr/bin/python

source myenv/bin/activate

# After activation
which python
# /home/user/myproject/myenv/bin/python

echo $PATH
# /home/user/myproject/myenv/bin:/usr/local/bin:/usr/bin:...
```

Your prompt changes to indicate active environment:
```bash
(myenv) user@host:~/project$
```

#### Working in the Environment

```bash
# Activate
source myenv/bin/activate

# Install packages (only affects this environment)
pip install numpy pandas tensorflow

# Check installed packages
pip list

# Run Python code (uses environment's packages)
python my_script.py

# Deactivate when done
deactivate
```

#### Environment Best Practices

**1. Environment Location**
```bash
# Good: In project root, gitignored
my-ml-project/
├── venv/              # or .venv/
├── src/
├── tests/
├── requirements.txt
└── .gitignore         # includes venv/
```

**2. Naming Conventions**
```bash
venv        # Most common
.venv       # Hidden, keeps directory clean
env         # Short alternative
virtualenv  # Explicit
```

**3. Gitignore Virtual Environments**
```gitignore
# .gitignore
venv/
.venv/
env/
*.pyc
__pycache__/
```

Never commit virtual environments to git—they're machine-specific and easily recreated.

### Advanced: virtualenv vs venv

While `venv` is built-in and sufficient, `virtualenv` offers additional features:

```bash
# Install virtualenv
pip install virtualenv

# Create environment
virtualenv myenv

# Features venv doesn't have:
virtualenv --python=python3.9 myenv     # Specify any Python version
virtualenv --system-site-packages myenv  # Access system packages
virtualenv --no-setuptools myenv         # Minimal environment
```

**When to use virtualenv**:
- Need Python version not managed by venv
- Want additional customization options
- Working with legacy Python 2.7 projects
- Need faster environment creation (it's optimized)

**For AI infrastructure work, venv is usually sufficient.**

### Alternative: pyenv and pyenv-virtualenv

For managing multiple Python versions AND virtual environments:

```bash
# Install pyenv (Linux/macOS)
curl https://pyenv.run | bash

# Install a specific Python version
pyenv install 3.11.5

# Set global Python version
pyenv global 3.11.5

# Create virtual environment with pyenv-virtualenv
pyenv virtualenv 3.11.5 my-ml-project

# Activate automatically when entering directory
cd my-ml-project
echo "my-ml-project" > .python-version
# Now auto-activates when you cd into directory!
```

**Advantages for ML work**:
- Test code against multiple Python versions
- Automatic activation per directory
- Manage Python versions without root access
- Integrates with venv seamlessly

---

## Package Management with pip

### Understanding pip

`pip` is Python's package installer, interfacing with PyPI (Python Package Index) and other repositories.

#### Basic pip Commands

```bash
# Install a package
pip install requests

# Install specific version
pip install requests==2.31.0

# Install version constraint
pip install "requests>=2.31.0,<3.0.0"

# Install multiple packages
pip install requests numpy pandas

# Upgrade a package
pip install --upgrade requests

# Uninstall a package
pip uninstall requests

# Show package information
pip show tensorflow

# List installed packages
pip list

# List outdated packages
pip list --outdated
```

#### Understanding Version Specifiers

```bash
# Exact version
pip install numpy==1.24.0

# Minimum version
pip install numpy>=1.24.0

# Compatible version (allows patch updates)
pip install numpy~=1.24.0     # Allows 1.24.x, not 1.25.0

# Exclude versions
pip install "numpy>=1.24.0,<2.0.0,!=1.24.1"  # Avoid buggy 1.24.1

# Latest version (dangerous for production)
pip install numpy
```

**For AI infrastructure, always pin versions in production!**

### Pip Configuration

Create `~/.pip/pip.conf` (Linux/macOS) or `%APPDATA%\pip\pip.ini` (Windows):

```ini
[global]
timeout = 60
index-url = https://pypi.org/simple

[install]
trusted-host = pypi.org
               pypi.python.org
               files.pythonhosted.org
```

**Private package repositories**:
```ini
[global]
index-url = https://my-company-pypi.example.com/simple
extra-index-url = https://pypi.org/simple
```

### Installing from Different Sources

```bash
# From PyPI (default)
pip install tensorflow

# From Git repository
pip install git+https://github.com/user/repo.git

# From specific branch
pip install git+https://github.com/user/repo.git@dev-branch

# From local directory (development mode)
pip install -e /path/to/package  # Editable install

# From local wheel file
pip install /path/to/package.whl

# From requirements file
pip install -r requirements.txt
```

### Dependency Resolution

When you `pip install tensorflow`, pip must:
1. Fetch tensorflow's metadata
2. Read its dependencies (numpy, protobuf, etc.)
3. Recursively fetch dependency metadata
4. Resolve compatible versions for all packages
5. Download and install in correct order

**Example dependency tree**:
```
tensorflow==2.13.0
├── numpy>=1.24.0,<2.0.0
├── protobuf>=3.20.0
├── tensorboard>=2.13.0
│   ├── numpy>=1.12.0
│   └── protobuf>=3.19.0
└── keras>=2.13.0
    └── numpy>=1.23.0
```

Pip finds versions satisfying ALL constraints: `numpy>=1.24.0` (from tensorflow's strictest requirement).

**Dependency conflicts** happen when no version satisfies all constraints:
```
Package A requires numpy>=1.24.0
Package B requires numpy<1.20.0
# No version of numpy satisfies both! pip will error.
```

---

## Requirements Files

Requirements files document your project's dependencies, enabling reproducibility.

### Basic Requirements.txt

```txt
# requirements.txt
numpy==1.24.3
pandas==2.0.3
scikit-learn==1.3.0
tensorflow==2.13.0
requests==2.31.0
```

**Creating from current environment**:
```bash
pip freeze > requirements.txt
```

**Installing from requirements file**:
```bash
pip install -r requirements.txt
```

### Requirements.txt Best Practices

#### 1. Pin Exact Versions for Production

```txt
# Good: Reproducible builds
numpy==1.24.3
tensorflow==2.13.0

# Bad: Unpredictable (may break between deployments)
numpy
tensorflow>=2.0.0
```

#### 2. Use Comments for Clarity

```txt
# Core ML frameworks
tensorflow==2.13.0      # Model training
scikit-learn==1.3.0     # Preprocessing

# Data processing
numpy==1.24.3
pandas==2.0.3

# API serving
fastapi==0.103.0
uvicorn==0.23.2

# Monitoring
prometheus-client==0.17.1
```

#### 3. Separate Dev and Production Requirements

**requirements.txt** (production):
```txt
tensorflow==2.13.0
numpy==1.24.3
fastapi==0.103.0
```

**requirements-dev.txt** (development):
```txt
-r requirements.txt     # Include production requirements

# Testing
pytest==7.4.0
pytest-cov==4.1.0
pytest-mock==3.11.1

# Code quality
black==23.7.0
flake8==6.1.0
mypy==1.5.1

# Development tools
ipython==8.14.0
jupyter==1.0.0
```

Install both:
```bash
pip install -r requirements-dev.txt
```

#### 4. Handle Platform-Specific Dependencies

```txt
# Common dependencies
numpy==1.24.3
pandas==2.0.3

# Linux-specific (GPU support)
tensorflow-gpu==2.13.0; sys_platform == 'linux'

# macOS-specific (CPU only)
tensorflow==2.13.0; sys_platform == 'darwin'

# Windows-specific
pywin32==306; sys_platform == 'win32'
```

### Advanced: Pip-tools for Lock Files

**Problem**: `requirements.txt` with pinned versions is hard to maintain.

**Solution**: Use `pip-tools` to separate high-level requirements from locked versions.

```bash
pip install pip-tools
```

**requirements.in** (high-level requirements):
```txt
tensorflow>=2.13.0,<3.0.0
numpy
pandas
```

**Generate locked requirements.txt**:
```bash
pip-compile requirements.in
```

**Produces requirements.txt** with ALL dependencies pinned:
```txt
# This file is autogenerated by pip-compile
# To update, run: pip-compile requirements.in

tensorflow==2.13.0
    # via -r requirements.in
numpy==1.24.3
    # via -r requirements.in
    # via pandas
    # via tensorflow
pandas==2.0.3
    # via -r requirements.in
protobuf==4.23.4
    # via tensorflow
# ... all transitive dependencies pinned
```

**Benefits**:
- Maintain simple `.in` file
- Get fully pinned, reproducible `.txt`
- Easy to update: `pip-compile --upgrade`
- See why each dependency exists

**Workflow**:
```bash
# Edit high-level requirements
vim requirements.in

# Regenerate lock file
pip-compile requirements.in

# Install exact versions
pip-sync requirements.txt

# Commit both files
git add requirements.in requirements.txt
git commit -m "Update dependencies"
```

---

## Python Version Management

AI/ML projects often require specific Python versions. TensorFlow 2.13 might require Python 3.8-3.11. You need flexibility.

### Using pyenv (Recommended)

**Installation (Linux/macOS)**:
```bash
curl https://pyenv.run | bash

# Add to ~/.bashrc or ~/.zshrc
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```

**Basic pyenv usage**:
```bash
# List available Python versions
pyenv install --list

# Install specific versions
pyenv install 3.11.5
pyenv install 3.10.13
pyenv install 3.9.18

# List installed versions
pyenv versions

# Set global Python version
pyenv global 3.11.5

# Set local version for project directory
cd my-ml-project
pyenv local 3.10.13
# Creates .python-version file

# Use specific version temporarily
pyenv shell 3.9.18
```

**Directory-specific Python versions**:
```bash
my-ml-project/
├── .python-version    # Contains "3.10.13"
├── venv/
└── requirements.txt

# When you cd into directory, Python 3.10.13 activates automatically!
cd my-ml-project
python --version  # Python 3.10.13
```

### Combining pyenv with Virtual Environments

**Create environment with specific Python version**:
```bash
# Install Python version
pyenv install 3.11.5

# Create virtual environment using that version
pyenv virtualenv 3.11.5 my-project-env

# Activate it
pyenv activate my-project-env

# Or set as local for directory
cd my-project
pyenv local my-project-env  # Auto-activates when entering directory
```

### Windows: Managing Python Versions

Windows doesn't have pyenv, but alternatives exist:

**Option 1: Python Launcher (py)**:
```cmd
REM Install multiple Python versions from python.org

REM List installed versions
py --list

REM Run specific version
py -3.11 script.py
py -3.10 -m venv myenv

REM Create venv with specific version
py -3.11 -m venv myenv-py311
```

**Option 2: Conda (heavy but cross-platform)**:
```bash
conda create -n myenv python=3.11
conda activate myenv
```

---

## Best Practices for AI Infrastructure

### 1. Reproducible Environments

**Always include**:
```
my-ml-project/
├── .python-version        # Specify Python version
├── requirements.txt       # Pinned dependencies
├── README.md             # Setup instructions
└── Makefile or setup.sh  # Automated setup
```

**setup.sh example**:
```bash
#!/bin/bash
set -e

echo "Setting up ML training environment..."

# Check Python version
python --version | grep "3.11" || {
    echo "Error: Python 3.11 required"
    exit 1
}

# Create virtual environment
python -m venv venv

# Activate
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

echo "Environment ready! Activate with: source venv/bin/activate"
```

Make it executable:
```bash
chmod +x setup.sh
./setup.sh
```

### 2. Docker for Complete Isolation

Virtual environments isolate Python packages, but not:
- System libraries (CUDA, cuDNN)
- Python interpreter itself
- OS-level dependencies

Docker provides full isolation:

**Dockerfile**:
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run application
CMD ["python", "train.py"]
```

Build and run:
```bash
docker build -t my-ml-training .
docker run my-ml-training
```

### 3. CI/CD Environment Consistency

**GitHub Actions example**:
```yaml
# .github/workflows/test.yml
name: Test ML Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Cache pip packages
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt

    - name: Run tests
      run: pytest tests/
```

This ensures tests run with exact dependencies every time.

### 4. Environment Variables for Configuration

Never hardcode configurations. Use environment variables:

**.env file**:
```bash
# .env (never commit to git!)
MODEL_PATH=/data/models
BATCH_SIZE=32
LEARNING_RATE=0.001
AWS_ACCESS_KEY_ID=your-key-id
AWS_SECRET_ACCESS_KEY=your-secret
```

**Load in Python**:
```python
import os
from dotenv import load_dotenv

load_dotenv()  # Loads .env file

model_path = os.getenv('MODEL_PATH', '/default/path')
batch_size = int(os.getenv('BATCH_SIZE', '16'))
```

**Include in .gitignore**:
```gitignore
.env
.env.local
.env.*.local
```

**Provide template**:
```bash
# .env.example (commit this)
MODEL_PATH=/data/models
BATCH_SIZE=32
LEARNING_RATE=0.001
AWS_ACCESS_KEY_ID=your-key-id-here
AWS_SECRET_ACCESS_KEY=your-secret-here
```

---

## Common Issues and Troubleshooting

### Issue 1: "Command 'python' not found"

**Problem**: System uses `python3` not `python`.

**Solution**:
```bash
# Option 1: Use python3 explicitly
python3 -m venv myenv

# Option 2: Create alias
echo "alias python=python3" >> ~/.bashrc
source ~/.bashrc

# Option 3: Symlink
sudo ln -s /usr/bin/python3 /usr/bin/python
```

### Issue 2: Permission Denied

**Problem**:
```bash
pip install tensorflow
# ERROR: Could not install packages due to an OSError: [Errno 13] Permission denied
```

**Solution**: Don't use sudo! Use virtual environment:
```bash
python -m venv myenv
source myenv/bin/activate
pip install tensorflow  # No permission issue
```

### Issue 3: Dependency Conflicts

**Problem**:
```
ERROR: Cannot install packageA and packageB because these package versions have conflicting dependencies.
```

**Solution**:
```bash
# 1. Check what's conflicting
pip install --dry-run packageA packageB

# 2. Try installing sequentially
pip install packageA
pip install packageB

# 3. Use compatible versions
pip install "packageA==1.0.0" "packageB==2.0.0"

# 4. Last resort: separate environments
python -m venv env-for-A
python -m venv env-for-B
```

### Issue 4: Wrong Package Version After Install

**Problem**: Installed new version but imports show old version.

**Solution**:
```bash
# 1. Check what's actually installed
pip show tensorflow

# 2. Restart Python (old import cached)
# exit() and restart

# 3. Force reinstall
pip install --force-reinstall tensorflow==2.13.0

# 4. Check for system-wide install shadowing venv
which python  # Should show venv path
```

### Issue 5: "No module named X" After Installing

**Problem**: Installed package but Python can't find it.

**Solution**:
```bash
# 1. Check virtual environment is activated
which python  # Should be in venv path

# 2. Check package installed in correct environment
pip list | grep package-name

# 3. Install in correct environment
source venv/bin/activate
pip install package-name

# 4. Check for typos
pip list  # See exact package name
```

---

## Summary and Key Takeaways

### Essential Commands Reference

```bash
# Virtual environment
python -m venv myenv
source myenv/bin/activate  # Linux/macOS
myenv\Scripts\activate     # Windows
deactivate

# Package management
pip install package-name
pip install -r requirements.txt
pip freeze > requirements.txt
pip list
pip show package-name

# Version management (pyenv)
pyenv install 3.11.5
pyenv global 3.11.5
pyenv local 3.11.5
```

### Best Practices Checklist

✅ Always use virtual environments for projects
✅ Pin exact versions in requirements.txt for production
✅ Separate dev dependencies from production
✅ Never commit virtual environments to git
✅ Use .env files for configuration
✅ Document setup process in README
✅ Test dependency installation on clean environment
✅ Use pip-tools or Poetry for complex projects
✅ Consider Docker for full environment reproducibility
✅ Keep requirements.txt updated as dependencies change

### What You've Learned

1. **Python's import system** and how it finds packages
2. **Virtual environments** for dependency isolation
3. **pip package management** and version specifiers
4. **Requirements files** for reproducible installations
5. **Python version management** with pyenv
6. **Best practices** for AI/ML infrastructure projects
7. **Troubleshooting** common environment issues

### Next Steps

You now understand Python environment management—the foundation for all AI infrastructure work. Next:

1. Complete **Exercise 01**: Create a full project with proper environment setup
2. Practice creating and managing multiple environments
3. Experiment with pip-tools or Poetry
4. Move to **Lecture 02**: Advanced Python patterns for infrastructure

### Additional Resources

- [Python Packaging User Guide](https://packaging.python.org/)
- [pip documentation](https://pip.pypa.io/)
- [pyenv GitHub repository](https://github.com/pyenv/pyenv)
- [pip-tools documentation](https://pip-tools.readthedocs.io/)
- [PEP 405 - Python Virtual Environments](https://peps.python.org/pep-0405/)

---

**Lecture Version**: 1.0
**Last Updated**: October 2025
**Word Count**: ~3,800 words
**Estimated Reading Time**: 45-60 minutes

**Ready for more?** Continue to `02-advanced-python.md` for type hints, logging, and configuration management.
