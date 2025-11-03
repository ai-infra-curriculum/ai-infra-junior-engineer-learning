# Exercise 07: ML Workloads on Kubernetes

## Exercise Overview

**Objective**: Deploy complete machine learning workloads on Kubernetes including training jobs, distributed training, model serving, GPU scheduling, and introduction to Kubeflow.

**Difficulty**: Advanced
**Estimated Time**: 4-5 hours
**Prerequisites**:
- All previous Module 006 exercises
- Module 004 (ML Basics)
- Module 005 (Docker ML containers)

## Learning Objectives

By completing this exercise, you will:
- Deploy ML training Jobs and scheduled CronJobs on Kubernetes
- Configure GPU resource requests and limits for ML workloads
- Implement distributed training with PyTorch using multiple pods
- Build scalable model serving deployments with autoscaling
- Orchestrate ML pipelines using Kubernetes primitives
- Set up Kubeflow components for ML workflow management
- Monitor ML-specific metrics (training progress, inference latency)
- Design complete end-to-end ML workflows on Kubernetes
- Optimize resource allocation for cost-effective ML operations
- Implement experiment tracking and model versioning in K8s

---

## Part 1: ML Training Jobs

### Step 1.1: Simple Training Job

```yaml
cat > ml-training-job.yaml << 'EOF'
apiVersion: v1
kind: ConfigMap
metadata:
  name: training-script
data:
  train.py: |
    import torch
    import torch.nn as nn
    import time
    import os

    print("Starting training...")
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")

    # Simple model
    model = nn.Sequential(
        nn.Linear(10, 50),
        nn.ReLU(),
        nn.Linear(50, 1)
    )

    # Dummy training
    optimizer = torch.optim.Adam(model.parameters())
    criterion = nn.MSELoss()

    for epoch in range(10):
        data = torch.randn(32, 10)
        target = torch.randn(32, 1)

        output = model(data)
        loss = criterion(output, target)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        print(f"Epoch {epoch + 1}/10, Loss: {loss.item():.4f}")
        time.sleep(1)

    # Save model
    torch.save(model.state_dict(), '/models/model.pth')
    print("Training complete! Model saved.")
---
apiVersion: batch/v1
kind: Job
metadata:
  name: ml-training-job
spec:
  template:
    spec:
      containers:
      - name: trainer
        image: pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime
        command: ["python", "/scripts/train.py"]
        volumeMounts:
        - name: scripts
          mountPath: /scripts
        - name: models
          mountPath: /models
        resources:
          limits:
            memory: "2Gi"
            cpu: "2"
      volumes:
      - name: scripts
        configMap:
          name: training-script
      - name: models
        persistentVolumeClaim:
          claimName: model-storage
      restartPolicy: Never
  backoffLimit: 3
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: model-storage
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
EOF

kubectl apply -f ml-training-job.yaml

# Watch job progress
kubectl get jobs -w

# View logs
kubectl logs job/ml-training-job

# Check if model was saved
kubectl exec -it $(kubectl get pod -l job-name=ml-training-job -o name) -- ls -la /models
```

### Step 1.2: Scheduled Training (CronJob)

```yaml
cat > ml-cronjob.yaml << 'EOF'
apiVersion: batch/v1
kind: CronJob
metadata:
  name: ml-retraining
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: trainer
            image: pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime
            command:
            - python
            - /scripts/train.py
            - --data-path=/data
            - --model-output=/models
            - --timestamp=$(date +%Y%m%d)
            env:
            - name: MLFLOW_TRACKING_URI
              value: "http://mlflow:5000"
            volumeMounts:
            - name: training-data
              mountPath: /data
              readOnly: true
            - name: model-output
              mountPath: /models
          volumes:
          - name: training-data
            persistentVolumeClaim:
              claimName: training-data
          - name: model-output
            persistentVolumeClaim:
              claimName: model-storage
          restartPolicy: OnFailure
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 1
EOF

kubectl apply -f ml-cronjob.yaml

# Trigger manually (don't wait for schedule)
kubectl create job --from=cronjob/ml-retraining manual-training-1

# View CronJob
kubectl get cronjobs
kubectl describe cronjob ml-retraining
```

### Step 1.3: Training with External Dataset

