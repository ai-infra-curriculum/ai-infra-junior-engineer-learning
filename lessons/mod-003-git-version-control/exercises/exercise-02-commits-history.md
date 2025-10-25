# Exercise 02: Working with Commits and History

## Overview

**Difficulty**: Beginner
**Estimated Time**: 75-90 minutes
**Prerequisites**: Exercise 01 - Creating Your First Repository, Lecture 01 - Git Fundamentals

In this exercise, you'll learn advanced commit techniques and how to effectively work with Git history. You'll practice making effective commits, viewing and searching history, amending commits, and reverting changes in a realistic ML project scenario.

## Learning Objectives

By completing this exercise, you will:

- Create atomic, well-documented commits following best practices
- Write professional commit messages using conventional formats
- Navigate commit history using various `git log` options
- Search commit history for specific changes
- Amend commits to fix mistakes
- Revert changes safely without losing history
- Use `git show` to inspect specific commits
- Understand when and how to modify commits
- Apply Git best practices for ML infrastructure projects

## Scenario

You're continuing work on the ML inference API from Exercise 01. Your team has established commit message conventions and code review practices. You need to implement new features, fix bugs, and maintain a clean, searchable Git history that helps your team understand the evolution of the codebase.

Today's tasks:
- Add model performance monitoring
- Fix a bug in image preprocessing
- Implement request rate limiting
- Add comprehensive logging
- Document API endpoints

## Prerequisites

Before starting, ensure you have:

```bash
# Git repository from Exercise 01
cd ml-inference-api

# Verify you're in the right place
git status
git log --oneline

# Should show clean working tree and previous commits
```

If you don't have the repository from Exercise 01, create a new one:

```bash
mkdir ml-inference-api
cd ml-inference-api
git init
git config init.defaultBranch main
# Follow Exercise 01 to create basic structure
```

---

## Part 1: Writing Effective Commit Messages

### Task 1.1: Implement Feature with Conventional Commits

Add a performance monitoring module following conventional commit format.

**Instructions:**

Create the monitoring module:

```bash
# Create monitoring file
cat > src/utils/monitoring.py << 'EOF'
"""
Performance Monitoring Module

Tracks model inference performance metrics.
"""

import time
from typing import Dict, List
from dataclasses import dataclass, field
from collections import defaultdict
import structlog

logger = structlog.get_logger()


@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""

    inference_times: List[float] = field(default_factory=list)
    request_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    error_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))

    def record_inference(self, duration: float):
        """Record inference duration."""
        self.inference_times.append(duration)

    def record_request(self, endpoint: str):
        """Record API request."""
        self.request_counts[endpoint] += 1

    def record_error(self, error_type: str):
        """Record error occurrence."""
        self.error_counts[error_type] += 1

    def get_average_inference_time(self) -> float:
        """Calculate average inference time."""
        if not self.inference_times:
            return 0.0
        return sum(self.inference_times) / len(self.inference_times)

    def get_p95_inference_time(self) -> float:
        """Calculate 95th percentile inference time."""
        if not self.inference_times:
            return 0.0
        sorted_times = sorted(self.inference_times)
        idx = int(len(sorted_times) * 0.95)
        return sorted_times[idx]

    def get_metrics_summary(self) -> Dict:
        """Get summary of all metrics."""
        return {
            "average_inference_ms": self.get_average_inference_time() * 1000,
            "p95_inference_ms": self.get_p95_inference_time() * 1000,
            "total_requests": sum(self.request_counts.values()),
            "total_errors": sum(self.error_counts.values()),
            "requests_by_endpoint": dict(self.request_counts),
            "errors_by_type": dict(self.error_counts)
        }


class PerformanceMonitor:
    """Monitor and track performance metrics."""

    def __init__(self):
        """Initialize performance monitor."""
        self.metrics = PerformanceMetrics()
        self.start_time = time.time()

    def track_inference(self, func):
        """Decorator to track inference performance."""
        async def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start
                self.metrics.record_inference(duration)
                logger.info("Inference completed", duration_ms=duration * 1000)
                return result
            except Exception as e:
                self.metrics.record_error(type(e).__name__)
                raise
        return wrapper

    def get_uptime(self) -> float:
        """Get service uptime in seconds."""
        return time.time() - self.start_time

    def reset_metrics(self):
        """Reset all metrics."""
        self.metrics = PerformanceMetrics()
        logger.info("Metrics reset")


# Global monitor instance
monitor = PerformanceMonitor()
EOF
```

