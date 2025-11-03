# Exercise 02: Building Custom Docker Images

## Exercise Overview

**Objective**: Master the art of creating custom Docker images using Dockerfiles, including optimization techniques and best practices for ML applications.

**Difficulty**: Beginner to Intermediate
**Estimated Time**: 3-4 hours
**Prerequisites**:
- Exercise 01 (Container Operations)
- Lecture 02 (Dockerfiles & Image Building)

## Learning Objectives

By completing this exercise, you will:
- Write production-ready Dockerfiles from scratch
- Implement multi-stage builds to reduce image size by 80%+
- Apply layer caching strategies to accelerate build times
- Containerize Python and ML applications with proper dependencies
- Tag and version Docker images using semantic versioning
- Push images to public and private Docker registries
- Implement security best practices (non-root users, minimal base images)
- Debug common Dockerfile build issues using inspection tools
- Optimize ML model serving containers for CPU/GPU deployments
- Create .dockerignore files to minimize build context

---

## Part 1: Your First Dockerfile

### Step 1.1: Simple Python Application

```bash
# Create project directory
mkdir -p ~/docker-exercises/python-app
cd ~/docker-exercises/python-app

# Create simple Python app
cat > app.py << 'EOF'
#!/usr/bin/env python3
"""
Simple Flask web application for Docker exercise
"""
from flask import Flask, jsonify
import os
import socket

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        'message': 'Hello from Docker!',
        'hostname': socket.gethostname(),
        'environment': os.environ.get('ENV', 'development')
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
EOF

# Create requirements
cat > requirements.txt << 'EOF'
flask==3.0.0
gunicorn==21.2.0
EOF
```

### Step 1.2: Write Your First Dockerfile

```dockerfile
# Create Dockerfile
cat > Dockerfile << 'EOF'
# Use official Python runtime as base
FROM python:3.11

# Set working directory
WORKDIR /app

# Copy requirements first (layer caching!)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Expose port
EXPOSE 5000

# Run application
CMD ["python", "app.py"]
EOF
```

### Step 1.3: Build and Run

```bash
# Build image
docker build -t my-python-app:v1 .

# What happened?
# 1. Downloaded Python 3.11 base image
# 2. Created working directory
# 3. Installed dependencies
# 4. Copied application code
# 5. Tagged image as my-python-app:v1

# Check image
docker images | grep my-python-app

# Run container
docker run -d -p 5000:5000 --name pyapp my-python-app:v1

# Test it
curl http://localhost:5000
curl http://localhost:5000/health

# Check logs
docker logs pyapp
```

**Questions**:
1. How large is your image? (`docker images my-python-app:v1`)
2. What happens if you change `app.py` and rebuild?
3. Which layers are cached?

✅ **Checkpoint**: You can build and run a custom Python application in Docker.

---

## Part 2: Optimizing Images

### Step 2.1: Use Smaller Base Image

```dockerfile
# Create optimized Dockerfile
cat > Dockerfile.slim << 'EOF'
# Use slim variant (much smaller!)
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 5000

CMD ["python", "app.py"]
EOF
```

```bash
# Build with slim base
docker build -f Dockerfile.slim -t my-python-app:v2-slim .

# Compare sizes
docker images | grep my-python-app

# Output should show significant size difference:
# my-python-app  v1       <timestamp>  1.02GB
# my-python-app  v2-slim  <timestamp>  182MB
```

### Step 2.2: Multi-Stage Build

```dockerfile
# Create multi-stage Dockerfile
cat > Dockerfile.multistage << 'EOF'
# Stage 1: Builder
FROM python:3.11 AS builder

WORKDIR /app

# Install dependencies to a local directory
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Copy only the installed packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application
COPY app.py .

# Make sure scripts are in PATH
ENV PATH=/root/.local/bin:$PATH

EXPOSE 5000

CMD ["python", "app.py"]
EOF
```

```bash
# Build multi-stage
docker build -f Dockerfile.multistage -t my-python-app:v3-multi .

# Compare all versions
docker images | grep my-python-app

# Run and verify it works
docker run -d -p 5001:5000 --name pyapp-multi my-python-app:v3-multi
curl http://localhost:5001
```

