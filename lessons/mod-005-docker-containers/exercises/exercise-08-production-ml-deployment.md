# Exercise 08: Production-Ready ML Docker Deployment

## Overview

This comprehensive exercise guides you through building production-ready Docker images for ML applications, implementing multi-stage builds for optimization, setting up health checks, configuring resource limits, and deploying to production with proper monitoring and security.

## Learning Objectives

By completing this exercise, you will:
- Build optimized multi-stage Docker images for ML applications
- Implement health checks and readiness probes
- Configure resource limits for GPU and CPU workloads
- Set up proper logging and monitoring
- Implement security best practices
- Create production deployment configurations
- Handle secrets and environment variables securely
- Build CI/CD pipelines for automated Docker builds

## Prerequisites

- Completed exercises 01-07 in this module
- All Docker lectures in Module 005
- Understanding of ML inference workflows
- Basic knowledge of Kubernetes (helpful but not required)

## Time Required

- Estimated: 120-150 minutes
- Difficulty: Advanced

---

## Part 1: Multi-Stage Dockerfile for ML Application

### Task 1.1: Create Production-Optimized Dockerfile

Create a FastAPI ML inference service with multi-stage build:

```dockerfile
# Dockerfile.production
# Stage 1: Build stage with development tools
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

# Copy requirements first (better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime stage (production)
FROM python:3.11-slim

# Add non-root user for security
RUN groupadd -r mluser && useradd -r -g mluser mluser

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=mluser:mluser app/ /app/
COPY --chown=mluser:mluser models/ /app/models/

# Switch to non-root user
USER mluser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Task 1.2: Create Application Files

**requirements.txt:**
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
onnxruntime==1.16.3
numpy==1.24.3
prometheus-client==0.19.0
```

**app/main.py:**
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import onnxruntime as ort
import numpy as np
from prometheus_client import Counter, Histogram, generate_latest
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
PREDICTION_COUNT = Counter('predictions_total', 'Total predictions')
PREDICTION_LATENCY = Histogram('prediction_latency_seconds', 'Prediction latency')
ERROR_COUNT = Counter('prediction_errors_total', 'Total prediction errors')

app = FastAPI(title="ML Inference API", version="1.0.0")

# Load model at startup
model_session = None

@app.on_event("startup")
async def load_model():
    global model_session
    try:
        model_session = ort.InferenceSession("models/model.onnx")
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise

class PredictionRequest(BaseModel):
    features: list[float]

class PredictionResponse(BaseModel):
    prediction: float
    latency_ms: float