Now commit using conventional commit format:

```bash
# Stage the file
git add src/utils/monitoring.py

# Commit with conventional format
git commit -m "feat: add performance monitoring for inference tracking

Implement PerformanceMetrics and PerformanceMonitor classes to track:
- Inference latency (average and p95)
- Request counts per endpoint
- Error counts by type
- Service uptime

This enables real-time monitoring and helps identify performance
bottlenecks in the ML inference pipeline.

The monitor uses a decorator pattern for easy integration with
existing inference functions."
```

**Checkpoint Questions:**
- What does "feat:" indicate in the commit message?
- Why include both what changed and why in the message?
- How does this help when reviewing history?

---

### Task 1.2: Fix a Bug with Proper Documentation

Find and fix a bug in the preprocessing module.

**Instructions:**

First, create the bug:

```bash
# Modify preprocessing to have a bug
cat > src/preprocessing/image.py << 'EOF'
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

    # BUG: Not converting to RGB - causes issues with grayscale/RGBA images

    # Apply preprocessing
    transform = get_preprocessing_transform()
    image_tensor = transform(image)

    # Add batch dimension
    image_tensor = image_tensor.unsqueeze(0)

    return image_tensor


def validate_image(image_bytes: bytes, max_size_mb: int = 10) -> bool:
    """
    Validate that bytes represent a valid image.

    Args:
        image_bytes: Raw bytes
        max_size_mb: Maximum allowed file size in MB

    Returns:
        True if valid image, False otherwise
    """
    # Check file size
    size_mb = len(image_bytes) / (1024 * 1024)
    if size_mb > max_size_mb:
        return False

    try:
        image = Image.open(io.BytesIO(image_bytes))
        # Verify it's a valid image by loading
        image.verify()
        return True
    except Exception:
        return False
EOF

# Commit the buggy version
git add src/preprocessing/image.py
git commit -m "refactor: improve image validation

Add file size checking to image validation function"
```

Now fix the bug:

```bash
# Fix the bug
cat > src/preprocessing/image.py << 'EOF'
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

    # Convert to RGB if needed (handles grayscale and RGBA)
    if image.mode != "RGB":
        image = image.convert("RGB")

    # Apply preprocessing
    transform = get_preprocessing_transform()
    image_tensor = transform(image)

    # Add batch dimension
    image_tensor = image_tensor.unsqueeze(0)

    return image_tensor


def validate_image(image_bytes: bytes, max_size_mb: int = 10) -> bool:
    """
    Validate that bytes represent a valid image.

    Args:
        image_bytes: Raw bytes
        max_size_mb: Maximum allowed file size in MB

    Returns:
        True if valid image, False otherwise
    """
    # Check file size
    size_mb = len(image_bytes) / (1024 * 1024)
    if size_mb > max_size_mb:
        return False

    try:
        image = Image.open(io.BytesIO(image_bytes))
        # Verify it's a valid image by loading
        image.verify()
        return True
    except Exception:
        return False
EOF

# Commit the fix with proper documentation
git add src/preprocessing/image.py
git commit -m "fix: convert images to RGB before preprocessing

The preprocessing pipeline now converts all images to RGB mode
before applying transformations. This fixes inference failures
when processing:
- Grayscale images (mode 'L')
- RGBA images with alpha channel
- Other non-RGB image formats

Without this conversion, the model receives incorrect tensor
dimensions causing inference to fail.

Fixes issue where grayscale medical images caused 500 errors."
```

**Expected Output:**
```
[main abc123] fix: convert images to RGB before preprocessing
 1 file changed, 4 insertions(+), 1 deletion(-)
```

**Checkpoint:**
View your commit history:
```bash
git log --oneline -3
```

---