### Step 2.3: Layer Caching Optimization

```dockerfile
# Create cache-optimized Dockerfile
cat > Dockerfile.optimized << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Copy and install dependencies FIRST
# This layer will be cached unless requirements change
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code LAST
# This changes frequently but won't invalidate dependency cache
COPY app.py .

EXPOSE 5000

CMD ["python", "app.py"]
EOF
```

```bash
# First build
time docker build -f Dockerfile.optimized -t my-python-app:v4 .

# Make a change to app.py
echo "# Comment added" >> app.py

# Rebuild - notice how fast it is!
time docker build -f Dockerfile.optimized -t my-python-app:v4 .

# Dependencies were cached!
```

**Challenge**: Modify `requirements.txt` and rebuild. What happens to build time?

✅ **Checkpoint**: You can optimize images using slim bases and multi-stage builds.

---

## Part 3: ML Application Image

### Step 3.1: Simple Model Serving App

```bash
# Create ML app directory
mkdir -p ~/docker-exercises/ml-app
cd ~/docker-exercises/ml-app

# Create model serving application
cat > serve.py << 'EOF'
"""
Simple ML model serving with Flask
"""
from flask import Flask, request, jsonify
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import io

app = Flask(__name__)

# Load model
print("Loading model...")
model = models.resnet18(pretrained=True)
model.eval()
print("Model loaded successfully!")

# Image preprocessing
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'model': 'resnet18'})

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    img_bytes = file.read()
    img = Image.open(io.BytesIO(img_bytes))

    # Preprocess and predict
    img_tensor = transform(img).unsqueeze(0)

    with torch.no_grad():
        output = model(img_tensor)
        probabilities = torch.nn.functional.softmax(output[0], dim=0)
        top5_prob, top5_catid = torch.topk(probabilities, 5)

    results = []
    for i in range(5):
        results.append({
            'class_id': top5_catid[i].item(),
            'probability': top5_prob[i].item()
        })

    return jsonify({'predictions': results})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
EOF

# Create requirements for ML app
cat > requirements.txt << 'EOF'
flask==3.0.0
torch==2.1.0
torchvision==0.16.0
pillow==10.1.0
gunicorn==21.2.0
EOF
```

### Step 3.2: ML Application Dockerfile

```dockerfile
cat > Dockerfile << 'EOF'
# Multi-stage build for ML application
FROM python:3.11 AS builder

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

# Install system dependencies for PyTorch
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed packages
COPY --from=builder /root/.local /root/.local

# Copy application
COPY serve.py .

# Update PATH
ENV PATH=/root/.local/bin:$PATH

EXPOSE 8000

# Use gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120", "serve:app"]
EOF
```

```bash
# Build ML image (this will take a few minutes)
docker build -t ml-serve:v1 .

# Check size
docker images ml-serve:v1

# Run ML server
docker run -d -p 8000:8000 --name ml-server ml-serve:v1

# Wait for model to load
sleep 10

# Check health
curl http://localhost:8000/health

# Test prediction (you'd need an image file)
# curl -X POST -F "file=@test_image.jpg" http://localhost:8000/predict
```

### Step 3.3: Optimize ML Image Size

```dockerfile
# Create optimized ML Dockerfile
cat > Dockerfile.optimized << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install CPU-only PyTorch (much smaller!)
COPY requirements.txt .
RUN pip install --no-cache-dir \
    flask==3.0.0 \
    pillow==10.1.0 \
    gunicorn==21.2.0 \
    torch==2.1.0+cpu \
    torchvision==0.16.0+cpu \
    --index-url https://download.pytorch.org/whl/cpu

COPY serve.py .

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120", "serve:app"]
EOF
```

```bash
# Build optimized version
docker build -f Dockerfile.optimized -t ml-serve:v2-cpu .

# Compare sizes
docker images | grep ml-serve

# The CPU version should be significantly smaller!
```

✅ **Checkpoint**: You can containerize ML applications with optimized images.

---

## Part 4: Dockerfile Instructions Deep Dive

