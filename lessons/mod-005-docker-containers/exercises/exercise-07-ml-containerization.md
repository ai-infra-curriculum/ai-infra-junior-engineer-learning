# Exercise 07: Complete ML Application Containerization

## Exercise Overview

**Objective**: Build a production-ready containerized machine learning application including model training, inference serving, monitoring, and complete CI/CD pipeline.

**Difficulty**: Advanced
**Estimated Time**: 5-6 hours
**Prerequisites**:
- All previous Docker exercises (01-06)
- All Docker lectures
- Module 004 (ML Basics)

## Learning Objectives

By completing this exercise, you will:
- Containerize ML training pipelines with reproducible environments
- Build production-ready ML inference APIs with FastAPI/Flask
- Configure GPU-enabled containers with CUDA and appropriate drivers
- Implement model versioning and management strategies
- Set up ML-specific monitoring (inference latency, throughput, accuracy)
- Design distributed training architectures using multi-container setups
- Deploy feature serving infrastructure for real-time predictions
- Create complete end-to-end ML deployment pipelines
- Optimize ML containers for performance and resource efficiency
- Integrate ML containers with model registries and experiment tracking

---

## Part 1: Simple ML Inference Service

### Step 1.1: Basic Model Serving

```bash
mkdir -p ~/docker-exercises/ml-app
cd ~/docker-exercises/ml-app

# Create inference application
cat > serve.py << 'EOF'
from flask import Flask, request, jsonify
import torch
import torchvision.transforms as transforms
import torchvision.models as models
from PIL import Image
import io
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load model
logger.info("Loading model...")
model = models.resnet18(pretrained=True)
model.eval()
logger.info("Model loaded successfully")

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

# Load ImageNet class labels
with open('imagenet_classes.txt') as f:
    labels = [line.strip() for line in f.readlines()]

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'model': 'resnet18',
        'version': '1.0'
    })

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    try:
        # Read and process image
        file = request.files['file']
        img_bytes = file.read()
        img = Image.open(io.BytesIO(img_bytes)).convert('RGB')

        # Preprocess
        img_tensor = transform(img).unsqueeze(0)

        # Inference
        with torch.no_grad():
            outputs = model(img_tensor)
            probabilities = torch.nn.functional.softmax(outputs[0], dim=0)

        # Get top 5 predictions
        top5_prob, top5_catid = torch.topk(probabilities, 5)

        results = []
        for i in range(5):
            results.append({
                'class': labels[top5_catid[i]],
                'probability': float(top5_prob[i])
            })

        logger.info(f"Prediction successful: {results[0]['class']}")

        return jsonify({
            'predictions': results,
            'success': True
        })

    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
EOF

# Create ImageNet labels (simplified)
cat > imagenet_classes.txt << 'EOF'
tench
goldfish
great white shark
tiger shark
hammerhead
# ... (1000 classes total, truncated for brevity)
EOF

# Create requirements
cat > requirements.txt << 'EOF'
torch==2.1.0
torchvision==0.16.0
flask==3.0.0
pillow==10.1.0
gunicorn==21.2.0
prometheus-client==0.19.0
EOF
```

### Step 1.2: Dockerfile for ML Inference

```dockerfile
cat > Dockerfile << 'EOF'
# Multi-stage build for ML inference
FROM python:3.11 AS builder

WORKDIR /app

# Install dependencies
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
RUN groupadd -r mluser && useradd -r -g mluser -u 1000 mluser

WORKDIR /app

# Copy Python packages
COPY --from=builder /root/.local /home/mluser/.local

# Copy application
COPY --chown=mluser:mluser serve.py imagenet_classes.txt ./

# Create directories for models and cache
RUN mkdir -p /home/mluser/.cache/torch && \
    chown -R mluser:mluser /home/mluser/.cache

USER mluser

ENV PATH=/home/mluser/.local/bin:$PATH \
    TORCH_HOME=/home/mluser/.cache/torch

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120", "serve:app"]
EOF
```

```bash
# Build and run
docker build -t ml-inference:v1 .

docker run -d \
    --name ml-server \
    -p 8000:8000 \
    ml-inference:v1

# Test
sleep 30  # Wait for model loading
curl http://localhost:8000/health

# Test with image (if you have one)
# curl -X POST -F "file=@test_image.jpg" http://localhost:8000/predict

# Cleanup
docker rm -f ml-server
```