### Task 1.3: Add Configuration Feature

Add rate limiting configuration.

**Instructions:**

```bash
# Update configuration
cat >> configs/default.yaml << 'EOF'

# Rate Limiting
rate_limiting:
  enabled: true
  requests_per_minute: 100
  burst_size: 20
  strategy: "sliding_window"  # Options: fixed_window, sliding_window

# Request Timeout
timeout:
  request_timeout_seconds: 30
  inference_timeout_seconds: 10
EOF

# Create rate limiter implementation
cat > src/utils/rate_limiter.py << 'EOF'
"""
Rate Limiting Module

Implements request rate limiting for API endpoints.
"""

import time
from collections import deque
from typing import Optional
import structlog

logger = structlog.get_logger()


class RateLimiter:
    """Token bucket rate limiter."""

    def __init__(
        self,
        requests_per_minute: int = 100,
        burst_size: int = 20
    ):
        """
        Initialize rate limiter.

        Args:
            requests_per_minute: Maximum requests allowed per minute
            burst_size: Maximum burst capacity
        """
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.tokens = burst_size
        self.last_update = time.time()
        self.requests = deque()

        logger.info(
            "Rate limiter initialized",
            rpm=requests_per_minute,
            burst=burst_size
        )

    def _refill_tokens(self):
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_update

        # Add tokens based on time elapsed
        tokens_to_add = elapsed * (self.requests_per_minute / 60.0)
        self.tokens = min(self.burst_size, self.tokens + tokens_to_add)
        self.last_update = now

    def allow_request(self) -> bool:
        """
        Check if request is allowed.

        Returns:
            True if request allowed, False if rate limited
        """
        self._refill_tokens()

        if self.tokens >= 1:
            self.tokens -= 1
            self.requests.append(time.time())
            logger.debug("Request allowed", tokens_remaining=self.tokens)
            return True

        logger.warning("Request rate limited", tokens_remaining=self.tokens)
        return False

    def get_wait_time(self) -> float:
        """
        Get time to wait before next request allowed.

        Returns:
            Seconds to wait, or 0 if request would be allowed
        """
        self._refill_tokens()

        if self.tokens >= 1:
            return 0.0

        # Calculate time needed to get 1 token
        return (1.0 - self.tokens) / (self.requests_per_minute / 60.0)

    def reset(self):
        """Reset rate limiter state."""
        self.tokens = self.burst_size
        self.last_update = time.time()
        self.requests.clear()
        logger.info("Rate limiter reset")
EOF

# Stage both files
git add configs/default.yaml src/utils/rate_limiter.py

# Commit with proper scope
git commit -m "feat(api): implement request rate limiting

Add token bucket rate limiter to prevent API abuse:

Configuration:
- Configurable requests per minute limit
- Burst capacity for traffic spikes
- Sliding window strategy

Implementation:
- Token bucket algorithm
- Automatic token refill
- Wait time calculation
- Request tracking

Default settings: 100 requests/min with burst of 20.

This protects the service from abuse while allowing legitimate
traffic spikes."
```

---

## Part 2: Viewing and Searching History

### Task 2.1: Explore Commit History

Learn different ways to view your Git history.

**Instructions:**

```bash
# Basic log
git log

# Compact one-line format
git log --oneline

# Last 5 commits
git log --oneline -5

# With file statistics
git log --stat

# With actual changes
git log -p

# With specific number of commits
git log -p -2

# Graphical representation (useful with branches)
git log --oneline --graph --all

# Pretty format with author and date
git log --pretty=format:"%h - %an, %ar : %s"

# Commits in last 24 hours
git log --since="24 hours ago"

# Commits by specific author
git log --author="Your Name"

# Commits affecting specific file
git log -- src/utils/monitoring.py

# Commits with specific word in message
git log --grep="fix"

# See what changed in each commit
git log --oneline --stat
```

**Checkpoint Exercise:**

Answer these using `git log`:

1. How many commits have you made?
2. What was your most recent commit message?
3. Which files did your third commit modify?
4. How many commits modified `configs/default.yaml`?

---

### Task 2.2: Search for Specific Changes