### Step 4.1: Understanding Layers

```dockerfile
# Create example with many layers
cat > Dockerfile.layers << 'EOF'
FROM python:3.11-slim

# Each RUN creates a new layer
RUN apt-get update
RUN apt-get install -y curl
RUN apt-get install -y wget
RUN apt-get install -y vim

# Better: Combine commands
# RUN apt-get update && \
#     apt-get install -y curl wget vim && \
#     rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY app.py .

CMD ["python", "app.py"]
EOF
```

```bash
# Build and inspect layers
docker build -f Dockerfile.layers -t layer-demo .

# See layer history
docker history layer-demo

# Notice each RUN command creates a layer
```

### Step 4.2: COPY vs ADD

```bash
# Create test files
mkdir -p ~/docker-exercises/copy-test
cd ~/docker-exercises/copy-test

echo "Hello" > file.txt
tar czf archive.tar.gz file.txt
```

```dockerfile
cat > Dockerfile.copy << 'EOF'
FROM alpine:latest

WORKDIR /app

# COPY: Simple file copy
COPY file.txt /app/

# ADD: Can extract archives automatically
ADD archive.tar.gz /app/extracted/

CMD ["sh"]
EOF
```

```bash
# Build and check
docker build -f Dockerfile.copy -t copy-demo .

# Run and explore
docker run --rm -it copy-demo sh
# Inside container:
# ls -la /app
# ls -la /app/extracted
# exit
```

**Best Practice**: Use `COPY` unless you specifically need `ADD`'s tar extraction.

### Step 4.3: ARG and ENV

```dockerfile
cat > Dockerfile.args << 'EOF'
FROM python:3.11-slim

# Build-time variable (only during build)
ARG PYTHON_VERSION=3.11
ARG APP_ENV=development

# Runtime variable (available in container)
ENV APP_ENV=${APP_ENV}
ENV DEBUG=true

WORKDIR /app

RUN echo "Building for environment: ${APP_ENV}"
RUN echo "Python version: ${PYTHON_VERSION}"

COPY app.py .

CMD ["python", "app.py"]
EOF
```

```bash
# Build with default args
docker build -f Dockerfile.args -t arg-demo:dev .

# Build with custom args
docker build -f Dockerfile.args -t arg-demo:prod \
  --build-arg APP_ENV=production \
  --build-arg PYTHON_VERSION=3.11 .

# Run and check env vars
docker run --rm arg-demo:dev python -c "import os; print(os.environ.get('APP_ENV'))"
docker run --rm arg-demo:prod python -c "import os; print(os.environ.get('APP_ENV'))"
```

### Step 4.4: USER Instruction (Security)

```dockerfile
cat > Dockerfile.user << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install dependencies as root
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app and set ownership
COPY --chown=appuser:appuser app.py .

# Switch to non-root user
USER appuser

CMD ["python", "app.py"]
EOF
```

```bash
# Build
docker build -f Dockerfile.user -t secure-app .

# Run and check user
docker run --rm secure-app whoami
# Output: appuser (not root!)

# Verify security
docker run --rm secure-app id
# Output shows non-root UID/GID
```

✅ **Checkpoint**: You understand Dockerfile instructions and best practices.

---

## Part 5: Build Context and .dockerignore

### Step 5.1: Understanding Build Context

```bash
# Create project with many files
mkdir -p ~/docker-exercises/build-context
cd ~/docker-exercises/build-context

# Create some files
echo "print('app')" > app.py
echo "flask" > requirements.txt

# Create large unnecessary files
dd if=/dev/zero of=large_file.bin bs=1M count=100
mkdir -p data
dd if=/dev/zero of=data/dataset.bin bs=1M count=500

# Simple Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py .
CMD ["python", "app.py"]
EOF

# Build - notice it sends ALL files to daemon
docker build -t context-demo .
# Output: Sending build context to Docker daemon  614.4MB
```

### Step 5.2: Create .dockerignore

