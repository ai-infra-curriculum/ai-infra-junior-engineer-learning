# Exercise 03: Branching for Feature Development

## Overview

**Difficulty**: Beginner to Intermediate
**Estimated Time**: 75-90 minutes
**Prerequisites**: Exercise 02 - Working with Commits and History, Lecture 02 - Branching and Merging

In this exercise, you'll learn how to effectively use Git branches for parallel feature development in ML projects. You'll practice creating branches, switching contexts, managing multiple features simultaneously, and cleaning up old branches.

## Learning Objectives

By completing this exercise, you will:

- Create and switch between feature branches
- Understand branch naming conventions
- Work on multiple features in parallel
- Use branches to isolate experimental work
- View and compare branches
- Delete merged and unmerged branches
- Apply branching strategies for ML projects
- Navigate between branches without losing work
- Use `git switch` and `git checkout` effectively

## Scenario

Your ML inference API is evolving. The team is working on multiple features simultaneously:
- Adding batch inference support
- Implementing model caching for faster predictions
- Adding Prometheus metrics export
- Experimenting with ONNX model support

Each feature needs to be developed in isolation to allow independent testing and deployment. You'll use Git branches to manage this parallel development.

## Prerequisites

Before starting, ensure you have:

```bash
# Repository from previous exercises
cd ml-inference-api

# Clean working directory
git status
# Should show: "nothing to commit, working tree clean"

# If you need a clean repo, commit or stash changes
git add .
git commit -m "wip: save current work"
```

---

## Part 1: Creating and Switching Branches

### Task 1.1: Understanding Branches

View your current branch structure.

**Instructions:**

```bash
# View current branch
git branch

# View all branches (including remote)
git branch -a

# View branches with last commit
git branch -v

# See where HEAD is pointing
cat .git/HEAD

# View commit that current branch points to
git log --oneline -1
```

**Expected Output:**
```
* main
```

The `*` indicates your current branch.

---

### Task 1.2: Create Your First Feature Branch

Create a branch for batch inference support.

**Instructions:**

```bash
# Create branch for batch inference feature
git branch feature/batch-inference

# List branches
git branch

# Notice: you created the branch but didn't switch to it
# HEAD is still on main

# Switch to the new branch
git switch feature/batch-inference

# Alternative (older syntax, still works):
# git checkout feature/batch-inference

# Verify you're on the new branch
git branch
git status

# Create and switch in one command (shortcut)
git switch -c feature/model-caching

# Alternative:
# git checkout -b feature/model-caching

# View branches with commit info
git branch -v
```

**Expected Output:**
```
* feature/model-caching
  feature/batch-inference
  main
```

---

### Task 1.3: Branch Naming Conventions

Learn and apply common branch naming patterns.

**Instructions:**

```bash
# Switch back to main
git switch main

# Create branches following conventions:

# Feature branches
git branch feature/prometheus-metrics
git branch feature/onnx-support

# Bug fix branches
git branch fix/memory-leak-preprocessing
git branch fix/timeout-handling

# Hotfix branches (urgent production fixes)
git branch hotfix/api-crash-on-large-images

# Experimental branches
git branch experiment/quantization
git branch experiment/tensorrt

# View all branches
git branch

# View in tree format
git log --oneline --graph --all --decorate
```

**Branch Naming Conventions:**

| Prefix | Use Case | Example |
|--------|----------|---------|
| `feature/` | New features | `feature/batch-inference` |
| `fix/` | Bug fixes | `fix/memory-leak` |
| `hotfix/` | Urgent production fixes | `hotfix/security-patch` |
| `experiment/` | Experimental work | `experiment/new-model` |
| `refactor/` | Code refactoring | `refactor/api-structure` |
| `docs/` | Documentation | `docs/api-guide` |
| `test/` | Testing improvements | `test/integration-tests` |

---

## Part 2: Working on Feature Branches

### Task 2.1: Implement Batch Inference Feature

Develop the batch inference feature on its branch.

**Instructions:**