Practice searching commit history for content.

**Instructions:**

```bash
# Find commits that added/removed "RateLimiter"
git log -S "RateLimiter"

# Find commits with "RateLimiter" in diff (more specific)
git log -G "RateLimiter"

# Show the actual changes
git log -S "RateLimiter" -p

# Find when a function was added
git log -S "def preprocess_image" --source --all

# Search for changes in specific file
git log -p -- src/preprocessing/image.py

# Show commits that changed a specific line range
git log -L 30,50:src/utils/monitoring.py
```

**Practical Exercise:**

Use Git to answer:

1. When was the `PerformanceMonitor` class added?
2. Which commit fixed the RGB conversion bug?
3. What changes were made to `default.yaml`?

```bash
# Example answer for #1:
git log -S "class PerformanceMonitor" --oneline

# Example for #2:
git log --grep="RGB" --oneline

# Example for #3:
git log --oneline -- configs/default.yaml
git show <commit-hash>
```

---

### Task 2.3: Inspect Specific Commits

Use `git show` to examine commits in detail.

**Instructions:**

```bash
# Show latest commit
git show

# Show specific commit
git show HEAD~1  # Previous commit
git show HEAD~2  # Two commits ago

# Show commit by hash
git log --oneline -5  # Get hash
git show abc123  # Replace with actual hash

# Show only the commit message and stats
git show --stat HEAD

# Show specific file in a commit
git show HEAD:src/utils/monitoring.py

# Show file from previous commit
git show HEAD~1:configs/default.yaml

# Compare file between commits
git diff HEAD~1 HEAD -- src/preprocessing/image.py
```

**Checkpoint:**

Practice these commands:

```bash
# What files changed in the rate limiting commit?
git log --grep="rate limiting" --oneline
git show <hash> --stat

# What was the exact change to preprocessing?
git log -- src/preprocessing/image.py --oneline
git show <hash>
```

---

## Part 3: Amending Commits

### Task 3.1: Fix Commit Message

Practice amending the last commit message.

**Instructions:**

```bash
# First, make a commit with a typo
echo "# API Documentation" > docs/api.md
git add docs/api.md
git commit -m "doc: add API documentaton"  # Note the typo

# Oops! Fix the commit message
git commit --amend -m "docs: add API documentation

Create initial API documentation file for endpoint reference."

# View the corrected commit
git log --oneline -1
```

**Important Notes:**
- `--amend` rewrites the last commit
- Only amend commits that haven't been pushed!
- Amending changes the commit hash

---

### Task 3.2: Add Forgotten Files

Practice adding files to the last commit.

**Instructions:**

```bash
# Add endpoint documentation
cat > docs/api.md << 'EOF'
# ML Inference API Documentation

## Endpoints

### POST /predict
Upload image for classification.

**Request:**
```
POST /predict
Content-Type: multipart/form-data

file: <image-file>
```

**Response:**
```json
{
  "success": true,
  "predictions": [
    {
      "class_id": 281,
      "class": "tabby_cat",
      "confidence": 0.94
    }
  ]
}
```

### GET /health
Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

### GET /models
List available models.

**Response:**
```json
{
  "current_model": "resnet50",
  "version": "1.0.0"
}
```
EOF

# Commit it
git add docs/api.md
git commit -m "docs: add API endpoint documentation"

# Oops! Forgot to add the README update
cat >> README.md << 'EOF'

## API Documentation

See [API Documentation](docs/api.md) for detailed endpoint information.
EOF

# Add the forgotten file to the last commit
git add README.md
git commit --amend --no-edit

# The --no-edit flag keeps the same commit message
# View the amended commit
git show --stat
```

**Checkpoint:**
- What files are in the last commit now?
- What happens to the commit hash when you amend?

---

### Task 3.3: Amend with Message and Files

Practice amending both message and content.

**Instructions:**

