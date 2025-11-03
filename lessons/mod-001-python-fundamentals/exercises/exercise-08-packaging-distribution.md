# Exercise 08: Python Packaging and Distribution

## Overview

**Estimated Time**: 2-3 hours
**Difficulty**: Intermediate
**Prerequisites**:
- Completed Exercises 01-07
- Lecture 05: Decorators and Packaging
- Basic understanding of Python modules and imports

## Learning Objectives

By completing this exercise, you will:
1. Create a distributable Python package with proper structure
2. Write `setup.py` and modern `pyproject.toml` configuration files
3. Build source distributions (sdist) and wheel distributions (bdist_wheel)
4. Publish packages to internal/local package indexes
5. Manage dependencies and implement semantic versioning
6. Apply best practices for package documentation and licensing

## Scenario

Your ML infrastructure team has developed several useful utility functions scattered across different projects: data preprocessing helpers, model evaluation metrics, logging utilities, and custom decorators for timing and retrying operations.

Currently, these utilities are copy-pasted between projects, leading to:
- **Version drift**: Different projects have different versions of the same function
- **Bug duplication**: Fixes in one project don't propagate to others
- **Maintenance burden**: Updating utilities requires editing multiple codebases
- **No testing**: Utilities aren't tested independently

Your task is to consolidate these utilities into a proper Python package called `ml-infra-utils` that can be:
- Installed via pip
- Versioned semantically
- Published to an internal package index
- Used across all team projects

---

## Part 1: Package Structure Creation

### Task 1.1: Create Directory Structure

Create the following package structure:

```
ml-infra-utils/
├── README.md
├── LICENSE
├── setup.py
├── pyproject.toml
├── .gitignore
├── CHANGELOG.md
├── src/
│   └── ml_infra_utils/
│       ├── __init__.py
│       ├── preprocessing/
│       │   ├── __init__.py
│       │   ├── normalization.py
│       │   └── validation.py
│       ├── metrics/
│       │   ├── __init__.py
│       │   └── classification.py
│       ├── decorators/
│       │   ├── __init__.py
│       │   ├── timing.py
│       │   └── retry.py
│       └── logging/
│           ├── __init__.py
│           └── structured.py
├── tests/
│   ├── __init__.py
│   ├── test_preprocessing.py
│   ├── test_metrics.py
│   ├── test_decorators.py
│   └── test_logging.py
├── docs/
│   ├── index.md
│   └── api.md
└── examples/
    └── usage_example.py
```

**TODO**: Create this directory structure on your system.

```bash
# Create the structure
mkdir -p ml-infra-utils/{src/ml_infra_utils/{preprocessing,metrics,decorators,logging},tests,docs,examples}

cd ml-infra-utils
```

### Task 1.2: Implement Core Utilities

**File**: `src/ml_infra_utils/preprocessing/normalization.py`

```python
"""Data normalization utilities for ML pipelines."""

from typing import List, Tuple
import statistics


def normalize(data: List[float]) -> List[float]:
    """
    Normalize data to [0, 1] range using min-max scaling.

    Args:
        data: List of numerical values to normalize

    Returns:
        List of normalized values in range [0, 1]

    Raises:
        ValueError: If data is empty or all values are the same

    Examples:
        >>> normalize([1, 2, 3, 4, 5])
        [0.0, 0.25, 0.5, 0.75, 1.0]
    """
    if not data:
        raise ValueError("Cannot normalize empty data")

    min_val = min(data)
    max_val = max(data)

    if min_val == max_val:
        raise ValueError("All values are identical, cannot normalize")

    range_val = max_val - min_val
    return [(x - min_val) / range_val for x in data]


def standardize(data: List[float]) -> List[float]:
    """
    Standardize data to mean=0, std=1 (z-score normalization).

    Args:
        data: List of numerical values to standardize

    Returns:
        List of standardized values

    Raises:
        ValueError: If data is empty or has zero standard deviation
    """
    if not data:
        raise ValueError("Cannot standardize empty data")

    mean = statistics.mean(data)
    stdev = statistics.stdev(data)

    if stdev == 0:
        raise ValueError("Standard deviation is zero, cannot standardize")

    return [(x - mean) / stdev for x in data]


def clip_outliers(data: List[float], lower_percentile: float = 5,
                  upper_percentile: float = 95) -> List[float]:
    """
    Clip outliers based on percentiles.

    Args:
        data: List of numerical values
        lower_percentile: Lower percentile threshold (0-100)
        upper_percentile: Upper percentile threshold (0-100)

    Returns:
        List with outliers clipped to percentile values
    """
    if not data:
        return []

    sorted_data = sorted(data)
    n = len(sorted_data)

    lower_idx = int(n * lower_percentile / 100)
    upper_idx = int(n * upper_percentile / 100)

    lower_bound = sorted_data[lower_idx]
    upper_bound = sorted_data[upper_idx]

    return [max(lower_bound, min(x, upper_bound)) for x in data]
```