```yaml
cat > training-with-data.yaml << 'EOF'
apiVersion: batch/v1
kind: Job
metadata:
  name: training-with-data
spec:
  template:
    spec:
      initContainers:
      # Download dataset
      - name: data-downloader
        image: alpine/curl
        command:
        - sh
        - -c
        - |
          curl -L https://example.com/dataset.tar.gz -o /data/dataset.tar.gz
          cd /data && tar xzf dataset.tar.gz
        volumeMounts:
        - name: data
          mountPath: /data
      containers:
      - name: trainer
        image: pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime
        command: ["python", "train.py"]
        workingDir: /workspace
        env:
        - name: DATA_DIR
          value: "/data"
        - name: OUTPUT_DIR
          value: "/models"
        volumeMounts:
        - name: data
          mountPath: /data
        - name: models
          mountPath: /models
        - name: code
          mountPath: /workspace
      volumes:
      - name: data
        emptyDir: {}  # Temporary, recreated each time
      - name: models
        persistentVolumeClaim:
          claimName: model-storage
      - name: code
        configMap:
          name: training-code
      restartPolicy: Never
EOF
```

✅ **Checkpoint**: You can run ML training jobs on Kubernetes.

---

## Part 2: GPU Scheduling

### Step 2.1: GPU Training Job

```yaml
cat > gpu-training-job.yaml << 'EOF'
apiVersion: batch/v1
kind: Job
metadata:
  name: gpu-training
spec:
  template:
    metadata:
      labels:
        app: gpu-training
    spec:
      containers:
      - name: trainer
        image: pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime
        command:
        - python
        - -c
        - |
          import torch
          print(f"CUDA available: {torch.cuda.is_available()}")
          print(f"GPU count: {torch.cuda.device_count()}")
          if torch.cuda.is_available():
              print(f"GPU name: {torch.cuda.get_device_name(0)}")
              print(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")

          # Train on GPU
          device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
          model = torch.nn.Linear(100, 10).to(device)
          print(f"Model device: {next(model.parameters()).device}")
        resources:
          limits:
            nvidia.com/gpu: 1  # Request 1 GPU
            memory: "4Gi"
            cpu: "4"
      restartPolicy: Never
      # Node selector for GPU nodes
      nodeSelector:
        nvidia.com/gpu.present: "true"
EOF

kubectl apply -f gpu-training-job.yaml

# Check GPU usage
kubectl logs job/gpu-training
```

### Step 2.2: Multi-GPU Training

```yaml
cat > multi-gpu-training.yaml << 'EOF'
apiVersion: batch/v1
kind: Job
metadata:
  name: multi-gpu-training
spec:
  template:
    spec:
      containers:
      - name: trainer
        image: pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime
        command:
        - python
        - train_multi_gpu.py
        resources:
          limits:
            nvidia.com/gpu: 4  # Request 4 GPUs
            memory: "16Gi"
            cpu: "16"
        env:
        - name: NVIDIA_VISIBLE_DEVICES
          value: "all"
        volumeMounts:
        - name: training-code
          mountPath: /workspace
        - name: shm
          mountPath: /dev/shm  # Shared memory for multi-GPU
      volumes:
      - name: training-code
        configMap:
          name: training-scripts
      - name: shm
        emptyDir:
          medium: Memory
          sizeLimit: 8Gi
      restartPolicy: Never
EOF
```

### Step 2.3: GPU Sharing and Fractions

```yaml
cat > gpu-sharing.yaml << 'EOF'
# Using NVIDIA MIG (Multi-Instance GPU) or time-slicing
apiVersion: v1
kind: Pod
metadata:
  name: gpu-shared-1
spec:
  containers:
  - name: app
    image: nvidia/cuda:11.7.0-base-ubuntu20.04
    command: ["sleep", "3600"]
    resources:
      limits:
        nvidia.com/gpu: 1
---
apiVersion: v1
kind: Pod
metadata:
  name: gpu-shared-2
spec:
  containers:
  - name: app
    image: nvidia/cuda:11.7.0-base-ubuntu20.04
    command: ["sleep", "3600"]
    resources:
      limits:
        nvidia.com/gpu: 1
# With time-slicing, both pods can share same GPU
EOF
```

✅ **Checkpoint**: You can schedule GPU workloads.

---

## Part 3: Distributed Training

### Step 3.1: PyTorch Distributed Training