✅ **Checkpoint**: You can containerize a basic ML inference service.

---

## Part 2: GPU-Enabled ML Container

### Step 2.1: GPU-Enabled Dockerfile

```dockerfile
cat > Dockerfile.gpu << 'EOF'
# NVIDIA CUDA base image
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Install Python
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3.11 \
        python3.11-dev \
        python3-pip \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install PyTorch with CUDA support
COPY requirements-gpu.txt .
RUN pip3 install --no-cache-dir \
    torch==2.1.0 \
    torchvision==0.16.0 \
    --index-url https://download.pytorch.org/whl/cu118

RUN pip3 install --no-cache-dir -r requirements-gpu.txt

# Create non-root user
RUN groupadd -r mluser && useradd -r -g mluser -u 1000 mluser

# Copy application
COPY --chown=mluser:mluser serve_gpu.py imagenet_classes.txt ./

USER mluser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "--timeout", "300", "serve_gpu:app"]
EOF

cat > requirements-gpu.txt << 'EOF'
flask==3.0.0
pillow==10.1.0
gunicorn==21.2.0
prometheus-client==0.19.0
EOF
```

### Step 2.2: GPU-Enabled Inference Script

```python
cat > serve_gpu.py << 'EOF'
from flask import Flask, request, jsonify
import torch
import torchvision.transforms as transforms
import torchvision.models as models
from PIL import Image
import io
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Check for GPU
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
logger.info(f"Using device: {device}")

# Load model to GPU
logger.info("Loading model...")
model = models.resnet50(pretrained=True).to(device)
model.eval()
logger.info("Model loaded successfully")

transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'device': str(device),
        'cuda_available': torch.cuda.is_available(),
        'gpu_count': torch.cuda.device_count() if torch.cuda.is_available() else 0
    })

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    try:
        file = request.files['file']
        img = Image.open(io.BytesIO(file.read())).convert('RGB')
        img_tensor = transform(img).unsqueeze(0).to(device)

        with torch.no_grad():
            outputs = model(img_tensor)
            probabilities = torch.nn.functional.softmax(outputs[0], dim=0)

        top5_prob, top5_catid = torch.topk(probabilities, 5)

        return jsonify({
            'predictions': [
                {'class_id': int(top5_catid[i]), 'probability': float(top5_prob[i])}
                for i in range(5)
            ],
            'device': str(device)
        })

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
EOF
```

### Step 2.3: Docker Compose with GPU

```yaml
cat > docker-compose-gpu.yml << 'EOF'
version: '3.8'

services:
  ml-gpu:
    build:
      context: .
      dockerfile: Dockerfile.gpu
    ports:
      - "8000:8000"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    environment:
      - NVIDIA_VISIBLE_DEVICES=0
    restart: unless-stopped
EOF
```

```bash
# Build and run (requires nvidia-docker)
# docker compose -f docker-compose-gpu.yml up -d

# Check GPU usage
# nvidia-smi
```

✅ **Checkpoint**: You can create GPU-enabled ML containers.

---

## Part 3: Model Training Container

### Step 3.1: Training Script