**TODO**: Implement similar files for:
- `src/ml_infra_utils/metrics/classification.py` (accuracy, precision, recall, f1_score)
- `src/ml_infra_utils/decorators/timing.py` (timer decorator)
- `src/ml_infra_utils/decorators/retry.py` (retry decorator with exponential backoff)

### Task 1.3: Create Package Init Files

**File**: `src/ml_infra_utils/__init__.py`

```python
"""ML Infrastructure Utilities Package.

A collection of reusable utilities for ML infrastructure projects.
"""

__version__ = "0.1.0"
__author__ = "ML Infrastructure Team"
__email__ = "ml-team@example.com"

# Import commonly used functions for convenience
from ml_infra_utils.preprocessing.normalization import normalize, standardize
from ml_infra_utils.metrics.classification import accuracy, precision, recall
from ml_infra_utils.decorators.timing import timer
from ml_infra_utils.decorators.retry import retry

__all__ = [
    "normalize",
    "standardize",
    "accuracy",
    "precision",
    "recall",
    "timer",
    "retry",
    "__version__",
]
```

**TODO**: Create `__init__.py` files for each subpackage that export their public functions.

---

## Part 2: Package Configuration

### Task 2.1: Write setup.py (Legacy Method)

**File**: `setup.py`

```python
"""Setup configuration for ml-infra-utils package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read long description from README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read version from package
about = {}
with open("src/ml_infra_utils/__init__.py", encoding="utf-8") as f:
    for line in f:
        if line.startswith("__version__"):
            about["__version__"] = line.split('"')[1]
            break

setup(
    name="ml-infra-utils",
    version=about["__version__"],
    author="ML Infrastructure Team",
    author_email="ml-team@example.com",
    description="Reusable ML infrastructure utilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourorg/ml-infra-utils",
    project_urls={
        "Bug Tracker": "https://github.com/yourorg/ml-infra-utils/issues",
        "Documentation": "https://ml-infra-utils.readthedocs.io",
        "Source Code": "https://github.com/yourorg/ml-infra-utils",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        # Runtime dependencies
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "isort>=5.10.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            # Add CLI tools if needed
            # "ml-utils=ml_infra_utils.cli:main",
        ],
    },
)
```

### Task 2.2: Write pyproject.toml (Modern Method - Preferred)

**File**: `pyproject.toml`

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "ml-infra-utils"
version = "0.1.0"
description = "Reusable ML infrastructure utilities"
readme = "README.md"
authors = [
    {name = "ML Infrastructure Team", email = "ml-team@example.com"}
]
maintainers = [
    {name = "ML Infrastructure Team", email = "ml-team@example.com"}
]
license = {text = "MIT"}
keywords = ["machine-learning", "infrastructure", "utilities", "ml-ops"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
]
requires-python = ">=3.8"
dependencies = [
    # No runtime dependencies for this simple package
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=22.0.0",
    "flake8>=5.0.0",
    "mypy>=1.0.0",
    "isort>=5.10.0",
]
docs = [
    "sphinx>=5.0.0",
    "sphinx-rtd-theme>=1.0.0",
]

