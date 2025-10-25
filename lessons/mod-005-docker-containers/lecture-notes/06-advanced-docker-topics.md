# Lecture 06: Advanced Docker Topics for ML Infrastructure

## Learning Objectives

By the end of this lecture, you will be able to:
- Implement multi-stage Docker builds for optimized ML images
- Apply security best practices for containerized ML workloads
- Integrate Docker into CI/CD pipelines
- Understand container orchestration fundamentals
- Optimize Docker performance for ML applications
- Use Docker build cache effectively
- Implement health checks and readiness probes

## Prerequisites

- Completed Lectures 01-05 in this module
- Understanding of ML workflows
- Basic knowledge of CI/CD concepts
- Familiarity with security principles

---

## 1. Multi-Stage Docker Builds

### 1.1 What Are Multi-Stage Builds?

Multi-stage builds allow you to use multiple `FROM` statements in a single Dockerfile. Each `FROM` instruction starts a new build stage, and you can selectively copy artifacts from one stage to another.

**Benefits for ML Applications:**
- Significantly smaller final images (often 50-80% reduction)
- Separation of build tools from runtime
- Better security (fewer attack surfaces)
- Faster deployment and startup times

### 1.2 Basic Multi-Stage Build Pattern

```dockerfile
# Stage 1: Builder stage with all build tools
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime stage (production)
FROM python:3.11-slim

# Copy only the virtual environment (not build tools)
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy application code
COPY app/ /app/

# Run application
CMD ["python", "main.py"]
```

**How It Works:**
- **Stage 1 (builder):** Compiles dependencies, builds wheels, creates artifacts
- **Stage 2 (runtime):** Copies only compiled artifacts, not build tools
- Build tools (gcc, g++, build-essential) are left in the builder stage
- Final image only contains Python runtime + compiled packages

### 1.3 Advanced ML Multi-Stage Build

```dockerfile
# Stage 1: Download and convert model
FROM python:3.11-slim as model-prep

RUN pip install transformers torch onnx

WORKDIR /models
# Download and convert model to ONNX
RUN python -c "from transformers import AutoModel; \
    model = AutoModel.from_pretrained('bert-base-uncased'); \
    # Convert to ONNX format (smaller, faster)"

# Stage 2: Build dependencies
FROM python:3.11-slim as builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 3: Final runtime
FROM python:3.11-slim

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy optimized model from model-prep stage
COPY --from=model-prep /models /app/models

# Copy application code
WORKDIR /app
COPY app/ /app/

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Key Techniques:**
- Three stages: model preparation, dependency building, runtime
- Each stage is optimized for its specific task
- Final image only contains what's needed at runtime

---

## 2. Docker Security Best Practices

### 2.1 Run as Non-Root User

**Why:** Running containers as root is a security risk. If a container is compromised, the attacker has root privileges.

```dockerfile
# Create non-root user
RUN groupadd -r mluser && useradd -r -g mluser mluser

# Change file ownership
COPY --chown=mluser:mluser app/ /app/

# Switch to non-root user
USER mluser

# From this point, all commands run as mluser
CMD ["python", "app.py"]
```

### 2.2 Minimize Attack Surface

**Use Minimal Base Images:**

```dockerfile
# Bad: Full OS image (1GB+)
FROM ubuntu:22.04

# Better: Slim Python image (~150MB)
FROM python:3.11-slim

# Best: Distroless image (smallest, most secure)
FROM gcr.io/distroless/python3-debian11
```

**Distroless images:**
- No shell, package manager, or unnecessary tools
- Reduces attack surface by 80-90%
- Only application and runtime dependencies
- Cannot execute arbitrary commands (more secure)

### 2.3 Scan for Vulnerabilities

Use tools like **Trivy**, **Snyk**, or **Docker Scan** to identify vulnerabilities:

```bash
# Install Trivy
sudo apt-get install trivy

# Scan Docker image
trivy image ml-inference:v1.0.0

# Scan for HIGH and CRITICAL only
trivy image --severity HIGH,CRITICAL ml-inference:v1.0.0

# Generate JSON report
trivy image --format json --output report.json ml-inference:v1.0.0
```

**Example Output:**
```
Total: 45 (UNKNOWN: 0, LOW: 12, MEDIUM: 18, HIGH: 12, CRITICAL: 3)

HIGH: CVE-2024-1234 in libssl1.1
CRITICAL: CVE-2024-5678 in numpy
```

**Remediation:**
- Update base image to latest patched version
- Update vulnerable packages: `pip install numpy==1.24.4`
- Use alternative packages if vulnerabilities persist

### 2.4 Secrets Management

**Never hardcode secrets in Dockerfiles or images:**

```dockerfile
# ❌ BAD - Secret in Dockerfile
ENV API_KEY="sk-1234567890abcdef"

