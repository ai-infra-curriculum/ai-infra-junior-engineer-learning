# Exercise 04: Merging and Conflict Resolution

## Overview

**Difficulty**: Intermediate
**Estimated Time**: 90-120 minutes
**Prerequisites**: Exercise 03 - Branching, Lecture 02 - Branching and Merging

In this exercise, you'll learn how to merge feature branches, handle merge conflicts, and resolve conflicts in ML project files including code, configuration, and data files. You'll practice different merge strategies and learn when to use each approach.

## Learning Objectives

By completing this exercise, you will:

- Perform fast-forward merges
- Execute three-way merges
- Identify and resolve merge conflicts
- Handle conflicts in Python code, YAML configs, and documentation
- Use merge tools effectively
- Understand merge strategies (merge, squash, rebase)
- Abort and retry merges
- Handle complex multi-file conflicts
- Prevent common merge mistakes

## Scenario

Your team has been developing multiple features in parallel. Now it's time to integrate them back into the main branch. Some features will merge cleanly, while others will have conflicts that need manual resolution. You'll need to carefully merge changes while maintaining code quality and functionality.

Features to merge:
- Batch inference (developed in Exercise 03)
- Model caching
- Enhanced health checks
- Bug fixes from hotfix branch

## Prerequisites

```bash
# Continue from Exercise 03 repository
cd ml-inference-api

# Ensure you have branches from Exercise 03
git branch

# Should show:
# - main
# - feature/batch-inference
# - feature/model-caching
# - feature/health-check-enhancements
# - hotfix/fix-timeout
```

---

## Part 1: Fast-Forward Merges

### Task 1.1: Understanding Fast-Forward

Merge a simple, non-conflicting branch.

**Instructions:**

```bash
# Switch to main
git switch main

# View current commit
git log --oneline -1

# View health check branch
git log --oneline feature/health-check-enhancements

# Merge health check feature (fast-forward)
git merge feature/health-check-enhancements

# View result
git log --oneline --graph -5
```

**Expected Output:**
```
Updating abc123..def456
Fast-forward
 docs/api.md             | 8 ++++++++
 src/api/health.py       | 45 +++++++++++++++++++++++++++++++++++++++++++
 tests/unit/test_health.py | 20 +++++++++++++++++++
 3 files changed, 73 insertions(+)
```

**Checkpoint:**
- What does "Fast-forward" mean?
- Why was this merge simple?

---

### Task 1.2: No Fast-Forward Merge

Force a merge commit even when fast-forward is possible.

**Instructions:**

```bash
# Create a simple branch
git switch -c feature/add-version-info

# Add version info
cat > src/version.py << 'EOF'
"""Version information."""

__version__ = "0.2.0"
__api_version__ = "v1"

def get_version_info():
    """Get version information."""
    return {
        "version": __version__,
        "api_version": __api_version__
    }
EOF

git add src/version.py
git commit -m "feat: add version information module"

# Switch back and merge with --no-ff
git switch main
git merge --no-ff feature/add-version-info -m "Merge feature: version information

Adds version tracking module for API versioning."

# View the graph - notice the merge commit
git log --oneline --graph -5
```

**Why use --no-ff?**
- Preserves branch history
- Shows when features were integrated
- Useful for code review tracking

---

## Part 2: Three-Way Merges

### Task 2.1: Basic Three-Way Merge

Merge branches that have diverged.

**Instructions:**

```bash
# Both main and feature/batch-inference have new commits
# This requires a three-way merge

# View the divergence
git log --oneline --graph --all -10

# Merge batch inference feature
git merge feature/batch-inference

# Git opens editor for merge commit message
# Default message is fine, or customize:
# "Merge feature: batch inference
#
# Integrates batch prediction capability:
# - Process multiple images in single request
# - Configurable batch size (max 32)
# - Concurrent preprocessing
# - Batch validation"

# View the merge commit
git log --oneline --graph -8
git show HEAD
```

**Expected Result:**
A merge commit with two parents (three-way merge).

---

## Part 3: Resolving Merge Conflicts

### Task 3.1: Create and Resolve a Simple Conflict

Intentionally create a conflict to practice resolution.

**Instructions:**

```bash
# Create two branches that modify the same file

# Branch 1: Update default config
git switch main
git switch -c feature/config-update-1

cat >> configs/default.yaml << 'EOF'

# Feature Toggle
features:
  batch_inference: true
  caching: false
  metrics_export: true
EOF

git add configs/default.yaml
git commit -m "feat: add feature toggles to config"

# Branch 2: Also update config (conflicting change)
git switch main
git switch -c feature/config-update-2

cat >> configs/default.yaml << 'EOF'

# Performance Settings
performance:
  max_workers: 4
  timeout_seconds: 30
  enable_profiling: false
EOF

git add configs/default.yaml
git commit -m "feat: add performance settings to config"

# Merge first branch
git switch main
git merge feature/config-update-1 --no-edit

# Try to merge second branch - CONFLICT!
git merge feature/config-update-2
```

