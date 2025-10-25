# Project Requirements: ML Pipeline with Experiment Tracking

**Version:** 1.0
**Last Updated:** October 18, 2025

---

## Table of Contents

1. [Functional Requirements](#functional-requirements)
2. [Non-Functional Requirements](#non-functional-requirements)
3. [Technical Specifications](#technical-specifications)
4. [Acceptance Criteria](#acceptance-criteria)
5. [Constraints and Assumptions](#constraints-and-assumptions)

---

## Functional Requirements

### FR-1: Data Pipeline

#### FR-1.1: Data Ingestion
**Description:** System must ingest data from multiple sources

**Requirements:**
- Support CSV file ingestion
- Support REST API data fetching
- Support database querying (PostgreSQL)
- Handle data from different schemas
- Store raw data with timestamps

**Inputs:**
- CSV files from local filesystem or cloud storage
- REST API endpoints returning JSON
- SQL queries against PostgreSQL databases

**Outputs:**
- Raw data saved to `data/raw/` directory
- Ingestion logs with record counts
- Metadata about data source and timestamp

**Acceptance Criteria:**
- [ ] Successfully ingest 100K+ records from CSV
- [ ] Fetch data from public API (e.g., OpenML, Kaggle API)
- [ ] Query data from PostgreSQL database
- [ ] Handle network errors gracefully with retries
- [ ] Log all ingestion activities

---

#### FR-1.2: Data Validation
**Description:** Validate data quality using Great Expectations

**Requirements:**
- Define expectation suite for dataset schema
- Validate row counts (min/max bounds)
- Validate column presence and types
- Validate value ranges and categories
- Detect null values in required columns
- Generate validation reports

**Validation Rules:**
- Minimum 1,000 records, maximum 1,000,000 records
- Required columns: `image_path`, `label`, `split`
- Label values must be in defined set (e.g., ["cat", "dog", "bird", "fish"])
- No null values in critical columns
- Image file paths must exist

**Outputs:**
- Validation report (HTML)
- Boolean validation result (pass/fail)
- Detailed error messages for failures

**Acceptance Criteria:**
- [ ] Expectation suite created with 5+ expectations
- [ ] Validation catches schema violations
- [ ] Validation catches missing values
- [ ] Validation catches invalid labels
- [ ] Pipeline stops if validation fails

---

#### FR-1.3: Data Versioning
**Description:** Version datasets using DVC (Data Version Control)

**Requirements:**
- Initialize DVC in project
- Configure remote storage (MinIO/S3)
- Track raw and processed datasets
- Tag versions with meaningful names
- Enable data retrieval from any version

**DVC Workflow:**
```bash
# Add dataset to DVC
dvc add data/raw/dataset.csv

# Commit DVC file to Git
git add data/raw/dataset.csv.dvc
git commit -m "Dataset v1.0 - Initial import"
git tag -a "data-v1.0" -m "Dataset version 1.0"

# Push to remote
dvc push
```

**Acceptance Criteria:**
- [ ] DVC initialized and configured
- [ ] Raw data tracked with DVC
- [ ] Processed data tracked with DVC
- [ ] Remote storage configured (MinIO)
- [ ] Data retrievable with `dvc pull`
- [ ] At least 3 data versions tagged

---

#### FR-1.4: Data Preprocessing
**Description:** Clean and preprocess data for model training

**Requirements:**
- Remove duplicate records
- Handle missing values (drop or impute)
- Encode categorical labels
- Normalize/standardize features
- Create train/validation/test splits (70/15/15)
- Save preprocessing artifacts (encoders, scalers)

**Preprocessing Steps:**
1. **Cleaning:**
   - Remove exact duplicates
   - Drop rows with missing critical values
   - Fix data type inconsistencies

2. **Encoding:**
   - Label encode categorical targets
   - Save encoder for inference

3. **Splitting:**
   - Stratified split to preserve class balance
   - Fixed random seed for reproducibility

**Outputs:**
- `data/processed/train.csv`
- `data/processed/val.csv`
- `data/processed/test.csv`
- `artifacts/label_encoder.pkl`
- `artifacts/scaler.pkl` (if applicable)

**Acceptance Criteria:**
- [ ] Preprocessing removes duplicates
- [ ] Missing values handled appropriately
- [ ] Labels encoded to integers
- [ ] Data split into train/val/test
- [ ] Split sizes follow 70/15/15 ratio
- [ ] Encoders saved for reuse
- [ ] Preprocessing reproducible with fixed seed

---

#### FR-1.5: Feature Store (Optional)
**Description:** Store processed features in PostgreSQL

**Requirements:**
- Create feature tables in PostgreSQL
- Store feature vectors with IDs
- Enable feature retrieval by ID
- Track feature versions

**Schema:**
```sql
CREATE TABLE features (
    id SERIAL PRIMARY KEY,
    image_id VARCHAR(255) UNIQUE,
    feature_vector FLOAT[],
    label INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Acceptance Criteria:**
- [ ] Feature table created
- [ ] Features stored successfully
- [ ] Features retrievable by ID
- [ ] Feature versions tracked

---

### FR-2: Model Training Pipeline

#### FR-2.1: Model Training
**Description:** Train image classification model with PyTorch

**Requirements:**
- Support multiple model architectures (ResNet18, MobileNetV2)
- Implement training loop with validation
- Support transfer learning (pretrained models)
- Track training progress (loss, accuracy)
- Save best model based on validation accuracy
- Support early stopping

**Model Architectures:**
1. **ResNet18** (baseline)
2. **MobileNetV2** (lightweight)

**Training Configuration:**
```python
{
    "model_name": "resnet18",
    "num_epochs": 20,
    "batch_size": 32,
    "learning_rate": 0.001,
    "optimizer": "adam",
    "lr_scheduler": "step_lr",
    "lr_step_size": 7,
    "lr_gamma": 0.1,
    "early_stopping_patience": 5
}
```

**Acceptance Criteria:**
- [ ] Model trains successfully
- [ ] Training and validation loss decrease
- [ ] Model achieves >75% validation accuracy
- [ ] Best model saved based on val accuracy
- [ ] Training completes in <30 minutes per experiment

---

#### FR-2.2: Hyperparameter Tuning
**Description:** Systematic hyperparameter optimization

**Requirements:**
- Support grid search or Optuna optimization
- Tune at least 3 hyperparameters
- Run minimum 10 configurations
- Track all experiments in MLflow

**Hyperparameters to Tune:**
- Learning rate: [0.0001, 0.001, 0.01]
- Batch size: [16, 32, 64]
- Model architecture: [resnet18, mobilenet_v2]
- Optimizer: [adam, sgd]

**Search Space:**
```python
{
    "learning_rate": [0.0001, 0.001, 0.01],
    "batch_size": [16, 32, 64],
    "model_name": ["resnet18", "mobilenet_v2"],
    "optimizer": ["adam", "sgd"]
}
```

**Acceptance Criteria:**
- [ ] Minimum 10 experiments with different configurations
- [ ] All experiments tracked in MLflow
- [ ] Best hyperparameters identified
- [ ] Results compared systematically

---

#### FR-2.3: Experiment Tracking
**Description:** Track all training runs with MLflow

**Requirements:**
- Log all hyperparameters
- Log metrics per epoch (train/val loss, accuracy)
- Log final evaluation metrics
- Save model artifacts
- Tag runs with meaningful identifiers
- Capture code version (git commit hash)

**What to Log:**

**Parameters:**
```python
{
    "model_name": "resnet18",
    "num_epochs": 20,
    "batch_size": 32,
    "learning_rate": 0.001,
    "optimizer": "adam",
    "dataset_version": "v1.2",
    "git_commit": "a3b4c5d"
}
```

**Metrics (per epoch):**
```python
{
    "train_loss": 0.345,
    "train_accuracy": 87.5,
    "val_loss": 0.412,
    "val_accuracy": 85.2,
    "learning_rate": 0.001
}
```

**Artifacts:**
- `model.pth` - Saved model weights
- `training_plot.png` - Loss/accuracy curves
- `confusion_matrix.png` - Classification results
- `metrics.json` - Final evaluation metrics

**Acceptance Criteria:**
- [ ] All parameters logged
- [ ] Metrics logged per epoch
- [ ] Model artifacts saved
- [ ] Runs tagged appropriately
- [ ] Git commit hash captured
- [ ] MLflow UI shows all experiments

---

#### FR-2.4: Model Artifacts
**Description:** Save and organize model artifacts

**Requirements:**
- Save model weights in PyTorch format
- Save ONNX export for inference
- Save training plots (loss/accuracy curves)
- Save evaluation metrics (JSON)
- Organize artifacts by run ID

**Artifact Structure:**
```
mlruns/
└── 0/                          # Experiment ID
    └── abc123def456/           # Run ID
        └── artifacts/
            ├── model/
            │   ├── model.pth           # PyTorch weights
            │   ├── model.onnx          # ONNX export
            │   └── config.json         # Model config
            ├── plots/
            │   ├── training_curves.png
            │   └── confusion_matrix.png
            └── metrics/
                └── evaluation.json
```

**Acceptance Criteria:**
- [ ] Model weights saved
- [ ] ONNX export created
- [ ] Training plots generated
- [ ] Metrics saved as JSON
- [ ] Artifacts organized properly

---

#### FR-2.5: Model Evaluation
**Description:** Evaluate models on held-out test set

**Requirements:**
- Evaluate on test set (never seen during training)
- Compute multiple metrics (accuracy, precision, recall, F1)
- Generate confusion matrix
- Generate classification report
- Compare with baseline

**Metrics to Compute:**
- Accuracy
- Precision (per class and macro)
- Recall (per class and macro)
- F1 Score (per class and macro)
- Confusion Matrix

**Evaluation Output:**
```python
{
    "test_accuracy": 86.4,
    "test_precision": 85.7,
    "test_recall": 86.1,
    "test_f1": 85.9,
    "per_class_metrics": {
        "cat": {"precision": 88.2, "recall": 89.1, "f1": 88.6},
        "dog": {"precision": 87.5, "recall": 86.8, "f1": 87.1},
        "bird": {"precision": 82.1, "recall": 83.0, "f1": 82.5},
        "fish": {"precision": 85.0, "recall": 85.5, "f1": 85.2}
    }
}
```

**Acceptance Criteria:**
- [ ] Test set evaluation performed
- [ ] Multiple metrics computed
- [ ] Confusion matrix generated
- [ ] Per-class metrics calculated
- [ ] Results logged to MLflow

---

### FR-3: Model Registry

#### FR-3.1: Model Registration
**Description:** Register models in MLflow Model Registry

**Requirements:**
- Register models after successful training
- Assign semantic versions
- Add model metadata (description, tags)
- Link to training run
- Track registration timestamp

**Registration Process:**
```python
# Register model
model_uri = f"runs:/{run_id}/model"
result = mlflow.register_model(
    model_uri=model_uri,
    name="image_classifier",
    tags={
        "architecture": "resnet18",
        "dataset_version": "v1.2",
        "framework": "pytorch"
    }
)

# Add description
client.update_model_version(
    name="image_classifier",
    version=result.version,
    description="ResNet18 trained on v1.2 dataset, 86.4% test accuracy"
)
```

**Acceptance Criteria:**
- [ ] Models registered successfully
- [ ] Versions numbered sequentially
- [ ] Metadata attached to models
- [ ] Run linkage preserved
- [ ] Registration visible in MLflow UI

---

#### FR-3.2: Model Lifecycle Stages
**Description:** Manage model lifecycle through stages

**Requirements:**
- Support stage transitions (None → Staging → Production → Archived)
- Track stage history
- Allow only one Production model at a time
- Require approval for Production promotion (manual step)

**Lifecycle Stages:**
1. **None** - Newly registered model
2. **Staging** - Model being tested
3. **Production** - Currently deployed model
4. **Archived** - Deprecated model

**Stage Transition:**
```python
client.transition_model_version_stage(
    name="image_classifier",
    version=3,
    stage="Production",
    archive_existing_versions=True  # Archive previous Production model
)
```

**Acceptance Criteria:**
- [ ] Models can be transitioned between stages
- [ ] Only one Production model at a time
- [ ] Stage history tracked
- [ ] Previous Production models archived automatically

---

#### FR-3.3: Model Metadata
**Description:** Attach comprehensive metadata to models

**Requirements:**
- Record training dataset version
- Record evaluation metrics
- Record hyperparameters
- Record code version (git commit)
- Record training duration
- Record hardware used

**Metadata Structure:**
```python
{
    "dataset_version": "v1.2",
    "data_size": 50000,
    "test_accuracy": 86.4,
    "hyperparameters": {
        "learning_rate": 0.001,
        "batch_size": 32,
        "num_epochs": 20
    },
    "code_version": "a3b4c5d",
    "training_duration": 1847,  # seconds
    "hardware": "NVIDIA Tesla T4",
    "trained_by": "airflow-pipeline",
    "training_date": "2025-10-18T14:32:00Z"
}
```

**Acceptance Criteria:**
- [ ] All metadata fields populated
- [ ] Metadata searchable in MLflow
- [ ] Lineage traceable

---

#### FR-3.4: Model Retrieval API
**Description:** API to retrieve production models

**Requirements:**
- Get latest Production model
- Get specific model version
- Download model artifacts
- Retrieve model metadata

**API Examples:**
```python
# Get latest Production model
model = mlflow.pyfunc.load_model(
    model_uri="models:/image_classifier/Production"
)

# Get specific version
model = mlflow.pyfunc.load_model(
    model_uri="models:/image_classifier/3"
)

# Get model metadata
client = mlflow.tracking.MlflowClient()
model_version = client.get_model_version(
    name="image_classifier",
    version="3"
)
print(model_version.description)
```

**Acceptance Criteria:**
- [ ] Can load Production model
- [ ] Can load specific versions
- [ ] Can retrieve metadata
- [ ] Model ready for inference

---

### FR-4: Workflow Orchestration

#### FR-4.1: Airflow DAG Design
**Description:** Implement ML pipeline as Airflow DAG

**Requirements:**
- Define task dependencies
- Implement task retries
- Configure task timeouts
- Pass data between tasks (XCom)
- Visualize DAG in Airflow UI

**DAG Structure:**
```python
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

**Task Configuration:**
```python
default_args = {
    'owner': 'ml-team',
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(hours=2),
    'email_on_failure': True,
    'email': ['mlops@example.com']
}
```

**Acceptance Criteria:**
- [ ] DAG visible in Airflow UI
- [ ] Task dependencies correct
- [ ] Tasks execute in order
- [ ] Failed tasks retry automatically
- [ ] DAG can be triggered manually

---

#### FR-4.2: Pipeline Scheduling
**Description:** Schedule automatic pipeline execution

**Requirements:**
- Run pipeline on schedule (weekly, daily, etc.)
- Support manual triggers
- Support parameterized runs
- Handle concurrent runs

**Schedule Configuration:**
```python
dag = DAG(
    'ml_training_pipeline',
    schedule_interval='@weekly',  # Every Sunday at midnight
    catchup=False,  # Don't run for past dates
    max_active_runs=1,  # No concurrent runs
    start_date=datetime(2025, 10, 1)
)
```

**Acceptance Criteria:**
- [ ] Pipeline runs on schedule
- [ ] Manual trigger works
- [ ] Catchup disabled
- [ ] Concurrent runs prevented

---

#### FR-4.3: Error Handling
**Description:** Robust error handling and recovery

**Requirements:**
- Retry transient failures (max 3 times)
- Send failure notifications (email/Slack)
- Log errors with stack traces
- Continue downstream tasks when possible
- Implement circuit breakers

**Error Handling:**
```python
@task(retries=3, retry_delay=timedelta(minutes=5))
def train_model(**context):
    try:
        # Training code
        pass
    except MemoryError as e:
        logger.error(f"OOM error: {e}")
        raise AirflowFailException("Insufficient memory")
    except Exception as e:
        logger.error(f"Training failed: {e}", exc_info=True)
        raise
```

**Acceptance Criteria:**
- [ ] Failed tasks retry 3 times
- [ ] Errors logged with details
- [ ] Failure emails sent
- [ ] Pipeline stops on critical failures
- [ ] Graceful degradation when possible

---

#### FR-4.4: Pipeline Monitoring
**Description:** Monitor pipeline execution and health

**Requirements:**
- Track task duration
- Monitor success/failure rates
- Alert on SLA violations
- Visualize pipeline metrics
- Generate execution reports

**Monitoring Metrics:**
- Task duration (avg, p95, p99)
- Success rate (last 7 days, 30 days)
- Failure rate by task
- Pipeline end-to-end duration
- Resource usage (CPU, memory)

**Acceptance Criteria:**
- [ ] Task durations logged
- [ ] Success rates tracked
- [ ] SLA violations detected
- [ ] Metrics visualized in Airflow UI
- [ ] Weekly execution reports generated

---

#### FR-4.5: Notifications
**Description:** Notify team of pipeline status

**Requirements:**
- Email notification on failure
- Slack notification on success/failure
- Include run details in notifications
- Attach logs for failures
- Summary reports for successes

**Notification Content:**

**Failure Email:**
```
Subject: [FAILURE] ML Training Pipeline - 2025-10-18

Pipeline: ml_training_pipeline
Status: FAILED
Failed Task: train_model
Execution Date: 2025-10-18 14:30:00
Duration: 45 minutes

Error: OutOfMemoryError during model training

Logs: [Attached]
Airflow Link: http://airflow:8080/dags/ml_training_pipeline/grid
```

**Success Email:**
```
Subject: [SUCCESS] ML Training Pipeline - 2025-10-18

Pipeline: ml_training_pipeline
Status: SUCCESS
Execution Date: 2025-10-18 14:30:00
Duration: 2 hours 15 minutes

Results:
- Test Accuracy: 86.4%
- Model Version: 12
- Model Stage: Staging

MLflow Link: http://mlflow:5000/experiments/0
```

**Acceptance Criteria:**
- [ ] Failure notifications sent
- [ ] Success notifications sent
- [ ] Notifications include relevant details
- [ ] Links to Airflow and MLflow included

---

## Non-Functional Requirements

### NFR-1: Reproducibility

**Description:** All experiments must be fully reproducible

**Requirements:**
- Fixed random seeds for all operations
- Version control for code (Git)
- Version control for data (DVC)
- Pinned dependency versions
- Documented environment setup

**Reproducibility Checklist:**
- [ ] Random seeds fixed (`torch.manual_seed(42)`)
- [ ] Dependencies pinned in `requirements.txt`
- [ ] Data versioned with DVC
- [ ] Code versioned with Git
- [ ] Environment documented (Docker/Conda)
- [ ] Experiments reproducible from metadata

---

### NFR-2: Performance

**Description:** Pipeline must meet performance targets

**Performance Targets:**
- Data ingestion: Process 100K records in <10 minutes
- Data validation: Complete in <5 minutes
- Preprocessing: Complete in <10 minutes
- Training: Complete in <30 minutes per experiment
- MLflow UI: Load experiments in <2 seconds
- Airflow: Handle 10+ concurrent tasks

**Acceptance Criteria:**
- [ ] Data pipeline completes in <25 minutes
- [ ] Training completes in <30 minutes
- [ ] MLflow UI responsive (<2s load)
- [ ] Airflow handles concurrent tasks
- [ ] No memory leaks during long runs

---

### NFR-3: Reliability

**Description:** Pipeline must be highly reliable

**Reliability Targets:**
- Pipeline success rate: >95%
- Automatic retry on transient failures
- Data validation prevents bad data
- Monitoring alerts on anomalies

**Acceptance Criteria:**
- [ ] 95%+ success rate over 20 runs
- [ ] Transient failures retried automatically
- [ ] Bad data caught by validation
- [ ] Monitoring alerts working

---

### NFR-4: Scalability

**Description:** System must scale to handle growth

**Scalability Targets:**
- Support 100+ experiments in MLflow
- Handle datasets up to 1GB
- Model registry supports 50+ versions
- Airflow schedules 10+ pipelines

**Acceptance Criteria:**
- [ ] 100+ experiments tracked
- [ ] 1GB dataset processed successfully
- [ ] 50+ model versions registered
- [ ] Multiple pipelines scheduled

---

### NFR-5: Usability

**Description:** System must be easy to use

**Requirements:**
- Clear error messages
- Comprehensive documentation
- Example notebooks
- Setup automation
- Intuitive UI navigation

**Acceptance Criteria:**
- [ ] Error messages actionable
- [ ] Documentation complete
- [ ] Setup script works
- [ ] Example notebooks provided
- [ ] New users can start in <1 hour

---

### NFR-6: Maintainability

**Description:** Code must be maintainable

**Requirements:**
- Modular code structure
- Comprehensive logging
- Unit tests for components
- Integration tests for pipeline
- Code documentation (docstrings)

**Acceptance Criteria:**
- [ ] Code organized in modules
- [ ] All functions have docstrings
- [ ] Logging at appropriate levels
- [ ] 70%+ test coverage
- [ ] Integration tests pass

---

## Technical Specifications

### Technology Stack Versions

```yaml
python: "3.11+"
pytorch: "2.1.0"
mlflow: "2.8.1"
airflow: "2.7.3"
dvc: "3.30.1"
great-expectations: "0.18.3"
postgresql: "15"
redis: "7"
minio: "latest"
```

### Infrastructure Requirements

**Minimum Hardware:**
- CPU: 4 cores
- RAM: 16GB
- Storage: 50GB
- GPU: Optional (speeds up training)

**Recommended Hardware:**
- CPU: 8 cores
- RAM: 32GB
- Storage: 100GB
- GPU: NVIDIA T4 or better

### Network Requirements

**Ports to Expose:**
- 5000: MLflow UI
- 8080: Airflow UI
- 9000: MinIO API
- 9001: MinIO Console
- 5432: PostgreSQL
- 6379: Redis

---

## Acceptance Criteria

### Phase 1: Infrastructure ✅

- [ ] Docker Compose file created
- [ ] All services start successfully
- [ ] MLflow UI accessible at http://localhost:5000
- [ ] Airflow UI accessible at http://localhost:8080
- [ ] MinIO Console accessible at http://localhost:9001
- [ ] PostgreSQL accessible on port 5432
- [ ] Services persist data across restarts

### Phase 2: Data Pipeline ✅

- [ ] Data ingestion module completed
- [ ] Ingests from CSV, API, database
- [ ] Data validation with Great Expectations
- [ ] Validation suite has 5+ expectations
- [ ] Preprocessing pipeline functional
- [ ] Train/val/test split created
- [ ] DVC initialized and configured
- [ ] Data versioned with DVC
- [ ] 3+ data versions tagged

### Phase 3: Training & Tracking ✅

- [ ] Training module completed
- [ ] Supports ResNet18 and MobileNetV2
- [ ] MLflow tracking integrated
- [ ] Parameters logged
- [ ] Metrics logged per epoch
- [ ] Model artifacts saved
- [ ] 5+ experiments tracked
- [ ] Models achieve >75% val accuracy
- [ ] Training completes in <30 min

### Phase 4: Model Registry ✅

- [ ] Models registered in MLflow
- [ ] 3+ model versions present
- [ ] Lifecycle stages working
- [ ] Production model designated
- [ ] Model metadata complete
- [ ] Rollback to previous version tested

### Phase 5: Orchestration ✅

- [ ] Airflow DAG implemented
- [ ] 7+ tasks in DAG
- [ ] Task dependencies correct
- [ ] DAG runs successfully end-to-end
- [ ] Pipeline scheduled weekly
- [ ] Error handling and retries working
- [ ] Notifications configured
- [ ] 3+ successful scheduled runs

### Phase 6: Documentation ✅

- [ ] README.md complete
- [ ] Architecture.md with diagrams
- [ ] Setup guide created
- [ ] MLflow usage guide
- [ ] DVC workflow documented
- [ ] Troubleshooting guide
- [ ] Code comments and docstrings
- [ ] Example notebooks

---

## Constraints and Assumptions

### Constraints

1. **Local development only** - No cloud deployment required
2. **Small dataset** - Max 1GB for fast iteration
3. **No GPU required** - CPU training acceptable
4. **Single machine** - No distributed training
5. **English documentation** - All docs in English

### Assumptions

1. **Docker available** - User has Docker installed
2. **Internet access** - For downloading models and data
3. **Basic ML knowledge** - User understands ML concepts
4. **Git knowledge** - User familiar with Git
5. **Linux/MacOS** - Primary development platforms (Windows works with adjustments)

---

## Out of Scope

The following are **NOT** required for this project:

- ❌ Cloud deployment (AWS, GCP, Azure)
- ❌ Distributed training (multi-GPU, multi-node)
- ❌ Production-scale infrastructure
- ❌ Model serving/deployment (covered in Projects 1-2)
- ❌ A/B testing framework
- ❌ Model drift detection
- ❌ Feature store (Feast) - Optional, not required
- ❌ AutoML integration
- ❌ Real-time inference
- ❌ Model explainability (SHAP, LIME)

These topics are covered in later projects (Senior Engineer level).

---

**Requirements Version:** 1.0
**Approval:** AI Infrastructure Curriculum Team
**Review Date:** October 18, 2025
