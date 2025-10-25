# Exercise 05: Collaboration and Pull Requests

## Overview

**Difficulty**: Intermediate
**Estimated Time**: 90-120 minutes
**Prerequisites**: Exercise 04 - Merging and Conflicts, Lecture 03 - Collaboration

In this exercise, you'll learn collaborative Git workflows including forking repositories, creating pull requests, conducting code reviews, and working with remote repositories. You'll practice the complete GitHub collaboration workflow used in professional ML engineering teams.

## Learning Objectives

By completing this exercise, you will:

- Fork and clone repositories
- Work with remote repositories
- Create and manage pull requests
- Conduct effective code reviews
- Understand PR best practices
- Handle review feedback
- Use GitHub CLI for efficiency
- Collaborate on ML projects
- Manage upstream synchronization

## Scenario

You're joining an ML infrastructure team that uses GitHub for collaboration. You'll contribute to the team's inference API project by forking the repository, implementing features, creating pull requests, and participating in code review.

## Prerequisites

```bash
# Ensure you have GitHub CLI installed
gh --version

# If not installed:
# Mac: brew install gh
# Linux: Download from https://cli.github.com/
# Windows: Download from https://cli.github.com/

# Authenticate with GitHub
gh auth login

# Follow prompts to authenticate
```

---

## Part 1: Forking and Cloning

### Task 1.1: Fork a Repository

**Instructions:**

For this exercise, we'll simulate the fork workflow locally. In a real scenario:

```bash
# On GitHub website:
# 1. Navigate to repository
# 2. Click "Fork" button
# 3. Fork to your account

# Using GitHub CLI:
# gh repo fork <owner>/<repo> --clone

# For this exercise, create a simulated "upstream" repo
cd /tmp
mkdir ml-inference-api-upstream
cd ml-inference-api-upstream
git init
git config init.defaultBranch main

# Create basic project
cat > README.md << 'EOF'
# ML Inference API (Team Repository)

Production ML inference service.

## Contributing

1. Fork this repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request
EOF

git add README.md
git commit -m "Initial commit"

# Tag as v1.0.0
git tag -a v1.0.0 -m "Initial release"

# Now "fork" it (simulate by cloning)
cd ~
git clone /tmp/ml-inference-api-upstream ml-inference-api-fork
cd ml-inference-api-fork

# Add upstream remote
git remote add upstream /tmp/ml-inference-api-upstream
git remote -v
```

**Output:**
```
origin  /tmp/ml-inference-api-upstream (fetch)
origin  /tmp/ml-inference-api-upstream (push)
upstream        /tmp/ml-inference-api-upstream (fetch)
upstream        /tmp/ml-inference-api-upstream (push)
```

---

### Task 1.2: Sync with Upstream

Keep your fork updated.

**Instructions:**

```bash
# Fetch updates from upstream
git fetch upstream

# View upstream branches
git branch -r

# Merge upstream changes into your main
git switch main
git merge upstream/main

# Alternative: rebase instead of merge
# git rebase upstream/main

# Push to your fork
# git push origin main
```

---

## Part 2: Creating Pull Requests

### Task 2.1: Create a Feature Branch for PR

Implement a feature for pull request submission.

**Instructions:**