```yaml
cat > distributed-training.yaml << 'EOF'
apiVersion: v1
kind: ConfigMap
metadata:
  name: distributed-training-script
data:
  train_distributed.py: |
    import torch
    import torch.distributed as dist
    import torch.nn as nn
    import os

    def setup_distributed():
        rank = int(os.environ['RANK'])
        world_size = int(os.environ['WORLD_SIZE'])
        master_addr = os.environ['MASTER_ADDR']
        master_port = os.environ['MASTER_PORT']

        dist.init_process_group(
            backend='nccl' if torch.cuda.is_available() else 'gloo',
            init_method=f'tcp://{master_addr}:{master_port}',
            world_size=world_size,
            rank=rank
        )

    def cleanup():
        dist.destroy_process_group()

    def main():
        setup_distributed()
        rank = dist.get_rank()
        world_size = dist.get_world_size()

        print(f"[Rank {rank}/{world_size}] Starting distributed training")

        # Create model and wrap with DDP
        model = nn.Linear(10, 10)
        if torch.cuda.is_available():
            device = torch.device(f'cuda:{rank}')
            model = model.to(device)
            model = nn.parallel.DistributedDataParallel(model, device_ids=[rank])
        else:
            model = nn.parallel.DistributedDataParallel(model)

        # Training loop
        optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
        for epoch in range(10):
            data = torch.randn(20, 10)
            target = torch.randn(20, 10)

            if torch.cuda.is_available():
                data = data.to(device)
                target = target.to(device)

            output = model(data)
            loss = nn.MSELoss()(output, target)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            if rank == 0:
                print(f"Epoch {epoch + 1}, Loss: {loss.item():.4f}")

        cleanup()
        print(f"[Rank {rank}] Training complete")

    if __name__ == '__main__':
        main()
---
# Master node
apiVersion: v1
kind: Service
metadata:
  name: distributed-training-master
spec:
  clusterIP: None  # Headless service
  selector:
    job-name: distributed-training-master
  ports:
  - port: 29500
    name: dist-training
---
apiVersion: batch/v1
kind: Job
metadata:
  name: distributed-training-master
spec:
  template:
    metadata:
      labels:
        job-name: distributed-training-master
    spec:
      containers:
      - name: trainer
        image: pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime
        command: ["python", "/scripts/train_distributed.py"]
        env:
        - name: MASTER_ADDR
          value: "distributed-training-master"
        - name: MASTER_PORT
          value: "29500"
        - name: WORLD_SIZE
          value: "3"
        - name: RANK
          value: "0"
        volumeMounts:
        - name: scripts
          mountPath: /scripts
        resources:
          limits:
            nvidia.com/gpu: 1
      volumes:
      - name: scripts
        configMap:
          name: distributed-training-script
      restartPolicy: Never
---
# Worker node 1
apiVersion: batch/v1
kind: Job
metadata:
  name: distributed-training-worker-1
spec:
  template:
    spec:
      containers:
      - name: trainer
        image: pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime
        command: ["python", "/scripts/train_distributed.py"]
        env:
        - name: MASTER_ADDR
          value: "distributed-training-master"
        - name: MASTER_PORT
          value: "29500"
        - name: WORLD_SIZE
          value: "3"
        - name: RANK
          value: "1"
        volumeMounts:
        - name: scripts
          mountPath: /scripts
        resources:
          limits:
            nvidia.com/gpu: 1
      volumes:
      - name: scripts
        configMap:
          name: distributed-training-script
      restartPolicy: Never
---
# Worker node 2
apiVersion: batch/v1
kind: Job
metadata:
  name: distributed-training-worker-2
spec:
  template:
    spec:
      containers:
      - name: trainer
        image: pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime
        command: ["python", "/scripts/train_distributed.py"]
        env:
        - name: MASTER_ADDR
          value: "distributed-training-master"
        - name: MASTER_PORT
          value: "29500"
        - name: WORLD_SIZE
          value: "3"
        - name: RANK
          value: "2"
        volumeMounts:
        - name: scripts
          mountPath: /scripts
        resources:
          limits:
            nvidia.com/gpu: 1
      volumes:
      - name: scripts
        configMap:
          name: distributed-training-script
      restartPolicy: Never
EOF

kubectl apply -f distributed-training.yaml

# Watch all jobs
kubectl get jobs -w

# View logs from each rank
kubectl logs job/distributed-training-master
kubectl logs job/distributed-training-worker-1
kubectl logs job/distributed-training-worker-2
```