# ❌ BAD - Secret in image layer
RUN echo "password123" > /app/secret.txt

# ✅ GOOD - Use environment variables at runtime
# Pass via docker run: -e API_KEY="${API_KEY}"

# ✅ GOOD - Use Docker secrets (Swarm mode)
# docker secret create api_key secret.txt
# docker service create --secret api_key myapp

# ✅ GOOD - Mount secret files at runtime
# docker run -v /secure/secrets:/app/secrets:ro myapp
```

**Best Practices:**
- Use environment variables passed at runtime
- Mount secrets as read-only volumes
- Use orchestration-native secret management (Kubernetes Secrets, Docker Secrets)
- Never commit `.env` files to Git

### 2.5 Limit Container Capabilities

By default, Docker containers run with many Linux capabilities. Restrict them:

```bash
# Drop all capabilities, add only what's needed
docker run --cap-drop=ALL --cap-add=NET_BIND_SERVICE myapp

# Run in read-only filesystem (prevents tampering)
docker run --read-only --tmpfs /tmp myapp

# Limit resources to prevent DoS
docker run --memory="2g" --cpus="2.0" myapp
```

---

## 3. Docker Build Optimization

### 3.1 Layer Caching Strategy

Docker caches each layer. Order instructions from least to most frequently changing:

```dockerfile
# ✅ GOOD - Leverages cache effectively
FROM python:3.11-slim

# 1. Install system packages (rarely changes)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# 2. Copy requirements (changes occasionally)
COPY requirements.txt .

# 3. Install Python packages (cached if requirements unchanged)
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy application code (changes frequently)
COPY app/ /app/

# ❌ BAD - Busts cache on every code change
FROM python:3.11-slim
COPY . /app  # Copies everything, including code
RUN pip install -r /app/requirements.txt  # Reinstalls on every build
```

**Cache Busting:**
- If any layer changes, all subsequent layers are rebuilt
- Put frequently changing files (code) at the end
- Put rarely changing files (dependencies) at the beginning

### 3.2 BuildKit and Advanced Features

Enable BuildKit for better performance:

```bash
# Enable BuildKit
export DOCKER_BUILDKIT=1

# Or prefix the build command
DOCKER_BUILDKIT=1 docker build -t myapp .
```

**BuildKit Features:**

```dockerfile
# Syntax directive (enables BuildKit features)
# syntax=docker/dockerfile:1.4

FROM python:3.11-slim

# Mount cache for pip (speeds up repeated builds)
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Mount secrets securely (not stored in image layers)
RUN --mount=type=secret,id=api_key \
    export API_KEY=$(cat /run/secrets/api_key) && \
    python download_model.py
```

Build with secrets:

```bash
docker build --secret id=api_key,src=./api_key.txt -t myapp .
```

### 3.3 .dockerignore File

Exclude unnecessary files to speed up builds:

```
# .dockerignore
__pycache__/
*.pyc
*.pyo
.pytest_cache/
.git/
.gitignore
*.md
docs/
tests/
.venv/
venv/
*.log
.DS_Store
*.swp
data/  # Exclude large datasets
models/checkpoints/  # Exclude training checkpoints
```

**Impact:**
- Faster builds (less data to transfer to Docker daemon)
- Smaller build context
- Avoids accidentally copying sensitive files

---

## 4. Health Checks and Readiness Probes

### 4.1 Docker HEALTHCHECK

Health checks tell Docker if a container is running correctly:

```dockerfile
# Basic HTTP health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# For Python apps without curl
HEALTHCHECK --interval=30s --timeout=3s \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1
```

**Parameters:**
- `--interval=30s`: Check every 30 seconds
- `--timeout=3s`: Fail if check takes >3 seconds
- `--start-period=40s`: Grace period (don't mark unhealthy during startup)
- `--retries=3`: Mark unhealthy after 3 consecutive failures

**Health Endpoint Example (FastAPI):**

```python
from fastapi import FastAPI

app = FastAPI()

model = None  # Global model variable

@app.on_event("startup")
async def load_model():
    global model
    model = load_my_model()

@app.get("/health")
async def health_check():
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "healthy", "model": "loaded"}
```

### 4.2 Kubernetes Readiness and Liveness Probes

While not Docker-specific, understanding these is crucial for ML infrastructure:

```yaml
# Kubernetes deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-inference
spec:
  template:
    spec:
      containers:
      - name: ml-api
        image: ml-inference:v1.0.0
        ports:
        - containerPort: 8000

        # Liveness probe: Is the container alive?
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10

        # Readiness probe: Is the container ready to serve traffic?
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