```bash
# Create .dockerignore file
cat > .dockerignore << 'EOF'
# Ignore large data files
*.bin
data/
datasets/

# Ignore git
.git/
.gitignore

# Ignore Python cache
__pycache__/
*.pyc
*.pyo
*.pyd
.Python

# Ignore virtual environments
venv/
env/
ENV/

# Ignore IDE files
.vscode/
.idea/
*.swp
*.swo

# Ignore OS files
.DS_Store
Thumbs.db

# Ignore documentation
docs/
*.md
!README.md

# Ignore tests (if not needed in image)
tests/
*.test.py
EOF

# Rebuild
docker build -t context-demo:v2 .
# Output: Sending build context to Docker daemon  3.072kB
# Much better!
```

**Challenge**: Create a Python project with tests, docs, and data. Write a `.dockerignore` that only includes production files.

✅ **Checkpoint**: You can optimize build context with .dockerignore.

---

## Part 6: Image Tagging and Versioning

### Step 6.1: Tag Strategies

```bash
# Build with multiple tags
docker build -t myapp:1.0.0 .
docker build -t myapp:1.0 .
docker build -t myapp:1 .
docker build -t myapp:latest .

# Or tag existing image
docker tag myapp:1.0.0 myapp:latest
docker tag myapp:1.0.0 myapp:stable

# Semantic versioning
docker build -t myapp:1.0.0-alpha .
docker build -t myapp:1.0.0-beta .
docker build -t myapp:1.0.0-rc1 .
docker build -t myapp:1.0.0 .

# Include git commit
GIT_COMMIT=$(git rev-parse --short HEAD)
docker build -t myapp:${GIT_COMMIT} .
docker build -t myapp:dev-${GIT_COMMIT} .
```

### Step 6.2: Best Practices for Tags

```bash
# Good tagging strategy for CI/CD
VERSION="2.1.3"
BUILD_DATE=$(date +%Y%m%d)
GIT_SHA=$(git rev-parse --short HEAD)

# Build with comprehensive tags
docker build \
  -t myapp:${VERSION} \
  -t myapp:${VERSION}-${BUILD_DATE} \
  -t myapp:${VERSION}-${GIT_SHA} \
  -t myapp:latest \
  .

# List all tags
docker images myapp
```

**Tagging Best Practices**:
1. **Always tag with specific version** (1.2.3)
2. **Use semantic versioning** (MAJOR.MINOR.PATCH)
3. **Tag latest** for most recent stable
4. **Avoid using latest in production** (pin versions!)
5. **Include build metadata** when needed

✅ **Checkpoint**: You can version and tag images properly.

---

## Part 7: Working with Registries

### Step 7.1: Docker Hub

```bash
# Login to Docker Hub
docker login

# Tag for Docker Hub (username/image:tag)
docker tag myapp:1.0.0 yourusername/myapp:1.0.0
docker tag myapp:1.0.0 yourusername/myapp:latest

# Push to Docker Hub
docker push yourusername/myapp:1.0.0
docker push yourusername/myapp:latest

# Pull from Docker Hub
docker pull yourusername/myapp:1.0.0

# Logout
docker logout
```

### Step 7.2: Private Registry (Local)

```bash
# Run local registry
docker run -d -p 5000:5000 --name registry registry:2

# Tag for local registry
docker tag myapp:1.0.0 localhost:5000/myapp:1.0.0

# Push to local registry
docker push localhost:5000/myapp:1.0.0

# Pull from local registry
docker pull localhost:5000/myapp:1.0.0

# List images in registry
curl http://localhost:5000/v2/_catalog
curl http://localhost:5000/v2/myapp/tags/list
```

### Step 7.3: Registry Authentication

```bash
# Create htpasswd file
docker run --rm \
  --entrypoint htpasswd \
  httpd:2 -Bbn testuser testpass > htpasswd

# Run registry with authentication
docker run -d -p 5001:5000 \
  --name secure-registry \
  -v $(pwd)/htpasswd:/auth/htpasswd \
  -e "REGISTRY_AUTH=htpasswd" \
  -e "REGISTRY_AUTH_HTPASSWD_REALM=Registry Realm" \
  -e "REGISTRY_AUTH_HTPASSWD_PATH=/auth/htpasswd" \
  registry:2

# Login to secure registry
docker login localhost:5001
# Username: testuser
# Password: testpass

# Push to secure registry
docker tag myapp:1.0.0 localhost:5001/myapp:1.0.0
docker push localhost:5001/myapp:1.0.0
```