### Step 3.2: Using PyTorchJob (Kubeflow Training Operator)

```yaml
# Install PyTorch Training Operator first
# kubectl apply -k "github.com/kubeflow/training-operator/manifests/overlays/standalone"

cat > pytorchjob.yaml << 'EOF'
apiVersion: kubeflow.org/v1
kind: PyTorchJob
metadata:
  name: pytorch-distributed
spec:
  pytorchReplicaSpecs:
    Master:
      replicas: 1
      restartPolicy: OnFailure
      template:
        spec:
          containers:
          - name: pytorch
            image: pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime
            command:
            - python
            - /workspace/train.py
            resources:
              limits:
                nvidia.com/gpu: 1
                memory: "4Gi"
    Worker:
      replicas: 2
      restartPolicy: OnFailure
      template:
        spec:
          containers:
          - name: pytorch
            image: pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime
            command:
            - python
            - /workspace/train.py
            resources:
              limits:
                nvidia.com/gpu: 1
                memory: "4Gi"
EOF

# kubectl apply -f pytorchjob.yaml
# kubectl get pytorchjobs
# kubectl logs -f pytorch-distributed-master-0
```

✅ **Checkpoint**: You can run distributed training.

---

## Part 4: Model Serving

### Step 4.1: Simple Model Serving Deployment

```yaml
cat > model-serving.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: model-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: model-server
  template:
    metadata:
      labels:
        app: model-server
    spec:
      initContainers:
      # Load model from storage
      - name: model-loader
        image: busybox
        command:
        - sh
        - -c
        - cp /models-source/*.pth /models/
        volumeMounts:
        - name: model-source
          mountPath: /models-source
        - name: model-cache
          mountPath: /models
      containers:
      - name: server
        image: pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: MODEL_PATH
          value: "/models/model.pth"
        - name: WORKERS
          value: "4"
        volumeMounts:
        - name: model-cache
          mountPath: /models
        - name: serving-code
          mountPath: /app
        command:
        - gunicorn
        - --bind=0.0.0.0:8000
        - --workers=4
        - --timeout=120
        - app:app
        workingDir: /app
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
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
          initialDelaySeconds: 10
          periodSeconds: 5
      volumes:
      - name: model-source
        persistentVolumeClaim:
          claimName: model-storage
      - name: model-cache
        emptyDir: {}
      - name: serving-code
        configMap:
          name: serving-code
---
apiVersion: v1
kind: Service
metadata:
  name: model-server
spec:
  selector:
    app: model-server
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: model-server-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: model-server
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
EOF

kubectl apply -f model-serving.yaml

# Test the service
kubectl get svc model-server
# curl http://<EXTERNAL-IP>/predict -d '{"input": [1,2,3]}'
```

### Step 4.2: GPU-Accelerated Inference

```yaml
cat > gpu-inference.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gpu-inference
spec:
  replicas: 2
  selector:
    matchLabels:
      app: gpu-inference
  template:
    metadata:
      labels:
        app: gpu-inference
    spec:
      containers:
      - name: inference
        image: pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime
        ports:
        - containerPort: 8000
        env:
        - name: CUDA_VISIBLE_DEVICES
          value: "0"
        resources:
          limits:
            nvidia.com/gpu: 1
            memory: "8Gi"
          requests:
            nvidia.com/gpu: 1
            memory: "4Gi"
        volumeMounts:
        - name: models
          mountPath: /models
          readOnly: true
      volumes:
      - name: models
        persistentVolumeClaim:
          claimName: model-storage
      nodeSelector:
        nvidia.com/gpu.present: "true"
EOF
```

### Step 4.3: Model Versioning and Canary

```yaml
cat > model-canary.yaml << 'EOF'
# Stable model (v1)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: model-v1
spec:
  replicas: 9
  selector:
    matchLabels:
      app: model-server
      version: v1
  template:
    metadata:
      labels:
        app: model-server
        version: v1
    spec:
      containers:
      - name: server
        image: mymodel:v1
        env:
        - name: MODEL_VERSION
          value: "1.0.0"
---
# Canary model (v2)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: model-v2
spec:
  replicas: 1  # 10% traffic
  selector:
    matchLabels:
      app: model-server
      version: v2
  template:
    metadata:
      labels:
        app: model-server
        version: v2
    spec:
      containers:
      - name: server
        image: mymodel:v2
        env:
        - name: MODEL_VERSION
          value: "2.0.0"
---
apiVersion: v1
kind: Service
metadata:
  name: model-server
spec:
  selector:
    app: model-server  # Routes to both v1 and v2
  ports:
  - port: 80
    targetPort: 8000
EOF
```