```bash
# Create incomplete implementation
cat > src/api/middleware.py << 'EOF'
"""
API Middleware

Custom middleware for request processing.
"""

from fastapi import Request
import time

async def logging_middleware(request: Request, call_next):
    """Log all requests."""
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    print(f"{request.method} {request.url.path} - {duration:.3f}s")
    return response
EOF

git add src/api/middleware.py
git commit -m "feat: add middleware"

# Realize we should add rate limiting and improve message
cat > src/api/middleware.py << 'EOF'
"""
API Middleware

Custom middleware for request processing.
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import time
import structlog

from src.utils.rate_limiter import RateLimiter

logger = structlog.get_logger()
rate_limiter = RateLimiter()


async def logging_middleware(request: Request, call_next):
    """Log all requests with timing."""
    start_time = time.time()

    logger.info(
        "Request started",
        method=request.method,
        path=request.url.path,
        client=request.client.host
    )

    response = await call_next(request)
    duration = time.time() - start_time

    logger.info(
        "Request completed",
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        duration_ms=duration * 1000
    )

    return response


async def rate_limit_middleware(request: Request, call_next):
    """Apply rate limiting to requests."""
    if not rate_limiter.allow_request():
        wait_time = rate_limiter.get_wait_time()
        logger.warning(
            "Rate limit exceeded",
            client=request.client.host,
            wait_time=wait_time
        )
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "retry_after": wait_time
            }
        )

    return await call_next(request)
EOF

# Amend with better message and updated file
git add src/api/middleware.py
git commit --amend -m "feat(api): add request logging and rate limiting middleware

Implement two middleware components:

1. Logging Middleware:
   - Logs all incoming requests
   - Tracks request duration
   - Uses structured logging

2. Rate Limiting Middleware:
   - Enforces rate limits per client
   - Returns 429 status when limited
   - Includes retry-after in response

These middleware protect the API and provide observability."

# View the result
git show
```

---

## Part 4: Reverting Changes

### Task 4.1: Revert a Commit

Learn to safely undo commits.

**Instructions:**

```bash
# First, make a bad change
cat > src/utils/cache.py << 'EOF'
"""
Caching Module - EXPERIMENTAL

WARNING: This implementation has issues!
"""

cache = {}  # Global cache - not thread-safe!

def get_from_cache(key):
    return cache.get(key)

def add_to_cache(key, value):
    cache[key] = value
EOF

git add src/utils/cache.py
git commit -m "feat: add caching module"

# Check history
git log --oneline -3

# Oops, this cache implementation is broken!
# Revert the commit (creates a new commit that undoes changes)
git revert HEAD

# Git will open an editor with a default message like:
# "Revert "feat: add caching module""
#
# You can modify it to be more descriptive:
git revert HEAD --no-commit  # Let's try again with no-commit

# Actually, let's do it properly:
git revert --abort  # Cancel the above
git revert HEAD     # Revert with editor

# In the editor, change message to:
# Revert "feat: add caching module"
#
# The cache implementation has thread-safety issues.
# Will reimplement using proper locking mechanisms.

# Check the result
git log --oneline -4
git show HEAD
```

**Important:** `git revert` creates a NEW commit that undoes changes. It doesn't delete history!

---

### Task 4.2: Revert Multiple Commits

Practice reverting a range of commits.

**Instructions:**

```bash
# Make several bad commits
echo "config1" > bad_config1.txt
git add bad_config1.txt
git commit -m "bad commit 1"

echo "config2" > bad_config2.txt
git add bad_config2.txt
git commit -m "bad commit 2"

echo "config3" > bad_config3.txt
git add bad_config3.txt
git commit -m "bad commit 3"

# Check history
git log --oneline -6

# Revert all three (in reverse order)
git revert HEAD HEAD~1 HEAD~2 --no-edit

# Check result
git log --oneline -9
ls *.txt  # Files should be gone
```

---

### Task 4.3: Revert vs Reset (Understanding the Difference)

**Instructions:**