✅ **Checkpoint**: You can work with Docker registries.

---

## Part 8: Debugging Build Issues

### Step 8.1: Common Build Errors

```dockerfile
# Create Dockerfile with issues
cat > Dockerfile.broken << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Issue 1: File not found
COPY nonexistent.txt .

# Issue 2: Command fails
RUN pip install fake-package-that-doesnt-exist

# Issue 3: Permission denied
COPY app.py /root/protected/

CMD ["python", "app.py"]
EOF
```

```bash
# Try to build - will fail
docker build -f Dockerfile.broken -t broken-app .

# Debug technique 1: Build up to working stage
# Comment out failing lines and build incrementally

# Debug technique 2: Check build context
ls -la

# Debug technique 3: Use --no-cache
docker build --no-cache -f Dockerfile.broken -t broken-app .
```

### Step 8.2: Interactive Debugging

```bash
# Build up to a certain point
cat > Dockerfile.debug << 'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

# Stop here for debugging
CMD ["/bin/bash"]
EOF

# Build
docker build -f Dockerfile.debug -t debug-app .

# Run interactively
docker run --rm -it debug-app bash

# Inside container, test commands:
# pwd
# ls -la
# python --version
# pip list
# exit
```

### Step 8.3: Inspect Build Layers

```bash
# Build with verbose output
docker build --progress=plain -t myapp .

# Inspect specific layer
docker history myapp

# Get detailed info
docker inspect myapp

# Find which layer added size
docker history myapp --human --no-trunc
```

**Debugging Checklist**:
- [ ] Is the file in build context?
- [ ] Check .dockerignore isn't excluding needed files
- [ ] Verify base image exists and is accessible
- [ ] Check network access for downloads
- [ ] Review file permissions
- [ ] Ensure correct syntax in Dockerfile
- [ ] Use --no-cache to avoid stale layers

✅ **Checkpoint**: You can debug Dockerfile build issues.

---

## Part 9: Advanced Patterns

### Step 9.1: Health Checks in Dockerfile

```dockerfile
cat > Dockerfile.health << 'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 5000

# Add health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:5000/health')" || exit 1

CMD ["python", "app.py"]
EOF
```

```bash
# Build and run
docker build -f Dockerfile.health -t health-app .
docker run -d -p 5000:5000 --name health-demo health-app

# Check health status
docker ps  # Shows health status
docker inspect health-demo | grep -A 10 Health
```

### Step 9.2: Build Secrets

```bash
# Create secret file (API key, password, etc.)
echo "super-secret-api-key" > api_key.txt

# Dockerfile using build secrets
cat > Dockerfile.secrets << 'EOF'
# syntax=docker/dockerfile:1.4

FROM python:3.11-slim

WORKDIR /app

# Use secret during build (not stored in image!)
RUN --mount=type=secret,id=api_key \
    API_KEY=$(cat /run/secrets/api_key) && \
    echo "Using API key: ${API_KEY:0:5}..." && \
    # Use API key for build operations
    echo "Build completed with secret"

COPY app.py .

CMD ["python", "app.py"]
EOF

# Build with secret
docker build --secret id=api_key,src=api_key.txt \
  -f Dockerfile.secrets -t secret-app .

# Secret is NOT in the image!
docker history secret-app
```

### Step 9.3: Target Stage in Multi-Stage

```dockerfile
cat > Dockerfile.targets << 'EOF'
# Base stage
FROM python:3.11-slim AS base
WORKDIR /app
COPY requirements.txt .

# Development stage
FROM base AS development
RUN pip install -r requirements.txt
RUN pip install pytest black flake8
COPY . .
CMD ["python", "app.py"]

# Testing stage
FROM development AS testing
RUN pytest tests/
CMD ["pytest"]

# Production stage
FROM base AS production
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
CMD ["gunicorn", "app:app"]
EOF
```