**Expected Output:**
```
Auto-merging configs/default.yaml
CONFLICT (content): Merge conflict in configs/default.yaml
Automatic merge failed; fix conflicts and then commit the result.
```

**Resolution:**

```bash
# Check status
git status

# View the conflict
cat configs/default.yaml

# You'll see conflict markers:
# <<<<<<< HEAD
# (your changes)
# =======
# (their changes)
# >>>>>>> feature/config-update-2

# Edit the file to resolve
# Remove conflict markers and keep both sections:

cat > configs/default.yaml << 'EOF'
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
  device: "cpu"
  batch_size: 32

preprocessing:
  image_size: [224, 224]
  normalize_mean: [0.485, 0.456, 0.406]
  normalize_std: [0.229, 0.224, 0.225]

api:
  max_upload_size: 10485760
  allowed_extensions:
    - jpg
    - jpeg
    - png
  rate_limit: 100

logging:
  level: "INFO"
  format: "json"
  output: "stdout"

monitoring:
  enable_metrics: true
  metrics_port: 9090

# Rate Limiting
rate_limiting:
  enabled: true
  requests_per_minute: 100
  burst_size: 20
  strategy: "sliding_window"

# Request Timeout
timeout:
  request_timeout_seconds: 30
  inference_timeout_seconds: 10

# Prediction Cache
cache:
  enabled: true
  max_size: 1000
  ttl_seconds: 3600

# Feature Toggles
features:
  batch_inference: true
  caching: false
  metrics_export: true

# Performance Settings
performance:
  max_workers: 4
  timeout_seconds: 30
  enable_profiling: false
EOF

# Stage the resolved file
git add configs/default.yaml

# Check status - should show "all conflicts fixed"
git status

# Complete the merge
git commit -m "Merge feature: config updates

Resolved conflicts by integrating both feature toggles
and performance settings into default configuration."

# Verify
git log --oneline --graph -5
```

---

### Task 3.2: Resolve Python Code Conflict

Handle conflicts in source code.

**Instructions:**

```bash
# Create conflicting changes to the API

# Branch 1: Add request validation
git switch main
git switch -c feature/request-validation

# Modify app.py
cat > src/api/app.py << 'EOF'
"""ML Inference API - Main Application"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import structlog

from src.models.classifier import ImageClassifier
from src.preprocessing.image import preprocess_image, validate_image

logger = structlog.get_logger()

app = FastAPI(
    title="ML Inference API",
    description="REST API for image classification",
    version="0.2.0"
)

classifier = None

@app.on_event("startup")
async def startup_event():
    global classifier
    logger.info("Loading model...")
    classifier = ImageClassifier()
    await classifier.load_model()
    logger.info("Model loaded successfully")

@app.get("/")
async def root():
    return {
        "name": "ML Inference API",
        "version": "0.2.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    if classifier is None or not classifier.is_loaded():
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {
        "status": "healthy",
        "model_loaded": True
    }

@app.post("/predict")
async def predict(file: UploadFile = File(...)) -> JSONResponse:
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Read file
    image_bytes = await file.read()

    # Validate image
    if not validate_image(image_bytes):
        raise HTTPException(status_code=400, detail="Invalid image file")

    try:
        processed_image = await preprocess_image(image_bytes)
        predictions = await classifier.predict(processed_image)

        logger.info("Prediction made", filename=file.filename)

        return JSONResponse(content={
            "success": True,
            "predictions": predictions
        })
    except Exception as e:
        logger.error("Prediction failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
EOF

git add src/api/app.py
git commit -m "feat: add image validation to predict endpoint"

# Branch 2: Add metrics tracking
git switch main
git switch -c feature/metrics-tracking

cat > src/api/app.py << 'EOF'
"""ML Inference API - Main Application"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import structlog
import time

from src.models.classifier import ImageClassifier
from src.preprocessing.image import preprocess_image
from src.utils.monitoring import monitor

logger = structlog.get_logger()

app = FastAPI(
    title="ML Inference API",
    description="REST API for image classification",
    version="0.2.0"
)

classifier = None

@app.on_event("startup")
async def startup_event():
    global classifier
    logger.info("Loading model...")
    classifier = ImageClassifier()
    await classifier.load_model()
    logger.info("Model loaded successfully")

@app.get("/")
async def root():
    return {
        "name": "ML Inference API",
        "version": "0.2.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    if classifier is None or not classifier.is_loaded():
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {
        "status": "healthy",
        "model_loaded": True
    }

@app.post("/predict")
async def predict(file: UploadFile = File(...)) -> JSONResponse:
    # Track request
    monitor.metrics.record_request("/predict")
    start_time = time.time()

    # Validate file type
    if not file.content_type.startswith("image/"):
        monitor.metrics.record_error("InvalidFileType")
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        image_bytes = await file.read()
        processed_image = await preprocess_image(image_bytes)
        predictions = await classifier.predict(processed_image)

        # Record inference time
        inference_time = time.time() - start_time
        monitor.metrics.record_inference(inference_time)

        logger.info("Prediction made", filename=file.filename, duration=inference_time)

        return JSONResponse(content={
            "success": True,
            "predictions": predictions
        })
    except Exception as e:
        monitor.metrics.record_error(type(e).__name__)
        logger.error("Prediction failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
EOF

git add src/api/app.py
git commit -m "feat: add metrics tracking to predict endpoint"

# Merge first feature
git switch main
git merge feature/request-validation --no-edit

# Merge second - CONFLICT!
git merge feature/metrics-tracking
```