**Difference:**
- **Liveness:** If fails, Kubernetes restarts the container
- **Readiness:** If fails, Kubernetes stops sending traffic but doesn't restart

---

## 5. CI/CD Integration

### 5.1 GitHub Actions Example

```yaml
# .github/workflows/docker-build.yml
name: Build and Push Docker Image

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Log in to Container Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=semver,pattern={{version}}

      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Run Trivy security scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload scan results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
```

**This workflow:**
1. Triggers on push to main or version tags
2. Builds Docker image with BuildKit caching
3. Pushes to GitHub Container Registry
4. Runs security scan with Trivy
5. Uploads scan results to GitHub Security tab

### 5.2 Docker Compose for Testing in CI

```yaml
# docker-compose.test.yml
version: '3.8'

services:
  ml-api:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      - MODEL_PATH=/app/models/test_model.onnx
    ports:
      - "8000:8000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 5s
      timeout: 3s
      retries: 5

  test-runner:
    image: python:3.11-slim
    depends_on:
      ml-api:
        condition: service_healthy
    volumes:
      - ./tests:/tests
    command: |
      bash -c "pip install pytest requests &&
               pytest /tests/integration_tests.py --api-url=http://ml-api:8000"
```

Run in CI:

```bash
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

---

## 6. Performance Optimization for ML Workloads

### 6.1 GPU Support

**NVIDIA Docker Runtime:**

```dockerfile
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

RUN apt-get update && apt-get install -y python3 python3-pip

RUN pip3 install torch torchvision --extra-index-url https://download.pytorch.org/whl/cu118

COPY app/ /app/
WORKDIR /app

CMD ["python3", "inference.py"]
```

Run with GPU:

```bash
# Single GPU
docker run --gpus all ml-gpu:latest

# Specific GPU
docker run --gpus '"device=0"' ml-gpu:latest

# Multiple GPUs
docker run --gpus '"device=0,1"' ml-gpu:latest
```

### 6.2 Memory and CPU Limits

```bash
# Limit memory and CPUs
docker run -d \
    --name ml-api \
    --memory="4g" \
    --memory-swap="4g" \
    --cpus="2.0" \
    --oom-kill-disable \
    ml-inference:v1.0.0

# View resource usage
docker stats ml-api
```

### 6.3 Shared Memory for PyTorch DataLoaders

PyTorch DataLoaders with `num_workers > 0` need shared memory:

```bash
# Increase shared memory size
docker run --shm-size=2g ml-training:latest

# Or use host's shared memory
docker run --ipc=host ml-training:latest
```

Without sufficient shared memory, you'll see:

```
RuntimeError: DataLoader worker (pid 1234) is killed by signal: Bus error
```

---

## 7. Container Orchestration Basics

### 7.1 Docker Swarm Quick Overview

**Initialize Swarm:**

```bash
docker swarm init
```

**Deploy Service:**

```bash
docker service create \
    --name ml-inference \
    --replicas 3 \
    --publish 8000:8000 \
    ml-inference:v1.0.0

# Scale service
docker service scale ml-inference=5

# Update service (rolling update)
docker service update --image ml-inference:v2.0.0 ml-inference
```

### 7.2 Kubernetes Fundamentals

**Key Concepts:**
- **Pod:** Smallest deployable unit (1+ containers)
- **Deployment:** Manages replicas of Pods
- **Service:** Exposes Pods to network traffic
- **ConfigMap/Secret:** Configuration and secrets

**Simple Deployment:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-inference
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ml-inference
  template:
    metadata:
      labels:
        app: ml-inference
    spec:
      containers:
      - name: ml-api
        image: ml-inference:v1.0.0
        ports:
        - containerPort: 8000
        resources:
          requests:
            cpu: "500m"
            memory: "1Gi"
          limits:
            cpu: "2000m"
            memory: "2Gi"
---
apiVersion: v1
kind: Service
metadata:
  name: ml-inference-service
spec:
  selector:
    app: ml-inference
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

---

## 8. Advanced Dockerfile Techniques

### 8.1 Conditional Logic with ARG

```dockerfile
ARG ENV=production

FROM python:3.11-slim