```bash
# Switch to batch inference branch
git switch feature/batch-inference

# Verify you're on the right branch
git branch

# Create batch inference module
cat > src/api/batch.py << 'EOF'
"""
Batch Inference Module

Handles batch prediction requests for efficiency.
"""

from typing import List, Dict
from fastapi import UploadFile
import asyncio
import structlog

from src.models.classifier import ImageClassifier
from src.preprocessing.image import preprocess_image

logger = structlog.get_logger()


class BatchInferenceService:
    """Service for processing multiple images in batch."""

    def __init__(self, classifier: ImageClassifier, max_batch_size: int = 32):
        """
        Initialize batch inference service.

        Args:
            classifier: Image classifier instance
            max_batch_size: Maximum images per batch
        """
        self.classifier = classifier
        self.max_batch_size = max_batch_size
        logger.info("Batch inference service initialized", max_batch=max_batch_size)

    async def process_batch(self, files: List[UploadFile]) -> List[Dict]:
        """
        Process multiple images in batch.

        Args:
            files: List of uploaded image files

        Returns:
            List of prediction results
        """
        if len(files) > self.max_batch_size:
            raise ValueError(f"Batch size {len(files)} exceeds max {self.max_batch_size}")

        logger.info("Processing batch", num_images=len(files))

        # Preprocess all images concurrently
        preprocess_tasks = [
            preprocess_image(await f.read()) for f in files
        ]
        preprocessed_images = await asyncio.gather(*preprocess_tasks)

        # Run batch inference
        results = []
        for idx, image_tensor in enumerate(preprocessed_images):
            predictions = await self.classifier.predict(image_tensor)
            results.append({
                "file_index": idx,
                "filename": files[idx].filename,
                "predictions": predictions
            })

        logger.info("Batch processing complete", num_images=len(results))
        return results
EOF

# Commit the module
git add src/api/batch.py
git commit -m "feat(batch): add batch inference service

Implement BatchInferenceService for processing multiple images:
- Concurrent image preprocessing
- Configurable max batch size (default 32)
- Returns predictions for all images in batch

This improves throughput for bulk classification tasks."

# Add batch endpoint to API
cat > src/api/routes/batch.py << 'EOF'
"""
Batch Inference Routes

API endpoints for batch prediction.
"""

from typing import List
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from src.api.batch import BatchInferenceService
from src.models.classifier import ImageClassifier

router = APIRouter()

# Initialize batch service (will be properly injected later)
classifier = ImageClassifier()
batch_service = BatchInferenceService(classifier, max_batch_size=32)


@router.post("/batch/predict")
async def batch_predict(files: List[UploadFile] = File(...)) -> JSONResponse:
    """
    Predict classifications for multiple images.

    Args:
        files: List of image files (max 32)

    Returns:
        JSON response with predictions for all images
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    if len(files) > 32:
        raise HTTPException(
            status_code=400,
            detail=f"Too many files. Maximum batch size is 32, got {len(files)}"
        )

    try:
        results = await batch_service.process_batch(files)
        return JSONResponse(content={
            "success": True,
            "batch_size": len(files),
            "results": results
        })
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Batch prediction failed: {str(e)}"
        )
EOF

# Create directory and commit
mkdir -p src/api/routes
git add src/api/routes/batch.py
git commit -m "feat(batch): add batch prediction endpoint

Add POST /batch/predict endpoint:
- Accepts up to 32 images per request
- Returns predictions for all images
- Validates batch size
- Error handling for batch failures

Example usage:
  POST /batch/predict
  files: [image1.jpg, image2.jpg, ...]"

# Add tests
cat > tests/unit/test_batch.py << 'EOF'
"""Tests for batch inference."""

import pytest
from src.api.batch import BatchInferenceService
from src.models.classifier import ImageClassifier


@pytest.fixture
def batch_service():
    """Create batch service for testing."""
    classifier = ImageClassifier()
    return BatchInferenceService(classifier, max_batch_size=5)


def test_batch_service_initialization(batch_service):
    """Test batch service initializes correctly."""
    assert batch_service.max_batch_size == 5
    assert batch_service.classifier is not None


def test_batch_size_validation(batch_service):
    """Test batch size validation."""
    # This would need actual UploadFile objects
    # Placeholder for proper test implementation
    assert batch_service.max_batch_size == 5
EOF

git add tests/unit/test_batch.py
git commit -m "test(batch): add batch inference tests

Add unit tests for batch service initialization and validation."

# View your work on this branch
git log --oneline
```

