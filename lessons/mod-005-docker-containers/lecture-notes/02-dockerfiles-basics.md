# Lecture 02: Dockerfiles and Image Building

## Learning Objectives

By the end of this lecture, you will be able to:

- Understand Dockerfile syntax and instructions
- Write Dockerfiles for Python and web applications
- Build Docker images from Dockerfiles
- Understand image layers and caching
- Optimize Dockerfile for faster builds
- Use multi-stage builds to reduce image size
- Tag and version Docker images
- Debug image building issues

**Duration**: 120 minutes
**Difficulty**: Beginner to Intermediate
**Prerequisites**: Lecture 01 (Docker Fundamentals)

---

## 1. Introduction to Dockerfiles

### What is a Dockerfile?

A **Dockerfile** is a text file containing instructions to build a Docker image.

**Analogy**: If an image is a blueprint and a container is a house, then a Dockerfile is the **construction manual**.

```
Dockerfile → Build → Image → Run → Container

instructions   process   template   process   running app
```

### Why Write Dockerfiles?

**Instead of this:**
```bash
# Manual process (error-prone, not reproducible)
docker run -it ubuntu bash
apt-get update
apt-get install python3
pip install flask
# ... many manual steps ...
# Exit and commit? Messy!
```

**Do this:**
```dockerfile
# Dockerfile (reproducible, versionable)
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip3 install flask
COPY app.py /app/
CMD ["python3", "/app/app.py"]
```

### Dockerfile Benefits

✅ **Reproducible**: Same Dockerfile = Same image every time
✅ **Versionable**: Store in Git like code
✅ **Documented**: Dockerfile shows exactly how image is built
✅ **Automated**: Can be built in CI/CD pipelines
✅ **Shareable**: Team uses same build process

---

## 2. Dockerfile Syntax Basics

### Basic Structure

```dockerfile
# Comment
INSTRUCTION arguments
```

**Example**:
```dockerfile
# Start from Python 3.11 base image
FROM python:3.11

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "app.py"]
```

### Common Instructions

| Instruction | Purpose | Example |
|-------------|---------|---------|
| `FROM` | Base image | `FROM python:3.11` |
| `RUN` | Execute command during build | `RUN apt-get update` |
| `COPY` | Copy files from host to image | `COPY app.py /app/` |
| `ADD` | Copy files (with extra features) | `ADD archive.tar.gz /app/` |
| `WORKDIR` | Set working directory | `WORKDIR /app` |
| `ENV` | Set environment variable | `ENV PORT=8000` |
| `EXPOSE` | Document port | `EXPOSE 8000` |
| `CMD` | Default command to run | `CMD ["python", "app.py"]` |
| `ENTRYPOINT` | Main executable | `ENTRYPOINT ["python"]` |
| `USER` | Set user | `USER appuser` |
| `VOLUME` | Create mount point | `VOLUME /data` |
| `ARG` | Build-time variable | `ARG VERSION=1.0` |
| `LABEL` | Add metadata | `LABEL version="1.0"` |

---

## 3. Essential Dockerfile Instructions

### FROM: Choosing a Base Image

**Every Dockerfile starts with `FROM`**:

```dockerfile
# Official Python image
FROM python:3.11

# Specific version (recommended)
FROM python:3.11.6

# Slim variant (smaller)
FROM python:3.11-slim

# Alpine variant (smallest)
FROM python:3.11-alpine

# Ubuntu base
FROM ubuntu:22.04
```

**Choosing Base Images**:
```
Full Image (python:3.11)
├─ Pros: Everything included, compatible
└─ Cons: Large size (~1GB)

Slim Image (python:3.11-slim)
├─ Pros: Smaller (~100-200MB), most tools included
└─ Cons: Some packages missing

Alpine Image (python:3.11-alpine)
├─ Pros: Tiny (~50MB)
└─ Cons: Different package manager, compatibility issues
```

### RUN: Executing Commands

**RUN** executes commands during image build:

```dockerfile
# Single command
RUN apt-get update

# Multiple commands (creates multiple layers)
RUN apt-get update
RUN apt-get install -y curl
RUN apt-get install -y git

# Better: Chain commands (single layer)
RUN apt-get update && \
    apt-get install -y curl git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
```

**Best Practice**: Combine related commands:
```dockerfile
# Install Python dependencies
RUN pip install --no-cache-dir \
    flask==2.3.0 \
    requests==2.31.0 \
    numpy==1.25.0
```

### COPY vs ADD