[project.urls]
Homepage = "https://github.com/yourorg/ml-infra-utils"
Documentation = "https://ml-infra-utils.readthedocs.io"
Repository = "https://github.com/yourorg/ml-infra-utils.git"
"Bug Tracker" = "https://github.com/yourorg/ml-infra-utils/issues"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = "--cov=ml_infra_utils --cov-report=html --cov-report=term"

[tool.black]
line-length = 88
target-version = ['py38', 'py39', 'py310', 'py311']
include = '\.pyi?$'

[tool.isort]
profile = "black"
line_length = 88

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

### Task 2.3: Create README.md

**File**: `README.md`

```markdown
# ML Infrastructure Utilities

A collection of reusable utilities for machine learning infrastructure projects.

## Features

- **Preprocessing**: Data normalization, standardization, outlier clipping
- **Metrics**: Classification metrics (accuracy, precision, recall, F1)
- **Decorators**: Timing, retry with exponential backoff
- **Logging**: Structured logging for ML pipelines

## Installation

### From PyPI (when published)

\```bash
pip install ml-infra-utils
\```

### From source

\```bash
git clone https://github.com/yourorg/ml-infra-utils.git
cd ml-infra-utils
pip install -e .
\```

### With development dependencies

\```bash
pip install -e ".[dev]"
\```

## Quick Start

\```python
from ml_infra_utils import normalize, accuracy, timer

# Normalize data
data = [1, 2, 3, 4, 5]
normalized = normalize(data)
print(normalized)  # [0.0, 0.25, 0.5, 0.75, 1.0]

# Calculate accuracy
predictions = [1, 0, 1, 1, 0]
labels = [1, 0, 1, 0, 0]
acc = accuracy(predictions, labels)
print(f"Accuracy: {acc:.2%}")  # 80%

# Time function execution
@timer
def train_model():
    # Training code
    pass

train_model()  # Prints execution time
\```

## Documentation

Full documentation available at: https://ml-infra-utils.readthedocs.io

## Development

### Running tests

\```bash
pytest
\```

### Code formatting

\```bash
black src/ tests/
isort src/ tests/
\```

### Type checking

\```bash
mypy src/
\```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.
```

**TODO**: Create the README.md file with this content.

---

## Part 3: Build Distribution

### Task 3.1: Install Build Tools

```bash
# Install/upgrade build tools
pip install --upgrade pip setuptools wheel build twine
```

### Task 3.2: Build Source Distribution and Wheel

```bash
# Build both sdist and wheel
python -m build

# This creates:
# dist/ml-infra-utils-0.1.0.tar.gz  (source distribution)
# dist/ml_infra_utils-0.1.0-py3-none-any.whl  (wheel)
```

**Expected output structure**:
```
dist/
├── ml-infra-utils-0.1.0.tar.gz
└── ml_infra_utils-0.1.0-py3-none-any.whl
```

### Task 3.3: Inspect Package Contents

```bash
# List wheel contents
unzip -l dist/ml_infra_utils-0.1.0-py3-none-any.whl

# Extract and inspect source distribution
tar -tzf dist/ml-infra-utils-0.1.0.tar.gz

# Check package metadata
python -m twine check dist/*
```

**TODO**: Verify that:
- ✅ All source files are included
- ✅ `__init__.py` files are present
- ✅ README and LICENSE are included
- ✅ No unnecessary files (*.pyc, __pycache__, etc.)

---

## Part 4: Test Installation

### Task 4.1: Create Test Virtual Environment

```bash
# Create fresh virtual environment
python -m venv test-env
source test-env/bin/activate  # On Windows: test-env\Scripts\activate

# Install from wheel
pip install dist/ml_infra_utils-0.1.0-py3-none-any.whl
```

### Task 4.2: Test Imports