**Resolve the conflict:**

```bash
# View conflict
git diff

# The predict function has conflicts
# Need to combine both changes: validation AND metrics

# Edit src/api/app.py to include BOTH features:

cat > src/api/app.py << 'EOF'
"""ML Inference API - Main Application"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import structlog
import time

from src.models.classifier import ImageClassifier
from src.preprocessing.image import preprocess_image, validate_image
from src.utils.monitoring import monitor

logger = structlog.get_logger()

app = FastAPI(
    title="ML Inference API",
    description="REST API for image classification",
    version="0.2.0"
)

classifier = None

@app.on_event("startup")
async def startup_event():
    global classifier
    logger.info("Loading model...")
    classifier = ImageClassifier()
    await classifier.load_model()
    logger.info("Model loaded successfully")

@app.get("/")
async def root():
    return {
        "name": "ML Inference API",
        "version": "0.2.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    if classifier is None or not classifier.is_loaded():
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {
        "status": "healthy",
        "model_loaded": True
    }

@app.post("/predict")
async def predict(file: UploadFile = File(...)) -> JSONResponse:
    # Track request (from metrics-tracking branch)
    monitor.metrics.record_request("/predict")
    start_time = time.time()

    # Validate file type
    if not file.content_type.startswith("image/"):
        monitor.metrics.record_error("InvalidFileType")
        raise HTTPException(status_code=400, detail="File must be an image")

    # Read file
    image_bytes = await file.read()

    # Validate image (from request-validation branch)
    if not validate_image(image_bytes):
        monitor.metrics.record_error("InvalidImage")
        raise HTTPException(status_code=400, detail="Invalid image file")

    try:
        processed_image = await preprocess_image(image_bytes)
        predictions = await classifier.predict(processed_image)

        # Record inference time (from metrics-tracking branch)
        inference_time = time.time() - start_time
        monitor.metrics.record_inference(inference_time)

        logger.info("Prediction made", filename=file.filename, duration=inference_time)

        return JSONResponse(content={
            "success": True,
            "predictions": predictions
        })
    except Exception as e:
        monitor.metrics.record_error(type(e).__name__)
        logger.error("Prediction failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
EOF

# Stage and commit
git add src/api/app.py
git commit -m "Merge feature: metrics tracking

Combined metrics tracking with image validation.
Both features now work together:
- Validate images before processing
- Track all requests and errors
- Record inference timing"

# Verify
git log --oneline --graph -6
```

---

### Task 3.3: Resolve Multi-File Conflict

Handle conflicts across multiple files.

**Instructions:**

```bash
# Try to merge model caching feature
git merge feature/model-caching

# This might conflict if app.py was modified

# Check which files have conflicts
git status

# Resolve each conflict
# Then:
git add <resolved-files>
git commit -m "Merge feature: model caching

Integrated prediction caching with existing features."
```

---

## Part 4: Merge Strategies

### Task 4.1: Squash Merge

Combine all commits from a feature branch into one.

**Instructions:**

```bash
# Create a feature with multiple small commits
git switch -c feature/logging-improvements

echo "improvement 1" >> src/utils/logging.py
git add src/utils/logging.py
git commit -m "logging: add timestamp format"

echo "improvement 2" >> src/utils/logging.py
git add src/utils/logging.py
git commit -m "logging: add log rotation"

echo "improvement 3" >> src/utils/logging.py
git add src/utils/logging.py
git commit -m "logging: add structured fields"

# View commits
git log --oneline -3

# Switch and squash merge
git switch main
git merge --squash feature/logging-improvements

# All changes staged, but not committed yet
git status

# Commit as single commit
git commit -m "feat: improve logging system

Consolidated improvements:
- Timestamp formatting
- Log rotation
- Structured field support"

# Note: Only ONE commit on main, not three
git log --oneline -3
```

**When to use squash:**
- Feature has many WIP commits
- Want clean history on main
- Individual commits not important

---

### Task 4.2: Abort a Merge