```python
cat > train.py << 'EOF'
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
import os
import json
from datetime import datetime

def train_model(
    data_dir='/data',
    model_dir='/models',
    epochs=10,
    batch_size=32,
    learning_rate=0.001
):
    # Device configuration
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")

    # Data transforms
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    # Load dataset (example: ImageNet-style structure)
    train_dataset = datasets.ImageFolder(
        os.path.join(data_dir, 'train'),
        transform=transform
    )
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=4
    )

    # Model
    model = models.resnet18(pretrained=True)
    num_classes = len(train_dataset.classes)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    model = model.to(device)

    # Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    # Training loop
    metrics = {'epochs': [], 'loss': [], 'accuracy': []}

    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        for i, (images, labels) in enumerate(train_loader):
            images, labels = images.to(device), labels.to(device)

            # Forward pass
            outputs = model(images)
            loss = criterion(outputs, labels)

            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            # Statistics
            running_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

            if (i + 1) % 10 == 0:
                print(f'Epoch [{epoch+1}/{epochs}], Step [{i+1}/{len(train_loader)}], '
                      f'Loss: {loss.item():.4f}')

        # Epoch metrics
        epoch_loss = running_loss / len(train_loader)
        epoch_acc = 100 * correct / total

        metrics['epochs'].append(epoch + 1)
        metrics['loss'].append(epoch_loss)
        metrics['accuracy'].append(epoch_acc)

        print(f'Epoch [{epoch+1}/{epochs}] completed - '
              f'Loss: {epoch_loss:.4f}, Accuracy: {epoch_acc:.2f}%')

    # Save model
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    model_path = os.path.join(model_dir, f'model_{timestamp}.pth')
    torch.save({
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'metrics': metrics,
        'classes': train_dataset.classes
    }, model_path)

    print(f'Model saved to {model_path}')

    # Save metrics
    metrics_path = os.path.join(model_dir, f'metrics_{timestamp}.json')
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)

    return model_path

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--data-dir', default='/data')
    parser.add_argument('--model-dir', default='/models')
    parser.add_argument('--epochs', type=int, default=10)
    parser.add_argument('--batch-size', type=int, default=32)
    parser.add_argument('--lr', type=float, default=0.001)

    args = parser.parse_args()

    train_model(
        data_dir=args.data_dir,
        model_dir=args.model_dir,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr
    )
EOF
```

### Step 3.2: Training Dockerfile

```dockerfile
cat > Dockerfile.train << 'EOF'
FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime

WORKDIR /workspace

# Install additional dependencies
RUN pip install --no-cache-dir \
    tensorboard \
    mlflow \
    scikit-learn

# Copy training script
COPY train.py .

# Create directories
RUN mkdir -p /data /models /logs

# Set environment variables
ENV PYTHONUNBUFFERED=1

CMD ["python", "train.py"]
EOF
```

### Step 3.3: Training with Docker Compose

```yaml
cat > docker-compose-train.yml << 'EOF'
version: '3.8'

services:
  trainer:
    build:
      context: .
      dockerfile: Dockerfile.train
    volumes:
      - ./data:/data:ro  # Training data (read-only)
      - ./models:/models  # Model output
      - ./logs:/logs  # Training logs
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    environment:
      - EPOCHS=20
      - BATCH_SIZE=64
      - LEARNING_RATE=0.001
    command: >
      python train.py
        --epochs ${EPOCHS}
        --batch-size ${BATCH_SIZE}
        --lr ${LEARNING_RATE}

  tensorboard:
    image: tensorflow/tensorflow:latest
    ports:
      - "6006:6006"
    volumes:
      - ./logs:/logs:ro
    command: tensorboard --logdir=/logs --host=0.0.0.0

volumes:
  models:
  logs:
EOF
```

✅ **Checkpoint**: You can containerize ML training pipelines.

---

## Part 4: Complete ML Pipeline

### Step 4.1: Full ML Stack

```yaml
cat > docker-compose-ml-stack.yml << 'EOF'
version: '3.8'

services:
  # PostgreSQL for metadata
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=mlflow
      - POSTGRES_USER=mlflow
      - POSTGRES_PASSWORD=mlflow
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U mlflow"]
      interval: 10s
      timeout: 5s
      retries: 5

  # MinIO for artifact storage
  minio:
    image: minio/minio
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio-data:/data
    environment:
      - MINIO_ROOT_USER=minioadmin
      - MINIO_ROOT_PASSWORD=minioadmin
    command: server /data --console-address ":9001"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 20s
      retries: 3

  # MLflow tracking server
  mlflow:
    image: ghcr.io/mlflow/mlflow:latest
    ports:
      - "5000:5000"
    environment:
      - MLFLOW_S3_ENDPOINT_URL=http://minio:9000
      - AWS_ACCESS_KEY_ID=minioadmin
      - AWS_SECRET_ACCESS_KEY=minioadmin
    command: >
      mlflow server
        --backend-store-uri postgresql://mlflow:mlflow@postgres/mlflow
        --default-artifact-root s3://mlflow/
        --host 0.0.0.0
    depends_on:
      postgres:
        condition: service_healthy
      minio:
        condition: service_healthy

  # Redis for caching
  redis:
    image: redis:7-alpine
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  # Feature store
  feast:
    image: feastdev/feature-server:latest
    ports:
      - "6566:6566"
    volumes:
      - ./feature_repo:/feature_repo
    command: feast -c /feature_repo serve

  # Model serving
  inference:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - MODEL_URI=s3://mlflow/models/production/model.pth
      - REDIS_HOST=redis
      - MLFLOW_TRACKING_URI=http://mlflow:5000
    depends_on:
      - redis
      - mlflow
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1.0'
          memory: 2G

  # Prometheus for monitoring
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus

  # Grafana for visualization
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana

volumes:
  postgres-data:
  minio-data:
  prometheus-data:
  grafana-data:
EOF
```

