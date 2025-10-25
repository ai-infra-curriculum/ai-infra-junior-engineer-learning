# Architecture Documentation: Production ML System

**Project:** Project 05 - Production ML System (Capstone)
**Version:** 1.0
**Last Updated:** October 18, 2025

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Overview](#system-overview)
3. [Architecture Diagrams](#architecture-diagrams)
4. [Component Details](#component-details)
5. [Data Flow](#data-flow)
6. [Deployment Architecture](#deployment-architecture)
7. [Security Architecture](#security-architecture)
8. [Scalability & Performance](#scalability--performance)
9. [Disaster Recovery](#disaster-recovery)
10. [Technology Decisions](#technology-decisions)

---

## Executive Summary

This document describes the architecture of a production-ready ML system that integrates model serving, orchestration, ML pipelines, and observability into a unified platform capable of:

- Serving 1000+ predictions per second
- Maintaining 99.9% uptime
- Automatically training and deploying models
- Scaling from 3 to 20 replicas based on demand
- Providing complete observability across all components

### Key Architectural Principles

1. **Cloud-Native**: Kubernetes-based, containerized, horizontally scalable
2. **GitOps**: Infrastructure and configuration as code
3. **Security by Default**: Authentication, encryption, least privilege
4. **Observability First**: Metrics, logs, and traces for all components
5. **Automation**: CI/CD, ML lifecycle, scaling, recovery
6. **Resilience**: High availability, fault tolerance, auto-healing

---

## System Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Production ML System                        │
│                                                                     │
│  ┌────────────────┐                                                │
│  │  External      │                                                │
│  │  Clients       │                                                │
│  │ (Web, Mobile,  │                                                │
│  │  API)          │                                                │
│  └───────┬────────┘                                                │
│          │ HTTPS (TLS)                                             │
│          ▼                                                          │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │              Ingress Layer                               │     │
│  │  ┌────────────────────────────────────────────────────┐  │     │
│  │  │  NGINX Ingress Controller                          │  │     │
│  │  │  - TLS Termination (cert-manager)                  │  │     │
│  │  │  - Rate Limiting (100 req/min global)              │  │     │
│  │  │  - Authentication (API Key validation)             │  │     │
│  │  │  - Path Routing (/predict, /health, /metrics)      │  │     │
│  │  └────────────────────────────────────────────────────┘  │     │
│  └──────────────────────┬───────────────────────────────────┘     │
│                         ▼                                          │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │         Application Layer (Kubernetes Cluster)           │     │
│  │                                                           │     │
│  │  ┌────────────────────────────────────────────────────┐  │     │
│  │  │  ML API Deployment (Project 1)                     │  │     │
│  │  │  ┌──────┐  ┌──────┐  ┌──────┐  ...  ┌──────┐     │  │     │
│  │  │  │ Pod 1│  │ Pod 2│  │ Pod 3│       │ Pod N│     │  │     │
│  │  │  │Flask │  │Flask │  │Flask │       │Flask │     │  │     │
│  │  │  │+Model│  │+Model│  │+Model│       │+Model│     │  │     │
│  │  │  └──────┘  └──────┘  └──────┘       └──────┘     │  │     │
│  │  │                                                     │  │     │
│  │  │  - Horizontal Pod Autoscaler (HPA)                 │  │     │
│  │  │  - Min: 3 replicas, Max: 20 replicas               │  │     │
│  │  │  - Scale on CPU (70%) and Memory (80%)             │  │     │
│  │  │  - Rolling update strategy (maxSurge=1, max=0)     │  │     │
│  │  └────────────────────────────────────────────────────┘  │     │
│  │                                                           │     │
│  │  ┌────────────────────────────────────────────────────┐  │     │
│  │  │  ML Pipeline Layer (Project 3)                     │  │     │
│  │  │  ┌──────────────────────────────────────────────┐  │  │     │
│  │  │  │  Airflow Scheduler                           │  │  │     │
│  │  │  │  - ml_training_pipeline DAG (weekly)         │  │  │     │
│  │  │  │  - data_validation_pipeline DAG (daily)      │  │  │     │
│  │  │  └──────────────────────────────────────────────┘  │  │     │
│  │  │                                                     │  │     │
│  │  │  Pipeline Flow:                                     │  │     │
│  │  │  [Data Ingestion] → [Validation] → [Preprocessing] │  │     │
│  │  │         ↓                                           │  │     │
│  │  │  [Feature Engineering] → [Training] → [Evaluation] │  │     │
│  │  │         ↓                                           │  │     │
│  │  │  [MLflow Registry] → [Deploy to Staging/Prod]      │  │     │
│  │  └────────────────────────────────────────────────────┘  │     │
│  │                                                           │     │
│  │  ┌────────────────────────────────────────────────────┐  │     │
│  │  │  Monitoring & Observability (Project 4)            │  │     │
│  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐           │  │     │
│  │  │  │Prometheus│ │ Grafana  │ │ELK Stack │           │  │     │
│  │  │  │(Metrics) │ │(Dashboards)│(Logs)    │           │  │     │
│  │  │  └──────────┘ └──────────┘ └──────────┘           │  │     │
│  │  │  ┌────────────────┐                                │  │     │
│  │  │  │ Alertmanager   │                                │  │     │
│  │  │  │ (Notifications)│                                │  │     │
│  │  │  └────────────────┘                                │  │     │
│  │  └────────────────────────────────────────────────────┘  │     │
│  └───────────────────────┬───────────────────────────────────┘     │
│                          ▼                                         │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │              Data & Storage Layer                        │     │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │     │
│  │  │PostgreSQL│ │  MinIO/  │ │   DVC    │ │  MLflow  │   │     │
│  │  │(MLflow   │ │   S3     │ │ (Data    │ │ Registry │   │     │
│  │  │ metadata)│ │(Artifacts)│ │ Versions)│ │ (Models) │   │     │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │     │
│  └──────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────┘
```

### Component Summary

| Layer | Components | Purpose |
|-------|------------|---------|
| **Ingress** | NGINX Ingress, cert-manager | TLS termination, routing, rate limiting |
| **Application** | Flask API, Model serving | Serve predictions to clients |
| **ML Pipeline** | Airflow, MLflow, DVC | Train, version, and deploy models |
| **Monitoring** | Prometheus, Grafana, ELK | Observe system health and performance |
| **Data** | PostgreSQL, S3/MinIO | Store metadata, models, and datasets |
| **Security** | RBAC, Secrets, NetworkPolicies | Protect system and data |

---

## Architecture Diagrams

### Logical Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Logical Layers                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  Presentation Layer                                             │
│  - REST API (OpenAPI/Swagger)                                   │
│  - API Gateway (NGINX Ingress)                                  │
│  - Authentication & Authorization                               │
└─────────────────────────────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  Business Logic Layer                                           │
│  - Model Inference (PyTorch/TensorFlow)                         │
│  - Input Validation & Preprocessing                             │
│  - Response Formatting                                          │
│  - Error Handling                                               │
└─────────────────────────────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  ML Operations Layer                                            │
│  - Model Training (Airflow DAGs)                                │
│  - Model Versioning (MLflow)                                    │
│  - Model Deployment (Kubernetes Operator)                       │
│  - A/B Testing Framework                                        │
└─────────────────────────────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  Data Layer                                                     │
│  - Model Registry (MLflow + PostgreSQL)                         │
│  - Artifact Storage (S3/MinIO)                                  │
│  - Data Versioning (DVC)                                        │
│  - Feature Store (optional)                                     │
└─────────────────────────────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  Infrastructure Layer                                           │
│  - Container Orchestration (Kubernetes)                         │
│  - Service Mesh (optional)                                      │
│  - Load Balancing                                               │
│  - Auto-scaling (HPA)                                           │
└─────────────────────────────────────────────────────────────────┘
```

### Network Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Network Topology                         │
└─────────────────────────────────────────────────────────────────┘

Internet
    │
    ▼
┌─────────────────────────┐
│  Cloud Load Balancer    │ (Layer 4/7)
│  - DDoS Protection      │
│  - SSL Offloading       │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│  Kubernetes Cluster                                             │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  Ingress Namespace                                        │ │
│  │  ┌──────────────────────────────────────────────┐         │ │
│  │  │  NGINX Ingress Controller                    │         │ │
│  │  │  - External LoadBalancer IP: XXX.XXX.XXX.XXX │         │ │
│  │  │  - Listens on ports 80 (HTTP) and 443 (HTTPS)│         │ │
│  │  └──────────────────────────────────────────────┘         │ │
│  └───────────────────────┬───────────────────────────────────┘ │
│                          │                                     │
│  ┌───────────────────────┼───────────────────────────────────┐ │
│  │  ml-system Namespace  │                                   │ │
│  │                       ▼                                   │ │
│  │  ┌──────────────────────────────────────────────┐        │ │
│  │  │  ml-api Service (ClusterIP)                  │        │ │
│  │  │  IP: 10.96.0.100                             │        │ │
│  │  │  Port: 80 → targetPort: 5000                 │        │ │
│  │  └──────────┬───────────────────────────────────┘        │ │
│  │             │                                             │ │
│  │             ├─────► Pod 1 (10.244.1.10:5000)             │ │
│  │             ├─────► Pod 2 (10.244.2.11:5000)             │ │
│  │             └─────► Pod N (10.244.3.12:5000)             │ │
│  │                                                           │ │
│  │  NetworkPolicy:                                          │ │
│  │  - Allow ingress from ingress-nginx namespace            │ │
│  │  - Allow ingress from monitoring namespace               │ │
│  │  - Allow egress to postgres (port 5432)                  │ │
│  │  - Allow egress to mlflow (port 5000)                    │ │
│  │  - Allow egress to DNS (port 53)                         │ │
│  │  - Deny all other traffic                                │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  monitoring Namespace                                     │ │
│  │  - Prometheus (scrapes metrics from all namespaces)       │ │
│  │  - Grafana (visualizes metrics)                           │ │
│  │  - Alertmanager (sends alerts)                            │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  data Namespace                                           │ │
│  │  - PostgreSQL (MLflow backend)                            │ │
│  │  - MinIO/S3 (artifact storage)                            │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. ML API Service (Project 1 Integration)

**Purpose:** Serve ML model predictions via REST API

**Technology Stack:**
- Flask or FastAPI
- PyTorch or TensorFlow
- Gunicorn (production WSGI server)
- Prometheus client library

**Key Features:**
- RESTful endpoints (`/predict`, `/health`, `/metrics`)
- Model loading from MLflow registry
- Request validation and preprocessing
- Response formatting
- Error handling and logging
- Metrics instrumentation

**Deployment:**
- Containerized with Docker
- Deployed as Kubernetes Deployment
- 3-20 replicas (HPA)
- Resource limits: CPU 1000m, Memory 2Gi
- Health checks: liveness and readiness probes

**Configuration:**
- Model version from ConfigMap
- API keys from Secrets
- MLflow URI from environment variables

**Example Code Stub:**
```python
# TODO: Implement model loading from MLflow
# TODO: Add request validation
# TODO: Implement prediction endpoint
# TODO: Add Prometheus metrics
# TODO: Configure health checks
```

---

### 2. Kubernetes Orchestration (Project 2 Integration)

**Purpose:** Orchestrate, scale, and manage containerized applications

**Components:**
- **Deployment:** Manages API pods, ensures desired state
- **Service:** Load balances traffic to pods (ClusterIP)
- **Ingress:** External access with TLS termination
- **HPA:** Auto-scales based on CPU/memory
- **ConfigMap:** Stores configuration
- **Secret:** Stores sensitive data

**Deployment Strategy:**
- Rolling update (maxSurge: 1, maxUnavailable: 0)
- Zero-downtime deployments
- Automatic rollback on health check failures

**Auto-Scaling:**
```yaml
# TODO: Configure HPA
# Min replicas: 3
# Max replicas: 20
# Target CPU: 70%
# Target Memory: 80%
```

**High Availability:**
- Pod anti-affinity (spread across nodes)
- Node affinity (prefer nodes with GPUs if applicable)
- Pod disruption budget (min available: 2)

---

### 3. ML Pipeline (Project 3 Integration)

**Purpose:** Automate model training, evaluation, and deployment

**Components:**

#### Airflow DAG: `ml_training_pipeline`

**Schedule:** Weekly (every Sunday at 2 AM UTC)

**Tasks:**
1. **data_ingestion** - Fetch latest data from source
2. **data_validation** - Run Great Expectations checks
3. **data_preprocessing** - Clean and transform data
4. **feature_engineering** - Extract features
5. **model_training** - Train model with hyperparameter tuning
6. **model_evaluation** - Evaluate on test set
7. **model_registration** - Register in MLflow if performance > threshold
8. **deploy_to_staging** - Deploy to staging environment
9. **notify_team** - Send Slack notification

**Data Flow:**
```
Data Source → DVC → Validation → Preprocessing → Training
    ↓
MLflow Experiment → Model Registry → Deployment
```

**Model Versioning:**
- All models versioned in MLflow
- Git SHA tagged for reproducibility
- Dataset version tracked with DVC
- Hyperparameters logged

**Deployment Automation:**
```python
# TODO: Implement automated deployment
# TODO: Update ConfigMap with new model version
# TODO: Trigger rolling restart of API pods
# TODO: Monitor deployment health
```

---

### 4. Monitoring & Observability (Project 4 Integration)

**Purpose:** Provide visibility into system health and performance

#### Prometheus (Metrics)

**Metrics Collected:**

| Metric | Type | Description |
|--------|------|-------------|
| `http_requests_total` | Counter | Total HTTP requests |
| `http_request_duration_seconds` | Histogram | Request latency |
| `http_request_errors_total` | Counter | Failed requests |
| `model_prediction_duration_seconds` | Histogram | Inference latency |
| `model_predictions_total` | Counter | Total predictions |
| `model_version` | Gauge | Current model version |
| `pod_cpu_usage` | Gauge | CPU usage per pod |
| `pod_memory_usage` | Gauge | Memory usage per pod |

**Scrape Configuration:**
```yaml
# TODO: Configure Prometheus to scrape ml-api pods
# TODO: Set up ServiceMonitor for auto-discovery
# TODO: Configure retention (30 days)
```

#### Grafana (Dashboards)

**Dashboards:**
1. **API Overview** - Request rate, latency, errors
2. **Infrastructure** - CPU, memory, disk, network
3. **ML Metrics** - Predictions/sec, inference latency, model version
4. **SLO Dashboard** - Uptime, error budget, SLI tracking

**Alerting:**
```yaml
# TODO: Configure alerts for:
# - High error rate (>1%)
# - High latency (P95 >500ms)
# - Low replica count (<3)
# - Disk space low (<10%)
```

#### ELK Stack (Logging)

**Log Collection:**
- Filebeat: Collects logs from pods
- Logstash: Parses and transforms logs
- Elasticsearch: Stores logs (30-day retention)
- Kibana: Visualizes and searches logs

**Log Format (Structured JSON):**
```json
{
  "timestamp": "2025-10-18T12:34:56Z",
  "level": "INFO",
  "service": "ml-api",
  "pod": "ml-api-7d8f9c6b5-abc12",
  "trace_id": "a1b2c3d4",
  "message": "Prediction completed",
  "duration_ms": 87,
  "model_version": "12"
}
```

---

### 5. Data & Storage Layer

#### PostgreSQL (MLflow Backend)

**Purpose:** Store MLflow experiment metadata and model registry

**Configuration:**
- Replicated (primary + 2 replicas)
- Automatic failover
- Daily backups to S3/GCS
- Encrypted at rest

**Schema:**
```sql
-- TODO: MLflow database schema
-- Tables: experiments, runs, metrics, params, tags, models
```

#### MinIO/S3 (Artifact Storage)

**Purpose:** Store model artifacts, datasets, logs

**Buckets:**
- `ml-models-production` - Production model artifacts
- `ml-models-staging` - Staging model artifacts
- `ml-datasets` - Training datasets
- `ml-backups` - System backups

**Lifecycle Policies:**
- Staging models: Delete after 30 days
- Production models: Keep indefinitely
- Datasets: Transition to cold storage after 90 days
- Backups: Keep for 30 days

#### DVC (Data Version Control)

**Purpose:** Version datasets and track lineage

**Configuration:**
```yaml
# TODO: Configure DVC remote storage
# TODO: Set up data versioning workflow
# TODO: Document dataset versions
```

---

## Data Flow

### Prediction Request Flow

```
1. Client → HTTPS Request → NGINX Ingress
   ├─ TLS Termination
   ├─ Rate Limiting Check
   ├─ API Key Validation
   └─ Route to Service
       ▼
2. Service → Load Balance → API Pod
   ├─ Readiness Check
   └─ Forward Request
       ▼
3. API Pod → Process Request
   ├─ Validate Input (file type, size)
   ├─ Preprocess (resize, normalize)
   ├─ Load Model (from cache or MLflow)
   ├─ Run Inference
   ├─ Format Response
   └─ Log Metrics
       ▼
4. Response → Service → Ingress → Client
   └─ Include headers: X-Model-Version, X-Request-ID
```

**Latency Breakdown (Target):**
- Ingress: <10ms
- Preprocessing: <20ms
- Model inference: <100ms
- Postprocessing: <10ms
- **Total (P95): <500ms**

### Model Training & Deployment Flow

```
┌──────────────────────────────────────────────────────────────┐
│  Weekly Schedule (Sunday 2 AM UTC) or Manual Trigger         │
└────────────────────────┬─────────────────────────────────────┘
                         ▼
┌──────────────────────────────────────────────────────────────┐
│  Airflow DAG: ml_training_pipeline                           │
├──────────────────────────────────────────────────────────────┤
│  Task 1: data_ingestion                                      │
│    - Fetch latest data from source                           │
│    - Store in DVC-tracked directory                          │
│    - Tag with version: YYYY-MM-DD-HHMMSS                     │
│                                                               │
│  Task 2: data_validation                                     │
│    - Run Great Expectations checks                           │
│    - Validate schema, distributions, ranges                  │
│    - If validation fails → Alert team, stop pipeline         │
│                                                               │
│  Task 3: data_preprocessing                                  │
│    - Clean data (remove nulls, outliers)                     │
│    - Split: train (70%), val (15%), test (15%)               │
│    - Save splits with DVC                                    │
│                                                               │
│  Task 4: feature_engineering                                 │
│    - Extract features                                        │
│    - Normalize/scale                                         │
│    - Save feature transformers                               │
│                                                               │
│  Task 5: model_training                                      │
│    - Train model with hyperparameter tuning                  │
│    - Log metrics, params, artifacts to MLflow                │
│    - Save best model checkpoint                              │
│                                                               │
│  Task 6: model_evaluation                                    │
│    - Evaluate on test set                                    │
│    - Metrics: accuracy, precision, recall, F1                │
│    - Compare to current production model                     │
│    - If accuracy < threshold (85%) → Alert, stop             │
│                                                               │
│  Task 7: model_registration                                  │
│    - Register model in MLflow Model Registry                 │
│    - Tag: "Staging"                                          │
│    - Metadata: dataset version, hyperparameters, metrics     │
│                                                               │
│  Task 8: deploy_to_staging                                   │
│    - Update staging ConfigMap with new model version         │
│    - Trigger rolling restart of staging pods                 │
│    - Wait for pods to be ready                               │
│    - Run smoke tests                                         │
│    - If tests fail → Alert, rollback                         │
│                                                               │
│  Task 9: notify_team                                         │
│    - Send Slack notification with results                    │
│    - Include: model version, metrics, staging URL            │
│    - Request manual approval for production                  │
└──────────────────────────────────────────────────────────────┘
                         ▼
┌──────────────────────────────────────────────────────────────┐
│  Manual Approval (via Slack, UI, or CLI)                     │
│    - Team lead reviews metrics                               │
│    - Approves or rejects production deployment               │
└────────────────────────┬─────────────────────────────────────┘
                         ▼ (if approved)
┌──────────────────────────────────────────────────────────────┐
│  Production Deployment (Canary Strategy)                     │
├──────────────────────────────────────────────────────────────┤
│  1. Update production ConfigMap (new model version)          │
│  2. Deploy canary pods (10% of traffic)                      │
│  3. Monitor metrics for 10 minutes:                          │
│     - Error rate < 0.1%                                      │
│     - Latency P95 < 500ms                                    │
│     - No crashes                                             │
│  4. If metrics healthy:                                      │
│     - Gradually shift traffic: 10% → 50% → 100%             │
│     - Tag model "Production" in MLflow                       │
│     - Notify team of successful deployment                   │
│  5. If metrics unhealthy:                                    │
│     - Rollback to previous version                           │
│     - Alert team of failure                                  │
│     - Keep model in "Staging"                                │
└──────────────────────────────────────────────────────────────┘
```

---

## Deployment Architecture

### Multi-Environment Strategy

```
┌─────────────────────────────────────────────────────────────────┐
│                      Environments                               │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│   Development        │  │   Staging            │  │   Production         │
├──────────────────────┤  ├──────────────────────┤  ├──────────────────────┤
│ - Local (Minikube)   │  │ - Cloud (GKE/EKS)    │  │ - Cloud (GKE/EKS)    │
│ - 1 node             │  │ - 3 nodes            │  │ - 5+ nodes           │
│ - No HA              │  │ - HA enabled         │  │ - Multi-zone HA      │
│ - No TLS             │  │ - TLS (staging cert) │  │ - TLS (prod cert)    │
│ - Test data          │  │ - Anonymized data    │  │ - Real data          │
│ - Debug logging      │  │ - Info logging       │  │ - Warn logging       │
│ - No monitoring      │  │ - Basic monitoring   │  │ - Full monitoring    │
│ - Manual deploy      │  │ - Auto deploy        │  │ - Manual approval    │
└──────────────────────┘  └──────────────────────┘  └──────────────────────┘
```

### Deployment Workflow (GitOps)

```
Developer → git commit → git push
    ▼
GitHub Repository
    ▼
┌──────────────────────────────────────────┐
│  CI Pipeline (GitHub Actions)            │
│  1. Code quality checks                  │
│  2. Unit tests                           │
│  3. Security scanning                    │
│  4. Docker build                         │
│  5. Image push (tag: git SHA)            │
└──────────────┬───────────────────────────┘
               ▼
    ┌──────────────────┐
    │ Pull Request?    │
    └────┬─────────┬───┘
         │ Yes     │ No (merged)
         │         ▼
         │    ┌────────────────────────────┐
         │    │  CD Pipeline (Staging)     │
         │    │  1. Deploy to staging      │
         │    │  2. Run smoke tests        │
         │    │  3. Run integration tests  │
         │    │  4. Notify team            │
         │    └────────────────────────────┘
         │         │
         │         ▼
         │    ┌────────────────────────────┐
         │    │  Manual Approval Required  │
         │    │  (via GitHub UI)           │
         │    └──────────┬─────────────────┘
         │               ▼
         │    ┌────────────────────────────┐
         │    │  CD Pipeline (Production)  │
         │    │  1. Canary deployment      │
         │    │  2. Monitor metrics        │
         │    │  3. Gradual rollout        │
         │    │  4. Notify team            │
         │    └────────────────────────────┘
         ▼
   Preview deployment (ephemeral)
```

---

## Security Architecture

### Defense in Depth

```
┌─────────────────────────────────────────────────────────────────┐
│  Layer 1: Network Security                                      │
│  - Cloud firewall rules (whitelist IPs)                         │
│  - DDoS protection                                              │
│  - Rate limiting (100 req/min global)                           │
└─────────────────────────────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 2: Transport Security                                    │
│  - TLS 1.2+ (cert-manager + Let's Encrypt)                      │
│  - Strong ciphers only                                          │
│  - HSTS headers                                                 │
└─────────────────────────────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 3: Application Security                                  │
│  - API key authentication                                       │
│  - Input validation (file type, size, content)                  │
│  - Output encoding                                              │
│  - Error handling (no info disclosure)                          │
└─────────────────────────────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 4: Container Security                                    │
│  - Non-root user                                                │
│  - Read-only root filesystem                                    │
│  - No privileged containers                                     │
│  - Image scanning (Trivy)                                       │
│  - Pod Security Standards (restricted)                          │
└─────────────────────────────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 5: Network Policies                                      │
│  - Default deny ingress/egress                                  │
│  - Explicit allow rules only                                    │
│  - Namespace isolation                                          │
└─────────────────────────────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 6: Secrets Management                                    │
│  - Kubernetes Secrets (encrypted at rest)                       │
│  - HashiCorp Vault (optional)                                   │
│  - No secrets in code or Git                                    │
│  - Least privilege access                                       │
└─────────────────────────────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 7: Access Control (RBAC)                                 │
│  - ServiceAccount per application                               │
│  - Minimal permissions (get, list only)                         │
│  - No cluster-admin usage                                       │
│  - Audit logging enabled                                        │
└─────────────────────────────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 8: Data Security                                         │
│  - Encryption at rest (cloud provider managed keys)             │
│  - Encryption in transit (TLS)                                  │
│  - Data retention policies                                      │
│  - No PII in logs                                               │
└─────────────────────────────────────────────────────────────────┘
```

### Security Controls Checklist

- [ ] TODO: Implement API key authentication
- [ ] TODO: Configure cert-manager for TLS
- [ ] TODO: Create NetworkPolicies for all namespaces
- [ ] TODO: Set up RBAC with least privilege
- [ ] TODO: Enable Pod Security Standards
- [ ] TODO: Configure secrets management (Kubernetes Secrets or Vault)
- [ ] TODO: Implement input validation
- [ ] TODO: Set up rate limiting
- [ ] TODO: Enable audit logging
- [ ] TODO: Run security scanning in CI (Trivy, Bandit)

---

## Scalability & Performance

### Horizontal Scaling

**Auto-Scaling Configuration:**
```yaml
# TODO: HPA configuration
# Scale based on:
# - CPU utilization > 70%
# - Memory utilization > 80%
# - Custom metric: requests_per_second > 100
#
# Scaling behavior:
# - Scale up: +1 pod every 30 seconds (max)
# - Scale down: -1 pod every 5 minutes (avoid flapping)
```

**Load Testing:**
```bash
# TODO: Run load tests with k6
# Target: 1000 requests/second
# Duration: 10 minutes
# Success criteria:
# - P95 latency < 500ms
# - P99 latency < 1s
# - Error rate < 0.1%
```

### Performance Optimization

**Model Optimization:**
- [ ] TODO: Quantize model (FP32 → FP16 or INT8)
- [ ] TODO: Batch predictions when possible
- [ ] TODO: Cache models in memory
- [ ] TODO: Use model serving framework (TorchServe, TF Serving)

**Infrastructure Optimization:**
- [ ] TODO: Use GPU nodes for inference (if cost-effective)
- [ ] TODO: Configure resource requests/limits correctly
- [ ] TODO: Use local SSD for model caching
- [ ] TODO: Enable HTTP/2 for connection multiplexing

---

## Disaster Recovery

### Backup Strategy

**What to Backup:**
1. **Database (PostgreSQL)** - MLflow metadata
2. **Object Storage (S3/MinIO)** - Model artifacts
3. **Kubernetes Resources** - Deployments, ConfigMaps, Secrets
4. **Git Repositories** - Code and configurations (already versioned)

**Backup Schedule:**
- Daily automated backups (2 AM UTC)
- Weekly full backups (Sunday 1 AM UTC)
- Monthly snapshots (1st of month)

**Backup Retention:**
- Daily: 7 days
- Weekly: 4 weeks
- Monthly: 12 months

**Backup Storage:**
- Primary: S3/GCS in same region
- Secondary: S3/GCS in different region (disaster recovery)

### Recovery Procedures

**RTO (Recovery Time Objective):** <1 hour
**RPO (Recovery Point Objective):** <24 hours

**Recovery Scenarios:**

1. **Pod Failure** (automatic, <30 seconds)
   - Kubernetes restarts pod automatically
   - No manual intervention required

2. **Node Failure** (automatic, <2 minutes)
   - Kubernetes reschedules pods to healthy nodes
   - No manual intervention required

3. **Database Failure** (<10 minutes)
   - Promote replica to primary
   - Update connection strings
   - Restart dependent services

4. **Complete Cluster Failure** (<1 hour)
   - Provision new cluster
   - Restore from backups (database, configs)
   - Deploy applications
   - Verify functionality

**Disaster Recovery Checklist:**
- [ ] TODO: Document backup procedures
- [ ] TODO: Document restore procedures
- [ ] TODO: Test restore quarterly
- [ ] TODO: Set up automated backups
- [ ] TODO: Configure cross-region replication
- [ ] TODO: Create runbooks for common failure scenarios

---

## Technology Decisions

### Architecture Decision Records (ADRs)

#### ADR-001: Use Kubernetes for Orchestration

**Decision:** Use Kubernetes as the container orchestration platform

**Rationale:**
- Industry standard for container orchestration
- Excellent auto-scaling, self-healing capabilities
- Rich ecosystem (Helm, Operators, monitoring tools)
- Cloud-agnostic (can run on GKE, EKS, AKS, or on-prem)
- Strong community support

**Alternatives Considered:**
- Docker Swarm: Simpler but less feature-rich
- Nomad: Good but smaller ecosystem
- ECS/Fargate: Cloud-specific, vendor lock-in

---

#### ADR-002: Use MLflow for Model Registry

**Decision:** Use MLflow for experiment tracking and model registry

**Rationale:**
- Open-source, vendor-neutral
- Supports multiple ML frameworks (PyTorch, TF, sklearn)
- Good UI for experiment comparison
- REST API for programmatic access
- Model versioning and metadata tracking

**Alternatives Considered:**
- Weights & Biases: Great but proprietary/expensive
- Neptune.ai: Proprietary
- Custom solution: Too much maintenance

---

#### ADR-003: Use Prometheus + Grafana for Monitoring

**Decision:** Use Prometheus for metrics and Grafana for visualization

**Rationale:**
- CNCF graduated projects (production-ready)
- Pull-based metrics (no client-side config needed)
- PromQL powerful for queries
- Grafana excellent for dashboards
- Well-integrated with Kubernetes

**Alternatives Considered:**
- Datadog: Expensive, vendor lock-in
- New Relic: Expensive
- Custom solution: Reinventing the wheel

---

#### ADR-004: Use GitHub Actions for CI/CD

**Decision:** Use GitHub Actions for CI/CD pipelines

**Rationale:**
- Integrated with GitHub (where code lives)
- Free for public repos, affordable for private
- Good marketplace of actions
- YAML-based, easy to version control
- Built-in secrets management

**Alternatives Considered:**
- GitLab CI: Good but requires GitLab
- Jenkins: Powerful but complex, self-hosted
- CircleCI: Good but expensive for large teams

---

#### ADR-005: Use Kustomize for Multi-Environment Configs

**Decision:** Use Kustomize for managing environment-specific configurations

**Rationale:**
- Built into kubectl (no separate tool)
- Overlay pattern keeps configs DRY
- No templating language (pure YAML)
- Good for GitOps workflows

**Alternatives Considered:**
- Helm: More complex, templating can be error-prone
- Custom scripts: Not maintainable
- Environment variables: Not sufficient for all configs

---

## Summary

This architecture provides a production-ready ML system with:
- ✅ **High availability** - Multi-replica, auto-healing, zero-downtime updates
- ✅ **Scalability** - Auto-scaling from 3-20 replicas, handles 1000+ req/sec
- ✅ **Security** - Multiple layers of defense, encrypted, authenticated
- ✅ **Observability** - Metrics, logs, alerts, dashboards
- ✅ **Automation** - CI/CD, ML lifecycle, scaling, recovery
- ✅ **Maintainability** - Infrastructure as code, GitOps, comprehensive docs

**Next Steps:**
1. Review this architecture document thoroughly
2. Understand how components interact
3. Begin implementation starting with system integration
4. Refer back to this document as the "source of truth"

---

**Document Version:** 1.0
**Last Updated:** October 18, 2025
**Maintained By:** AI Infrastructure Curriculum Team