```python
# test_install.py
"""Test that package installs and imports correctly."""

# Test top-level imports
from ml_infra_utils import normalize, accuracy, timer

# Test submodule imports
from ml_infra_utils.preprocessing import standardize
from ml_infra_utils.metrics.classification import precision, recall
from ml_infra_utils.decorators.retry import retry

# Test version
import ml_infra_utils
print(f"Installed version: {ml_infra_utils.__version__}")

# Test functionality
data = [1, 2, 3, 4, 5]
normalized = normalize(data)
print(f"Normalized data: {normalized}")
assert normalized == [0.0, 0.25, 0.5, 0.75, 1.0], "Normalization failed!"

predictions = [1, 0, 1, 1, 0]
labels = [1, 0, 1, 0, 0]
acc = accuracy(predictions, labels)
print(f"Accuracy: {acc:.2%}")
assert acc == 0.8, "Accuracy calculation failed!"

print("✅ All tests passed!")
```

**TODO**: Run this test script and verify all imports work.

---

## Part 5: Internal Package Publishing

### Task 5.1: Set Up Local PyPI Server (Option 1: devpi)

```bash
# Install devpi
pip install devpi-server devpi-client

# Initialize devpi server
devpi-init

# Start devpi server
devpi-server --start --port 3141

# Configure devpi client
devpi use http://localhost:3141
devpi user -c testuser password=testpass
devpi login testuser --password=testpass
devpi index -c dev bases=root/pypi
devpi use testuser/dev
```

### Task 5.2: Upload Package to devpi

```bash
# Upload package
devpi upload dist/*

# Verify upload
devpi list ml-infra-utils
```

### Task 5.3: Install from Internal Index

```bash
# In a new virtual environment
python -m venv install-test
source install-test/bin/activate

# Install from devpi
pip install --index-url http://localhost:3141/testuser/dev/+simple/ ml-infra-utils

# Verify installation
python -c "import ml_infra_utils; print(ml_infra_utils.__version__)"
```

### Task 5.4: Set Up Simple HTTP Server (Option 2: Simpler)

```bash
# Create package index directory
mkdir -p ~/pypi-packages/ml-infra-utils

# Copy distributions
cp dist/* ~/pypi-packages/ml-infra-utils/

# Start simple HTTP server
cd ~/pypi-packages
python -m http.server 8080

# In another terminal, install from local index
pip install --index-url http://localhost:8080/simple/ ml-infra-utils
```

---

## Part 6: Semantic Versioning and Releases

### Task 6.1: Understand Semantic Versioning

**Format**: MAJOR.MINOR.PATCH (e.g., 1.2.3)

- **MAJOR**: Incompatible API changes
- **MINOR**: Backward-compatible new features
- **PATCH**: Backward-compatible bug fixes

**Examples**:
- `0.1.0` → `0.1.1`: Bug fix
- `0.1.1` → `0.2.0`: New feature added
- `0.2.0` → `1.0.0`: Stable API, production-ready
- `1.0.0` → `2.0.0`: Breaking changes

### Task 6.2: Create CHANGELOG.md

**File**: `CHANGELOG.md`

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Nothing yet

## [0.1.0] - 2024-01-15

### Added
- Initial release
- Preprocessing utilities (normalize, standardize, clip_outliers)
- Classification metrics (accuracy, precision, recall, f1_score)
- Decorators (timer, retry)
- Structured logging utilities

### Changed
- Nothing yet

### Deprecated
- Nothing yet

### Removed
- Nothing yet

### Fixed
- Nothing yet

### Security
- Nothing yet

[Unreleased]: https://github.com/yourorg/ml-infra-utils/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourorg/ml-infra-utils/releases/tag/v0.1.0
```

### Task 6.3: Create Git Tags for Releases

```bash
# Initialize git repo (if not already done)
git init
git add .
git commit -m "Initial release v0.1.0"

# Create annotated tag
git tag -a v0.1.0 -m "Release version 0.1.0"

# View tags
git tag -l