@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers"""
    if model_session is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "healthy", "model": "loaded"}

@app.get("/ready")
async def readiness_check():
    """Readiness check for Kubernetes"""
    if model_session is None:
        raise HTTPException(status_code=503, detail="Not ready")
    return {"status": "ready"}

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """Make prediction"""
    start_time = time.time()

    try:
        # Prepare input
        input_data = np.array([request.features], dtype=np.float32)

        # Run inference
        outputs = model_session.run(None, {"input": input_data})
        prediction = float(outputs[0][0])

        # Metrics
        latency = (time.time() - start_time) * 1000
        PREDICTION_COUNT.inc()
        PREDICTION_LATENCY.observe(time.time() - start_time)

        return PredictionResponse(
            prediction=prediction,
            latency_ms=latency
        )

    except Exception as e:
        ERROR_COUNT.inc()
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()

@app.get("/")
async def root():
    return {
        "service": "ML Inference API",
        "version": "1.0.0",
        "endpoints": {
            "/health": "Health check",
            "/ready": "Readiness check",
            "/predict": "Prediction endpoint (POST)",
            "/metrics": "Prometheus metrics"
        }
    }
```

### Task 1.3: Build and Test

```bash
# Build multi-stage image
docker build -t ml-inference:v1.0.0 -f Dockerfile.production .

# Check image size (should be smaller than single-stage)
docker images ml-inference:v1.0.0

# Run container
docker run -d \
    --name ml-api \
    -p 8000:8000 \
    --memory="2g" \
    --cpus="2.0" \
    ml-inference:v1.0.0

# Test health check
curl http://localhost:8000/health

# Test prediction
curl -X POST http://localhost:8000/predict \
    -H "Content-Type: application/json" \
    -d '{"features": [1.0, 2.0, 3.0, 4.0]}'

# Check metrics
curl http://localhost:8000/metrics

# View logs
docker logs ml-api

# Check resource usage
docker stats ml-api

# Stop container
docker stop ml-api && docker rm ml-api
```

---

## Part 2: Docker Compose for Development

### Task 2.1: Create docker-compose.yml

```yaml
version: '3.8'

services:
  ml-api:
    build:
      context: .
      dockerfile: Dockerfile.production
    container_name: ml-inference-api
    ports:
      - "8000:8000"
    environment:
      - LOG_LEVEL=INFO
      - MODEL_PATH=/app/models/model.onnx
    volumes:
      - ./models:/app/models:ro  # Read-only model mount
    networks:
      - ml-network
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 40s
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    networks:
      - ml-network
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana
    networks:
      - ml-network
    restart: unless-stopped

networks:
  ml-network:
    driver: bridge

volumes:
  prometheus-data:
  grafana-data:
```

### Task 2.2: Prometheus Configuration

**prometheus.yml:**
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'ml-api'
    static_configs:
      - targets: ['ml-api:8000']
    metrics_path: '/metrics'
```

### Task 2.3: Launch Stack

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f ml-api

# Check services
docker-compose ps

# Test API
curl http://localhost:8000/health

# Access Prometheus
open http://localhost:9090

# Access Grafana (admin/admin)
open http://localhost:3000

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

---

## Part 3: GPU Support

### Task 3.1: Dockerfile with CUDA

```dockerfile
# Dockerfile.gpu
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Install Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install PyTorch with CUDA
RUN pip3 install --no-cache-dir \
    torch==2.0.1+cu118 \
    torchvision==0.15.2+cu118 \
    --extra-index-url https://download.pytorch.org/whl/cu118

# Copy requirements and app
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

WORKDIR /app
COPY app/ /app/

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Task 3.2: Run with GPU

```bash
# Build GPU image
docker build -t ml-inference:v1.0.0-gpu -f Dockerfile.gpu .

# Run with GPU access
docker run -d \
    --name ml-api-gpu \
    --gpus all \
    -p 8000:8000 \
    --memory="4g" \
    ml-inference:v1.0.0-gpu

# Verify GPU access inside container
docker exec ml-api-gpu nvidia-smi

# Monitor GPU usage
watch -n 1 docker exec ml-api-gpu nvidia-smi
```

---

## Part 4: Security Best Practices

### Task 4.1: Scan for Vulnerabilities

```bash
# Install Trivy
sudo apt-get install wget apt-transport-https gnupg lsb-release
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
sudo apt-get update
sudo apt-get install trivy

# Scan image for vulnerabilities
trivy image ml-inference:v1.0.0

# Scan for high/critical only
trivy image --severity HIGH,CRITICAL ml-inference:v1.0.0

# Generate report
trivy image --format json --output report.json ml-inference:v1.0.0
```

### Task 4.2: Implement Secrets Management

**Using Docker secrets:**

```bash
# Create secret
echo "my-api-key-12345" | docker secret create api_key -

# Run with secret (Swarm mode)
docker service create \
    --name ml-api \
    --secret api_key \
    --publish 8000:8000 \
    ml-inference:v1.0.0
```

**Using environment file:**

**.env (DO NOT commit to Git!):**
```bash
API_KEY=my-secure-api-key
MODEL_PATH=/app/models/model.onnx
LOG_LEVEL=INFO
```

```bash
# Run with env file
docker run -d \
    --env-file .env \
    -p 8000:8000 \
    ml-inference:v1.0.0
```

---

## Part 5: CI/CD Pipeline

### Task 5.1: GitHub Actions Workflow

**.github/workflows/docker-build.yml:**
```yaml
name: Build and Push Docker Image

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-push:
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
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}

      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          file: ./Dockerfile.production
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels}}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload Trivy results to GitHub Security
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
```

---

## Part 6: Kubernetes Deployment

### Task 6.1: Create Kubernetes Manifests

**deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-inference
  labels:
    app: ml-inference
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
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        env:
        - name: LOG_LEVEL
          value: "INFO"
---
apiVersion: v1
kind: Service
metadata:
  name: ml-inference-service
spec:
  selector:
    app: ml-inference
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

---

## Deliverables

Submit the following:

1. **Dockerfiles**:
   - Multi-stage Dockerfile for CPU
   - Dockerfile for GPU workloads
   - docker-compose.yml for full stack

2. **Application Code**:
   - FastAPI inference service
   - Health check endpoints
   - Prometheus metrics

3. **CI/CD**:
   - GitHub Actions workflow
   - Automated vulnerability scanning

4. **Documentation**:
   - Deployment guide
   - Security checklist
   - Troubleshooting runbook

5. **Evidence**:
   - Build logs
   - Trivy scan results
   - Performance benchmarks

---

## Challenge Questions

1. **Image Size**: Your image is 2GB. How can you reduce it to <500MB?

2. **Security**: What are the top 5 security risks in ML Docker images?

3. **Performance**: How do you optimize container startup time for models >1GB?

4. **Scaling**: How do you auto-scale based on GPU utilization?

5. **Monitoring**: What metrics should you track for production ML containers?

---

## Additional Resources

- [Docker Multi-Stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [NVIDIA Container Toolkit](https://github.com/NVIDIA/nvidia-docker)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [Trivy Documentation](https://aquasecurity.github.io/trivy/)

---

**Congratulations!** You've built a production-ready ML Docker deployment with security, monitoring, and CI/CD automation.