```bash
# Always branch from latest main
git switch main
git pull upstream main

# Create feature branch with descriptive name
git switch -c feature/add-model-metrics

# Implement the feature
mkdir -p src/monitoring
cat > src/monitoring/model_metrics.py << 'EOF'
"""
Model Performance Metrics

Track model-specific performance indicators.
"""

from dataclasses import dataclass
from typing import Dict, List
import numpy as np


@dataclass
class ModelMetrics:
    """Track model performance metrics."""

    predictions: List[float] = None
    ground_truth: List[float] = None

    def __post_init__(self):
        """Initialize lists if None."""
        if self.predictions is None:
            self.predictions = []
        if self.ground_truth is None:
            self.ground_truth = []

    def add_prediction(self, prediction: float, truth: float = None):
        """
        Record a prediction.

        Args:
            prediction: Model prediction
            truth: Ground truth value (if available)
        """
        self.predictions.append(prediction)
        if truth is not None:
            self.ground_truth.append(truth)

    def calculate_accuracy(self) -> float:
        """
        Calculate prediction accuracy.

        Returns:
            Accuracy percentage (0-100)
        """
        if not self.predictions or not self.ground_truth:
            return 0.0

        if len(self.predictions) != len(self.ground_truth):
            raise ValueError("Predictions and ground truth lengths don't match")

        correct = sum(
            1 for pred, truth in zip(self.predictions, self.ground_truth)
            if abs(pred - truth) < 0.01
        )

        return (correct / len(self.predictions)) * 100

    def get_summary(self) -> Dict:
        """
        Get metrics summary.

        Returns:
            Dictionary of metrics
        """
        return {
            "total_predictions": len(self.predictions),
            "accuracy": self.calculate_accuracy() if self.ground_truth else None,
            "mean_prediction": np.mean(self.predictions) if self.predictions else 0,
            "std_prediction": np.std(self.predictions) if self.predictions else 0
        }


# Global metrics instance
model_metrics = ModelMetrics()
EOF

# Add tests
mkdir -p tests/monitoring
cat > tests/monitoring/test_model_metrics.py << 'EOF'
"""Tests for model metrics."""

import pytest
from src.monitoring.model_metrics import ModelMetrics


def test_model_metrics_initialization():
    """Test metrics initialization."""
    metrics = ModelMetrics()
    assert metrics.predictions == []
    assert metrics.ground_truth == []


def test_add_prediction():
    """Test adding predictions."""
    metrics = ModelMetrics()
    metrics.add_prediction(0.95, 1.0)
    metrics.add_prediction(0.87, 1.0)

    assert len(metrics.predictions) == 2
    assert len(metrics.ground_truth) == 2


def test_calculate_accuracy():
    """Test accuracy calculation."""
    metrics = ModelMetrics()
    metrics.add_prediction(1.0, 1.0)
    metrics.add_prediction(1.0, 1.0)
    metrics.add_prediction(0.0, 1.0)

    accuracy = metrics.calculate_accuracy()
    assert accuracy == pytest.approx(66.67, rel=0.1)


def test_get_summary():
    """Test metrics summary."""
    metrics = ModelMetrics()
    metrics.add_prediction(0.9)
    metrics.add_prediction(0.8)

    summary = metrics.get_summary()
    assert summary["total_predictions"] == 2
    assert "mean_prediction" in summary
EOF

# Commit with good messages
git add src/monitoring/model_metrics.py
git commit -m "feat: add model performance metrics tracking

Implement ModelMetrics class for tracking:
- Prediction accuracy
- Statistical summaries
- Ground truth comparison

This enables monitoring model performance in production."

git add tests/monitoring/test_model_metrics.py
git commit -m "test: add tests for model metrics

Add comprehensive tests for ModelMetrics:
- Initialization
- Adding predictions
- Accuracy calculation
- Summary generation

All tests passing with 100% coverage."

# Update documentation
cat >> README.md << 'EOF'

## Model Monitoring

Track model performance with `ModelMetrics`:

```python
from src.monitoring.model_metrics import model_metrics

# Record predictions
model_metrics.add_prediction(prediction=0.95, truth=1.0)

# Get summary
summary = model_metrics.get_summary()
```
EOF

git add README.md
git commit -m "docs: add model metrics usage to README"

# View your commits
git log --oneline origin/main..HEAD
```

---

### Task 2.2: Push and Create Pull Request

Submit your feature for review.

**Instructions:**