```bash
# Build specific stage
docker build --target development -t myapp:dev -f Dockerfile.targets .
docker build --target production -t myapp:prod -f Dockerfile.targets .
docker build --target testing -t myapp:test -f Dockerfile.targets .

# Each has different tools and configs!
docker run --rm myapp:dev python --version
docker run --rm myapp:prod gunicorn --version
```

✅ **Checkpoint**: You can use advanced Dockerfile patterns.

---

## Part 10: Production-Ready Dockerfile

### Step 10.1: Complete Production Example

```dockerfile
cat > Dockerfile.production << 'EOF'
# syntax=docker/dockerfile:1.4

# Build stage
FROM python:3.11 AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && \
    useradd -r -g appuser -u 1000 appuser

WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application with correct ownership
COPY --chown=appuser:appuser . .

# Update PATH
ENV PATH=/root/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Switch to non-root user
USER appuser

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Use production server
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "serve:app"]
EOF
```

**Production Checklist**:
- [x] Multi-stage build
- [x] Minimal base image (slim)
- [x] Non-root user
- [x] Health check
- [x] Production server (gunicorn)
- [x] Environment variables
- [x] No cache in layers
- [x] Proper signal handling
- [x] Security best practices

✅ **Checkpoint**: You can create production-ready Dockerfiles.

---

## Part 11: Practical Challenges

### Challenge 1: Optimize a Bloated Image

You're given this Dockerfile:

```dockerfile
FROM ubuntu:latest

RUN apt-get update
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN apt-get install -y curl wget vim git

WORKDIR /app

COPY . .

RUN pip3 install flask
RUN pip3 install requests
RUN pip3 install numpy

CMD ["python3", "app.py"]
```

**Task**: Optimize this to be < 200MB

**Solution**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Combine RUN commands and clean up
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Use requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

CMD ["python", "app.py"]
```

### Challenge 2: Multi-Service Application

**Task**: Create a Dockerfile that can be used for:
1. Web server (production)
2. Worker process (background jobs)
3. Database migration

**Solution**:
```dockerfile
FROM python:3.11-slim AS base

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default: web server
CMD ["gunicorn", "app:app"]

# Override with:
# docker run myapp python worker.py
# docker run myapp python migrate.py
```

### Challenge 3: Build-Time Configuration

**Task**: Create a Dockerfile that accepts:
- Environment (dev/staging/prod)
- Feature flags
- Version number

**Solution**:
```dockerfile
ARG ENV=production
ARG ENABLE_FEATURE_X=false
ARG VERSION=1.0.0

FROM python:3.11-slim

LABEL version="${VERSION}"
LABEL environment="${ENV}"

ENV APP_ENV=${ENV} \
    FEATURE_X=${ENABLE_FEATURE_X} \
    VERSION=${VERSION}

WORKDIR /app

COPY requirements.${ENV}.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]
```

```bash
# Build for different environments
docker build --build-arg ENV=development --build-arg VERSION=1.2.3 -t myapp:dev .
docker build --build-arg ENV=production --build-arg VERSION=1.2.3 -t myapp:prod .
```

---

## Part 12: Testing Your Images

### Step 12.1: Create Test Script

```bash
cat > test_image.sh << 'EOF'
#!/bin/bash

IMAGE=$1

echo "Testing image: ${IMAGE}"

# Test 1: Image exists
echo "Test 1: Checking image exists..."
docker images ${IMAGE} | grep -q ${IMAGE}
if [ $? -eq 0 ]; then
    echo "✓ Image exists"
else
    echo "✗ Image not found"
    exit 1
fi

# Test 2: Container starts
echo "Test 2: Checking container starts..."
CONTAINER=$(docker run -d ${IMAGE})
sleep 2
docker ps | grep -q ${CONTAINER}
if [ $? -eq 0 ]; then
    echo "✓ Container started"
else
    echo "✗ Container failed to start"
    docker logs ${CONTAINER}
    exit 1
fi