**Checkpoint:**
- How many commits are on this branch?
- Are these commits on the `main` branch?

---

### Task 2.2: Implement Model Caching Feature

Switch to another feature branch and develop in parallel.

**Instructions:**

```bash
# Switch to model caching branch
git switch feature/model-caching

# Notice: the batch inference files are gone!
ls src/api/batch.py  # File not found

# This is expected - you're on a different branch
# View branch status
git log --oneline -3

# Now implement caching
cat > src/utils/cache.py << 'EOF'
"""
Model Caching Module

Implements LRU cache for model predictions.
"""

from functools import lru_cache
from typing import Optional, Tuple
import hashlib
import pickle
import structlog
from datetime import datetime, timedelta

logger = structlog.get_logger()


class PredictionCache:
    """Cache for model predictions with TTL."""

    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        """
        Initialize prediction cache.

        Args:
            max_size: Maximum number of cached predictions
            ttl_seconds: Time to live for cache entries
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache = {}
        self.timestamps = {}
        logger.info("Cache initialized", max_size=max_size, ttl=ttl_seconds)

    def _generate_key(self, image_bytes: bytes) -> str:
        """
        Generate cache key from image bytes.

        Args:
            image_bytes: Raw image bytes

        Returns:
            SHA256 hash as cache key
        """
        return hashlib.sha256(image_bytes).hexdigest()

    def get(self, image_bytes: bytes) -> Optional[dict]:
        """
        Get cached prediction.

        Args:
            image_bytes: Raw image bytes

        Returns:
            Cached prediction or None if not found/expired
        """
        key = self._generate_key(image_bytes)

        if key not in self.cache:
            logger.debug("Cache miss", key=key[:16])
            return None

        # Check TTL
        timestamp = self.timestamps.get(key)
        if timestamp:
            age = (datetime.now() - timestamp).total_seconds()
            if age > self.ttl_seconds:
                logger.debug("Cache entry expired", key=key[:16], age=age)
                self._remove(key)
                return None

        logger.debug("Cache hit", key=key[:16])
        return self.cache[key]

    def set(self, image_bytes: bytes, prediction: dict):
        """
        Cache prediction.

        Args:
            image_bytes: Raw image bytes
            prediction: Prediction result to cache
        """
        key = self._generate_key(image_bytes)

        # Evict oldest if at max size
        if len(self.cache) >= self.max_size:
            self._evict_oldest()

        self.cache[key] = prediction
        self.timestamps[key] = datetime.now()
        logger.debug("Cached prediction", key=key[:16])

    def _remove(self, key: str):
        """Remove key from cache."""
        self.cache.pop(key, None)
        self.timestamps.pop(key, None)

    def _evict_oldest(self):
        """Evict oldest cache entry."""
        if not self.timestamps:
            return

        oldest_key = min(self.timestamps, key=self.timestamps.get)
        logger.debug("Evicting oldest entry", key=oldest_key[:16])
        self._remove(oldest_key)

    def clear(self):
        """Clear all cache entries."""
        self.cache.clear()
        self.timestamps.clear()
        logger.info("Cache cleared")

    def stats(self) -> dict:
        """Get cache statistics."""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "ttl_seconds": self.ttl_seconds
        }


# Global cache instance
prediction_cache = PredictionCache()
EOF

git add src/utils/cache.py
git commit -m "feat(cache): implement prediction caching with TTL

Add PredictionCache for caching model predictions:
- LRU eviction policy
- Configurable TTL (default 1 hour)
- SHA256-based cache keys
- Cache statistics

Benefits:
- Reduces redundant inference
- Improves response time for duplicate requests
- Configurable cache size (default 1000 entries)"

# Update configuration
cat >> configs/default.yaml << 'EOF'

# Prediction Cache
cache:
  enabled: true
  max_size: 1000
  ttl_seconds: 3600
EOF

git add configs/default.yaml
git commit -m "config: add cache configuration settings"

# View this branch's history
git log --oneline
```