### Step 4.2: Model Registry Integration

```python
cat > model_registry.py << 'EOF'
import mlflow
import mlflow.pytorch
import torch
import os

class ModelRegistry:
    def __init__(self, tracking_uri='http://localhost:5000'):
        mlflow.set_tracking_uri(tracking_uri)

    def register_model(self, model, model_name, metrics=None):
        """Register a trained model"""
        with mlflow.start_run():
            # Log model
            mlflow.pytorch.log_model(model, "model")

            # Log metrics
            if metrics:
                for key, value in metrics.items():
                    mlflow.log_metric(key, value)

            # Register model
            model_uri = f"runs:/{mlflow.active_run().info.run_id}/model"
            mlflow.register_model(model_uri, model_name)

    def load_production_model(self, model_name):
        """Load production model"""
        model_uri = f"models:/{model_name}/Production"
        return mlflow.pytorch.load_model(model_uri)

    def promote_model(self, model_name, version, stage='Production'):
        """Promote model to production"""
        client = mlflow.tracking.MlflowClient()
        client.transition_model_version_stage(
            name=model_name,
            version=version,
            stage=stage
        )
EOF
```

✅ **Checkpoint**: You can build a complete ML pipeline with Docker.

---

## Part 5: Distributed Training

### Step 5.1: Distributed Training Script

```python
cat > train_distributed.py << 'EOF'
import torch
import torch.nn as nn
import torch.distributed as dist
import torch.multiprocessing as mp
from torch.nn.parallel import DistributedDataParallel as DDP
import os

def setup(rank, world_size):
    """Initialize distributed training"""
    os.environ['MASTER_ADDR'] = os.environ.get('MASTER_ADDR', 'localhost')
    os.environ['MASTER_PORT'] = os.environ.get('MASTER_PORT', '12355')

    # Initialize process group
    dist.init_process_group("nccl", rank=rank, world_size=world_size)

def cleanup():
    """Cleanup distributed training"""
    dist.destroy_process_group()

def train(rank, world_size):
    """Training function for each process"""
    print(f"Running DDP on rank {rank}")
    setup(rank, world_size)

    # Create model and move to GPU
    model = nn.Linear(10, 10).to(rank)
    ddp_model = DDP(model, device_ids=[rank])

    # Loss and optimizer
    loss_fn = nn.MSELoss()
    optimizer = torch.optim.SGD(ddp_model.parameters(), lr=0.001)

    # Training loop
    for epoch in range(10):
        optimizer.zero_grad()
        outputs = ddp_model(torch.randn(20, 10).to(rank))
        labels = torch.randn(20, 10).to(rank)
        loss = loss_fn(outputs, labels)
        loss.backward()
        optimizer.step()

        if rank == 0:
            print(f"Epoch {epoch}, Loss: {loss.item()}")

    cleanup()

def main():
    world_size = torch.cuda.device_count()
    mp.spawn(train, args=(world_size,), nprocs=world_size, join=True)

if __name__ == '__main__':
    main()
EOF
```

### Step 5.2: Distributed Training Compose