**COPY**: Copies files/directories from host to image:
```dockerfile
# Copy single file
COPY app.py /app/app.py

# Copy directory
COPY src/ /app/src/

# Copy multiple files
COPY app.py requirements.txt /app/

# Copy with wildcards
COPY *.py /app/
```

**ADD**: Like COPY, but with extra features:
```dockerfile
# Can extract tar archives
ADD archive.tar.gz /app/

# Can download from URLs (not recommended)
ADD https://example.com/file.txt /app/
```

**When to Use Which**:
- ✅ **Use COPY** for simple file copying (recommended)
- ⚠️ **Use ADD** only for tar extraction

### WORKDIR: Setting Working Directory

**WORKDIR** sets the directory for subsequent instructions:

```dockerfile
# Without WORKDIR (messy)
RUN mkdir /app
RUN mkdir /app/src
COPY app.py /app/app.py
RUN cd /app && python app.py  # cd doesn't persist!

# With WORKDIR (clean)
WORKDIR /app
COPY app.py .
RUN python app.py  # Already in /app
```

**Best Practice**: Use WORKDIR instead of `cd`:
```dockerfile
FROM python:3.11
WORKDIR /app
# Now all commands run in /app
```

### ENV: Environment Variables

**ENV** sets environment variables:

```dockerfile
# Single variable
ENV APP_ENV=production

# Multiple variables
ENV APP_ENV=production \
    PORT=8000 \
    LOG_LEVEL=INFO

# Use in other instructions
ENV APP_HOME=/app
WORKDIR $APP_HOME
```

**Environment variables persist in running containers**:
```bash
docker run myimage env | grep APP_ENV
# APP_ENV=production
```

### EXPOSE: Documenting Ports

**EXPOSE** documents which ports the container listens on:

```dockerfile
# Expose single port
EXPOSE 8000

# Expose multiple ports
EXPOSE 8000 8443

# Different protocols
EXPOSE 8000/tcp
EXPOSE 5353/udp
```

**Important**: EXPOSE is **documentation only**, doesn't actually publish ports!

```bash
# Still need -p when running
docker run -p 8000:8000 myimage
```

### CMD vs ENTRYPOINT

Both define what runs when container starts, but differently:

**CMD**: Default command, can be overridden:
```dockerfile
FROM python:3.11
COPY app.py /app/
CMD ["python", "/app/app.py"]
```

```bash
# Uses CMD
docker run myimage

# Overrides CMD
docker run myimage python /app/other.py
```

**ENTRYPOINT**: Main executable, args can be appended:
```dockerfile
FROM python:3.11
COPY app.py /app/
ENTRYPOINT ["python", "/app/app.py"]
```

```bash
# Runs python /app/app.py
docker run myimage

# Runs python /app/app.py --debug
docker run myimage --debug
```

**Combining ENTRYPOINT and CMD**:
```dockerfile
# ENTRYPOINT = main command
ENTRYPOINT ["python"]

# CMD = default arguments
CMD ["/app/app.py"]

# Can override just arguments:
# docker run myimage /app/other.py
```

---

## 4. Building Images

### The Build Command

```bash
# Basic build
docker build -t myimage .

# -t = tag (name) the image
# . = build context (current directory)
```

### Build Context

The **build context** is the set of files sent to Docker daemon:

```
your-project/
├── Dockerfile
├── app.py
├── requirements.txt
├── src/
│   └── utils.py
└── data/          ← Large files!
    └── model.bin  (1GB)
```

```bash
# Docker sends ENTIRE directory to daemon
docker build -t myimage .
# Sending build context... 1.05GB ← Slow!
```

**Solution**: Use `.dockerignore`:
```
# .dockerignore
data/
*.log
__pycache__/
.git/
*.pyc
.env
```

### Build Process

```dockerfile
FROM python:3.11
RUN pip install flask
COPY app.py /app/
CMD ["python", "/app/app.py"]
```

**What happens during build**:
```
Step 1/4 : FROM python:3.11
 ---> Pulling python:3.11 (if needed)
 ---> <image_id>

Step 2/4 : RUN pip install flask
 ---> Running in <container_id>
 ---> <new_image_id>

Step 3/4 : COPY app.py /app/
 ---> <new_image_id>

Step 4/4 : CMD ["python", "/app/app.py"]
 ---> <final_image_id>

Successfully built <final_image_id>
Successfully tagged myimage:latest
```

Each step creates a new layer!

---

## 5. Understanding Layers and Caching