```bash
# DEMONSTRATION ONLY - DO NOT RUN ON IMPORTANT CODE

# Show current state
git log --oneline

# git reset moves the branch pointer (DESTRUCTIVE!)
# git reset --hard HEAD~1  # ⚠️ DELETES last commit and changes!

# git revert creates new commit (SAFE!)
# git revert HEAD  # ✅ Keeps history, undoes changes

# Let's demonstrate reset in a safe way
# Create a test branch
git branch test-branch
git checkout test-branch

# Make a commit
echo "test" > test.txt
git add test.txt
git commit -m "test commit"

# Reset it (only on test branch)
git reset --hard HEAD~1

# test.txt is gone, commit is gone
ls test.txt  # File not found

# Go back to main
git checkout main

# The test branch commit is gone, but main is safe
```

**Key Differences:**

| Command | Effect | History | Use When |
|---------|--------|---------|----------|
| `git revert` | New commit that undoes changes | Preserved | Changes are pushed/shared |
| `git reset` | Moves branch pointer | Rewritten | Changes are local only |

**Rule:** Use `revert` for published commits, `reset` only for local commits!

---

## Part 5: Practical Workflow Exercise

### Task 5.1: Complete Feature Development Workflow

Implement a complete feature following best practices.

**Instructions:**

```bash
# 1. Add metrics endpoint
cat > src/api/metrics.py << 'EOF'
"""
Metrics Endpoint

Exposes performance metrics for monitoring.
"""

from fastapi import APIRouter
from src.utils.monitoring import monitor

router = APIRouter()


@router.get("/metrics")
async def get_metrics():
    """
    Get performance metrics.

    Returns:
        Dictionary of current metrics
    """
    metrics = monitor.metrics.get_metrics_summary()
    metrics["uptime_seconds"] = monitor.get_uptime()
    return metrics


@router.post("/metrics/reset")
async def reset_metrics():
    """Reset all metrics (admin only)."""
    monitor.reset_metrics()
    return {"status": "metrics reset"}
EOF

git add src/api/metrics.py
git commit -m "feat(api): add metrics endpoint for monitoring

Expose /metrics endpoint to retrieve:
- Average inference time
- P95 inference latency
- Request counts by endpoint
- Error counts by type
- Service uptime

Includes /metrics/reset for admin use.

This enables integration with Prometheus and Grafana
for infrastructure monitoring."

# 2. Realize we need to add this to main app
cat >> src/api/app.py << 'EOF'

# Import metrics router
from src.api.metrics import router as metrics_router

# Include metrics routes
app.include_router(metrics_router, tags=["monitoring"])
EOF

git add src/api/app.py
git commit -m "feat(api): register metrics router in main application

Include metrics endpoints in FastAPI app routing."

# 3. Add tests
cat > tests/unit/test_metrics.py << 'EOF'
"""Tests for metrics endpoint."""

import pytest
from fastapi.testclient import TestClient
from src.api.app import app

client = TestClient(app)


def test_metrics_endpoint():
    """Test metrics endpoint returns data."""
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "uptime_seconds" in data
    assert "average_inference_ms" in data


def test_metrics_reset():
    """Test metrics can be reset."""
    response = client.post("/metrics/reset")
    assert response.status_code == 200
    assert response.json()["status"] == "metrics reset"
EOF

git add tests/unit/test_metrics.py
git commit -m "test: add unit tests for metrics endpoint

Test metrics retrieval and reset functionality."

# 4. Update documentation
cat >> docs/api.md << 'EOF'

### GET /metrics
Get current performance metrics.

**Response:**
```json
{
  "average_inference_ms": 45.2,
  "p95_inference_ms": 78.5,
  "total_requests": 1523,
  "total_errors": 3,
  "uptime_seconds": 86400
}
```

### POST /metrics/reset
Reset all metrics (admin only).

**Response:**
```json
{
  "status": "metrics reset"
}
```
EOF

git add docs/api.md
git commit -m "docs: document metrics endpoints

Add documentation for metrics retrieval and reset endpoints."

# 5. View your work
git log --oneline -10
git log --graph --oneline --all
```

---

## Validation and Review

### Task 6.1: Audit Your Commit History

Review the quality of your commits.

**Instructions:**

```bash
# View all commit messages
git log --oneline

# Check commit message quality
git log --pretty=format:"%s" | head -10

# Find commits without conventional format
git log --pretty=format:"%s" --grep="^feat:" --grep="^fix:" --grep="^docs:" --all-match --invert-grep

# View commits with statistics
git log --stat --oneline -10

# Check for large commits (should be atomic)
git log --shortstat | grep -E "files? changed"
```