```yaml
cat > docker-compose-distributed.yml << 'EOF'
version: '3.8'

services:
  master:
    build:
      context: .
      dockerfile: Dockerfile.train
    environment:
      - MASTER_ADDR=master
      - MASTER_PORT=12355
      - WORLD_SIZE=3
      - RANK=0
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    command: python train_distributed.py

  worker1:
    build:
      context: .
      dockerfile: Dockerfile.train
    environment:
      - MASTER_ADDR=master
      - MASTER_PORT=12355
      - WORLD_SIZE=3
      - RANK=1
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    depends_on:
      - master
    command: python train_distributed.py

  worker2:
    build:
      context: .
      dockerfile: Dockerfile.train
    environment:
      - MASTER_ADDR=master
      - MASTER_PORT=12355
      - WORLD_SIZE=3
      - RANK=2
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    depends_on:
      - master
    command: python train_distributed.py
EOF
```

✅ **Checkpoint**: You can set up distributed training with Docker.

---

## Part 6: Monitoring ML Services

### Step 6.1: Prometheus Metrics

```python
cat > serve_with_metrics.py << 'EOF'
from flask import Flask, request, jsonify
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import torch
import time

app = Flask(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('ml_requests_total', 'Total requests', ['endpoint', 'status'])
REQUEST_LATENCY = Histogram('ml_request_duration_seconds', 'Request latency')
MODEL_LOAD_TIME = Gauge('ml_model_load_time_seconds', 'Model load time')
GPU_MEMORY = Gauge('ml_gpu_memory_bytes', 'GPU memory usage')
PREDICTIONS = Counter('ml_predictions_total', 'Total predictions', ['class'])

# Load model and track load time
start_time = time.time()
model = torch.hub.load('pytorch/vision', 'resnet18', pretrained=True)
model.eval()
load_time = time.time() - start_time
MODEL_LOAD_TIME.set(load_time)

@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()

@app.route('/health')
def health():
    REQUEST_COUNT.labels(endpoint='/health', status='success').inc()

    # Update GPU metrics if available
    if torch.cuda.is_available():
        GPU_MEMORY.set(torch.cuda.memory_allocated())

    return jsonify({
        'status': 'healthy',
        'gpu_available': torch.cuda.is_available()
    })

@app.route('/predict', methods=['POST'])
@REQUEST_LATENCY.time()
def predict():
    try:
        # Prediction logic here
        # ...

        REQUEST_COUNT.labels(endpoint='/predict', status='success').inc()
        PREDICTIONS.labels(class='example_class').inc()

        return jsonify({'result': 'prediction'})

    except Exception as e:
        REQUEST_COUNT.labels(endpoint='/predict', status='error').inc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
EOF
```

### Step 6.2: Custom ML Dashboards

```yaml
# Grafana dashboard configuration
cat > grafana-dashboard.json << 'EOF'
{
  "dashboard": {
    "title": "ML Service Monitoring",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(ml_requests_total[5m])"
          }
        ]
      },
      {
        "title": "Latency (p95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, ml_request_duration_seconds_bucket)"
          }
        ]
      },
      {
        "title": "GPU Memory Usage",
        "targets": [
          {
            "expr": "ml_gpu_memory_bytes"
          }
        ]
      },
      {
        "title": "Predictions by Class",
        "targets": [
          {
            "expr": "ml_predictions_total"
          }
        ]
      }
    ]
  }
}
EOF
```

✅ **Checkpoint**: You can monitor ML services with Prometheus and Grafana.

---

## Part 7: CI/CD for ML Applications

### Step 7.1: GitHub Actions ML Pipeline

```yaml
cat > .github-workflows-ml.yml << 'EOF'
name: ML Model CI/CD

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build test image
        run: docker build -t ml-app:test .

      - name: Run unit tests
        run: |
          docker run --rm ml-app:test pytest tests/unit

      - name: Run integration tests
        run: |
          docker compose -f docker-compose.test.yml up -d
          docker compose -f docker-compose.test.yml exec -T app pytest tests/integration
          docker compose -f docker-compose.test.yml down

  train:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3

      - name: Train model
        run: |
          docker compose -f docker-compose-train.yml up --abort-on-container-exit

      - name: Upload model artifact
        uses: actions/upload-artifact@v3
        with:
          name: trained-model
          path: models/

  deploy:
    needs: train
    runs-on: ubuntu-latest
    steps:
      - name: Download model
        uses: actions/download-artifact@v3
        with:
          name: trained-model

      - name: Build production image
        run: |
          docker build -f Dockerfile.prod -t ml-inference:${{ github.sha }} .

      - name: Push to registry
        run: |
          docker tag ml-inference:${{ github.sha }} registry.example.com/ml-inference:latest
          docker push registry.example.com/ml-inference:latest

      - name: Deploy to production
        run: |
          # Deployment commands here
          echo "Deploying to production..."
EOF
```