# Install dev tools only in development
RUN if [ "$ENV" = "development" ]; then \
        apt-get update && apt-get install -y vim curl && \
        rm -rf /var/lib/apt/lists/*; \
    fi

COPY requirements${ENV:+-$ENV}.txt requirements.txt
RUN pip install -r requirements.txt
```

Build with different environments:

```bash
# Production build
docker build --build-arg ENV=production -t app:prod .

# Development build
docker build --build-arg ENV=development -t app:dev .
```

### 8.2 ONBUILD Instructions

```dockerfile
# Base image for multiple ML projects
FROM python:3.11-slim

# These run when another image builds FROM this one
ONBUILD COPY requirements.txt .
ONBUILD RUN pip install -r requirements.txt
ONBUILD COPY app/ /app/
ONBUILD WORKDIR /app
```

Child Dockerfile:

```dockerfile
FROM my-ml-base:latest
# ONBUILD instructions execute automatically
CMD ["python", "main.py"]
```

---

## 9. Debugging Containerized Applications

### 9.1 Interactive Debugging

```bash
# Run container interactively
docker run -it --entrypoint /bin/bash ml-inference:v1.0.0

# Execute command in running container
docker exec -it ml-api bash

# View logs
docker logs -f ml-api

# Inspect container details
docker inspect ml-api
```

### 9.2 Remote Debugging

```dockerfile
# Development Dockerfile
FROM python:3.11-slim

RUN pip install debugpy

COPY app/ /app/
WORKDIR /app

# Enable remote debugging on port 5678
CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "--wait-for-client", "main.py"]
```

Run and connect debugger:

```bash
docker run -p 8000:8000 -p 5678:5678 ml-api:dev
# Connect VSCode or PyCharm debugger to localhost:5678
```

---

## 10. Real-World ML Docker Architecture

### 10.1 Complete Production Stack

```yaml
# docker-compose.production.yml
version: '3.8'

services:
  # ML Inference API
  ml-api:
    build:
      context: .
      dockerfile: Dockerfile.production
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
    environment:
      - MODEL_PATH=/models/model.onnx
      - REDIS_URL=redis://redis:6379
    volumes:
      - models:/models:ro
    networks:
      - ml-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
    depends_on:
      - redis

  # Redis for caching
  redis:
    image: redis:7-alpine
    command: redis-server --maxmemory 512mb --maxmemory-policy allkeys-lru
    networks:
      - ml-network
    volumes:
      - redis-data:/data

  # Prometheus monitoring
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    networks:
      - ml-network
    ports:
      - "9090:9090"

  # Grafana dashboards
  grafana:
    image: grafana/grafana:latest
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana
    networks:
      - ml-network
    ports:
      - "3000:3000"

  # NGINX reverse proxy
  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    networks:
      - ml-network
    ports:
      - "80:80"
    depends_on:
      - ml-api

networks:
  ml-network:
    driver: bridge

volumes:
  models:
  redis-data:
  prometheus-data:
  grafana-data:
```

---

## Summary

In this lecture, you learned:

1. **Multi-Stage Builds:** Reduce image size by 50-80% using separate build and runtime stages
2. **Security Best Practices:** Non-root users, minimal base images, vulnerability scanning, secrets management
3. **Build Optimization:** Layer caching, BuildKit, `.dockerignore` for faster builds
4. **Health Checks:** Implement robust health and readiness probes
5. **CI/CD Integration:** Automate builds, tests, and security scans with GitHub Actions
6. **Performance:** GPU support, resource limits, shared memory for ML workloads
7. **Orchestration Basics:** Introduction to Docker Swarm and Kubernetes
8. **Advanced Techniques:** Conditional builds, ONBUILD, remote debugging
9. **Production Architecture:** Complete ML inference stack with monitoring and caching

## Next Steps

1. **Practice:** Refactor an existing ML Dockerfile using multi-stage builds
2. **Security:** Scan your Docker images with Trivy and fix vulnerabilities
3. **CI/CD:** Set up GitHub Actions to build and test your Docker images
4. **Exercise:** Complete Exercise 08 - Production-Ready ML Docker Deployment
5. **Explore:** Try Kubernetes for orchestrating containerized ML workloads

## Additional Resources

- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Docker Security](https://docs.docker.com/engine/security/)
- [BuildKit Documentation](https://github.com/moby/buildkit)
- [NVIDIA Container Toolkit](https://github.com/NVIDIA/nvidia-docker)
- [Trivy Security Scanner](https://aquasecurity.github.io/trivy/)
- [Kubernetes Documentation](https://kubernetes.io/docs/home/)

---

**Congratulations!** You now have advanced knowledge of Docker for ML infrastructure, including production-ready patterns, security, and optimization techniques.