✅ **Checkpoint**: You can deploy ML model serving.

---

## Part 5: Kubeflow Basics

### Step 5.1: Install Kubeflow Pipelines

```bash
# Install Kubeflow Pipelines (standalone)
export PIPELINE_VERSION=2.0.1
kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/cluster-scoped-resources?ref=$PIPELINE_VERSION"
kubectl wait --for condition=established --timeout=60s crd/applications.app.k8s.io
kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/env/platform-agnostic?ref=$PIPELINE_VERSION"

# Wait for deployments
kubectl wait --for=condition=available --timeout=600s deployment/ml-pipeline -n kubeflow

# Port forward to access UI
kubectl port-forward -n kubeflow svc/ml-pipeline-ui 8080:80

# Access at http://localhost:8080
```

### Step 5.2: Simple Kubeflow Pipeline

```python
# Create pipeline (pipeline.py)
cat > pipeline.py << 'EOF'
from kfp import dsl
from kfp import compiler

@dsl.component
def preprocess_data():
    """Preprocess training data"""
    import pandas as pd
    # Preprocessing logic
    print("Data preprocessed")

@dsl.component
def train_model():
    """Train ML model"""
    import torch
    # Training logic
    print("Model trained")

@dsl.component
def evaluate_model():
    """Evaluate model"""
    # Evaluation logic
    print("Model evaluated")

@dsl.pipeline(
    name='ML Training Pipeline',
    description='Complete ML training workflow'
)
def ml_pipeline():
    preprocess_task = preprocess_data()
    train_task = train_model().after(preprocess_task)
    evaluate_task = evaluate_model().after(train_task)

if __name__ == '__main__':
    compiler.Compiler().compile(ml_pipeline, 'pipeline.yaml')
EOF

# Compile pipeline
python pipeline.py

# Upload pipeline.yaml to Kubeflow UI
```

### Step 5.3: Complete ML Pipeline

```yaml
cat > complete-ml-pipeline.yaml << 'EOF'
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  name: ml-pipeline
spec:
  entrypoint: ml-workflow
  templates:
  - name: ml-workflow
    steps:
    - - name: data-ingestion
        template: ingest-data
    - - name: data-preprocessing
        template: preprocess
    - - name: train-model
        template: train
    - - name: evaluate-model
        template: evaluate
    - - name: deploy-model
        template: deploy

  - name: ingest-data
    container:
      image: python:3.11
      command: [python]
      args:
      - -c
      - |
        print("Ingesting data...")
        # Data ingestion logic

  - name: preprocess
    container:
      image: python:3.11
      command: [python]
      args:
      - -c
      - |
        print("Preprocessing data...")
        # Preprocessing logic

  - name: train
    container:
      image: pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime
      command: [python]
      args: ["/scripts/train.py"]
      resources:
        limits:
          nvidia.com/gpu: 1

  - name: evaluate
    container:
      image: pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime
      command: [python]
      args: ["/scripts/evaluate.py"]

  - name: deploy
    container:
      image: kubectl:latest
      command: [kubectl]
      args:
      - apply
      - -f
      - /manifests/deployment.yaml
EOF
```

✅ **Checkpoint**: You understand Kubeflow basics.

---

## Part 6: ML Monitoring

### Step 6.1: Model Metrics

```yaml
cat > model-monitoring.yaml << 'EOF'
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s

    scrape_configs:
    - job_name: 'model-server'
      kubernetes_sd_configs:
      - role: pod
      relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        action: keep
        regex: model-server
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: model-server-instrumented
spec:
  replicas: 3
  selector:
    matchLabels:
      app: model-server
  template:
    metadata:
      labels:
        app: model-server
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8000"
        prometheus.io/path: "/metrics"
    spec:
      containers:
      - name: server
        image: mymodel:latest
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: ENABLE_METRICS
          value: "true"
EOF
```

### Step 6.2: Prediction Logging