Learn to cancel a problematic merge.

**Instructions:**

```bash
# Start a merge that creates conflicts
git switch -c feature/conflicting-change

# Make conflicting change
cat > src/api/app.py << 'EOF'
# Completely different implementation
print("This will conflict!")
EOF

git add src/api/app.py
git commit -m "Conflicting change"

git switch main
git merge feature/conflicting-change

# Lots of conflicts!
git status

# Decide to abort and try later
git merge --abort

# Back to pre-merge state
git status
git diff  # No changes
```

---

## Part 5: Advanced Conflict Resolution

### Task 5.1: Use Merge Tools

Configure and use merge tools.

**Instructions:**

```bash
# Configure merge tool (optional)
git config merge.tool vimdiff
# Or: meld, kdiff3, vscode, etc.

# When you have a conflict:
# git mergetool

# This opens a visual diff tool
# Make changes, save, exit

# Verify resolution
# git add <file>
# git commit
```

---

### Task 5.2: Choose One Side

Keep one version entirely.

**Instructions:**

```bash
# During a conflict, choose one side:

# Keep "ours" (current branch)
git checkout --ours path/to/file
git add path/to/file

# Or keep "theirs" (merging branch)
git checkout --theirs path/to/file
git add path/to/file

# Then commit
git commit
```

---

## Part 6: Preventing Merge Issues

### Task 6.1: Pre-Merge Checks

Validate before merging.

**Instructions:**

```bash
# Before merging:

# 1. Update main
git switch main
git pull  # (if working with remote)

# 2. Check for conflicts without merging
git merge --no-commit --no-ff feature/branch-name

# Review changes
git status
git diff --cached

# If good, commit
git commit

# If not, abort
git merge --abort
```

---

### Task 6.2: Test After Merge

Create a merge validation script.

**Instructions:**

```bash
cat > scripts/post-merge-check.sh << 'EOF'
#!/bin/bash
# Post-merge validation

echo "Running post-merge checks..."

# Check syntax
echo "1. Checking Python syntax..."
python -m py_compile src/**/*.py

# Run tests
echo "2. Running tests..."
pytest tests/ -v

# Check for conflict markers
echo "3. Checking for unresolved conflicts..."
if grep -r "<<<<<<< HEAD" src/; then
    echo "ERROR: Unresolved conflict markers found!"
    exit 1
fi

echo "All checks passed!"
EOF

chmod +x scripts/post-merge-check.sh

# Run after each merge
./scripts/post-merge-check.sh
```

---

## Validation

### Verify Your Merges

```bash
# View merge history
git log --oneline --graph --all

# Check for unresolved conflicts
git status

# Verify all features are integrated
ls src/api/
ls src/utils/

# Run tests
# pytest tests/

# Check commit history
git log --merges --oneline
```

---

## Challenge Tasks

### Challenge 1: Three-Way Merge with Conflicts

Create and resolve a complex three-way merge with multiple conflicting files.

### Challenge 2: Cherry-Pick Commits

Use `git cherry-pick` to selectively apply commits:

```bash
# Pick specific commit from another branch
git log feature/some-branch --oneline
git cherry-pick <commit-hash>
```

### Challenge 3: Merge Strategy Comparison

Compare different merge strategies and document when to use each.

---

## Troubleshooting

**Issue**: "Cannot merge, uncommitted changes"
```bash
git stash
git merge <branch>
git stash pop
```

**Issue**: "Merge created unexpected results"
```bash
# Undo the merge
git reset --hard HEAD~1
```

**Issue**: "Lost track of what I'm merging"
```bash
git status  # Shows merge in progress
cat .git/MERGE_HEAD  # Shows branch being merged
```

---

## Reflection Questions

1. **What's the difference between fast-forward and three-way merge?**
2. **When should you use `--squash` vs. regular merge?**
3. **How do you identify the cause of a merge conflict?**
4. **What's the safest way to handle a complex conflict?**
5. **Why validate after merging?**

---

## Summary

Congratulations! You've mastered merging and conflict resolution:

- ✅ Fast-forward merges
- ✅ Three-way merges
- ✅ Conflict resolution in code and configs
- ✅ Merge strategies (squash, no-ff)
- ✅ Aborting problematic merges
- ✅ Using merge tools
- ✅ Pre and post-merge validation

### Key Commands

```bash
git merge <branch>           # Merge branch
git merge --no-ff <branch>   # Force merge commit
git merge --squash <branch>  # Squash commits
git merge --abort            # Cancel merge
git checkout --ours <file>   # Keep our version
git checkout --theirs <file> # Keep their version
git mergetool                # Open merge tool
git log --merges             # Show merge commits
```

### Next Steps

- Exercise 05: Collaboration workflows
- Practice merging in team projects

**Excellent work!** You can now confidently merge and resolve conflicts.