### Image Layers

**Every instruction creates a layer**:

```dockerfile
FROM ubuntu:22.04       ← Layer 1 (base)
RUN apt-get update      ← Layer 2
RUN apt-get install -y python3  ← Layer 3
COPY app.py /app/       ← Layer 4
```

```
┌────────────────────┐
│  Layer 4 (app.py)  │
├────────────────────┤
│  Layer 3 (python3) │
├────────────────────┤
│  Layer 2 (update)  │
├────────────────────┤
│  Layer 1 (ubuntu)  │
└────────────────────┘
```

**Why layers matter**:
- ✅ **Caching**: Unchanged layers reused
- ✅ **Sharing**: Multiple images share base layers
- ⚠️ **Size**: Each layer adds to total size

### Build Cache

Docker caches layers to speed up builds:

```dockerfile
FROM python:3.11           ← Cached (base image)
WORKDIR /app               ← Cached (no changes)
COPY requirements.txt .    ← Cached (file unchanged)
RUN pip install -r requirements.txt  ← Cached!
COPY app.py .              ← Changed! Cache invalidated
CMD ["python", "app.py"]   ← Rebuilt
```

**First build**:
```
Step 1/6 : FROM python:3.11
 ---> Running...  (2 min)
...
```

**Second build** (no changes):
```
Step 1/6 : FROM python:3.11
 ---> Using cache
...
Successfully built in 1s  ← Fast!
```

### Optimizing Layer Order

**Bad** (invalidates cache on every code change):
```dockerfile
FROM python:3.11
COPY . .                    ← Changes every time!
RUN pip install -r requirements.txt  ← Re-runs every time!
```

**Good** (dependencies cached):
```dockerfile
FROM python:3.11
COPY requirements.txt .     ← Only changes when deps change
RUN pip install -r requirements.txt  ← Cached!
COPY . .                    ← Code changes don't affect deps
```

**Optimization principle**: Copy dependencies first, code last.

---

## 6. Complete Python Application Example

### Project Structure

```
myapp/
├── Dockerfile
├── requirements.txt
├── app.py
├── src/
│   ├── __init__.py
│   └── utils.py
└── .dockerignore
```

### requirements.txt

```
flask==2.3.0
requests==2.31.0
```

### app.py

```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello from Docker!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
```

### Dockerfile (Basic)

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "app.py"]
```

### .dockerignore

```
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.git/
.gitignore
README.md
.dockerignore
Dockerfile
.pytest_cache/
.coverage
htmlcov/
```

### Building and Running

```bash
# Build image
docker build -t myapp:1.0 .

# Run container
docker run -d -p 8000:8000 --name myapp myapp:1.0

# Test
curl http://localhost:8000
# Hello from Docker!

# View logs
docker logs myapp

# Stop and remove
docker stop myapp
docker rm myapp
```

---

## 7. Multi-Stage Builds

### Why Multi-Stage Builds?

**Problem**: Build tools bloat final image:
```dockerfile
FROM python:3.11
RUN apt-get update && apt-get install -y build-essential gcc
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]

# Image size: 1.2GB (includes build tools!)
```

**Solution**: Multi-stage build separates build and runtime:

### Multi-Stage Example

```dockerfile
# Stage 1: Build environment
FROM python:3.11 AS builder

WORKDIR /app
COPY requirements.txt .

# Install dependencies in virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime environment
FROM python:3.11-slim

# Copy only the virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Set PATH to use venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app
COPY . .

CMD ["python", "app.py"]

# Image size: 200MB (much smaller!)
```

**How it works**:
```
Stage 1 (builder)
├─ Install build tools
├─ Compile dependencies
└─ Create artifacts
       │
       │ Copy only artifacts
       ↓
Stage 2 (final)
├─ Start from clean base
├─ Copy compiled artifacts
└─ No build tools included!
```

### Multi-Stage for Compiled Languages

```dockerfile
# Build stage
FROM golang:1.21 AS builder
WORKDIR /app
COPY . .
RUN CGO_ENABLED=0 go build -o myapp

# Runtime stage
FROM alpine:3.18
WORKDIR /app
COPY --from=builder /app/myapp .
CMD ["./myapp"]

# Image size: 10MB (vs 800MB with Go tools!)
```

---

## 8. Tagging and Versioning Images

### Image Tags

```bash
# Format: repository:tag
docker build -t myapp:latest .
docker build -t myapp:1.0 .
docker build -t myapp:1.0.0 .
```

### Multiple Tags

```bash
# Tag during build
docker build -t myapp:1.0 -t myapp:latest .