```bash
# Push feature branch to your fork
# git push origin feature/add-model-metrics

# Create PR using GitHub CLI
# gh pr create --title "Add model performance metrics" \
#              --body "## Summary
#
# Adds ModelMetrics class for tracking model performance in production.
#
# ## Changes
# - New ModelMetrics class with accuracy tracking
# - Comprehensive test coverage
# - Documentation updates
#
# ## Testing
# - All tests passing
# - Manual testing completed
#
# ## Screenshots
# (Add if relevant)
#
# Closes #123" \
#              --base main

# Or create PR on GitHub website:
# 1. Go to your fork
# 2. Click "Compare & pull request"
# 3. Fill in title and description
# 4. Click "Create pull request"

# For this exercise, simulate PR creation
cat > .git/PR_TEMPLATE.md << 'EOF'
# Pull Request: Add Model Performance Metrics

## Summary
Adds ModelMetrics class for tracking model performance in production.

## Type of Change
- [x] New feature
- [ ] Bug fix
- [ ] Breaking change
- [ ] Documentation update

## Changes
- New `ModelMetrics` class with accuracy tracking
- Comprehensive test coverage (100%)
- Documentation updates in README

## Testing
- [x] All existing tests passing
- [x] New tests added and passing
- [x] Manual testing completed
- [ ] Integration tests updated

## Checklist
- [x] Code follows project style guidelines
- [x] Self-review completed
- [x] Comments added for complex logic
- [x] Documentation updated
- [x] No new warnings generated
- [x] Tests added for new functionality
- [x] All tests passing

## Related Issues
Closes #123

## Additional Notes
This is foundational work for the model monitoring dashboard (future PR).

## Reviewer Notes
Please pay special attention to:
- Accuracy calculation logic
- Error handling in edge cases
EOF

echo "PR template created! This would be submitted to GitHub."
```

---

## Part 3: Code Review Process

### Task 3.1: Review a Pull Request

Practice reviewing code.

**Instructions:**

```bash
# Simulate receiving a PR to review

# Create a branch simulating someone else's work
git switch main
git switch -c review/teammate-pr

# Add some code with issues
cat > src/utils/image_processing.py << 'EOF'
"""Image processing utilities."""

def resize_image(img, size):
    # TODO: Add validation
    return img.resize(size)

def normalize(img):
    # FIXME: This doesn't handle edge cases
    return img / 255.0
EOF

git add src/utils/image_processing.py
git commit -m "Add image processing utils"

# Review checklist:
cat > review_checklist.md << 'EOF'
# Code Review Checklist

## Functionality
- [ ] Code does what it claims to do
- [ ] Edge cases handled
- [ ] Error handling present
- [ ] No obvious bugs

## Code Quality
- [ ] Follows project style guide
- [ ] DRY principle followed
- [ ] Functions are focused and single-purpose
- [ ] Variable/function names are clear
- [ ] No unnecessary complexity

## Testing
- [ ] Tests exist and pass
- [ ] Edge cases tested
- [ ] Test coverage adequate
- [ ] Tests are maintainable

## Documentation
- [ ] Code is self-documenting or well-commented
- [ ] Docstrings present
- [ ] README updated if needed
- [ ] API documentation updated

## Security
- [ ] No secrets in code
- [ ] Input validation present
- [ ] No SQL injection vulnerabilities
- [ ] Dependencies are safe

## Performance
- [ ] No obvious performance issues
- [ ] Algorithms are efficient
- [ ] No memory leaks
- [ ] Caching used where appropriate

## ML-Specific
- [ ] Model versioning handled
- [ ] Data validation present
- [ ] Metrics tracked
- [ ] Reproducibility maintained
EOF

# Review comments to leave:
cat > review_comments.md << 'EOF'
# Review Comments for PR #123

## Summary
Good start on image processing utilities! A few suggestions below.

## Comments

### src/utils/image_processing.py

**Line 5: `resize_image` function**
```suggestion
def resize_image(img, size):
    """
    Resize image to specified dimensions.

    Args:
        img: PIL Image object
        size: Tuple of (width, height)

    Returns:
        Resized PIL Image

    Raises:
        ValueError: If size is invalid
    """
    if not isinstance(size, tuple) or len(size) != 2:
        raise ValueError("Size must be tuple of (width, height)")
    if not all(isinstance(x, int) and x > 0 for x in size):
        raise ValueError("Dimensions must be positive integers")
    return img.resize(size)
```

Please add:
1. Docstring
2. Input validation
3. Type hints

**Line 9: `normalize` function**
⚠️ **Issue**: Division by 255.0 assumes RGB images. What about grayscale or other formats?

```suggestion
def normalize(img, max_value=255.0):
    """
    Normalize image pixel values to [0, 1] range.

    Args:
        img: Image array
        max_value: Maximum pixel value (default 255 for RGB)

    Returns:
        Normalized image array
    """
    if img.max() == 0:
        return img  # Avoid division by zero
    return img / max_value