**Checkpoint:**
Run `git log --oneline --all --graph` to see both branches!

---

### Task 2.3: Quick Bug Fix on Main

Practice switching branches for urgent fixes.

**Instructions:**

```bash
# You're on feature/model-caching
# Urgent bug reported on main!

# Switch back to main
git switch main

# Verify your feature work is safely stored
ls src/utils/cache.py  # File not found (it's on the other branch)

# Create hotfix branch from main
git switch -c hotfix/fix-timeout

# Fix the issue
cat > src/api/middleware.py << 'EOF'
"""
API Middleware

Custom middleware for request processing.
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import time
import structlog
import asyncio

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


async def timeout_middleware(request: Request, call_next):
    """Enforce request timeout."""
    try:
        # 30 second timeout for all requests
        response = await asyncio.wait_for(
            call_next(request),
            timeout=30.0
        )
        return response
    except asyncio.TimeoutError:
        logger.error(
            "Request timeout",
            method=request.method,
            path=request.url.path
        )
        return JSONResponse(
            status_code=504,
            content={"error": "Request timeout"}
        )
EOF

git add src/api/middleware.py
git commit -m "fix: add timeout middleware to prevent hanging requests

Add timeout_middleware to enforce 30-second timeout on all requests.
Prevents server resources from being tied up by slow clients.

Returns 504 Gateway Timeout on timeout."

# View all branches
git branch -v
```

---

## Part 3: Viewing and Comparing Branches

### Task 3.1: Compare Branches

Learn to view differences between branches.

**Instructions:**

```bash
# List all branches
git branch -a

# View commits on feature/batch-inference not in main
git log main..feature/batch-inference --oneline

# View commits on feature/model-caching not in main
git log main..feature/model-caching --oneline

# View all commits on both feature branches
git log main..feature/batch-inference main..feature/model-caching --oneline

# Compare files between branches
git diff main feature/batch-inference

# Compare specific file
git diff main feature/batch-inference -- src/api/

# Show which files differ
git diff --name-only main feature/batch-inference

# Graphical view of all branches
git log --oneline --graph --all --decorate

# More detailed graph
git log --graph --all --decorate --pretty=format:"%h %an: %s"
```

**Checkpoint Exercise:**

Answer using Git commands:

1. How many commits are on `feature/batch-inference`?
2. How many commits are on `feature/model-caching`?
3. What files are different between `main` and `feature/batch-inference`?

```bash
# Answers:
git rev-list --count main..feature/batch-inference
git rev-list --count main..feature/model-caching
git diff --name-only main feature/batch-inference
```

---

### Task 3.2: View Branch History

Visualize branch relationships.

**Instructions:**

```bash
# Graphical history
git log --oneline --graph --all

# With dates
git log --graph --all --pretty=format:"%h %ad | %s%d [%an]" --date=short

# Only show branches
git log --oneline --graph --all --simplify-by-decoration

# See where branches diverged
git merge-base main feature/batch-inference
git log --oneline $(git merge-base main feature/batch-inference)

# Show commits on feature branch since branching
git log --oneline main..feature/batch-inference
```

---

## Part 4: Managing Multiple Features

### Task 4.1: Switch Between Branches

Practice context switching.

**Instructions:**

```bash
# Work on batch inference
git switch feature/batch-inference

# Make a change
cat >> src/api/batch.py << 'EOF'


def validate_batch_size(num_files: int, max_size: int = 32) -> bool:
    """Validate batch size is within limits."""
    return 0 < num_files <= max_size
EOF

# Check status
git status

# Save work (commit it)
git add src/api/batch.py
git commit -m "feat(batch): add batch size validation helper"

# Switch to caching feature
git switch feature/model-caching

# Make a change there
cat >> src/utils/cache.py << 'EOF'


def get_cache_stats_summary():
    """Get human-readable cache statistics."""
    stats = prediction_cache.stats()
    return f"Cache: {stats['size']}/{stats['max_size']} (TTL: {stats['ttl_seconds']}s)"
EOF

git add src/utils/cache.py
git commit -m "feat(cache): add cache stats summary helper"

# View where you are
git branch

# View all branch tips
git branch -v
```