# Tag existing image
docker tag myapp:1.0 myapp:latest
docker tag myapp:1.0 myrepo/myapp:1.0
```

### Versioning Strategies

**Semantic Versioning**:
```bash
docker build -t myapp:1.0.0 .
docker tag myapp:1.0.0 myapp:1.0
docker tag myapp:1.0.0 myapp:1
docker tag myapp:1.0.0 myapp:latest
```

**Git-based**:
```bash
# Use git commit hash
docker build -t myapp:$(git rev-parse --short HEAD) .

# Use git tag
docker build -t myapp:$(git describe --tags) .
```

**Date-based**:
```bash
docker build -t myapp:$(date +%Y%m%d-%H%M%S) .
# myapp:20251018-143022
```

---

## 9. Building for AI/ML Applications

### PyTorch Application

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir \
    torch==2.1.0 \
    torchvision==0.16.0 \
    --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Copy model weights
COPY models/ /app/models/

EXPOSE 8000

CMD ["python", "serve.py"]
```

### TensorFlow Application

```dockerfile
FROM tensorflow/tensorflow:2.14.0

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["python", "tf_serve.py"]
```

### Jupyter Notebook Environment

```dockerfile
FROM jupyter/scipy-notebook:latest

# Install additional packages
RUN pip install --no-cache-dir \
    torch \
    transformers \
    scikit-learn

# Copy notebooks
COPY notebooks/ /home/jovyan/work/

# Expose Jupyter port
EXPOSE 8888

CMD ["start-notebook.sh"]
```

---

## 10. Debugging and Troubleshooting

### Debugging Build Failures

**View build output**:
```bash
# Verbose build output
docker build -t myapp . --progress=plain
```

**Debug specific layer**:
```bash
# Build up to specific step
docker build -t myapp:debug --target builder .

# Run intermediate image
docker run -it myapp:debug bash
```

**Common Build Errors**:

**1. COPY failed**:
```
ERROR: COPY failed: file not found
```
Solution: Check build context and .dockerignore

**2. RUN command failed**:
```
ERROR: The command '/bin/sh -c pip install -r requirements.txt' returned a non-zero code: 1
```
Solution: Check requirements.txt exists, check internet connection

**3. Cache issues**:
```bash
# Force rebuild without cache
docker build --no-cache -t myapp .
```

### Inspecting Images

```bash
# View image history
docker history myapp:1.0

# Inspect image details
docker inspect myapp:1.0

# Analyze image layers
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  wagoodman/dive:latest myapp:1.0
```

---

## Key Takeaways

✅ **Dockerfiles** define how to build images
✅ **Each instruction** creates a new layer
✅ **Layer order matters** for caching
✅ **COPY dependencies first**, code last
✅ **Multi-stage builds** reduce image size
✅ **Use specific base image versions**, not `:latest`
✅ **Combine RUN commands** to reduce layers
✅ **Use .dockerignore** to exclude files
✅ **Tag images** with versions
✅ **CMD vs ENTRYPOINT**: CMD for defaults, ENTRYPOINT for fixed commands

---

## Quick Reference

### Dockerfile Template

```dockerfile
# Base image
FROM python:3.11-slim

# Metadata
LABEL maintainer="you@example.com"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    package1 package2 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["python", "app.py"]
```

### Build Commands

```bash
# Build with tag
docker build -t myapp:1.0 .

# Build with multiple tags
docker build -t myapp:1.0 -t myapp:latest .

# Build with build argument
docker build --build-arg VERSION=1.0 -t myapp .

# Build without cache
docker build --no-cache -t myapp .

# Build targeting specific stage
docker build --target builder -t myapp:builder .
```

---

## Practice Exercises

1. **Create a Dockerfile** for a Flask web application
2. **Optimize the Dockerfile** using multi-stage builds
3. **Add .dockerignore** to exclude unnecessary files
4. **Build multiple versions** with different tags
5. **Compare image sizes** between optimized and unoptimized builds

---

## What's Next?

In the next lecture, we'll explore:
- **Docker Compose**: Managing multi-container applications
- **docker-compose.yml** syntax
- **Service orchestration**
- **Real-world application stacks**

Continue to `lecture-notes/03-docker-compose.md`

---

**Lecture Version**: 1.0
**Last Updated**: October 2025
**Estimated Time**: 120 minutes
**Difficulty**: Beginner to Intermediate