```yaml
cat > prediction-logger.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: model-with-logging
spec:
  replicas: 2
  selector:
    matchLabels:
      app: model-logging
  template:
    spec:
      containers:
      - name: model-server
        image: mymodel:latest
        volumeMounts:
        - name: logs
          mountPath: /logs
      - name: log-shipper
        image: fluent/fluent-bit:latest
        volumeMounts:
        - name: logs
          mountPath: /logs
          readOnly: true
        - name: fluent-bit-config
          mountPath: /fluent-bit/etc
      volumes:
      - name: logs
        emptyDir: {}
      - name: fluent-bit-config
        configMap:
          name: fluent-bit-config
EOF
```

✅ **Checkpoint**: You can monitor ML models.

---

## Part 7: Complete ML Workflow

### Step 7.1: End-to-End ML System

```yaml
cat > complete-ml-system.yaml << 'EOF'
# Namespace for ML workloads
apiVersion: v1
kind: Namespace
metadata:
  name: ml-system
---
# Training Job
apiVersion: batch/v1
kind: CronJob
metadata:
  name: model-retraining
  namespace: ml-system
spec:
  schedule: "0 2 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: trainer
            image: mytrainer:latest
            env:
            - name: MLFLOW_TRACKING_URI
              value: http://mlflow:5000
            resources:
              limits:
                nvidia.com/gpu: 2
          restartPolicy: OnFailure
---
# Model Registry (MLflow)
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mlflow
  namespace: ml-system
spec:
  serviceName: mlflow
  replicas: 1
  selector:
    matchLabels:
      app: mlflow
  template:
    metadata:
      labels:
        app: mlflow
    spec:
      containers:
      - name: mlflow
        image: ghcr.io/mlflow/mlflow:latest
        ports:
        - containerPort: 5000
        volumeMounts:
        - name: mlflow-data
          mountPath: /mlflow
  volumeClaimTemplates:
  - metadata:
      name: mlflow-data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi
---
# Feature Store
apiVersion: apps/v1
kind: Deployment
metadata:
  name: feast
  namespace: ml-system
spec:
  replicas: 2
  selector:
    matchLabels:
      app: feast
  template:
    spec:
      containers:
      - name: feast
        image: feastdev/feature-server:latest
        ports:
        - containerPort: 6566
---
# Model Serving
apiVersion: apps/v1
kind: Deployment
metadata:
  name: model-serving
  namespace: ml-system
spec:
  replicas: 5
  selector:
    matchLabels:
      app: model-serving
  template:
    spec:
      containers:
      - name: server
        image: mymodel:latest
        resources:
          limits:
            nvidia.com/gpu: 1
        ports:
        - containerPort: 8000
---
# Monitoring
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
  namespace: ml-system
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    spec:
      containers:
      - name: prometheus
        image: prom/prometheus:latest
        ports:
        - containerPort: 9090
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana
  namespace: ml-system
spec:
  replicas: 1
  selector:
    matchLabels:
      app: grafana
  template:
    spec:
      containers:
      - name: grafana
        image: grafana/grafana:latest
        ports:
        - containerPort: 3000
EOF

kubectl apply -f complete-ml-system.yaml
```

✅ **Checkpoint**: You built a complete ML system on Kubernetes!

---

## Summary

**What You Accomplished**:
✅ Ran ML training jobs and CronJobs
✅ Scheduled GPU resources
✅ Implemented distributed training
✅ Deployed model serving with autoscaling
✅ Used Kubeflow for ML pipelines
✅ Monitored ML model performance
✅ Built complete end-to-end ML workflow

**Key Concepts**:
- Jobs for one-time training
- CronJobs for scheduled retraining
- GPU scheduling with nvidia.com/gpu
- Distributed training with PyTorch DDP
- PyTorchJob operator for easier distributed training
- Model serving with HPA
- Kubeflow for ML orchestration
- Prometheus metrics for ML monitoring

**Production Patterns**:
- Automated retraining pipelines
- GPU resource management
- Model versioning and canary deployments
- Metrics and logging for model monitoring
- Complete ML platform on Kubernetes

**Architecture**:
```
Training Pipeline:
  Data → Preprocessing → Training (GPU) → Evaluation → Model Registry

Serving Pipeline:
  Model Registry → Model Server (GPU/CPU) → Load Balancer → Users

Monitoring:
  Metrics (Prometheus) → Dashboards (Grafana) → Alerts
```

---

**Exercise Version**: 1.0
**Last Updated**: October 2025
**Estimated Time**: 4-5 hours
**Difficulty**: Advanced