---

### Task 4.2: Create Experiment Branch

Use branches for experimental work.

**Instructions:**

```bash
# Switch to main
git switch main

# Create experiment branch
git switch -c experiment/onnx-runtime

# Add experimental ONNX support
mkdir -p src/models/onnx
cat > src/models/onnx/runtime.py << 'EOF'
"""
ONNX Runtime Integration (Experimental)

⚠️  EXPERIMENTAL - Not for production use!

Explores using ONNX Runtime for faster inference.
"""

import onnxruntime as ort
import numpy as np
from typing import List, Dict
import structlog

logger = structlog.get_logger()


class ONNXClassifier:
    """Experimental ONNX-based classifier."""

    def __init__(self, model_path: str):
        """
        Initialize ONNX classifier.

        Args:
            model_path: Path to ONNX model file
        """
        logger.warning("Loading experimental ONNX model")
        self.session = ort.InferenceSession(model_path)
        self.input_name = self.session.get_inputs()[0].name

    def predict(self, image_array: np.ndarray) -> List[Dict]:
        """
        Run inference with ONNX Runtime.

        Args:
            image_array: Preprocessed image array

        Returns:
            List of predictions
        """
        # Run inference
        outputs = self.session.run(None, {self.input_name: image_array})

        # Process outputs
        probabilities = outputs[0][0]
        top5_idx = np.argsort(probabilities)[-5:][::-1]

        predictions = []
        for idx in top5_idx:
            predictions.append({
                "class_id": int(idx),
                "confidence": float(probabilities[idx])
            })

        return predictions
EOF

git add src/models/onnx/
git commit -m "experiment: add ONNX Runtime integration

⚠️  EXPERIMENTAL BRANCH

Exploring ONNX Runtime for potential performance gains.

TODO:
- Benchmark against PyTorch
- Test accuracy parity
- Measure memory usage

DO NOT MERGE until thoroughly tested!"

# Mark as experimental in branch description
git config branch.experiment/onnx-runtime.description "Experimental ONNX Runtime support - do not merge"
```

---

## Part 5: Branch Cleanup

### Task 5.1: Delete Merged Branches

Learn to clean up completed branches.

**Instructions:**

```bash
# First, let's simulate a merged branch
git switch main

# Create a small feature
git switch -c feature/update-readme

# Make a change
cat >> README.md << 'EOF'

## Recent Updates

- Added batch inference support
- Implemented prediction caching
- Enhanced middleware with timeouts
EOF

git add README.md
git commit -m "docs: update README with recent features"

# Merge it to main (we'll learn merging in detail in Exercise 04)
git switch main
git merge feature/update-readme --no-edit

# Now the feature branch is merged
git log --oneline -3

# Try to delete the branch
git branch -d feature/update-readme

# Success! The -d flag only deletes merged branches

# List remaining branches
git branch
```

**Expected Output:**
```
Deleted branch feature/update-readme (was abc123).
```

---

### Task 5.2: Delete Unmerged Branches

Handle deletion of branches with unmerged work.

**Instructions:**

```bash
# Try to delete an unmerged feature branch
git branch -d feature/batch-inference

# Error! Branch has unmerged changes
```

**Expected Output:**
```
error: The branch 'feature/batch-inference' is not fully merged.
If you are sure you want to delete it, run 'git branch -D feature/batch-inference'.
```

```bash
# Git is protecting you from losing work!

# If you really want to delete it (CAREFUL!)
# git branch -D feature/batch-inference  # DON'T RUN THIS

# Instead, let's keep it
git branch

# View unmerged branches
git branch --no-merged

# View merged branches
git branch --merged
```

---

### Task 5.3: Rename Branches

Practice renaming branches.

**Instructions:**