```

## Required Changes
- [ ] Add input validation to `resize_image`
- [ ] Add docstrings to all functions
- [ ] Handle edge cases in `normalize`
- [ ] Add unit tests

## Nice to Have
- [ ] Add type hints
- [ ] Add integration test
- [ ] Consider adding batch processing support

## Verdict
**Request Changes** - Please address the required changes above.

Great work overall! Just needs a bit more robustness.
EOF

echo "Review completed! Comments ready to submit."
```

---

### Task 3.2: Address Review Feedback

Respond to code review comments.

**Instructions:**

```bash
# Address the feedback
cat > src/utils/image_processing.py << 'EOF'
"""
Image Processing Utilities

Common image preprocessing operations.
"""

from typing import Tuple
from PIL import Image
import numpy as np


def resize_image(img: Image.Image, size: Tuple[int, int]) -> Image.Image:
    """
    Resize image to specified dimensions.

    Args:
        img: PIL Image object
        size: Tuple of (width, height)

    Returns:
        Resized PIL Image

    Raises:
        ValueError: If size is invalid
        TypeError: If img is not a PIL Image
    """
    if not isinstance(img, Image.Image):
        raise TypeError("img must be a PIL Image")

    if not isinstance(size, tuple) or len(size) != 2:
        raise ValueError("Size must be tuple of (width, height)")

    if not all(isinstance(x, int) and x > 0 for x in size):
        raise ValueError("Dimensions must be positive integers")

    return img.resize(size)


def normalize(
    img: np.ndarray,
    max_value: float = 255.0,
    epsilon: float = 1e-8
) -> np.ndarray:
    """
    Normalize image pixel values to [0, 1] range.

    Args:
        img: Image array (numpy)
        max_value: Maximum pixel value (default 255 for RGB)
        epsilon: Small value to prevent division by zero

    Returns:
        Normalized image array

    Raises:
        ValueError: If img is empty or max_value <= 0
    """
    if img.size == 0:
        raise ValueError("Cannot normalize empty image")

    if max_value <= 0:
        raise ValueError("max_value must be positive")

    # Prevent division by zero
    actual_max = max(img.max(), epsilon)

    return img / actual_max
EOF

# Add tests
cat > tests/utils/test_image_processing.py << 'EOF'
"""Tests for image processing utilities."""

import pytest
import numpy as np
from PIL import Image
from src.utils.image_processing import resize_image, normalize


def test_resize_image_valid():
    """Test resizing with valid input."""
    img = Image.new('RGB', (100, 100))
    resized = resize_image(img, (50, 50))
    assert resized.size == (50, 50)


def test_resize_image_invalid_size():
    """Test resizing with invalid size."""
    img = Image.new('RGB', (100, 100))
    with pytest.raises(ValueError):
        resize_image(img, (50,))  # Wrong tuple length


def test_resize_image_negative_size():
    """Test resizing with negative dimensions."""
    img = Image.new('RGB', (100, 100))
    with pytest.raises(ValueError):
        resize_image(img, (-50, 50))


def test_normalize_standard():
    """Test normalization with standard RGB values."""
    img = np.array([0, 127, 255])
    normalized = normalize(img, max_value=255.0)
    assert normalized[0] == pytest.approx(0.0)
    assert normalized[2] == pytest.approx(1.0)


def test_normalize_empty_image():
    """Test normalization with empty array."""
    img = np.array([])
    with pytest.raises(ValueError):
        normalize(img)


def test_normalize_all_zeros():
    """Test normalization with all-zero image."""
    img = np.zeros((10, 10))
    normalized = normalize(img)
    assert np.all(normalized == 0.0)
EOF

git add src/utils/image_processing.py tests/utils/test_image_processing.py
git commit -m "refactor: address code review feedback

Changes:
- Added type hints to all functions
- Added comprehensive docstrings
- Added input validation
- Added edge case handling in normalize()
- Added unit tests with 100% coverage

Addresses review comments from @reviewer"

# Leave a comment
cat > review_response.md << 'EOF'
# Response to Review Comments

Thanks for the thorough review! I've addressed all the feedback:

## Changes Made

✅ Added input validation to `resize_image`
✅ Added docstrings to all functions
✅ Handle edge cases in `normalize` (division by zero, empty arrays)
✅ Added comprehensive unit tests

## Additional Improvements

- Added type hints throughout
- Increased test coverage to 100%
- Added more specific error messages

## Test Results

```
tests/utils/test_image_processing.py ......  [100%]

