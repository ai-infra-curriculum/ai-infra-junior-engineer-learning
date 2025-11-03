# Lecture 05: Workflow Orchestration and Airflow Monitoring

## Table of Contents
1. [Introduction](#introduction)
2. [Workflow Orchestration Fundamentals](#workflow-orchestration-fundamentals)
3. [Apache Airflow Architecture](#apache-airflow-architecture)
4. [Installing Airflow](#installing-airflow)
5. [Creating DAGs](#creating-dags)
6. [Monitoring Airflow Workflows](#monitoring-airflow-workflows)
7. [Integrating Prometheus with Airflow](#integrating-prometheus-with-airflow)
8. [Building Grafana Dashboards for Airflow](#building-grafana-dashboards-for-airflow)
9. [Alerting on Workflow Failures](#alerting-on-workflow-failures)
10. [ML Pipeline Monitoring Patterns](#ml-pipeline-monitoring-patterns)
11. [Summary and Best Practices](#summary-and-best-practices)

---

## Introduction

### Why Workflow Orchestration?

ML infrastructure involves complex, multi-step workflows:

**Data Pipeline**:
1. Extract data from sources
2. Transform and clean data
3. Feature engineering
4. Store in feature store

**Training Pipeline**:
1. Load training data
2. Train model
3. Evaluate performance
4. Save checkpoint if improved

**Deployment Pipeline**:
1. Load best model
2. Run validation tests
3. Deploy to staging
4. Run integration tests
5. Deploy to production

Without orchestration, you'd manage dependencies manually with cron jobs and shell scripts—a recipe for failure.

### What Is Apache Airflow?

**Apache Airflow** is an open-source workflow orchestration platform that:
- Defines workflows as **Directed Acyclic Graphs (DAGs)** in Python
- Schedules and executes tasks with dependencies
- Monitors execution and retries failures
- Provides rich UI for observability
- Integrates with monitoring systems

### Learning Objectives

By the end of this lecture, you will:
- Understand workflow orchestration concepts
- Install and configure Apache Airflow
- Write DAGs for ML pipelines
- Monitor DAG execution and task status
- Integrate Airflow with Prometheus/Grafana
- Build dashboards for workflow metrics
- Set up alerting for pipeline failures
- Apply best practices for production workflows

---

## Workflow Orchestration Fundamentals

### Key Concepts

#### Directed Acyclic Graph (DAG)
A **DAG** represents a workflow:
- **Directed**: Tasks flow in specific direction (A → B → C)
- **Acyclic**: No circular dependencies (can't go A → B → A)
- **Graph**: Collection of nodes (tasks) and edges (dependencies)

```
    ┌────────────┐
    │ Extract    │
    │ Data       │
    └──────┬─────┘
           │
           ▼
    ┌────────────┐
    │ Transform  │
    │ Data       │
    └──────┬─────┘
           │
           ▼
    ┌────────────┐
    │ Load       │
    │ Data       │
    └────────────┘
```

#### Task
A **task** is a single unit of work (Python function, Bash script, etc.).

#### Operator
An **operator** defines what a task does:
- `PythonOperator`: Run Python function
- `BashOperator`: Run shell command
- `SQLOperator`: Run SQL query
- `KubernetesPodOperator`: Run in K8s Pod

#### Dependencies
**Dependencies** define task order:
```python
task_a >> task_b >> task_c  # Sequential
task_a >> [task_b, task_c]  # Parallel after A
```

### Workflow Orchestrators Comparison

| Feature | Cron | Airflow | Prefect | Kubeflow Pipelines |
|---------|------|---------|---------|---------------------|
| DAG Definition | No | Python | Python | Python |
| Dependency Management | Manual | Automatic | Automatic | Automatic |
| Retries | Manual | Built-in | Built-in | Built-in |
| Web UI | No | Yes | Yes | Yes |
| Monitoring | Basic logs | Rich | Rich | Rich |
| Cloud Native | No | Partial | Yes | Yes (K8s) |
| Use Case | Simple schedules | General workflows | Modern workflows | ML-specific |

---

## Apache Airflow Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────┐
│                    Airflow Architecture                  │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────┐     ┌──────────┐     ┌──────────┐        │
│  │   Web    │     │Scheduler │     │ Workers  │        │
│  │  Server  │     │          │     │  (Celery)│        │
│  └────┬─────┘     └────┬─────┘     └────┬─────┘        │
│       │                │                 │               │
│       └────────────────┼─────────────────┘               │
│                        │                                 │
│                  ┌─────┴─────┐                          │
│                  │  Metadata │                          │
│                  │  Database │                          │
│                  │(PostgreSQL)│                          │
│                  └───────────┘                          │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

#### 1. **Scheduler**
- Monitors DAGs and triggers tasks when dependencies are met
- Submits tasks to executors

#### 2. **Executor**
- Runs tasks (SequentialExecutor, LocalExecutor, CeleryExecutor, KubernetesExecutor)
- Manages task distribution

#### 3. **Workers**
- Execute actual task code
- Report status back to scheduler

#### 4. **Web Server**
- UI for monitoring and managing workflows
- Trigger manual runs
- View logs

#### 5. **Metadata Database**
- Stores DAG definitions, task states, execution history
- PostgreSQL or MySQL in production

---

## Installing Airflow

### Installation Methods

#### Option 1: Docker Compose (Recommended for Development)

```bash
# Download docker-compose.yaml
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.7.1/docker-compose.yaml'

# Create necessary directories
mkdir -p ./dags ./logs ./plugins ./config

# Set Airflow user ID
echo -e "AIRFLOW_UID=$(id -u)" > .env

# Initialize database
docker-compose up airflow-init

# Start all services
docker-compose up -d

# Verify services running
docker-compose ps

# Access UI at http://localhost:8080
# Default credentials: airflow / airflow
```

#### Option 2: pip Installation (Single Node)

```bash
# Set Airflow home
export AIRFLOW_HOME=~/airflow

# Install Airflow with constraints for specific Python version
AIRFLOW_VERSION=2.7.1
PYTHON_VERSION="$(python --version | cut -d " " -f 2 | cut -d "." -f 1-2)"
CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"

pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"

# Initialize database (SQLite by default)
airflow db init

# Create admin user
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin

# Start web server
airflow webserver --port 8080 &

# Start scheduler (in separate terminal)
airflow scheduler &
```

#### Option 3: Kubernetes with Helm

```bash
# Add Airflow Helm repo
helm repo add apache-airflow https://airflow.apache.org
helm repo update

# Create namespace
kubectl create namespace airflow

# Install Airflow
helm install airflow apache-airflow/airflow \
  --namespace airflow \
  --set executor=KubernetesExecutor

# Port-forward to access UI
kubectl port-forward svc/airflow-webserver 8080:8080 --namespace airflow
```

### Configuration

```python
# airflow.cfg (key settings)

[core]
# DAG folder location
dags_folder = /opt/airflow/dags

# Executor: SequentialExecutor, LocalExecutor, CeleryExecutor, KubernetesExecutor
executor = LocalExecutor

# Parallelism: max tasks across all DAGs
parallelism = 32

# DAG concurrency: max tasks per DAG run
dag_concurrency = 16

[webserver]
# Web server port
web_server_port = 8080

# Enable auth (RBAC)
rbac = True

[scheduler]
# How often to scan for DAG changes
dag_dir_list_interval = 30

# Catchup: backfill missed runs
catchup_by_default = False

[logging]
# Remote log storage (S3, GCS, etc.)
remote_logging = True
remote_base_log_folder = s3://my-bucket/airflow-logs

[metrics]
# Enable StatsD metrics
statsd_on = True
statsd_host = localhost
statsd_port = 8125
statsd_prefix = airflow
```

---

## Creating DAGs

### Simple DAG Structure

```python
# dags/simple_dag.py
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

# Default arguments for all tasks
default_args = {
    'owner': 'ml-team',
    'depends_on_past': False,
    'email': ['alerts@example.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

# Define DAG
with DAG(
    dag_id='simple_ml_pipeline',
    default_args=default_args,
    description='Simple ML training pipeline',
    schedule='0 2 * * *',  # Run daily at 2 AM
    start_date=datetime(2024, 1, 1),
    catchup=False,  # Don't backfill past dates
    tags=['ml', 'training'],
) as dag:

    # Task 1: Python function
    def extract_data(**context):
        """Extract data from source."""
        print("Extracting data...")
        # Return data to XCom for next task
        return {"records": 1000, "path": "/data/extracted.csv"}

    extract_task = PythonOperator(
        task_id='extract_data',
        python_callable=extract_data,
    )

    # Task 2: Bash command
    transform_task = BashOperator(
        task_id='transform_data',
        bash_command='python /scripts/transform.py --input /data/extracted.csv',
    )

    # Task 3: Python function with XCom
    def train_model(**context):
        """Train ML model."""
        # Get data from previous task via XCom
        ti = context['ti']
        extracted_data = ti.xcom_pull(task_ids='extract_data')
        print(f"Training on {extracted_data['records']} records")

        # Training code here
        accuracy = 0.92
        return {"accuracy": accuracy, "model_path": "/models/model.pkl"}

    train_task = PythonOperator(
        task_id='train_model',
        python_callable=train_model,
    )

    # Define dependencies
    extract_task >> transform_task >> train_task
```

### ML Pipeline DAG Example

```python
# dags/ml_training_pipeline.py
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator

default_args = {
    'owner': 'ml-engineers',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(hours=2),
}

def load_training_data(**context):
    """Load data from data warehouse."""
    import pandas as pd
    # Simulated data loading
    print("Loading training data...")
    record_count = 50000
    context['ti'].xcom_push(key='record_count', value=record_count)
    return record_count

def preprocess_data(**context):
    """Clean and preprocess data."""
    print("Preprocessing data...")
    # Feature engineering, scaling, etc.
    return "/data/processed/train.parquet"

def train_model(**context):
    """Train ML model."""
    import time
    print("Training model...")
    time.sleep(10)  # Simulate training

    # Return metrics
    metrics = {
        "accuracy": 0.92,
        "f1_score": 0.89,
        "training_time": 10.5
    }
    context['ti'].xcom_push(key='metrics', value=metrics)
    return metrics

def check_model_quality(**context):
    """Decide whether to deploy based on metrics."""
    metrics = context['ti'].xcom_pull(task_ids='train_model', key='metrics')
    accuracy = metrics['accuracy']

    # Branch logic
    if accuracy >= 0.90:
        return 'deploy_model'
    else:
        return 'notify_failure'

def deploy_model(**context):
    """Deploy model to production."""
    print("Deploying model to production...")
    # Deployment logic
    return "Model deployed successfully"

def notify_success(**context):
    """Send success notification."""
    metrics = context['ti'].xcom_pull(task_ids='train_model', key='metrics')
    print(f"✅ Pipeline succeeded! Accuracy: {metrics['accuracy']:.2%}")

def notify_failure(**context):
    """Send failure notification."""
    metrics = context['ti'].xcom_pull(task_ids='train_model', key='metrics')
    print(f"❌ Pipeline failed! Accuracy: {metrics['accuracy']:.2%} below threshold")

with DAG(
    dag_id='ml_training_pipeline',
    default_args=default_args,
    description='Complete ML training and deployment pipeline',
    schedule='0 2 * * *',  # Daily at 2 AM
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['ml', 'production'],
) as dag:

    start = DummyOperator(task_id='start')

    load_data = PythonOperator(
        task_id='load_data',
        python_callable=load_training_data,
    )

    preprocess = PythonOperator(
        task_id='preprocess_data',
        python_callable=preprocess_data,
    )

    train = PythonOperator(
        task_id='train_model',
        python_callable=train_model,
    )

    check_quality = BranchPythonOperator(
        task_id='check_quality',
        python_callable=check_model_quality,
    )

    deploy = PythonOperator(
        task_id='deploy_model',
        python_callable=deploy_model,
    )

    success = PythonOperator(
        task_id='notify_success',
        python_callable=notify_success,
        trigger_rule='one_success',  # Run if deployed
    )

    failure = PythonOperator(
        task_id='notify_failure',
        python_callable=notify_failure,
        trigger_rule='one_success',  # Run if quality check failed
    )

    end = DummyOperator(
        task_id='end',
        trigger_rule='none_failed_min_one_success',
    )

    # Define workflow
    start >> load_data >> preprocess >> train >> check_quality
    check_quality >> deploy >> success >> end
    check_quality >> failure >> end
```

---

## Monitoring Airflow Workflows

### Airflow UI Overview

**Key Pages**:

1. **DAGs View**: List all DAGs with status
2. **Graph View**: Visual representation of task dependencies
3. **Tree View**: Historical runs over time
4. **Gantt Chart**: Task duration timeline
5. **Task Instance Details**: Logs, XCom, duration

### Task States

| State | Meaning | Color |
|-------|---------|-------|
| `success` | Task completed successfully | Green |
| `running` | Task currently executing | Light green |
| `failed` | Task failed | Red |
| `up_for_retry` | Task failed, will retry | Orange |
| `queued` | Task waiting for executor slot | Gray |
| `scheduled` | Task scheduled to run | Tan |
| `skipped` | Task skipped (branching) | Pink |
| `upstream_failed` | Upstream task failed | Red outline |

### Viewing Logs

```bash
# Via UI: Click task → View Log

# Via CLI
airflow tasks logs ml_training_pipeline train_model 2024-01-15

# Tail logs in real-time
airflow tasks logs ml_training_pipeline train_model 2024-01-15 --follow

# View logs from specific task attempt
airflow tasks logs ml_training_pipeline train_model 2024-01-15 --try-number 2
```

### Triggering Manual Runs

```bash
# Via UI: Click "Play" button on DAG

# Via CLI
airflow dags trigger ml_training_pipeline

# With custom config
airflow dags trigger ml_training_pipeline \
  --conf '{"epochs": 100, "learning_rate": 0.001}'

# Backfill date range
airflow dags backfill ml_training_pipeline \
  --start-date 2024-01-01 \
  --end-date 2024-01-31
```

---

## Integrating Prometheus with Airflow

### Enabling StatsD Metrics

Airflow emits metrics via StatsD, which Prometheus scrapes.

**1. Configure Airflow to send StatsD metrics**:

```ini
# airflow.cfg
[metrics]
statsd_on = True
statsd_host = statsd-exporter
statsd_port = 9125
statsd_prefix = airflow
```

**2. Deploy StatsD Exporter**:

```yaml
# statsd-exporter.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: statsd-exporter
spec:
  replicas: 1
  selector:
    matchLabels:
      app: statsd-exporter
  template:
    metadata:
      labels:
        app: statsd-exporter
    spec:
      containers:
      - name: statsd-exporter
        image: prom/statsd-exporter:latest
        ports:
        - containerPort: 9125
          protocol: UDP
          name: statsd
        - containerPort: 9102
          protocol: TCP
          name: metrics
---
apiVersion: v1
kind: Service
metadata:
  name: statsd-exporter
spec:
  selector:
    app: statsd-exporter
  ports:
  - port: 9125
    protocol: UDP
    name: statsd
  - port: 9102
    protocol: TCP
    name: metrics
```

**3. Configure Prometheus to scrape**:

```yaml
# prometheus-config.yaml
scrape_configs:
  - job_name: 'airflow'
    static_configs:
      - targets: ['statsd-exporter:9102']
    metrics_path: /metrics
```

### Key Airflow Metrics

```promql
# DAG run duration
airflow_dagrun_duration_seconds_sum / airflow_dagrun_duration_seconds_count

# Task failures (rate per minute)
rate(airflow_ti_failures_total[5m])

# Task success rate
rate(airflow_ti_successes_total[5m])
/ (rate(airflow_ti_successes_total[5m]) + rate(airflow_ti_failures_total[5m]))

# Running tasks
airflow_executor_running_tasks

# Queued tasks
airflow_executor_queued_tasks

# Scheduler heartbeat (should be recent)
airflow_scheduler_heartbeat

# DAG processing time
airflow_dag_processing_total_parse_time_seconds
```

### Custom Metrics from DAGs

```python
from airflow.metrics import metrics

def train_model(**context):
    """Train model and emit custom metrics."""
    import time

    start_time = time.time()

    # Training code
    accuracy = 0.92

    # Emit custom metrics
    metrics.incr('ml_training.runs', 1)
    metrics.gauge('ml_training.accuracy', accuracy)
    metrics.timing('ml_training.duration', time.time() - start_time)

    return {"accuracy": accuracy}
```

---

## Building Grafana Dashboards for Airflow

### Dashboard Layout

```
┌────────────────────────────────────────────────────────┐
│          Airflow Monitoring Dashboard                  │
├────────────────────────────────────────────────────────┤
│  Overall Health                                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐             │
│  │   DAG    │ │  Task    │ │Scheduler │             │
│  │ Success  │ │Execution │ │ Health   │             │
│  │   Rate   │ │  Time    │ │          │             │
│  └──────────┘ └──────────┘ └──────────┘             │
│                                                        │
│  DAG Run Duration                                      │
│  ┌──────────────────────────────────────────────┐    │
│  │ [Graph showing DAG duration over time]       │    │
│  └──────────────────────────────────────────────┘    │
│                                                        │
│  Task Failures                                         │
│  ┌──────────────────────────────────────────────┐    │
│  │ [Graph showing failed tasks by DAG]          │    │
│  └──────────────────────────────────────────────┘    │
│                                                        │
│  Resource Usage                                        │
│  ┌──────────────────────────────────────────────┐    │
│  │ [Graph showing executor queue depth]         │    │
│  └──────────────────────────────────────────────┘    │
└────────────────────────────────────────────────────────┘
```

### Panel Queries

**1. DAG Success Rate (Stat Panel)**:
```promql
sum(rate(airflow_dagrun_duration_success_total[1h]))
/
sum(rate(airflow_dagrun_duration_total[1h]))
* 100
```

**2. Average Task Duration (Gauge)**:
```promql
avg(airflow_task_duration_seconds_sum / airflow_task_duration_seconds_count)
```

**3. Failed Tasks (Time Series)**:
```promql
sum by (dag_id) (rate(airflow_ti_failures_total[5m]))
```

**4. Executor Queue Depth (Time Series)**:
```promql
airflow_executor_queued_tasks
```

**5. DAG Run Duration by DAG (Time Series)**:
```promql
sum by (dag_id) (
  rate(airflow_dagrun_duration_seconds_sum[5m])
  /
  rate(airflow_dagrun_duration_seconds_count[5m])
)
```

**6. Scheduler Lag (Stat)**:
```promql
time() - airflow_scheduler_heartbeat
```

**7. Task Execution Count (Bar Gauge)**:
```promql
sum by (dag_id) (increase(airflow_ti_successes_total[1h]))
```

### Example Dashboard JSON

```json
{
  "dashboard": {
    "title": "Airflow Monitoring",
    "panels": [
      {
        "id": 1,
        "title": "DAG Success Rate",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(rate(airflow_dagrun_duration_success_total[1h])) / sum(rate(airflow_dagrun_duration_total[1h])) * 100"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "thresholds": {
              "steps": [
                {"color": "red", "value": 0},
                {"color": "yellow", "value": 90},
                {"color": "green", "value": 95}
              ]
            }
          }
        }
      },
      {
        "id": 2,
        "title": "Failed Tasks (5m rate)",
        "type": "timeseries",
        "targets": [
          {
            "expr": "sum by (dag_id) (rate(airflow_ti_failures_total[5m]))",
            "legendFormat": "{{dag_id}}"
          }
        ]
      }
    ]
  }
}
```

---

## Alerting on Workflow Failures

### Prometheus Alert Rules

```yaml
# airflow-alerts.yaml
groups:
  - name: airflow
    interval: 30s
    rules:
      # DAG failure alert
      - alert: AirflowDAGFailed
        expr: |
          increase(airflow_dagrun_duration_failed_total[15m]) > 0
        for: 5m
        labels:
          severity: warning
          component: airflow
        annotations:
          summary: "Airflow DAG failed"
          description: "DAG {{ $labels.dag_id }} has failed runs in the last 15 minutes"

      # High task failure rate
      - alert: AirflowHighTaskFailureRate
        expr: |
          sum(rate(airflow_ti_failures_total[5m]))
          /
          sum(rate(airflow_ti_total[5m]))
          > 0.1
        for: 10m
        labels:
          severity: warning
          component: airflow
        annotations:
          summary: "High Airflow task failure rate"
          description: "Task failure rate is {{ $value | humanizePercentage }} over last 10 minutes"

      # Scheduler not heartbeating
      - alert: AirflowSchedulerDown
        expr: |
          time() - airflow_scheduler_heartbeat > 300
        for: 5m
        labels:
          severity: critical
          component: airflow
        annotations:
          summary: "Airflow scheduler not responding"
          description: "Scheduler last heartbeat was {{ $value | humanizeDuration }} ago"

      # Tasks stuck in queue
      - alert: AirflowTasksStuck
        expr: |
          airflow_executor_queued_tasks > 100
        for: 30m
        labels:
          severity: warning
          component: airflow
        annotations:
          summary: "Many tasks stuck in queue"
          description: "{{ $value }} tasks have been queued for >30 minutes"

      # Long-running DAG
      - alert: AirflowDAGRunningTooLong
        expr: |
          airflow_dagrun_duration_seconds_sum
          / airflow_dagrun_duration_seconds_count
          > 7200
        for: 1h
        labels:
          severity: info
          component: airflow
        annotations:
          summary: "DAG running longer than expected"
          description: "{{ $labels.dag_id }} average duration is {{ $value | humanizeDuration }}"
```

### Airflow Email Alerts

```python
# In DAG definition
default_args = {
    'email': ['ml-team@example.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'email_on_success': False,  # Optional
}

# Custom email on failure
from airflow.operators.email import EmailOperator

send_failure_email = EmailOperator(
    task_id='send_failure_email',
    to='alerts@example.com',
    subject='ML Pipeline Failed: {{ dag.dag_id }}',
    html_content='''
    <h3>Pipeline Failure</h3>
    <p>DAG: {{ dag.dag_id }}</p>
    <p>Run ID: {{ run_id }}</p>
    <p>Execution Date: {{ ds }}</p>
    <p>Failed Task: {{ task_instance.task_id }}</p>
    <p><a href="{{ task_instance.log_url }}">View Logs</a></p>
    ''',
    trigger_rule='one_failed',  # Run only if upstream failed
)
```

### Slack Notifications

```python
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator

def slack_failed_task(context):
    """Send Slack notification on task failure."""
    slack_msg = f"""
:red_circle: Task Failed
*DAG*: {context['dag'].dag_id}
*Task*: {context['task'].task_id}
*Execution Time*: {context['execution_date']}
*Log*: {context['task_instance'].log_url}
    """

    return SlackWebhookOperator(
        task_id='slack_alert',
        http_conn_id='slack_webhook',
        message=slack_msg,
    ).execute(context=context)

# In task definition
train_task = PythonOperator(
    task_id='train_model',
    python_callable=train_model,
    on_failure_callback=slack_failed_task,
)
```

---

## ML Pipeline Monitoring Patterns

### 1. Data Quality Checks

```python
def validate_data_quality(**context):
    """Check data quality before training."""
    import pandas as pd

    df = pd.read_parquet("/data/train.parquet")

    # Check row count
    if len(df) < 1000:
        raise ValueError(f"Insufficient data: {len(df)} rows")

    # Check for nulls
    null_pct = df.isnull().sum().sum() / (len(df) * len(df.columns))
    if null_pct > 0.05:
        raise ValueError(f"Too many nulls: {null_pct:.2%}")

    # Check label distribution
    label_counts = df['label'].value_counts()
    if label_counts.min() / label_counts.max() < 0.1:
        raise ValueError("Imbalanced dataset detected")

    # Emit metrics
    metrics.gauge('data_quality.row_count', len(df))
    metrics.gauge('data_quality.null_pct', null_pct)

    return {"status": "passed", "row_count": len(df)}

quality_check = PythonOperator(
    task_id='check_data_quality',
    python_callable=validate_data_quality,
)
```

### 2. Model Performance Tracking

```python
def track_model_performance(**context):
    """Track model metrics over time."""
    metrics_dict = context['ti'].xcom_pull(task_ids='evaluate_model')

    # Emit to Prometheus
    metrics.gauge('model.accuracy', metrics_dict['accuracy'])
    metrics.gauge('model.precision', metrics_dict['precision'])
    metrics.gauge('model.recall', metrics_dict['recall'])
    metrics.gauge('model.f1_score', metrics_dict['f1_score'])

    # Store in metadata database
    from airflow.models import Variable
    import json

    history = json.loads(Variable.get('model_metrics_history', '[]'))
    history.append({
        'timestamp': datetime.now().isoformat(),
        'metrics': metrics_dict
    })

    # Keep last 100 runs
    Variable.set('model_metrics_history', json.dumps(history[-100:]))

    return metrics_dict

track_metrics = PythonOperator(
    task_id='track_metrics',
    python_callable=track_model_performance,
)
```

### 3. Resource Usage Monitoring

```python
def monitor_resource_usage(**context):
    """Monitor GPU/CPU usage during training."""
    import psutil
    import GPUtil

    # CPU metrics
    cpu_percent = psutil.cpu_percent(interval=1)
    memory_percent = psutil.virtual_memory().percent

    # GPU metrics (if available)
    try:
        gpus = GPUtil.getGPUs()
        gpu_usage = [gpu.load * 100 for gpu in gpus]
        gpu_memory = [gpu.memoryUtil * 100 for gpu in gpus]

        metrics.gauge('resource.gpu_usage', sum(gpu_usage) / len(gpu_usage))
        metrics.gauge('resource.gpu_memory', sum(gpu_memory) / len(gpu_memory))
    except:
        pass

    metrics.gauge('resource.cpu_percent', cpu_percent)
    metrics.gauge('resource.memory_percent', memory_percent)

    return {
        'cpu': cpu_percent,
        'memory': memory_percent
    }

resource_monitor = PythonOperator(
    task_id='monitor_resources',
    python_callable=monitor_resource_usage,
)
```

---

## Summary and Best Practices

### Key Takeaways

1. **Airflow orchestrates workflows** as Python-defined DAGs
2. **Tasks represent work units** (data processing, training, deployment)
3. **Dependencies define execution order** using `>>` operator
4. **Monitoring is built-in** via web UI and metrics
5. **Prometheus integration** provides centralized metrics
6. **Grafana dashboards** visualize workflow health
7. **Alerting catches failures** before they impact production

### Best Practices

```python
# 1. Set appropriate retries and timeouts
default_args = {
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(hours=2),
}

# 2. Use catchup=False for new DAGs
with DAG(
    'my_dag',
    catchup=False,  # Don't backfill past dates
    ...
) as dag:
    pass

# 3. Add task documentation
train_task = PythonOperator(
    task_id='train_model',
    python_callable=train_model,
    doc_md="""
    ## Train Model Task

    Trains XGBoost classifier on processed data.

    **Inputs**: /data/processed/train.parquet
    **Outputs**: /models/xgboost.pkl
    **Duration**: ~30 minutes
    """,
)

# 4. Use sensors for external dependencies
from airflow.sensors.filesystem import FileSensor

wait_for_data = FileSensor(
    task_id='wait_for_data',
    filepath='/data/new_batch.csv',
    poke_interval=60,  # Check every 60 seconds
    timeout=3600,      # Give up after 1 hour
)

# 5. Implement idempotency
def idempotent_task(**context):
    """Task can be safely retried."""
    output_path = "/output/result.csv"

    # Check if already completed
    if os.path.exists(output_path):
        print("Output exists, skipping...")
        return

    # Do work
    result = process_data()
    result.to_csv(output_path)

# 6. Use XCom for small data only
# ❌ Bad: Pass large DataFrames via XCom
# ✅ Good: Pass file paths via XCom

# 7. Monitor DAG performance
def emit_dag_metrics(**context):
    """Emit custom metrics for DAG."""
    run_id = context['run_id']
    duration = context['ti'].duration

    metrics.timing(f'dag.{dag_id}.duration', duration)
    metrics.incr(f'dag.{dag_id}.runs')

# 8. Use tags for organization
with DAG(
    'ml_training',
    tags=['ml', 'production', 'daily'],
    ...
) as dag:
    pass
```

### Common Pitfalls

```python
# ❌ Don't put heavy computation in DAG definition
# This runs every time Airflow parses the DAG
df = pd.read_csv('/large_file.csv')  # BAD!

with DAG('my_dag', ...) as dag:
    # Define tasks using df...
    pass

# ✅ Put computation in task functions
def load_and_process(**context):
    df = pd.read_csv('/large_file.csv')  # GOOD!
    # Process df...

# ❌ Don't use dynamic task generation without limits
for i in range(10000):  # Creates 10k tasks!
    task = PythonOperator(...)

# ✅ Use SubDAGs or dynamic task mapping (Airflow 2.3+)
@task_group
def process_group(items):
    for item in items[:100]:  # Limit tasks
        process_item(item)
```

### Troubleshooting Checklist

```bash
# Scheduler not picking up DAG?
airflow dags list  # Check if DAG appears
airflow dags list-import-errors  # Check for errors

# Task stuck in queued state?
airflow config get-value core executor  # Check executor type
airflow tasks test my_dag my_task 2024-01-01  # Test task locally

# Can't see logs?
airflow config get-value logging remote_logging  # Check log config
kubectl logs airflow-scheduler  # Check scheduler logs

# DAG not scheduling?
# Check start_date, schedule_interval, and catchup settings
```

### Next Steps

You now understand workflow orchestration and monitoring! Practice by:
1. Installing Airflow locally with Docker Compose
2. Creating a simple ML training DAG
3. Integrating Airflow with Prometheus
4. Building Grafana dashboards for your workflows
5. Setting up alerts for pipeline failures

Continue to **Exercise 06: Airflow Workflow Monitoring** to apply these concepts hands-on!

---

**Word Count**: ~5,400 words
**Estimated Reading Time**: 30-35 minutes