```bash
# Create a poorly named branch
git switch -c feature/new-stuff

# Oops, that's a terrible name!
# Rename it while on the branch
git branch -m feature/prometheus-integration

# Verify
git branch

# You can also rename from another branch
git switch main
git branch -m feature/prometheus-integration feature/monitoring-prometheus

# Verify
git branch
```

---

## Part 6: Advanced Branch Operations

### Task 6.1: Track Remote Branches

Simulate working with remote branches.

**Instructions:**

```bash
# See all branches including remote tracking
git branch -a

# Currently you only have local branches

# Simulate what you'd see with remote:
# * main
#   feature/batch-inference
#   feature/model-caching
#   remotes/origin/main
#   remotes/origin/feature/batch-inference

# Set upstream for a branch
git switch feature/batch-inference

# When you push, you'd set upstream:
# git push -u origin feature/batch-inference

# Then you can see tracking info
git branch -vv
```

---

### Task 6.2: Stash Changes When Switching

Handle uncommitted changes when switching branches.

**Instructions:**

```bash
# Switch to a feature branch
git switch feature/model-caching

# Make changes but don't commit
echo "# TODO: Add cache warming" >> src/utils/cache.py

# Check status
git status

# Try to switch branches
git switch main

# Git might complain if changes conflict

# Solution 1: Stash changes
git stash push -m "WIP: cache warming idea"

# Now switch
git switch main

# Later, go back and restore
git switch feature/model-caching
git stash list
git stash pop

# Solution 2: Commit the work
git add src/utils/cache.py
git commit -m "wip: exploring cache warming"
```

---

## Part 7: Practical Workflow

### Task 7.1: Complete Feature Development Workflow

Practice a full feature development cycle.

**Instructions:**

```bash
# 1. Start from main
git switch main

# 2. Create feature branch
git switch -c feature/health-check-enhancements

# 3. Develop feature
cat > src/api/health.py << 'EOF'
"""
Enhanced Health Check

Provides detailed health status.
"""

from fastapi import APIRouter
from src.models.classifier import ImageClassifier
import psutil
import os

router = APIRouter()


@router.get("/health/live")
async def liveness():
    """Liveness probe - is service running?"""
    return {"status": "alive"}


@router.get("/health/ready")
async def readiness(classifier: ImageClassifier):
    """Readiness probe - is service ready for traffic?"""
    ready = classifier.is_loaded()
    status_code = 200 if ready else 503
    return {
        "status": "ready" if ready else "not ready",
        "model_loaded": ready
    }, status_code


@router.get("/health/metrics")
async def health_metrics():
    """Health metrics for monitoring."""
    process = psutil.Process(os.getpid())
    return {
        "cpu_percent": psutil.cpu_percent(),
        "memory_mb": process.memory_info().rss / 1024 / 1024,
        "disk_usage_percent": psutil.disk_usage('/').percent
    }
EOF

git add src/api/health.py
git commit -m "feat(health): add enhanced health check endpoints

Add three health endpoints:
- /health/live: Liveness probe
- /health/ready: Readiness probe with model check
- /health/metrics: System resource metrics

Compatible with Kubernetes health checks."

# 4. Add tests
cat > tests/unit/test_health.py << 'EOF'
"""Tests for health check endpoints."""

import pytest
from fastapi.testclient import TestClient
from src.api.app import app

client = TestClient(app)


def test_liveness():
    """Test liveness endpoint."""
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"


def test_readiness():
    """Test readiness endpoint."""
    response = client.get("/health/ready")
    assert response.status_code in [200, 503]
    assert "model_loaded" in response.json()
EOF

git add tests/unit/test_health.py
git commit -m "test(health): add health endpoint tests"

# 5. Update docs
cat >> docs/api.md << 'EOF'

## Health Check Endpoints

### GET /health/live
Kubernetes liveness probe.

### GET /health/ready
Kubernetes readiness probe. Returns 503 if model not loaded.

### GET /health/metrics
System resource metrics (CPU, memory, disk).
EOF

git add docs/api.md
git commit -m "docs: document health check endpoints"

# 6. View your work
git log --oneline

# Ready for code review / merge!
```

---

## Validation

### Validate Your Branch Work

Check your branch structure.

**Instructions:**

