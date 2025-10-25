# Architecture: ML Pipeline with Experiment Tracking

**Version:** 1.0
**Last Updated:** October 18, 2025

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Component Design](#component-design)
3. [Data Flow](#data-flow)
4. [Infrastructure Architecture](#infrastructure-architecture)
5. [MLflow Architecture](#mlflow-architecture)
6. [Airflow Architecture](#airflow-architecture)
7. [Technology Decisions](#technology-decisions)
8. [Design Patterns](#design-patterns)
9. [Security Considerations](#security-considerations)
10. [Scalability Considerations](#scalability-considerations)

---

## System Architecture

### High-Level Overview

```
┌────────────────────────────────────────────────────────────────┐
│                   ML Pipeline Ecosystem                        │
└────────────────────────────────────────────────────────────────┘

                    ┌──────────────────┐
                    │   Data Sources   │
                    │  - CSV Files     │
                    │  - REST APIs     │
                    │  - Databases     │
                    └────────┬─────────┘
                             │
                             ▼
         ┌───────────────────────────────────────┐
         │      Data Ingestion & Validation      │
         │   - DataIngestion Class               │
         │   - Great Expectations Validator      │
         └─────────┬─────────────────────────────┘
                   │
                   ▼
         ┌─────────────────────┐    ┌──────────────┐
         │   Data Versioning   │◄───│     DVC      │
         │   - Raw Data        │    │  - MinIO     │
         │   - Processed Data  │    │  - Git       │
         └─────────┬───────────┘    └──────────────┘
                   │
                   ▼
         ┌───────────────────────────────────────┐
         │      Data Preprocessing               │
         │   - Cleaning                          │
         │   - Feature Engineering               │
         │   - Train/Val/Test Split              │
         └─────────┬─────────────────────────────┘
                   │
                   ▼
         ┌───────────────────────────────────────┐
         │      Feature Store (PostgreSQL)       │
         │   - Structured Features               │
         │   - Feature Metadata                  │
         └─────────┬─────────────────────────────┘
                   │
                   ▼
         ┌───────────────────────────────────────┐
         │      Model Training                   │
         │   - PyTorch Models                    │
         │   - Hyperparameter Tuning             │
         │   - Cross Validation                  │
         └─────────┬─────────────────────────────┘
                   │
                   ├──────────────────────────┐
                   │                          │
                   ▼                          ▼
         ┌──────────────────┐      ┌──────────────────┐
         │  Experiment      │      │  Model           │
         │  Tracking        │      │  Artifacts       │
         │  - MLflow        │      │  - PyTorch       │
         │  - Parameters    │      │  - ONNX          │
         │  - Metrics       │      │  - Plots         │
         └──────────────────┘      └──────────────────┘
                   │
                   ▼
         ┌───────────────────────────────────────┐
         │      Model Evaluation                 │
         │   - Test Set Metrics                  │
         │   - Confusion Matrix                  │
         │   - Per-Class Performance             │
         └─────────┬─────────────────────────────┘
                   │
                   ▼
         ┌───────────────────────────────────────┐
         │      Model Registry                   │
         │   - Versioned Models                  │
         │   - Lifecycle Stages                  │
         │   - Production Deployment             │
         └───────────────────────────────────────┘

                   ┌──────────────────────┐
                   │  Workflow            │
                   │  Orchestration       │
                   │  - Apache Airflow    │
                   │  - Task Scheduling   │
                   │  - Monitoring        │
                   └──────────────────────┘
```

---

## Component Design

### 1. Data Ingestion Component

**Purpose:** Load data from multiple sources into the pipeline

**Class Diagram:**
```python
class DataIngestion:
    """
    Handles data ingestion from multiple sources.

    Responsibilities:
    - Load data from CSV, APIs, databases
    - Validate source connectivity
    - Save raw data with metadata
    """

    def __init__(self, config: Dict[str, Any])
    def ingest_from_csv(self, file_path: str) -> pd.DataFrame
    def ingest_from_api(self, api_url: str, params: Dict) -> pd.DataFrame
    def ingest_from_database(self, conn_string: str, query: str) -> pd.DataFrame
    def save_raw_data(self, df: pd.DataFrame, filename: str) -> Path
    def get_metadata(self) -> Dict[str, Any]
```

**Input/Output:**
- **Input:** File paths, API URLs, database connection strings
- **Output:** Raw data saved to `data/raw/`, DataFrame objects
- **Side Effects:** Creates directories, writes files

**Error Handling:**
- Network errors: Retry with exponential backoff (max 3 retries)
- File not found: Log error and raise FileNotFoundError
- Database errors: Log connection details (sanitized) and raise

---

### 2. Data Validation Component

**Purpose:** Validate data quality before processing

**Class Diagram:**
```python
class DataValidator:
    """
    Validates data using Great Expectations.

    Responsibilities:
    - Define expectation suites
    - Run validation checks
    - Generate validation reports
    """

    def __init__(self, context_root_dir: str)
    def create_expectation_suite(self, suite_name: str) -> ExpectationSuite
    def validate_data(self, df: pd.DataFrame, suite_name: str) -> bool
    def get_validation_report(self) -> str
    def add_expectation(self, expectation: Dict) -> None
```

**Validation Rules:**
```python
expectations = [
    # Schema validation
    {
        "type": "expect_table_column_count_to_equal",
        "value": 10
    },
    # Data quality
    {
        "type": "expect_column_values_to_not_be_null",
        "column": "image_path"
    },
    # Domain validation
    {
        "type": "expect_column_values_to_be_in_set",
        "column": "label",
        "value_set": ["cat", "dog", "bird", "fish"]
    },
    # Range validation
    {
        "type": "expect_table_row_count_to_be_between",
        "min_value": 1000,
        "max_value": 1000000
    }
]
```

**Pipeline Integration:**
- Validation runs after ingestion
- Pipeline stops if validation fails
- Validation reports saved to `reports/` directory

---

### 3. Data Preprocessing Component

**Purpose:** Clean and transform data for training

**Class Diagram:**
```python
class DataPreprocessor:
    """
    Preprocesses data for model training.

    Responsibilities:
    - Clean data (duplicates, missing values)
    - Encode labels
    - Split data
    - Save artifacts
    """

    def __init__(self, config: Dict[str, Any])
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame
    def encode_labels(self, df: pd.DataFrame) -> pd.DataFrame
    def create_train_test_split(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, ...]
    def save_processed_data(self, train, val, test) -> None
    def run_pipeline(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, ...]
```

**Processing Pipeline:**
```
Raw Data
    ↓
Remove Duplicates (df.drop_duplicates())
    ↓
Handle Missing Values (dropna/fillna)
    ↓
Encode Categorical Labels (LabelEncoder)
    ↓
Stratified Split (train_test_split, stratify=y)
    ↓
Save Splits + Artifacts
```

**Artifacts Generated:**
- `artifacts/label_encoder.pkl` - For inference
- `artifacts/scaler.pkl` - If normalization applied
- `artifacts/preprocessing_config.json` - Reproducibility

---

### 4. Model Training Component

**Purpose:** Train ML models with experiment tracking

**Class Diagram:**
```python
class ModelTrainer:
    """
    Trains models with MLflow tracking.

    Responsibilities:
    - Create model architectures
    - Train with validation
    - Log to MLflow
    - Save best model
    """

    def __init__(self, config: Dict, mlflow_tracker: MLflowTracker)
    def create_model(self, num_classes: int, model_name: str) -> nn.Module
    def train_epoch(self, model, train_loader, criterion, optimizer) -> Tuple[float, float]
    def validate(self, model, val_loader, criterion) -> Tuple[float, float]
    def train(self, train_loader, val_loader, num_classes: int, params: Dict) -> Tuple[nn.Module, float]
```

**Training Loop:**
```python
for epoch in range(num_epochs):
    # Train
    train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer)

    # Validate
    val_loss, val_acc = validate(model, val_loader, criterion)

    # Log to MLflow
    mlflow.log_metrics({
        "train_loss": train_loss,
        "train_acc": train_acc,
        "val_loss": val_loss,
        "val_acc": val_acc
    }, step=epoch)

    # Save best model
    if val_acc > best_val_acc:
        best_val_acc = val_acc
        torch.save(model.state_dict(), "best_model.pth")

    # Early stopping
    if no_improvement_for(patience):
        break
```

**Supported Architectures:**
1. **ResNet18** - Good baseline, 11M parameters
2. **MobileNetV2** - Lightweight, 3.5M parameters

---

### 5. MLflow Tracker Component

**Purpose:** Centralize MLflow operations

**Class Diagram:**
```python
class MLflowTracker:
    """
    Wrapper for MLflow tracking operations.

    Responsibilities:
    - Start/end runs
    - Log parameters, metrics, artifacts
    - Register models
    - Manage model stages
    """

    def __init__(self, tracking_uri: str, experiment_name: str)
    def start_run(self, run_name: str, tags: Dict) -> Run
    def log_params(self, params: Dict) -> None
    def log_metrics(self, metrics: Dict, step: int) -> None
    def log_artifact(self, artifact_path: str) -> None
    def log_model(self, model, artifact_path: str) -> None
    def register_model(self, model_uri: str, model_name: str) -> ModelVersion
    def transition_model_stage(self, model_name: str, version: int, stage: str) -> None
    def end_run(self) -> None
```

**Usage Pattern:**
```python
# Initialize
tracker = MLflowTracker(
    tracking_uri="http://mlflow:5000",
    experiment_name="image_classification"
)

# Start run
tracker.start_run(run_name="resnet18_exp1", tags={"model": "resnet18"})

# Log during training
tracker.log_params({"lr": 0.001, "batch_size": 32})
tracker.log_metrics({"val_acc": 85.2}, step=10)

# Log model
tracker.log_model(model, "model")

# Register model
model_version = tracker.register_model(
    model_uri=f"runs:/{run_id}/model",
    model_name="image_classifier"
)

# Promote to production
tracker.transition_model_stage(
    model_name="image_classifier",
    version=model_version.version,
    stage="Production"
)

# End run
tracker.end_run()
```

---

### 6. Model Evaluator Component

**Purpose:** Comprehensive model evaluation

**Class Diagram:**
```python
class ModelEvaluator:
    """
    Evaluates models on test set.

    Responsibilities:
    - Compute metrics (accuracy, precision, recall, F1)
    - Generate confusion matrix
    - Create visualizations
    - Log results to MLflow
    """

    def __init__(self, config: Dict, mlflow_tracker: MLflowTracker)
    def evaluate(self, model, test_loader) -> Dict[str, float]
    def compute_metrics(self, y_true, y_pred) -> Dict
    def generate_confusion_matrix(self, y_true, y_pred) -> np.ndarray
    def plot_confusion_matrix(self, cm: np.ndarray, class_names: List[str]) -> plt.Figure
    def generate_classification_report(self, y_true, y_pred) -> str
```

**Metrics Computed:**
```python
metrics = {
    "test_accuracy": accuracy_score(y_true, y_pred),
    "test_precision": precision_score(y_true, y_pred, average='macro'),
    "test_recall": recall_score(y_true, y_pred, average='macro'),
    "test_f1": f1_score(y_true, y_pred, average='macro'),
    "per_class_precision": precision_score(y_true, y_pred, average=None),
    "per_class_recall": recall_score(y_true, y_pred, average=None),
    "per_class_f1": f1_score(y_true, y_pred, average=None)
}
```

---

## Data Flow

### End-to-End Pipeline Flow

```
┌─────────────────────┐
│  1. Data Ingestion  │
│  - Load from source │
│  - Save to raw/     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  2. Data Validation │
│  - GE expectations  │
│  - Pass/Fail check  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  3. Preprocessing   │
│  - Clean data       │
│  - Encode labels    │
│  - Split data       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  4. DVC Versioning  │
│  - dvc add          │
│  - git commit       │
│  - dvc push         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  5. Model Training  │
│  - Load data        │
│  - Train model      │
│  - Track in MLflow  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  6. Model Evaluation│
│  - Test metrics     │
│  - Confusion matrix │
│  - Log to MLflow    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  7. Model Registry  │
│  - Register model   │
│  - Stage transition │
│  - Metadata update  │
└─────────────────────┘
```

### Data Persistence Flow

```
┌───────────────┐
│   Raw Data    │
│   (CSV/API)   │
└───────┬───────┘
        │
        ▼
┌───────────────────┐      ┌─────────────┐
│  data/raw/        │─────▶│  DVC Track  │
│  dataset.csv      │      │  .dvc file  │
└───────┬───────────┘      └─────────────┘
        │                          │
        │                          ▼
        │                  ┌───────────────┐
        │                  │  MinIO/S3     │
        │                  │  (Remote)     │
        │                  └───────────────┘
        ▼
┌───────────────────┐
│  data/processed/  │
│  - train.csv      │
│  - val.csv        │
│  - test.csv       │
└───────┬───────────┘
        │
        ▼
┌───────────────────┐
│  PostgreSQL       │
│  Feature Store    │
└───────────────────┘
```

### MLflow Artifact Flow

```
┌──────────────┐
│  Training    │
│  Execution   │
└──────┬───────┘
       │
       ├────────────────────────────┐
       │                            │
       ▼                            ▼
┌──────────────┐            ┌──────────────┐
│  Parameters  │            │   Metrics    │
│  - lr: 0.001 │            │  - accuracy  │
│  - batch: 32 │            │  - loss      │
└──────┬───────┘            └──────┬───────┘
       │                            │
       ▼                            ▼
┌──────────────────────────────────────┐
│      PostgreSQL (MLflow Backend)     │
│      - Run metadata                  │
│      - Parameters                    │
│      - Metrics                       │
└──────────────────────────────────────┘
       │
       ▼
┌──────────────┐
│  Artifacts   │
│  - model.pth │
│  - plots/    │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────┐
│      MinIO/S3 (Artifact Store)       │
│      - Model files                   │
│      - Plots                         │
│      - Logs                          │
└──────────────────────────────────────┘
```

---

## Infrastructure Architecture

### Docker Compose Architecture

```yaml
┌─────────────────────────────────────────────────────┐
│              Docker Compose Network                 │
└─────────────────────────────────────────────────────┘

┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  PostgreSQL  │  │    Redis     │  │    MinIO     │
│   Port 5432  │  │   Port 6379  │  │  Ports 9000  │
│              │  │              │  │       9001   │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       │                 │                 │
       ▼                 │                 │
┌──────────────┐         │                 │
│   MLflow     │         │                 │
│  Tracking    │◄────────┘                 │
│   Port 5000  │◄──────────────────────────┘
└──────────────┘
       ▲
       │
┌──────┴───────────────────────────────────┐
│         Airflow Components               │
├──────────────────────────────────────────┤
│  ┌────────────┐  ┌─────────┐  ┌────────┐│
│  │ Webserver  │  │Scheduler│  │ Worker ││
│  │ Port 8080  │  │         │  │        ││
│  └────────────┘  └─────────┘  └────────┘│
└──────────────────────────────────────────┘
```

### Container Specifications

**PostgreSQL Container:**
```yaml
postgres:
  image: postgres:15
  environment:
    POSTGRES_USER: mlflow
    POSTGRES_PASSWORD: mlflow
    POSTGRES_DB: mlflow
  volumes:
    - postgres_data:/var/lib/postgresql/data
  ports:
    - "5432:5432"
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U mlflow"]
    interval: 10s
    timeout: 5s
    retries: 5
```

**MLflow Container:**
```yaml
mlflow:
  build: ./mlflow
  ports:
    - "5000:5000"
  environment:
    MLFLOW_BACKEND_STORE_URI: postgresql://mlflow:mlflow@postgres:5432/mlflow
    MLFLOW_S3_ENDPOINT_URL: http://minio:9000
    AWS_ACCESS_KEY_ID: minioadmin
    AWS_SECRET_ACCESS_KEY: minioadmin
  depends_on:
    postgres:
      condition: service_healthy
    minio:
      condition: service_started
  command: >
    mlflow server
    --backend-store-uri postgresql://mlflow:mlflow@postgres:5432/mlflow
    --default-artifact-root s3://mlflow/
    --host 0.0.0.0
    --port 5000
```

**MinIO Container:**
```yaml
minio:
  image: minio/minio:latest
  command: server /data --console-address ":9001"
  environment:
    MINIO_ROOT_USER: minioadmin
    MINIO_ROOT_PASSWORD: minioadmin
  ports:
    - "9000:9000"   # API
    - "9001:9001"   # Console
  volumes:
    - minio_data:/data
```

**Airflow Webserver:**
```yaml
airflow-webserver:
  build: ./airflow
  ports:
    - "8080:8080"
  environment:
    AIRFLOW__CORE__EXECUTOR: CeleryExecutor
    AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql://mlflow:mlflow@postgres:5432/airflow
    AIRFLOW__CELERY__BROKER_URL: redis://redis:6379/0
    AIRFLOW__CELERY__RESULT_BACKEND: db+postgresql://mlflow:mlflow@postgres:5432/airflow
  depends_on:
    - postgres
    - redis
  command: webserver
```

---

## MLflow Architecture

### MLflow Component Stack

```
┌──────────────────────────────────────────────┐
│          MLflow Tracking Server              │
│              (Port 5000)                     │
└────────────┬─────────────────────────────────┘
             │
             ├─────────────────────┬───────────────────┐
             │                     │                   │
             ▼                     ▼                   ▼
    ┌─────────────────┐   ┌─────────────────┐  ┌──────────────┐
    │  Experiments    │   │  Model Registry │  │  Artifacts   │
    │  - Runs         │   │  - Versions     │  │  - Models    │
    │  - Parameters   │   │  - Stages       │  │  - Plots     │
    │  - Metrics      │   │  - Metadata     │  │  - Logs      │
    └────────┬────────┘   └────────┬────────┘  └──────┬───────┘
             │                     │                   │
             ▼                     ▼                   ▼
    ┌──────────────────────────────────────────────────────┐
    │             PostgreSQL Backend Store                 │
    │  - Experiment metadata                               │
    │  - Run parameters and metrics                        │
    │  - Model registry data                               │
    └──────────────────────────────────────────────────────┘
                               │
                               │
    ┌──────────────────────────────────────────────────────┐
    │             MinIO/S3 Artifact Store                  │
    │  - Model artifacts (model.pth)                       │
    │  - Plots and visualizations                          │
    │  - Logs and other files                              │
    └──────────────────────────────────────────────────────┘
```

### MLflow Data Model

**Experiments Table:**
```sql
CREATE TABLE experiments (
    experiment_id INTEGER PRIMARY KEY,
    name VARCHAR(256) UNIQUE NOT NULL,
    artifact_location VARCHAR(256),
    lifecycle_stage VARCHAR(32),
    creation_time BIGINT,
    last_update_time BIGINT
);
```

**Runs Table:**
```sql
CREATE TABLE runs (
    run_uuid VARCHAR(32) PRIMARY KEY,
    name VARCHAR(256),
    source_type VARCHAR(20),
    source_name VARCHAR(500),
    entry_point_name VARCHAR(50),
    user_id VARCHAR(256),
    status VARCHAR(20),
    start_time BIGINT,
    end_time BIGINT,
    source_version VARCHAR(50),
    lifecycle_stage VARCHAR(20),
    artifact_uri VARCHAR(200),
    experiment_id INTEGER,
    FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id)
);
```

**Model Registry:**
```sql
CREATE TABLE registered_models (
    name VARCHAR(256) PRIMARY KEY,
    creation_time BIGINT,
    last_updated_time BIGINT,
    description VARCHAR(5000)
);

CREATE TABLE model_versions (
    name VARCHAR(256),
    version INTEGER,
    creation_time BIGINT,
    last_updated_time BIGINT,
    description VARCHAR(5000),
    user_id VARCHAR(256),
    current_stage VARCHAR(20),
    source VARCHAR(500),
    run_id VARCHAR(32),
    status VARCHAR(20),
    status_message VARCHAR(500),
    PRIMARY KEY (name, version),
    FOREIGN KEY (name) REFERENCES registered_models(name)
);
```

---

## Airflow Architecture

### Airflow Components

```
┌────────────────────────────────────────────────┐
│            Airflow Architecture                │
└────────────────────────────────────────────────┘

┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  Web Server  │      │  Scheduler   │      │    Worker    │
│  Port 8080   │      │  (Core)      │      │  (Executor)  │
│              │      │              │      │              │
│ - UI         │      │ - Parse DAGs │      │ - Run tasks  │
│ - REST API   │      │ - Schedule   │      │ - Report     │
│ - Auth       │      │ - Trigger    │      │   status     │
└──────┬───────┘      └──────┬───────┘      └──────┬───────┘
       │                     │                     │
       └─────────────────────┼─────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │   PostgreSQL   │
                    │   Metadata DB  │
                    │                │
                    │ - DAG metadata │
                    │ - Task state   │
                    │ - Run history  │
                    └────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │     Redis      │
                    │   (Broker)     │
                    │                │
                    │ - Task queue   │
                    │ - Messages     │
                    └────────────────┘
```

### DAG Execution Flow

```
User Triggers DAG
       │
       ▼
Scheduler picks up DAG
       │
       ▼
Parse DAG Python file
       │
       ▼
Create DAG Run instance
       │
       ▼
For each task in dependency order:
    │
    ├─▶ Create Task Instance
    │       │
    │       ▼
    │   Queue task to Redis
    │       │
    │       ▼
    │   Worker picks up task
    │       │
    │       ▼
    │   Execute task Python code
    │       │
    │       ▼
    │   Report status to PostgreSQL
    │       │
    │       ▼
    │   Pass data via XCom (if needed)
    │
    └─▶ Repeat for next task
```

### DAG Structure

```python
# ML Training Pipeline DAG
DAG(
    dag_id='ml_training_pipeline',
    schedule_interval='@weekly',
    start_date=datetime(2025, 10, 1),
    catchup=False,
    max_active_runs=1,
    default_args={
        'owner': 'ml-team',
        'retries': 3,
        'retry_delay': timedelta(minutes=5),
        'execution_timeout': timedelta(hours=2)
    }
)

# Task Dependency Graph
ingest_data
    ↓
validate_data
    ↓
preprocess_data
    ↓
version_data_dvc
    ↓
train_model
    ↓
evaluate_model
    ↓
register_model
    ↓
notify_success
```

---

## Technology Decisions

### Why Apache Airflow?

**Pros:**
✅ Industry standard (used by Airbnb, Netflix, Adobe)
✅ Rich UI for monitoring and debugging
✅ Extensive plugin ecosystem
✅ Python-native (easy for ML teams)
✅ Supports complex dependencies
✅ Built-in retry and error handling
✅ XCom for inter-task communication

**Cons:**
❌ Complex setup for beginners
❌ Resource intensive
❌ Overkill for simple pipelines

**Alternatives Considered:**
- **Prefect 2.0**: More modern, easier setup, but less mature
- **Kubeflow Pipelines**: Kubernetes-native, but complex
- **Luigi**: Simpler, but less feature-rich

**Decision:** Airflow chosen for industry relevance and learning value.

---

### Why MLflow?

**Pros:**
✅ Open source, vendor-neutral
✅ Most popular MLOps platform (15K+ stars)
✅ Complete ML lifecycle management
✅ Easy integration with PyTorch, TensorFlow, sklearn
✅ Built-in model registry
✅ REST API for automation
✅ Active community and development

**Cons:**
❌ UI could be more modern
❌ Limited built-in model serving
❌ Scalability challenges at very large scale

**Alternatives Considered:**
- **Weights & Biases**: Better UI, but commercial/SaaS
- **Neptune.ai**: More features, but commercial
- **TensorBoard**: Limited to TensorFlow ecosystem
- **Sacred**: Less actively maintained

**Decision:** MLflow chosen for open-source, completeness, and industry adoption.

---

### Why DVC?

**Pros:**
✅ Git-like workflow for data
✅ Storage-agnostic (S3, GCS, Azure, SSH)
✅ Integrates seamlessly with Git
✅ Lightweight and fast
✅ Supports pipelines and metrics tracking
✅ Open source and free

**Cons:**
❌ Requires Git knowledge
❌ Can be slow for very large files
❌ Learning curve for team adoption

**Alternatives Considered:**
- **Git LFS**: Limited features, no versioning logic
- **Pachyderm**: More complex, Kubernetes-dependent
- **LakeFS**: Git for data lakes, overkill for this project

**Decision:** DVC chosen for simplicity and Git integration.

---

### Why PostgreSQL?

**Pros:**
✅ Proven reliability
✅ ACID compliance
✅ Rich indexing and query optimization
✅ JSON support for metadata
✅ Free and open source
✅ Excellent Python support (psycopg2)

**Cons:**
❌ Not as scalable as NoSQL for huge datasets
❌ Vertical scaling limitations

**Alternatives Considered:**
- **MySQL**: Similar, but PostgreSQL has better JSON support
- **MongoDB**: NoSQL, but ACID compliance important for metadata
- **SQLite**: Too limited for multi-service setup

**Decision:** PostgreSQL chosen for reliability and feature richness.

---

## Design Patterns

### 1. Repository Pattern
Encapsulate data access logic in separate classes.

```python
class ExperimentRepository:
    """Abstracts MLflow experiment operations"""

    def get_all_runs(self, experiment_id: str) -> List[Run]:
        return mlflow.search_runs(experiment_ids=[experiment_id])

    def get_best_run(self, experiment_id: str, metric: str) -> Run:
        runs = self.get_all_runs(experiment_id)
        return runs.sort_values(f"metrics.{metric}", ascending=False).iloc[0]
```

### 2. Strategy Pattern
Allow different data ingestion strategies.

```python
class DataIngestionStrategy(ABC):
    @abstractmethod
    def ingest(self) -> pd.DataFrame:
        pass

class CSVIngestionStrategy(DataIngestionStrategy):
    def ingest(self) -> pd.DataFrame:
        return pd.read_csv(self.path)

class APIIngestionStrategy(DataIngestionStrategy):
    def ingest(self) -> pd.DataFrame:
        response = requests.get(self.url)
        return pd.DataFrame(response.json())
```

### 3. Factory Pattern
Create models based on configuration.

```python
class ModelFactory:
    @staticmethod
    def create_model(model_name: str, num_classes: int) -> nn.Module:
        if model_name == "resnet18":
            return create_resnet18(num_classes)
        elif model_name == "mobilenet_v2":
            return create_mobilenet_v2(num_classes)
        else:
            raise ValueError(f"Unknown model: {model_name}")
```

### 4. Observer Pattern
MLflow logging as observer of training events.

```python
class TrainingObserver(ABC):
    @abstractmethod
    def on_epoch_end(self, epoch: int, metrics: Dict) -> None:
        pass

class MLflowObserver(TrainingObserver):
    def on_epoch_end(self, epoch: int, metrics: Dict) -> None:
        mlflow.log_metrics(metrics, step=epoch)
```

---

## Security Considerations

### 1. Credentials Management
- Store credentials in environment variables
- Never commit secrets to Git
- Use `.env` files (gitignored)
- Consider HashiCorp Vault for production

### 2. Network Security
- Internal Docker network for service communication
- Only expose necessary ports to host
- Use PostgreSQL authentication
- MinIO access keys required

### 3. Data Privacy
- No PII (Personally Identifiable Information) in this project
- For real projects: encrypt data at rest and in transit
- Implement access controls

### 4. MLflow Security
- MLflow UI has no authentication by default (OK for local dev)
- For production: enable authentication plugin
- Restrict artifact store access

---

## Scalability Considerations

### Current Limitations
- Single-machine deployment
- No horizontal scaling
- Limited to local datasets (<1GB)
- Single Airflow worker

### Scaling Strategies (Future)

**Horizontal Scaling:**
- Multiple Airflow workers (Celery Executor)
- Multiple MLflow tracking servers (load balanced)
- PostgreSQL read replicas

**Data Scaling:**
- Partition large datasets
- Use data sampling for development
- Implement incremental loading
- Consider Spark for very large data

**Compute Scaling:**
- GPU acceleration for training
- Distributed training (PyTorch DDP)
- Cloud burst for intensive workloads

**Storage Scaling:**
- Object storage (S3, GCS) for artifacts
- Distributed file systems (HDFS)
- Data lake architecture

---

**Architecture Version:** 1.0
**Reviewed By:** AI Infrastructure Curriculum Team
**Last Updated:** October 18, 2025