**Quality Checklist:**

- [ ] Commits follow conventional format (feat:, fix:, docs:, etc.)
- [ ] Commit messages explain WHY, not just WHAT
- [ ] Commits are atomic (one logical change each)
- [ ] No "WIP" or "fix typo" commits (should be amended)
- [ ] No secrets or large files committed

---

## Challenge Tasks (Optional)

### Challenge 1: Interactive Rebase Preview

Learn about interactive rebase (covered more in Exercise 07):

```bash
# View what interactive rebase looks like
git rebase -i HEAD~5 --dry-run

# Don't actually run it yet - just see the interface
# This shows how you can reorder, squash, or edit commits
```

### Challenge 2: Bisect to Find a Bug

Use `git bisect` to find when a bug was introduced:

```bash
# We'll simulate this
# git bisect start
# git bisect bad                 # Current version is bad
# git bisect good HEAD~10        # 10 commits ago was good
# Git will checkout middle commit
# Test it, then:
# git bisect good   # or bad
# Repeat until git finds the problematic commit
# git bisect reset  # when done
```

### Challenge 3: Create a Release Tag

Tag an important commit:

```bash
# Tag current commit as a release
git tag -a v0.1.0 -m "Release version 0.1.0

Features:
- ML inference API
- Performance monitoring
- Rate limiting
- Comprehensive logging

This is the first stable release."

# View tags
git tag -l

# View tag details
git show v0.1.0
```

---

## Troubleshooting

### Common Issues

**Issue**: "Cannot amend because commit was pushed"
```bash
# Solution: Don't amend pushed commits!
# Instead, create a new commit with the fix
```

**Issue**: "Accidentally amended wrong commit"
```bash
# Solution: Use reflog to find the original commit
git reflog
git reset --hard HEAD@{1}  # Go back one step
```

**Issue**: "Revert created conflicts"
```bash
# Solution: Resolve conflicts manually
git status  # See conflicted files
# Edit files to resolve conflicts
git add <resolved-files>
git revert --continue
```

**Issue**: "Can't find a specific commit"
```bash
# Solution: Use more search options
git log --all --grep="search-term"
git log --all -S "code-snippet"
git reflog  # Shows all HEAD movements
```

---

## Reflection Questions

1. **Why use conventional commit format (feat:, fix:, docs:)?**
   - How does this help with automation and changelog generation?

2. **When should you amend a commit vs. creating a new one?**
   - What are the risks of amending?

3. **What's the difference between `git revert` and `git reset`?**
   - When would you use each?

4. **Why is atomic commit practice important?**
   - Give an example from this exercise.

5. **How does good commit history help in debugging?**
   - How would you use `git log` to find when a bug was introduced?

6. **What information should be in a commit message body?**
   - Why not just rely on the subject line?

---

## Summary

Congratulations! You've completed Exercise 02. You learned:

- ✅ Writing effective commit messages with conventional format
- ✅ Navigating Git history with various `git log` options
- ✅ Searching commit history for specific changes
- ✅ Inspecting commits with `git show`
- ✅ Amending commits to fix messages or add files
- ✅ Reverting commits safely without losing history
- ✅ Understanding revert vs. reset
- ✅ Following a complete feature development workflow
- ✅ Auditing commit history for quality

### Key Commands Learned

```bash
git commit -m "message"           # Create commit
git commit --amend                # Amend last commit
git log                           # View history
git log --oneline                 # Compact history
git log --stat                    # With file stats
git log -p                        # With changes
git log --grep="term"             # Search messages
git log -S "code"                 # Search for code
git show <commit>                 # Show commit details
git revert <commit>               # Safely undo commit
git reset                         # Move branch (careful!)
git tag                           # Create tags
```

### Next Steps

- Complete Exercise 03 to learn branching strategies
- Practice conventional commits in your projects
- Review Lecture 02 on branching and merging

**Excellent work!** You now have the skills to maintain a clean, professional Git history.