# Test 3: Health check
echo "Test 3: Checking health endpoint..."
PORT=$(docker port ${CONTAINER} | head -1 | cut -d: -f2)
curl -f http://localhost:${PORT}/health
if [ $? -eq 0 ]; then
    echo "✓ Health check passed"
else
    echo "✗ Health check failed"
fi

# Cleanup
docker rm -f ${CONTAINER}

echo "All tests passed!"
EOF

chmod +x test_image.sh

# Run tests
./test_image.sh my-python-app:v1
```

### Step 12.2: Automated Testing

```bash
# Create test matrix
cat > test_matrix.sh << 'EOF'
#!/bin/bash

IMAGES=(
    "my-python-app:v1"
    "my-python-app:v2-slim"
    "my-python-app:v3-multi"
    "ml-serve:v1"
)

for image in "${IMAGES[@]}"; do
    echo "========================================="
    echo "Testing: ${image}"
    echo "========================================="
    ./test_image.sh ${image}
    if [ $? -ne 0 ]; then
        echo "FAILED: ${image}"
        exit 1
    fi
done

echo "All images passed tests!"
EOF

chmod +x test_matrix.sh
./test_matrix.sh
```

✅ **Checkpoint**: You can test your Docker images.

---

## Validation and Reflection

### Validation Script

Create a comprehensive validation:

```bash
#!/bin/bash
# validate_exercise.sh

echo "Docker Image Building Exercise Validation"
echo "==========================================="

# Check all images were built
REQUIRED_IMAGES=(
    "my-python-app:v1"
    "my-python-app:v2-slim"
    "my-python-app:v3-multi"
    "ml-serve:v1"
)

for img in "${REQUIRED_IMAGES[@]}"; do
    if docker images | grep -q "${img%%:*}.*${img##*:}"; then
        echo "✓ ${img}"
    else
        echo "✗ ${img} - MISSING"
    fi
done

# Check image sizes
echo ""
echo "Image Size Analysis:"
echo "-------------------"
docker images | grep "my-python-app\|ml-serve" | awk '{print $1":"$2" - "$7$8}'

# Check for .dockerignore
if [ -f ".dockerignore" ]; then
    echo "✓ .dockerignore file exists"
else
    echo "✗ .dockerignore file missing"
fi

echo ""
echo "Validation complete!"
```

### Reflection Questions

1. **What's the difference between `COPY` and `ADD`?**
   - Your answer:

2. **Why use multi-stage builds?**
   - Your answer:

3. **How do you minimize image size?**
   - Your answer:

4. **When should you use `--no-cache-dir` with pip?**
   - Your answer:

5. **Why is layer caching important?**
   - Your answer:

6. **What's the benefit of non-root users?**
   - Your answer:

---

## Summary

**What You Accomplished**:
✅ Created custom Docker images from Dockerfiles
✅ Optimized images with multi-stage builds
✅ Containerized Python and ML applications
✅ Mastered Dockerfile instructions
✅ Implemented security best practices
✅ Tagged and versioned images properly
✅ Worked with Docker registries
✅ Debugged build issues
✅ Created production-ready Dockerfiles

**Key Concepts Mastered**:
- **Dockerfile syntax** and best practices
- **Layer caching** and build optimization
- **Multi-stage builds** for smaller images
- **Security practices** (non-root user, minimal base)
- **Image tagging** and versioning strategies
- **Registry operations** (push/pull)
- **Build context** and .dockerignore
- **Health checks** and production patterns

**Image Size Comparison**:
```
Full Python:        1.02 GB
Slim Python:        182 MB
Multi-stage:        ~150 MB
Optimized ML (CPU): ~400 MB
```

---

## Next Steps

**Practice More**:
1. Build images for different application types
2. Experiment with different base images
3. Optimize existing projects
4. Create reusable base images for your team

**Continue Learning**:
- **Exercise 03**: Docker Compose Applications
- **Exercise 04**: Networking and Service Discovery
- **Exercise 05**: Volume Management and Persistence

---

**Exercise Version**: 1.0
**Last Updated**: October 2025
**Estimated Time**: 3-4 hours
**Difficulty**: Beginner to Intermediate