# Push tags to remote
git push origin v0.1.0
```

### Task 6.4: Automate Version Bumping

**File**: `bump_version.sh`

```bash
#!/bin/bash
# Script to bump version and create release

set -e

VERSION_TYPE=$1  # major, minor, or patch

if [ -z "$VERSION_TYPE" ]; then
    echo "Usage: ./bump_version.sh [major|minor|patch]"
    exit 1
fi

# Get current version
CURRENT_VERSION=$(grep "__version__" src/ml_infra_utils/__init__.py | cut -d'"' -f2)
echo "Current version: $CURRENT_VERSION"

# Bump version using Python
NEW_VERSION=$(python -c "
import sys
major, minor, patch = map(int, '$CURRENT_VERSION'.split('.'))

if '$VERSION_TYPE' == 'major':
    major += 1
    minor = 0
    patch = 0
elif '$VERSION_TYPE' == 'minor':
    minor += 1
    patch = 0
elif '$VERSION_TYPE' == 'patch':
    patch += 1
else:
    print('Invalid version type', file=sys.stderr)
    sys.exit(1)

print(f'{major}.{minor}.{patch}')
")

echo "New version: $NEW_VERSION"

# Update version in __init__.py
sed -i "s/__version__ = \"$CURRENT_VERSION\"/__version__ = \"$NEW_VERSION\"/" src/ml_infra_utils/__init__.py

# Update version in pyproject.toml
sed -i "s/version = \"$CURRENT_VERSION\"/version = \"$NEW_VERSION\"/" pyproject.toml

# Commit changes
git add src/ml_infra_utils/__init__.py pyproject.toml
git commit -m "Bump version to $NEW_VERSION"

# Create tag
git tag -a "v$NEW_VERSION" -m "Release version $NEW_VERSION"

echo "✅ Version bumped to $NEW_VERSION"
echo "Next steps:"
echo "  1. Update CHANGELOG.md"
echo "  2. git push"
echo "  3. git push --tags"
echo "  4. python -m build"
echo "  5. devpi upload dist/*"
```

**TODO**: Make script executable and test it:

```bash
chmod +x bump_version.sh
./bump_version.sh patch  # Bumps 0.1.0 → 0.1.1
```

---

## Part 7: Dependency Management Best Practices

### Task 7.1: Pin Dependencies Appropriately

**For applications** (strict pinning):
```
# requirements.txt
numpy==1.24.2
pandas==2.0.1
scikit-learn==1.2.2
```

**For libraries** (flexible requirements):
```toml
# pyproject.toml
dependencies = [
    "numpy>=1.21.0,<2.0",
    "pandas>=1.3.0",
]
```

**Why?**
- Applications need reproducibility: exact versions
- Libraries need compatibility: version ranges

### Task 7.2: Create requirements.txt for Development

**File**: `requirements-dev.txt`

```
# Development dependencies
pytest>=7.0.0
pytest-cov>=4.0.0
black>=22.0.0
flake8>=5.0.0
mypy>=1.0.0
isort>=5.10.0

# Documentation
sphinx>=5.0.0
sphinx-rtd-theme>=1.0.0

# Release tools
build>=0.10.0
twine>=4.0.0
```

Install with:
```bash
pip install -r requirements-dev.txt
```

### Task 7.3: Use pip-tools for Reproducible Builds

```bash
# Install pip-tools
pip install pip-tools

# Create requirements.in
cat > requirements.in << EOF
ml-infra-utils
# Your project dependencies here
EOF

# Compile to requirements.txt with exact versions
pip-compile requirements.in

# Install exact versions
pip-sync requirements.txt
```

---

## Expected Outputs

### Deliverables

1. ✅ **Package structure** with all directories and files
2. ✅ **Built distributions**:
   - `dist/ml-infra-utils-0.1.0.tar.gz`
   - `dist/ml_infra_utils-0.1.0-py3-none-any.whl`
3. ✅ **Configuration files**:
   - `setup.py`
   - `pyproject.toml`
   - `README.md`
   - `CHANGELOG.md`
   - `LICENSE`
4. ✅ **Successful installation** in fresh virtual environment
5. ✅ **Working internal package index** (devpi or simple HTTP)
6. ✅ **Git repository** with version tags
7. ✅ **Documentation** for installation and usage

### Success Criteria

- [ ] Package builds without errors
- [ ] All imports work after installation
- [ ] Package installs from internal index
- [ ] Version can be imported: `ml_infra_utils.__version__`
- [ ] Functions work as documented
- [ ] Package metadata is complete (author, license, description)
- [ ] Dependencies install correctly

---

## Troubleshooting

### Issue: "ModuleNotFoundError" after installation

**Solution**: Check that package is installed in correct environment:
```bash
pip list | grep ml-infra-utils
python -c "import sys; print(sys.executable)"
```

### Issue: Package doesn't include source files

**Solution**: Verify `setup.py` uses `find_packages()` and check `MANIFEST.in`:
```
include README.md
include LICENSE
include CHANGELOG.md
recursive-include src *.py
```

### Issue: "Package not found" when installing from index

**Solution**: Check index URL and package name:
```bash
pip install --index-url http://localhost:3141/testuser/dev/+simple/ --verbose ml-infra-utils
```

### Issue: Version conflicts with dependencies

**Solution**: Use compatible version ranges:
```toml
dependencies = [
    "numpy>=1.21.0,<2.0",  # Compatible with numpy 1.x
]
```

---

## Bonus Challenges

### Challenge 1: Add Command-Line Interface

Create a CLI tool using the package:

```python
# src/ml_infra_utils/cli.py
import argparse
from ml_infra_utils import normalize

def main():
    parser = argparse.ArgumentParser(description="ML Infra Utils CLI")
    parser.add_argument("--normalize", nargs="+", type=float, help="Normalize data")
    args = parser.parse_args()

    if args.normalize:
        result = normalize(args.normalize)
        print(result)

if __name__ == "__main__":
    main()
```

Add to `pyproject.toml`:
```toml
[project.scripts]
ml-utils = "ml_infra_utils.cli:main"
```

Usage:
```bash
ml-utils --normalize 1 2 3 4 5
```

### Challenge 2: Set Up CI/CD for Package Publishing

Create `.github/workflows/publish.yml`:

```yaml
name: Publish Package

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install build twine

      - name: Build package
        run: python -m build

      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: twine upload dist/*
```

### Challenge 3: Add Type Stubs for Better IDE Support

Create `.pyi` stub files for better autocomplete:

```python
# src/ml_infra_utils/preprocessing/normalization.pyi
from typing import List

def normalize(data: List[float]) -> List[float]: ...
def standardize(data: List[float]) -> List[float]: ...
```

### Challenge 4: Implement Namespace Packages

For large organizations, use namespace packages:

```python
# Multiple packages under same namespace
# ml-infra-preprocessing/
# ml-infra-metrics/
# ml-infra-decorators/

# All installable as:
from ml_infra.preprocessing import normalize
from ml_infra.metrics import accuracy
from ml_infra.decorators import timer
```

---

## References

- **Lecture 05**: Decorators and Packaging
- **Python Packaging Guide**: https://packaging.python.org/
- **Semantic Versioning**: https://semver.org/
- **setuptools documentation**: https://setuptools.pypa.io/
- **PEP 517/518**: Modern Python packaging standards
- **devpi**: https://devpi.net/
- **Example Python packages**: Look at popular packages like `requests`, `flask` on GitHub

---

## Reflection Questions

1. What are the advantages of publishing internal packages vs copy-pasting code?
2. When would you use `setup.py` vs `pyproject.toml`?
3. How does semantic versioning help with dependency management?
4. What's the difference between a source distribution and a wheel?
5. Why should libraries use version ranges instead of pinned versions?
6. How would you handle security updates in published packages?

---

**Estimated Completion Time**: 2-3 hours

**Next Exercise**: Continue to Module 002 exercises or proceed with advanced Python topics.
