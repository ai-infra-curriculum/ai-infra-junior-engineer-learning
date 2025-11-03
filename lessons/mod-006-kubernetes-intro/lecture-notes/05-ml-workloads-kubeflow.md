# Lecture 05: ML Workloads and Kubeflow on Kubernetes

## Table of Contents
1. [Introduction](#introduction)
2. [Kubernetes Batch Workloads](#kubernetes-batch-workloads)
3. [GPU Scheduling in Kubernetes](#gpu-scheduling-in-kubernetes)
4. [Kubernetes Operators for ML](#kubernetes-operators-for-ml)
5. [Introduction to Kubeflow](#introduction-to-kubeflow)
6. [Installing Kubeflow](#installing-kubeflow)
7. [Kubeflow Components](#kubeflow-components)
8. [Distributed Training with Kubeflow](#distributed-training-with-kubeflow)
9. [ML Pipeline Orchestration](#ml-pipeline-orchestration)
10. [Model Serving with Kubeflow](#model-serving-with-kubeflow)
11. [Monitoring ML Workloads](#monitoring-ml-workloads)
12. [Summary and Best Practices](#summary-and-best-practices)

---

## Introduction

### ML Workloads Are Different

Traditional web applications run continuously and handle requests. ML workloads have unique characteristics:

**Training Jobs**:
- Batch workloads that run to completion
- Require GPUs for reasonable training times
- May run for hours or days
- Need checkpoint saving for fault tolerance
- Often distributed across multiple nodes

**Inference Services**:
- Stateless request/response pattern (like web apps)
- GPU acceleration for real-time inference
- Auto-scaling based on load
- A/B testing for model versions

### Why Kubernetes for ML?

1. **Resource management**: Schedule GPUs efficiently across teams
2. **Scalability**: Scale training from 1 to 100+ GPUs
3. **Reproducibility**: Define training jobs as code
4. **Multi-tenancy**: Isolate experiments and teams
5. **Standardization**: Consistent deployment across environments

### Learning Objectives

By the end of this lecture, you will:
- Run batch ML training jobs on Kubernetes
- Schedule workloads on GPU nodes
- Understand Kubernetes Operators for ML (PyTorchJob, TFJob)
- Install and configure Kubeflow components
- Run distributed training with Kubeflow
- Build ML pipelines for orchestration
- Deploy models for serving
- Monitor ML workloads in production

---

## Kubernetes Batch Workloads

### Jobs: Run-to-Completion Workloads

Unlike Pods (which restart on failure) or Deployments (which run continuously), **Jobs** run until successful completion.

```yaml
# training-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: mnist-training
spec:
  # Job configuration
  completions: 1          # Number of successful completions needed
  parallelism: 1         # Number of pods to run in parallel
  backoffLimit: 3        # Retry up to 3 times on failure

  template:
    metadata:
      labels:
        app: mnist-training
    spec:
      restartPolicy: Never  # Job pods should not auto-restart

      containers:
      - name: trainer
        image: pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime
        command:
          - python
          - train.py
          - --epochs=10
          - --batch-size=64

        resources:
          limits:
            memory: "8Gi"
            cpu: "4"
          requests:
            memory: "8Gi"
            cpu: "4"

        volumeMounts:
        - name: training-data
          mountPath: /data
        - name: model-output
          mountPath: /output

      volumes:
      - name: training-data
        persistentVolumeClaim:
          claimName: training-data-pvc
      - name: model-output
        persistentVolumeClaim:
          claimName: model-output-pvc
```

**Create and monitor the job**:

```bash
# Create job
kubectl apply -f training-job.yaml

# Check job status
kubectl get jobs
# NAME             COMPLETIONS   DURATION   AGE
# mnist-training   0/1           5s         5s

# Watch pods created by job
kubectl get pods --watch

# View logs
kubectl logs -f mnist-training-xxxxx

# Check job details
kubectl describe job mnist-training

# Delete job (and its pods)
kubectl delete job mnist-training
```

### CronJobs: Scheduled Training

Run training jobs on a schedule (like cron):

```yaml
# scheduled-retraining.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: daily-model-retrain
spec:
  # Schedule in cron format (minute hour day month weekday)
  schedule: "0 2 * * *"  # Every day at 2 AM

  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: OnFailure

          containers:
          - name: retrain
            image: my-ml-trainer:v1
            command:
              - python
              - retrain.py
              - --date=$(date +%Y%m%d)

            resources:
              limits:
                memory: "16Gi"
                cpu: "8"

          volumes:
          - name: data
            persistentVolumeClaim:
              claimName: training-data
```

```bash
# Create CronJob
kubectl apply -f scheduled-retraining.yaml

# List CronJobs
kubectl get cronjobs

# Manually trigger a job
kubectl create job --from=cronjob/daily-model-retrain manual-run-001

# View job history
kubectl get jobs --selector=job-name=daily-model-retrain

# Suspend CronJob (pause scheduling)
kubectl patch cronjob daily-model-retrain -p '{"spec":{"suspend":true}}'
```

---

## GPU Scheduling in Kubernetes

### Node Labels and GPU Discovery

Kubernetes discovers GPUs through device plugins (NVIDIA, AMD).

```bash
# Check nodes with GPUs
kubectl get nodes -o json | jq '.items[].status.capacity'

# Output shows GPU resources:
# {
#   "cpu": "48",
#   "memory": "196Gi",
#   "nvidia.com/gpu": "4",      ← 4 GPUs available
#   "pods": "110"
# }

# Label GPU nodes
kubectl label nodes gpu-node-1 accelerator=nvidia-tesla-v100
kubectl label nodes gpu-node-2 accelerator=nvidia-a100

# View GPU node details
kubectl describe node gpu-node-1 | grep -A 10 "Capacity"
```

### Requesting GPUs in Pods

```yaml
# gpu-training-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: gpu-training
spec:
  template:
    spec:
      restartPolicy: Never

      # Node selection
      nodeSelector:
        accelerator: nvidia-tesla-v100  # Schedule on specific GPU type

      containers:
      - name: trainer
        image: pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime

        command:
          - python
          - train_on_gpu.py

        resources:
          limits:
            nvidia.com/gpu: 1  # Request 1 GPU
            memory: "16Gi"
            cpu: "8"
          requests:
            nvidia.com/gpu: 1  # Must match limits for GPU
            memory: "16Gi"
            cpu: "8"

        env:
        - name: CUDA_VISIBLE_DEVICES
          value: "0"  # Use first GPU
```

**Multiple GPUs**:

```yaml
resources:
  limits:
    nvidia.com/gpu: 4  # Request 4 GPUs
  requests:
    nvidia.com/gpu: 4
```

### GPU Resource Quotas

Limit GPU usage per namespace:

```yaml
# gpu-quota.yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: gpu-quota
  namespace: ml-team
spec:
  hard:
    requests.nvidia.com/gpu: "8"  # Max 8 GPUs for this namespace
    limits.nvidia.com/gpu: "8"
```

---

## Kubernetes Operators for ML

### What Are Operators?

**Kubernetes Operators** extend Kubernetes with custom resources and controllers. For ML, operators provide higher-level abstractions for training jobs.

### Training Operators

The **Training Operator** (formerly Kubeflow Training Operator) provides CRDs for distributed training:

- **PyTorchJob**: Distributed PyTorch training
- **TFJob**: Distributed TensorFlow training
- **XGBoostJob**: Distributed XGBoost training
- **MPIJob**: MPI-based distributed training

### Installing Training Operator

```bash
# Install using kubectl
kubectl apply -k "github.com/kubeflow/training-operator/manifests/overlays/standalone"

# Verify installation
kubectl get pods -n kubeflow

# Check CRDs are created
kubectl get crd | grep kubeflow.org
# pytorchjobs.kubeflow.org
# tfjobs.kubeflow.org
# mxnetjobs.kubeflow.org
# xgboostjobs.kubeflow.org
```

### PyTorchJob Example

```yaml
# pytorch-distributed-job.yaml
apiVersion: kubeflow.org/v1
kind: PyTorchJob
metadata:
  name: pytorch-dist-mnist
spec:
  # Distributed training configuration
  pytorchReplicaSpecs:

    # Master replica (rank 0)
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
              - -m
              - torch.distributed.launch
              - --nproc_per_node=1
              - train_distributed.py

            resources:
              limits:
                nvidia.com/gpu: 1
                memory: "8Gi"
                cpu: "4"

    # Worker replicas (rank 1, 2, ...)
    Worker:
      replicas: 3  # 3 worker nodes
      restartPolicy: OnFailure
      template:
        spec:
          containers:
          - name: pytorch
            image: pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime
            command:
              - python
              - -m
              - torch.distributed.launch
              - --nproc_per_node=1
              - train_distributed.py

            resources:
              limits:
                nvidia.com/gpu: 1
                memory: "8Gi"
                cpu: "4"
```

**Managing PyTorchJobs**:

```bash
# Create PyTorchJob
kubectl apply -f pytorch-distributed-job.yaml

# List PyTorchJobs
kubectl get pytorchjobs
# NAME                   STATE     AGE
# pytorch-dist-mnist     Running   30s

# Get detailed status
kubectl describe pytorchjob pytorch-dist-mnist

# View logs from master
kubectl logs pytorch-dist-mnist-master-0

# View logs from workers
kubectl logs pytorch-dist-mnist-worker-0
kubectl logs pytorch-dist-mnist-worker-1

# Delete job
kubectl delete pytorchjob pytorch-dist-mnist
```

### TensorFlow Training

```yaml
# tensorflow-job.yaml
apiVersion: kubeflow.org/v1
kind: TFJob
metadata:
  name: tfjob-simple
spec:
  tfReplicaSpecs:

    # Parameter server
    PS:
      replicas: 1
      template:
        spec:
          containers:
          - name: tensorflow
            image: tensorflow/tensorflow:2.13.0-gpu
            command:
              - python
              - train.py
              - --job-type=ps

    # Chief worker
    Chief:
      replicas: 1
      template:
        spec:
          containers:
          - name: tensorflow
            image: tensorflow/tensorflow:2.13.0-gpu
            command:
              - python
              - train.py
              - --job-type=chief

            resources:
              limits:
                nvidia.com/gpu: 1

    # Workers
    Worker:
      replicas: 2
      template:
        spec:
          containers:
          - name: tensorflow
            image: tensorflow/tensorflow:2.13.0-gpu
            command:
              - python
              - train.py
              - --job-type=worker

            resources:
              limits:
                nvidia.com/gpu: 1
```

---

## Introduction to Kubeflow

### What Is Kubeflow?

**Kubeflow** is an open-source ML platform for Kubernetes that provides:
- End-to-end ML workflow orchestration
- Distributed training (PyTorch, TensorFlow)
- Hyperparameter tuning (Katib)
- Model serving (KServe)
- Pipelines for ML workflows
- Multi-user notebooks
- Experiment tracking

### Kubeflow Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Kubeflow Platform                  │
├─────────────────────────────────────────────────────┤
│                                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │ Notebooks│  │ Pipelines│  │  Katib   │          │
│  │  (JupyterHub)│ (Argo)   │(Hyperparams)│          │
│  └──────────┘  └──────────┘  └──────────┘          │
│                                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │ Training │  │ Serving  │  │Experiments│          │
│  │Operator  │  │ (KServe) │  │  (MLflow)│          │
│  └──────────┘  └──────────┘  └──────────┘          │
│                                                       │
├─────────────────────────────────────────────────────┤
│              Kubernetes Cluster                      │
└─────────────────────────────────────────────────────┘
```

### Kubeflow vs. Individual Tools

| Capability | Without Kubeflow | With Kubeflow |
|-----------|------------------|---------------|
| Training | Manual Job YAMLs | PyTorchJob/TFJob operators |
| Pipelines | Shell scripts | Kubeflow Pipelines (DAGs) |
| Notebooks | Local Jupyter | Multi-user JupyterHub |
| Hypertuning | Manual loops | Katib (automated) |
| Serving | Custom deployment | KServe (standard) |
| Tracking | Manual logging | Central experiment tracking |

---

## Installing Kubeflow

### Prerequisites

```bash
# Requirements:
# - Kubernetes 1.25+
# - kubectl configured
# - At least 12GB RAM, 4 CPUs, 50GB disk
# - (Optional) GPUs for training

# Verify cluster
kubectl cluster-info
kubectl get nodes
```

### Installation Methods

#### Option 1: Quick Install with Kustomize

```bash
# Clone Kubeflow manifests
git clone https://github.com/kubeflow/manifests.git
cd manifests

# Install all components (takes 5-10 minutes)
while ! kustomize build example | kubectl apply -f -; do
  echo "Retrying to apply resources"
  sleep 10
done

# Verify installation
kubectl get pods -n kubeflow
kubectl get pods -n istio-system
kubectl get pods -n auth
kubectl get pods -n cert-manager
kubectl get pods -n knative-serving
kubectl get pods -n kubeflow-user-example-com

# Wait for all pods to be running
kubectl wait --for=condition=Ready pods --all -n kubeflow --timeout=600s
```

#### Option 2: MiniKF (For Development)

```bash
# Install MiniKF on local machine (uses Vagrant + VirtualBox)
vagrant init arrikto/minikf
vagrant up

# Access at: http://10.10.10.10
```

#### Option 3: Managed Kubeflow (Cloud)

```bash
# Google Cloud AI Platform
# AWS: Amazon SageMaker (similar but not exactly Kubeflow)
# Azure: Azure ML (similar but not exactly Kubeflow)

# Example: GCP deployment
gcloud container clusters create kubeflow-cluster \
  --machine-type=n1-standard-8 \
  --num-nodes=3 \
  --zone=us-central1-a

# Then install Kubeflow manifests
```

### Accessing Kubeflow Dashboard

```bash
# Port-forward to access UI
kubectl port-forward -n istio-system svc/istio-ingressgateway 8080:80

# Access at: http://localhost:8080

# Default credentials (change immediately!):
# Email: user@example.com
# Password: 12341234
```

---

## Kubeflow Components

### 1. Central Dashboard

The main UI for accessing all Kubeflow features.

**Features**:
- Launch notebooks
- Create pipelines
- Monitor training jobs
- Manage experiments
- Access model serving

### 2. Notebooks (Multi-user Jupyter)

```yaml
# Create notebook via UI or YAML
apiVersion: kubeflow.org/v1
kind: Notebook
metadata:
  name: ml-notebook
  namespace: kubeflow-user-example-com
spec:
  template:
    spec:
      containers:
      - name: notebook
        image: jupyter/tensorflow-notebook:latest
        resources:
          limits:
            memory: "8Gi"
            cpu: "4"
            nvidia.com/gpu: "1"
        volumeMounts:
        - name: workspace
          mountPath: /home/jovyan

      volumes:
      - name: workspace
        persistentVolumeClaim:
          claimName: ml-notebook-workspace
```

**Access via UI**:
1. Navigate to **Notebooks** in dashboard
2. Click **New Notebook**
3. Select image (TensorFlow, PyTorch, etc.)
4. Configure resources (CPU, memory, GPU)
5. Click **Launch**

### 3. Kubeflow Pipelines

Define ML workflows as code using the Kubeflow Pipelines SDK.

```python
# simple_pipeline.py
import kfp
from kfp import dsl

@dsl.component
def preprocess_data(input_path: str, output_path: str):
    """Preprocess training data."""
    # Implementation
    pass

@dsl.component
def train_model(data_path: str, model_output: str, epochs: int = 10):
    """Train ML model."""
    # Implementation
    pass

@dsl.component
def evaluate_model(model_path: str, test_data: str) -> float:
    """Evaluate model accuracy."""
    # Implementation
    return accuracy

@dsl.pipeline(
    name="ML Training Pipeline",
    description="End-to-end ML training workflow"
)
def ml_pipeline(
    data_path: str = "/data/train",
    epochs: int = 10
):
    # Define pipeline DAG
    preprocess_task = preprocess_data(
        input_path=data_path,
        output_path="/data/processed"
    )

    train_task = train_model(
        data_path=preprocess_task.outputs["output_path"],
        model_output="/models/trained",
        epochs=epochs
    )
    train_task.set_gpu_limit(1)  # Request GPU

    evaluate_task = evaluate_model(
        model_path=train_task.outputs["model_output"],
        test_data="/data/test"
    )

# Compile pipeline
if __name__ == "__main__":
    kfp.compiler.Compiler().compile(ml_pipeline, "pipeline.yaml")
```

**Upload and run**:

```bash
# Install SDK
pip install kfp

# Compile pipeline
python simple_pipeline.py

# Upload via UI or CLI
kfp pipeline upload -p "ML Pipeline" pipeline.yaml

# Run pipeline
kfp run submit -e "my-experiment" -r "run-001" pipeline.yaml
```

### 4. Katib (Hyperparameter Tuning)

```yaml
# katib-experiment.yaml
apiVersion: kubeflow.org/v1beta1
kind: Experiment
metadata:
  name: tune-learning-rate
spec:
  objective:
    type: maximize
    goal: 0.99
    objectiveMetricName: accuracy

  algorithm:
    algorithmName: random  # or: grid, bayesian

  parameters:
  - name: learning_rate
    parameterType: double
    feasibleSpace:
      min: "0.0001"
      max: "0.1"
  - name: batch_size
    parameterType: int
    feasibleSpace:
      min: "16"
      max: "128"

  maxTrialCount: 20
  parallelTrialCount: 3

  trialTemplate:
    primaryContainerName: training
    trialSpec:
      apiVersion: batch/v1
      kind: Job
      spec:
        template:
          spec:
            containers:
            - name: training
              image: my-trainer:latest
              command:
                - python
                - train.py
                - --lr=${trialParameters.learningRate}
                - --batch-size=${trialParameters.batchSize}
```

```bash
# Create experiment
kubectl apply -f katib-experiment.yaml

# Monitor trials
kubectl get experiments -n kubeflow-user-example-com

# View trial results
kubectl get trials -n kubeflow-user-example-com

# Get best trial
kubectl describe experiment tune-learning-rate
```

---

## Distributed Training with Kubeflow

### PyTorchJob with Kubeflow

```yaml
# kubeflow-pytorch-job.yaml
apiVersion: kubeflow.org/v1
kind: PyTorchJob
metadata:
  name: imagenet-training
  namespace: kubeflow-user-example-com
spec:
  pytorchReplicaSpecs:

    Master:
      replicas: 1
      restartPolicy: OnFailure
      template:
        metadata:
          annotations:
            sidecar.istio.io/inject: "false"  # Disable Istio for training
        spec:
          containers:
          - name: pytorch
            image: my-pytorch-trainer:v1
            command:
              - python
              - -m
              - torch.distributed.launch
              - --nproc_per_node=4  # 4 GPUs per node
              - train.py
              - --epochs=100
              - --batch-size=256

            resources:
              limits:
                nvidia.com/gpu: 4
                memory: "64Gi"
                cpu: "32"

            volumeMounts:
            - name: data
              mountPath: /data
            - name: models
              mountPath: /models

          volumes:
          - name: data
            persistentVolumeClaim:
              claimName: imagenet-data
          - name: models
            persistentVolumeClaim:
              claimName: model-storage

    Worker:
      replicas: 3  # 3 additional worker nodes
      restartPolicy: OnFailure
      template:
        metadata:
          annotations:
            sidecar.istio.io/inject: "false"
        spec:
          containers:
          - name: pytorch
            image: my-pytorch-trainer:v1
            command:
              - python
              - -m
              - torch.distributed.launch
              - --nproc_per_node=4
              - train.py
              - --epochs=100
              - --batch-size=256

            resources:
              limits:
                nvidia.com/gpu: 4
                memory: "64Gi"
                cpu: "32"

            volumeMounts:
            - name: data
              mountPath: /data
            - name: models
              mountPath: /models

          volumes:
          - name: data
            persistentVolumeClaim:
              claimName: imagenet-data
          - name: models
            persistentVolumeClaim:
              claimName: model-storage
```

**This setup**:
- 4 nodes (1 master + 3 workers)
- 4 GPUs per node = 16 total GPUs
- Distributed data-parallel training

---

## ML Pipeline Orchestration

### Example: End-to-End Pipeline

```python
# complete_ml_pipeline.py
import kfp
from kfp import dsl

@dsl.component(base_image="python:3.9")
def download_data(dataset_url: str, output_path: dsl.OutputPath(str)):
    """Download dataset from URL."""
    import urllib.request
    urllib.request.urlretrieve(dataset_url, output_path)

@dsl.component(base_image="pytorch/pytorch:2.0.1")
def train_model(
    data_path: dsl.InputPath(str),
    model_path: dsl.OutputPath(str),
    epochs: int,
    learning_rate: float
) -> float:
    """Train PyTorch model."""
    import torch
    # Training code here
    accuracy = 0.92  # Placeholder
    torch.save(model, model_path)
    return accuracy

@dsl.component(base_image="python:3.9")
def deploy_model(
    model_path: dsl.InputPath(str),
    accuracy: float,
    min_accuracy: float = 0.90
):
    """Deploy model if accuracy threshold met."""
    if accuracy >= min_accuracy:
        # Deploy to serving infrastructure
        print(f"Deploying model with accuracy {accuracy}")
    else:
        raise ValueError(f"Model accuracy {accuracy} below threshold {min_accuracy}")

@dsl.pipeline(
    name="Complete ML Pipeline",
    description="Download, train, evaluate, and deploy"
)
def complete_pipeline(
    dataset_url: str = "https://example.com/data.tar.gz",
    epochs: int = 10,
    learning_rate: float = 0.001,
    min_accuracy: float = 0.90
):
    # Step 1: Download data
    download_task = download_data(dataset_url=dataset_url)

    # Step 2: Train model
    train_task = train_model(
        data_path=download_task.outputs["output_path"],
        epochs=epochs,
        learning_rate=learning_rate
    )
    train_task.set_gpu_limit(1)
    train_task.set_memory_limit("16Gi")

    # Step 3: Deploy if accuracy sufficient
    deploy_task = deploy_model(
        model_path=train_task.outputs["model_path"],
        accuracy=train_task.outputs["Output"],
        min_accuracy=min_accuracy
    )

# Compile and upload
if __name__ == "__main__":
    kfp.compiler.Compiler().compile(complete_pipeline, "complete_pipeline.yaml")
```

---

## Model Serving with Kubeflow

### KServe (Formerly KFServing)

```yaml
# model-serving.yaml
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: pytorch-model
spec:
  predictor:
    pytorch:
      storageUri: "s3://my-bucket/models/resnet50"
      resources:
        limits:
          nvidia.com/gpu: 1
          memory: "8Gi"
          cpu: "4"
        requests:
          nvidia.com/gpu: 1
          memory: "8Gi"
          cpu: "4"

      # Auto-scaling configuration
      minReplicas: 1
      maxReplicas: 5
```

```bash
# Deploy inference service
kubectl apply -f model-serving.yaml

# Get endpoint
kubectl get inferenceservice pytorch-model

# Test inference
curl -X POST http://pytorch-model.kubeflow.example.com/v1/models/pytorch-model:predict \
  -H "Content-Type: application/json" \
  -d '{"instances": [[1.0, 2.0, 3.0]]}'
```

---

## Monitoring ML Workloads

### Viewing Training Job Status

```bash
# List all PyTorchJobs
kubectl get pytorchjobs -n kubeflow-user-example-com

# Get detailed status
kubectl describe pytorchjob my-training-job

# View logs from all replicas
kubectl logs -l pytorch-job-name=my-training-job -n kubeflow-user-example-com

# Stream logs
kubectl logs -f my-training-job-master-0 -n kubeflow-user-example-com
```

### Metrics and Dashboards

Kubeflow integrates with Prometheus and Grafana for monitoring:

```bash
# Access Grafana dashboard
kubectl port-forward -n kubeflow svc/grafana 3000:3000

# Pre-configured dashboards show:
# - GPU utilization
# - Training job success rates
# - Pipeline execution times
# - Model serving latency
```

---

## Summary and Best Practices

### Key Takeaways

1. **Kubernetes Jobs** run ML training to completion (not continuous services)
2. **GPU scheduling** requires node labels and resource requests
3. **Training Operators** (PyTorchJob, TFJob) simplify distributed training
4. **Kubeflow** provides end-to-end ML platform on Kubernetes
5. **Kubeflow Pipelines** orchestrate complex ML workflows
6. **Katib** automates hyperparameter tuning
7. **KServe** standardizes model serving

### Best Practices

```yaml
# 1. Always set resource limits for training jobs
resources:
  limits:
    nvidia.com/gpu: 1
    memory: "16Gi"
    cpu: "8"
  requests:  # Must match limits for GPUs
    nvidia.com/gpu: 1
    memory: "16Gi"
    cpu: "8"

# 2. Use node selectors for GPU types
nodeSelector:
  accelerator: nvidia-a100

# 3. Save checkpoints to persistent storage
volumeMounts:
- name: checkpoints
  mountPath: /checkpoints

# 4. Set retry policies
restartPolicy: OnFailure
backoffLimit: 3

# 5. Use Kubeflow Operators instead of raw Jobs
# ✅ Good: PyTorchJob handles distributed setup
# ❌ Bad: Manual Job with custom distributed scripts
```

### Common Pitfalls to Avoid

```bash
# ❌ Don't request GPUs without limits
# This can cause scheduling issues
resources:
  requests:
    nvidia.com/gpu: 1  # Missing limits!

# ✅ Always match requests and limits for GPUs
resources:
  requests:
    nvidia.com/gpu: 1
  limits:
    nvidia.com/gpu: 1

# ❌ Don't use hostPath for training data
volumes:
- name: data
  hostPath:  # Not portable!
    path: /mnt/data

# ✅ Use PersistentVolumeClaims
volumes:
- name: data
  persistentVolumeClaim:
    claimName: training-data

# ❌ Don't ignore resource quotas
# Will cause mysterious scheduling failures

# ✅ Check namespace quotas
kubectl describe resourcequota -n my-namespace
```

### Troubleshooting Checklist

```bash
# Training job not starting?
kubectl describe pytorchjob my-job  # Check events
kubectl get pods -l pytorch-job-name=my-job  # Check pod status
kubectl describe pod my-job-master-0  # Check pod events

# GPU not detected?
kubectl describe node gpu-node-1 | grep nvidia.com/gpu  # Check GPU capacity
kubectl get pods -A | grep nvidia-device-plugin  # Check device plugin running

# Kubeflow dashboard not accessible?
kubectl get pods -n kubeflow  # Check all pods running
kubectl get svc -n istio-system istio-ingressgateway  # Check ingress
```

### Next Steps

You now understand ML workloads on Kubernetes! Practice by:
1. Running a simple training Job with GPUs
2. Installing Kubeflow on a test cluster
3. Creating a PyTorchJob for distributed training
4. Building a simple Kubeflow Pipeline
5. Setting up model serving with KServe

Continue to **Exercise 07: ML Workloads** to apply these concepts hands-on!

---

**Word Count**: ~4,900 words
**Estimated Reading Time**: 25-30 minutes