6 passed in 0.12s
```

Ready for another review!
EOF

echo "Feedback addressed! Ready for re-review."
```

---

## Part 4: Collaboration Best Practices

### Task 4.1: Write Good PR Descriptions

**Instructions:**

```bash
# Template for excellent PR descriptions
cat > .github/PULL_REQUEST_TEMPLATE.md << 'EOF'
## Description
<!-- Provide a brief description of the changes -->

## Motivation and Context
<!-- Why is this change needed? What problem does it solve? -->
<!-- Link to related issues: Fixes #123, Relates to #456 -->

## Type of Change
<!-- Mark relevant items with [x] -->
- [ ] 🐛 Bug fix (non-breaking change fixing an issue)
- [ ] ✨ New feature (non-breaking change adding functionality)
- [ ] 💥 Breaking change (fix or feature causing existing functionality to break)
- [ ] 📝 Documentation update
- [ ] 🎨 Code style update (formatting, renaming)
- [ ] ♻️ Code refactoring
- [ ] ⚡ Performance improvement
- [ ] ✅ Test update

## Changes Made
<!-- List the specific changes in this PR -->
-
-
-

## Testing
<!-- Describe the tests you ran -->
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed
- [ ] All existing tests pass

### Test Results
```
# Paste test output here
```

## Screenshots (if applicable)
<!-- Add screenshots for UI changes -->

## Checklist
- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have commented complex code sections
- [ ] I have updated the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix/feature works
- [ ] New and existing tests pass locally
- [ ] Any dependent changes have been merged

## Performance Impact
<!-- If applicable, describe performance implications -->
- Latency:
- Memory:
- Throughput:

## Security Considerations
<!-- If applicable, describe security implications -->

## Deployment Notes
<!-- Special deployment considerations -->
- Database migrations:
- Configuration changes:
- Dependencies added:

## Reviewer Focus Areas
<!-- Guide reviewers on what to focus on -->
Please pay special attention to:
-
-

## Additional Context
<!-- Any other context about the PR -->
EOF

git add .github/PULL_REQUEST_TEMPLATE.md
git commit -m "chore: add comprehensive PR template"
```

---

### Task 4.2: Effective Code Review Comments

**Instructions:**

Create a guide for code reviews:

```bash
cat > docs/CODE_REVIEW_GUIDE.md << 'EOF'
# Code Review Guidelines

## For Authors

### Before Creating PR
1. **Self-review** your code
2. **Run all tests** locally
3. **Update documentation**
4. **Write clear PR description**
5. **Link related issues**

### PR Title Format
```
<type>(<scope>): <subject>

Examples:
feat(api): add batch inference endpoint
fix(preprocessing): handle grayscale images correctly
docs(readme): update installation instructions
```

### PR Description
- **What** changed
- **Why** it changed
- **How** to test it
- **Any** breaking changes

## For Reviewers

### Review Checklist
- [ ] Code correctness
- [ ] Test coverage
- [ ] Documentation
- [ ] Performance
- [ ] Security
- [ ] ML-specific concerns

### Comment Types

**Blocking Issues** (must fix):
```
🚨 BLOCKER: This causes a memory leak in production.
```

**Important Suggestions**:
```
⚠️ Consider: Using a connection pool would improve performance.
```

**Nitpicks** (optional):
```
💅 Nitpick: Variable name could be more descriptive.
```

**Praise**:
```
👍 Nice: Excellent error handling!
```

**Questions**:
```
❓ Question: Why did you choose this approach over X?
```

### Comment Tone
✅ **Good**: "This function could benefit from error handling for null inputs."
❌ **Bad**: "This is wrong. You forgot error handling."

✅ **Good**: "Have you considered using a set here for O(1) lookup?"
❌ **Bad**: "Why aren't you using a set? This is inefficient."

### Approval Criteria
- ✅ **Approve**: No blocking issues, minor suggestions only
- 🔄 **Request Changes**: Blocking issues present
- 💬 **Comment**: Questions or non-blocking suggestions

## ML-Specific Review Points

### Model Changes
- [ ] Model versioning updated
- [ ] Backward compatibility maintained
- [ ] Migration path documented

### Data Processing
- [ ] Input validation present
- [ ] Data privacy maintained
- [ ] Reproducibility ensured

### Metrics
- [ ] Appropriate metrics tracked
- [ ] Logging comprehensive
- [ ] Monitoring alerts updated

### Performance
- [ ] Inference latency acceptable
- [ ] Memory usage reasonable
- [ ] Batching optimized
EOF

git add docs/CODE_REVIEW_GUIDE.md
git commit -m "docs: add code review guidelines"
```