### Step 7.2: Model Validation Pipeline

```python
cat > validate_model.py << 'EOF'
import torch
import json
import sys

def validate_model(model_path, validation_data_path):
    """Validate model before deployment"""

    # Load model
    model = torch.load(model_path)
    model.eval()

    # Load validation data
    # ... validation logic ...

    # Check metrics
    metrics = {
        'accuracy': 0.95,  # Replace with actual calculation
        'latency_ms': 50,
        'size_mb': 45
    }

    # Validation thresholds
    if metrics['accuracy'] < 0.90:
        print("FAIL: Accuracy below threshold")
        sys.exit(1)

    if metrics['latency_ms'] > 100:
        print("FAIL: Latency above threshold")
        sys.exit(1)

    if metrics['size_mb'] > 100:
        print("FAIL: Model size too large")
        sys.exit(1)

    print("PASS: Model validation successful")
    print(json.dumps(metrics, indent=2))

    return True

if __name__ == '__main__':
    validate_model('models/model.pth', 'data/validation')
EOF
```

✅ **Checkpoint**: You can implement CI/CD for ML applications.

---

## Part 8: Production Deployment

### Step 8.1: Production-Ready ML Stack

```yaml
cat > docker-compose.production.yml << 'EOF'
version: '3.8'

services:
  # Nginx load balancer
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/prod.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - inference
    restart: always

  # ML inference service (multiple replicas)
  inference:
    build:
      context: .
      dockerfile: Dockerfile.prod
    deploy:
      replicas: 5
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
      update_config:
        parallelism: 1
        delay: 30s
        failure_action: rollback
      restart_policy:
        condition: on-failure
        delay: 10s
        max_attempts: 3
    environment:
      - MODEL_PATH=/models/production/model.pth
      - REDIS_HOST=redis
      - PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus
    volumes:
      - model-store:/models:ro
      - inference-cache:/cache
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    read_only: true
    tmpfs:
      - /tmp
    security_opt:
      - no-new-privileges:true
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # Redis cache
  redis:
    image: redis:7-alpine
    command: redis-server --maxmemory 1gb --maxmemory-policy allkeys-lru
    volumes:
      - redis-data:/data
    restart: always

  # Monitoring
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    restart: always

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
    environment:
      - GF_SECURITY_ADMIN_PASSWORD_FILE=/run/secrets/grafana_password
    secrets:
      - grafana_password
    restart: always

volumes:
  model-store:
    driver: local
  inference-cache:
    driver: local
    driver_opts:
      type: tmpfs
      device: tmpfs
      o: size=2g
  redis-data:
  prometheus-data:
  grafana-data:

secrets:
  grafana_password:
    file: ./secrets/grafana_password.txt
EOF
```

✅ **Checkpoint**: You have a production-ready ML deployment.

---

## Summary

**What You Accomplished**:
✅ Built ML inference services
✅ Created GPU-enabled containers
✅ Containerized training pipelines
✅ Implemented complete ML stack
✅ Set up distributed training
✅ Added ML-specific monitoring
✅ Integrated CI/CD for ML
✅ Deployed production ML systems

**Complete ML Infrastructure**:
- Model training with GPU support
- Inference serving with caching
- Model registry (MLflow)
- Feature store (Feast)
- Monitoring (Prometheus/Grafana)
- Distributed training
- CI/CD pipeline
- Production deployment

**Best Practices Applied**:
- Multi-stage builds for optimization
- GPU resource management
- Model versioning
- Automated testing
- Health checks
- Security hardening
- Horizontal scaling
- Monitoring and logging

---

## Next Steps

**Continue Learning**:
- **Module 005 Quiz**: Test your complete Docker knowledge
- **Module 006**: Kubernetes orchestration
- **Module 007**: Production ML operations

---

**Exercise Version**: 1.0
**Last Updated**: October 2025
**Estimated Time**: 5-6 hours
**Difficulty**: Advanced