```bash
# List all branches
git branch -a

# Should have at least:
# - main
# - feature/batch-inference
# - feature/model-caching
# - feature/health-check-enhancements
# - experiment/onnx-runtime
# - hotfix/fix-timeout

# View branch graph
git log --oneline --graph --all --decorate

# Count commits per branch
for branch in $(git branch | sed 's/^..//'); do
    echo "Branch: $branch"
    git log main..$branch --oneline | wc -l
done

# Check for uncommitted changes
git status
```

**Quality Checklist:**

- [ ] All features on separate branches
- [ ] Branch names follow conventions
- [ ] No uncommitted changes
- [ ] Main branch is clean
- [ ] Experimental work isolated

---

## Challenge Tasks

### Challenge 1: Branch Cleanup Script

Create a script to clean up old branches:

```bash
# Create cleanup script
cat > scripts/cleanup-branches.sh << 'EOF'
#!/bin/bash
# Clean up merged branches

echo "Merged branches (safe to delete):"
git branch --merged main | grep -v "main"

echo ""
echo "Delete these branches? (y/n)"
read answer

if [ "$answer" = "y" ]; then
    git branch --merged main | grep -v "main" | xargs git branch -d
    echo "Cleanup complete!"
fi
EOF

chmod +x scripts/cleanup-branches.sh
```

### Challenge 2: Branch Status Report

Create a branch status report:

```bash
git switch main

cat > scripts/branch-report.sh << 'EOF'
#!/bin/bash
# Generate branch status report

echo "=== Branch Status Report ==="
echo ""
echo "Current branch: $(git branch --show-current)"
echo "Total branches: $(git branch | wc -l)"
echo ""
echo "Branches ahead of main:"
for branch in $(git branch | sed 's/^..//'); do
    if [ "$branch" != "main" ]; then
        commits=$(git log main..$branch --oneline | wc -l)
        if [ $commits -gt 0 ]; then
            echo "  $branch: $commits commits"
        fi
    fi
done
EOF

chmod +x scripts/branch-report.sh
./scripts/branch-report.sh
```

---

## Troubleshooting

**Issue**: "Cannot switch branch, uncommitted changes"
```bash
# Solution 1: Commit changes
git add .
git commit -m "wip: save work"

# Solution 2: Stash changes
git stash

# Solution 3: Force switch (loses changes!)
# git switch -f branch-name  # ⚠️ DANGEROUS
```

**Issue**: "Deleted wrong branch"
```bash
# If you just deleted it:
git reflog
git branch branch-name <commit-hash>
```

**Issue**: "Don't know which branch I'm on"
```bash
git branch  # Shows * on current
git status  # Shows "On branch X"
echo $(__git_ps1)  # If configured
```

---

## Reflection Questions

1. **Why use feature branches instead of committing to main?**
2. **When should you create a branch vs. committing to main?**
3. **What's the purpose of experiment branches?**
4. **How do branches help with code review?**
5. **What's the difference between `-d` and `-D` when deleting branches?**
6. **How do you handle switching branches with uncommitted work?**

---

## Summary

Congratulations! You've completed Exercise 03. You learned:

- ✅ Creating and switching between branches
- ✅ Branch naming conventions
- ✅ Parallel feature development
- ✅ Comparing and visualizing branches
- ✅ Managing multiple features simultaneously
- ✅ Deleting merged and unmerged branches
- ✅ Handling uncommitted changes when switching
- ✅ Complete feature development workflow

### Key Commands

```bash
git branch                    # List branches
git branch <name>             # Create branch
git switch <name>             # Switch branch
git switch -c <name>          # Create and switch
git branch -d <name>          # Delete merged branch
git branch -D <name>          # Force delete branch
git branch -m <new-name>      # Rename branch
git branch -v                 # List with commits
git log --graph --all         # Visualize branches
git diff branch1 branch2      # Compare branches
git stash                     # Save uncommitted work
```

### Next Steps

- Complete Exercise 04 to learn merging and conflict resolution
- Practice branching in your projects
- Review Lecture 02 on branching strategies

**Excellent work!** You now know how to manage parallel development with Git branches.