---

## Part 5: Advanced Collaboration

### Task 5.1: Handle Multiple Contributors

Manage conflicts with concurrent PRs.

**Instructions:**

```bash
# Scenario: Another developer merged their PR while you were working

# Update your main
git switch main
git fetch upstream
git merge upstream/main

# Rebase your feature branch
git switch feature/add-model-metrics
git rebase main

# If conflicts occur, resolve them
# git rebase --continue

# Force push (since history changed)
# git push --force-with-lease origin feature/add-model-metrics
```

---

### Task 5.2: Split Large PRs

Break down a large feature into smaller PRs.

**Instructions:**

```bash
# Instead of one large PR, create a series:

# PR 1: Foundation
git switch -c feature/metrics-foundation
# Add base metrics class
git commit -m "feat: add base metrics infrastructure"

# PR 2: Accuracy tracking (depends on PR 1)
git switch -c feature/metrics-accuracy
# Add accuracy calculations
git commit -m "feat: add accuracy tracking to metrics"

# PR 3: Dashboard integration (depends on PR 2)
git switch -c feature/metrics-dashboard
# Add dashboard
git commit -m "feat: integrate metrics with dashboard"

# Each PR is smaller, easier to review, and can be merged independently
```

---

## Validation

### Verify Your Workflow

```bash
# Check all remotes configured
git remote -v

# View all branches
git branch -a

# Check for pending changes
git status

# View recent PR-related commits
git log --oneline -10
```

---

## Challenge Tasks

### Challenge 1: Set Up Branch Protection

Configure branch protection rules (on GitHub):
- Require PR reviews
- Require status checks to pass
- Enforce linear history
- Require signed commits

### Challenge 2: Automate PR Checks

Create GitHub Actions workflow for PR validation:

```yaml
# .github/workflows/pr-checks.yml
name: PR Checks

on: [pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: pytest tests/
      - name: Lint
        run: flake8 src/
      - name: Type check
        run: mypy src/
```

---

## Troubleshooting

**Issue**: "PR has conflicts"
```bash
git fetch upstream
git rebase upstream/main
# Resolve conflicts
git rebase --continue
git push --force-with-lease
```

**Issue**: "Accidentally pushed to main"
```bash
# Revert on GitHub
# Or contact maintainer to remove commit
```

---

## Reflection Questions

1. **Why fork instead of branching directly?**
2. **What makes a good PR description?**
3. **How do you provide constructive code review feedback?**
4. **When should you split a PR into smaller PRs?**
5. **How do you handle disagreements in code review?**

---

## Summary

Congratulations! You've mastered Git collaboration:

- ✅ Forking and cloning repositories
- ✅ Creating professional pull requests
- ✅ Conducting effective code reviews
- ✅ Addressing review feedback
- ✅ Collaboration best practices
- ✅ Managing concurrent development
- ✅ PR templates and guidelines

### Key Commands

```bash
git remote add upstream <url>  # Add upstream remote
git fetch upstream             # Fetch upstream changes
git rebase upstream/main       # Rebase on upstream
gh pr create                   # Create PR (GitHub CLI)
gh pr checkout <number>        # Checkout PR locally
gh pr review                   # Review PR
git push --force-with-lease    # Safe force push
```

### Next Steps

- Exercise 06: ML-specific Git workflows
- Practice collaboration in team projects

**Excellent work!** You're ready for professional team collaboration.
