# Exercise 06: Apache Airflow - Workflow Orchestration and Monitoring

**Difficulty**: Beginner-Intermediate
**Duration**: 3-4 hours
**Prerequisites**: Docker, Python basics, monitoring fundamentals

## Learning Objectives

By the end of this exercise, you will:

1. Understand what workflow orchestration is and why it's needed
2. Install and configure Apache Airflow
3. Create and run DAGs (Directed Acyclic Graphs)
4. Monitor workflow execution and health
5. Integrate Airflow with Prometheus for metrics
6. Set up alerts for pipeline failures
7. Debug failed workflows

## What You'll Build

A complete Airflow setup with:
- Airflow running in Docker
- Sample ML data pipeline DAGs
- Prometheus metrics integration
- Grafana dashboard for workflow monitoring
- Alerting for failed tasks

## Background: What is Apache Airflow?

### The Problem: Managing Complex Workflows

**Without orchestration**:
```bash
# Manual workflow execution
python download_data.py
python preprocess_data.py
python train_model.py
python deploy_model.py

# Problems:
# - What if step 2 fails? Do we restart everything?
# - How do we schedule this daily?
# - How do we handle retries?
# - How do we monitor progress?
# - How do we manage dependencies?
```

### The Solution: Apache Airflow

**Airflow** is a workflow orchestration platform that lets you:
- ✅ Define workflows as code (Python)
- ✅ Schedule automated execution
- ✅ Manage dependencies between tasks
- ✅ Monitor task execution
- ✅ Retry failed tasks automatically
- ✅ View logs and history
- ✅ Alert on failures

### Key Concepts

**DAG (Directed Acyclic Graph)**:
- Workflow definition
- Collection of tasks with dependencies
- No circular dependencies allowed

**Task**:
- Single unit of work
- Can be Python function, bash command, etc.
- Has states: success, failed, running, queued

**Operator**:
- Template for creating tasks
- PythonOperator, BashOperator, etc.

**Scheduler**:
- Triggers DAG runs on schedule
- Manages task execution order

**Executor**:
- Runs tasks (local, Celery, Kubernetes, etc.)

**Webserver**:
- UI for monitoring and management

## Part 1: Airflow Setup with Docker

### Step 1: Create Project Directory

```bash
mkdir airflow-monitoring-lab
cd airflow-monitoring-lab
```

### Step 2: Create Docker Compose Configuration

Create `docker-compose.yml`:

```yaml
version: '3.8'

x-airflow-common:
  &airflow-common
  image: apache/airflow:2.7.3
  environment:
    &airflow-common-env
    AIRFLOW__CORE__EXECUTOR: LocalExecutor
    AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
    AIRFLOW__CORE__FERNET_KEY: ''
    AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION: 'true'
    AIRFLOW__CORE__LOAD_EXAMPLES: 'false'
    AIRFLOW__API__AUTH_BACKENDS: 'airflow.api.auth.backend.basic_auth'
    AIRFLOW__METRICS__STATSD_ON: 'true'
    AIRFLOW__METRICS__STATSD_HOST: statsd-exporter
    AIRFLOW__METRICS__STATSD_PORT: 9125
  volumes:
    - ./dags:/opt/airflow/dags
    - ./logs:/opt/airflow/logs
    - ./plugins:/opt/airflow/plugins
  user: "${AIRFLOW_UID:-50000}:0"
  depends_on:
    &airflow-common-depends-on
    postgres:
      condition: service_healthy

services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow
    volumes:
      - postgres-db-volume:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "airflow"]
      interval: 5s
      retries: 5
    restart: always

  airflow-webserver:
    <<: *airflow-common
    command: webserver
    ports:
      - 8080:8080
    healthcheck:
      test: ["CMD", "curl", "--fail", "http://localhost:8080/health"]
      interval: 10s
      timeout: 10s
      retries: 5
    restart: always
    depends_on:
      <<: *airflow-common-depends-on
      airflow-init:
        condition: service_completed_successfully

  airflow-scheduler:
    <<: *airflow-common
    command: scheduler
    healthcheck:
      test: ["CMD-SHELL", 'airflow jobs check --job-type SchedulerJob --hostname "$${HOSTNAME}"']
      interval: 10s
      timeout: 10s
      retries: 5
    restart: always
    depends_on:
      <<: *airflow-common-depends-on
      airflow-init:
        condition: service_completed_successfully

  airflow-init:
    <<: *airflow-common
    entrypoint: /bin/bash
    command:
      - -c
      - |
        mkdir -p /sources/logs /sources/dags /sources/plugins
        chown -R "${AIRFLOW_UID:-50000}:0" /sources/{logs,dags,plugins}
        exec /entrypoint airflow version
    environment:
      <<: *airflow-common-env
      _AIRFLOW_DB_UPGRADE: 'true'
      _AIRFLOW_WWW_USER_CREATE: 'true'
      _AIRFLOW_WWW_USER_USERNAME: airflow
      _AIRFLOW_WWW_USER_PASSWORD: airflow
    user: "0:0"
    volumes:
      - .:/sources

  # StatsD Exporter for Prometheus
  statsd-exporter:
    image: prom/statsd-exporter:latest
    ports:
      - 9102:9102
      - 9125:9125/udp
    command:
      - '--statsd.mapping-config=/tmp/statsd_mapping.yml'
    volumes:
      - ./statsd_mapping.yml:/tmp/statsd_mapping.yml

  # Prometheus
  prometheus:
    image: prom/prometheus:latest
    ports:
      - 9090:9090
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'

  # Grafana
  grafana:
    image: grafana/grafana:latest
    ports:
      - 3000:3000
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana-data:/var/lib/grafana

volumes:
  postgres-db-volume:
  prometheus-data:
  grafana-data:
```

### Step 3: Create Configuration Files

Create `statsd_mapping.yml`:

```yaml
mappings:
  - match: "airflow.dag_processing.*"
    name: "airflow_dag_processing"
    labels:
      job: "airflow"

  - match: "airflow.scheduler.*"
    name: "airflow_scheduler"
    labels:
      job: "airflow"

  - match: "airflow.executor.*"
    name: "airflow_executor"
    labels:
      job: "airflow"

  - match: "airflow.dagrun.*"
    name: "airflow_dagrun"
    labels:
      job: "airflow"

  - match: "airflow.task.*"
    name: "airflow_task"
    labels:
      job: "airflow"
```

Create `prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'airflow'
    static_configs:
      - targets: ['statsd-exporter:9102']
```

### Step 4: Create Directories

```bash
mkdir -p dags logs plugins
```

### Step 5: Start Airflow

```bash
# Set Airflow UID
echo -e "AIRFLOW_UID=$(id -u)" > .env

# Start services
docker-compose up -d

# Check status
docker-compose ps
```

**Wait 1-2 minutes for initialization**, then access:
- **Airflow UI**: http://localhost:8080 (user: airflow, password: airflow)
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (user: admin, password: admin)

## Part 2: Creating Your First DAG

### Step 6: Simple Data Pipeline DAG

Create `dags/ml_training_pipeline.py`:

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import time
import random

# Default arguments for all tasks
default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=1),
}

def download_dataset(**context):
    """Simulate downloading training dataset"""
    print("📥 Downloading dataset from S3...")
    time.sleep(3)
    print("✓ Downloaded 1.2GB of training data")

    # Pass data to next task via XCom
    return {"dataset_size_gb": 1.2, "num_samples": 10000}

def preprocess_data(**context):
    """Simulate data preprocessing"""
    # Get data from previous task
    ti = context['ti']
    dataset_info = ti.xcom_pull(task_ids='download_dataset')

    print(f"🔧 Preprocessing {dataset_info['num_samples']} samples...")
    time.sleep(4)
    print("✓ Data preprocessed: cleaned, normalized, augmented")

    return {"processed_samples": dataset_info['num_samples'], "validation_split": 0.2}

def train_model(**context):
    """Simulate model training"""
    ti = context['ti']
    data_info = ti.xcom_pull(task_ids='preprocess_data')

    print(f"🤖 Training model on {data_info['processed_samples']} samples...")
    time.sleep(5)

    # Simulate metrics
    accuracy = round(random.uniform(0.85, 0.95), 4)
    print(f"✓ Training complete! Validation accuracy: {accuracy}")

    return {"accuracy": accuracy, "model_size_mb": 450}

def evaluate_model(**context):
    """Simulate model evaluation"""
    ti = context['ti']
    model_info = ti.xcom_pull(task_ids='train_model')

    print(f"📊 Evaluating model (accuracy: {model_info['accuracy']})...")
    time.sleep(2)

    if model_info['accuracy'] < 0.88:
        raise ValueError(f"Model accuracy {model_info['accuracy']} below threshold 0.88")

    print("✓ Model passed evaluation!")
    return True

def deploy_model(**context):
    """Simulate model deployment"""
    print("🚀 Deploying model to production...")
    time.sleep(3)
    print("✓ Model deployed successfully")
    return {"deployment_url": "https://api.example.com/model/v1"}

# Define the DAG
with DAG(
    'ml_training_pipeline',
    default_args=default_args,
    description='ML model training and deployment pipeline',
    schedule_interval='0 2 * * *',  # Run daily at 2 AM
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['ml', 'training', 'production'],
) as dag:

    # Task 1: Download dataset
    download = PythonOperator(
        task_id='download_dataset',
        python_callable=download_dataset,
    )

    # Task 2: Preprocess data
    preprocess = PythonOperator(
        task_id='preprocess_data',
        python_callable=preprocess_data,
    )

    # Task 3: Train model
    train = PythonOperator(
        task_id='train_model',
        python_callable=train_model,
    )

    # Task 4: Evaluate model
    evaluate = PythonOperator(
        task_id='evaluate_model',
        python_callable=evaluate_model,
    )

    # Task 5: Deploy model
    deploy = PythonOperator(
        task_id='deploy_model',
        python_callable=deploy_model,
    )

    # Task 6: Send notification
    notify = BashOperator(
        task_id='send_notification',
        bash_command='echo "✅ ML pipeline completed successfully!"',
    )

    # Define task dependencies
    download >> preprocess >> train >> evaluate >> deploy >> notify
```

**DAG workflow**:
```
download_dataset → preprocess_data → train_model → evaluate_model → deploy_model → send_notification
```

### Step 7: Verify DAG

```bash
# Refresh Airflow UI (http://localhost:8080)
# You should see "ml_training_pipeline" DAG

# Or check via CLI
docker-compose exec airflow-webserver airflow dags list
docker-compose exec airflow-webserver airflow dags show ml_training_pipeline
```

### Step 8: Trigger DAG Manually

**Option 1: Via UI**:
1. Go to http://localhost:8080
2. Find "ml_training_pipeline"
3. Click the play button ▶️ on the right
4. Click "Trigger DAG"

**Option 2: Via CLI**:
```bash
docker-compose exec airflow-webserver airflow dags trigger ml_training_pipeline
```

**Monitor execution**:
1. Click on DAG name
2. View "Graph" tab to see task progress
3. Click individual tasks to see logs

## Part 3: Creating a Data Quality DAG

### Step 9: Data Quality Pipeline

Create `dags/data_quality_check.py`:

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
import random

default_args = {
    'owner': 'data-team',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def check_data_freshness(**context):
    """Check if data is fresh (< 24 hours old)"""
    print("🕐 Checking data freshness...")
    # Simulate check
    hours_old = random.randint(1, 30)
    print(f"Data is {hours_old} hours old")

    if hours_old > 24:
        print("⚠️  Data is stale!")
        return 'handle_stale_data'
    else:
        print("✓ Data is fresh")
        return 'check_data_completeness'

def check_data_completeness(**context):
    """Check if all expected data is present"""
    print("📋 Checking data completeness...")
    completeness = random.uniform(0.85, 1.0)
    print(f"Data completeness: {completeness:.2%}")

    if completeness < 0.95:
        raise ValueError(f"Data only {completeness:.2%} complete (expected >95%)")

    return True

def check_schema_validity(**context):
    """Validate data schema"""
    print("🔍 Validating schema...")
    # Simulate schema check
    print("✓ Schema is valid")
    return True

def check_data_quality_metrics(**context):
    """Check various data quality metrics"""
    print("📊 Checking data quality metrics...")

    metrics = {
        'null_percentage': random.uniform(0, 0.05),
        'duplicate_percentage': random.uniform(0, 0.02),
        'outlier_percentage': random.uniform(0, 0.03),
    }

    print(f"Metrics: {metrics}")

    for metric, value in metrics.items():
        if value > 0.05:  # 5% threshold
            raise ValueError(f"{metric} too high: {value:.2%}")

    print("✓ All quality metrics passed")
    return metrics

def handle_stale_data(**context):
    """Handle stale data scenario"""
    print("🚨 Initiating data refresh process...")
    print("Sending alert to data team...")
    return "refresh_data_needed"

with DAG(
    'data_quality_pipeline',
    default_args=default_args,
    description='Data quality validation pipeline',
    schedule_interval='0 * * * *',  # Run hourly
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['data-quality', 'monitoring'],
) as dag:

    freshness_check = BranchPythonOperator(
        task_id='check_data_freshness',
        python_callable=check_data_freshness,
    )

    completeness_check = PythonOperator(
        task_id='check_data_completeness',
        python_callable=check_data_completeness,
    )

    schema_check = PythonOperator(
        task_id='check_schema_validity',
        python_callable=check_schema_validity,
    )

    quality_check = PythonOperator(
        task_id='check_data_quality_metrics',
        python_callable=check_data_quality_metrics,
    )

    stale_data_handler = PythonOperator(
        task_id='handle_stale_data',
        python_callable=handle_stale_data,
    )

    success_notification = BashOperator(
        task_id='quality_check_passed',
        bash_command='echo "✅ All data quality checks passed!"',
    )

    # Define workflow
    freshness_check >> [completeness_check, stale_data_handler]
    completeness_check >> schema_check >> quality_check >> success_notification
```

## Part 4: Monitoring Airflow

### Step 10: View Metrics in Prometheus

1. Go to http://localhost:9090
2. Try these queries:

```promql
# DAG run duration
airflow_dagrun_duration_seconds

# Task failures
rate(airflow_task_failed[5m])

# Scheduler heartbeat
airflow_scheduler_heartbeat

# DAG processing time
airflow_dag_processing_total_parse_time
```

### Step 11: Create Grafana Dashboard

1. Go to http://localhost:3000
2. Add Prometheus data source:
   - Configuration → Data Sources → Add data source
   - Select Prometheus
   - URL: `http://prometheus:9090`
   - Save & Test

3. Create new dashboard:
   - Create → Dashboard → Add new panel

**Panel 1: Task Success Rate**
```promql
rate(airflow_task_success[5m]) / rate(airflow_task_start[5m])
```

**Panel 2: DAG Run Duration**
```promql
avg(airflow_dagrun_duration_seconds) by (dag_id)
```

**Panel 3: Task Failures**
```promql
sum(rate(airflow_task_failed[5m])) by (dag_id)
```

### Step 12: Viewing Logs

**Via UI**:
1. Click on DAG → Task
2. Click "Log" button
3. View real-time or historical logs

**Via CLI**:
```bash
# View task logs
docker-compose exec airflow-webserver airflow tasks logs ml_training_pipeline download_dataset 2024-01-15

# Follow logs
docker-compose logs -f airflow-scheduler
```

## Part 5: Handling Failures and Alerts

### Step 13: Create Failing DAG for Testing

Create `dags/failure_test.py`:

```python
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
import random

def task_that_sometimes_fails():
    """Task that fails 50% of the time"""
    if random.random() < 0.5:
        raise Exception("💥 Simulated failure!")
    print("✓ Task succeeded")

with DAG(
    'failure_test_pipeline',
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
    default_args={'retries': 3},
    tags=['testing'],
) as dag:

    failing_task = PythonOperator(
        task_id='sometimes_fails',
        python_callable=task_that_sometimes_fails,
    )
```

Trigger this DAG multiple times to see failures and retries!

### Step 14: Debug Failed Tasks

When a task fails:

1. **View logs**: Click task → View Log
2. **Check XCom**: See data passed between tasks
3. **Clear and rerun**: Click "Clear" to retry
4. **Mark success**: Override failure if needed

## Challenges

### Challenge 1: Add Email Alerts

Configure email alerts for failures:

```python
default_args = {
    'email': ['alerts@example.com'],
    'email_on_failure': True,
    'email_on_retry': False,
}
```

### Challenge 2: Create Feature Engineering Pipeline

Build a DAG that:
1. Extracts data from source
2. Computes features
3. Stores in feature store
4. Validates feature quality

### Challenge 3: Implement SLA Monitoring

Add SLAs to ensure tasks complete within time limits:

```python
train = PythonOperator(
    task_id='train_model',
    python_callable=train_model,
    sla=timedelta(hours=2),  # Alert if takes > 2 hours
)
```

### Challenge 4: Create Dynamic DAG

Generate tasks dynamically based on configuration:

```python
for model in ['resnet', 'vgg', 'efficientnet']:
    train_task = PythonOperator(
        task_id=f'train_{model}',
        python_callable=train_model,
        op_kwargs={'model_type': model},
    )
```

## Key Takeaways

1. **Airflow orchestrates workflows**: Define complex pipelines as code
2. **DAGs represent workflows**: Tasks with dependencies
3. **Monitoring is built-in**: UI, logs, metrics all available
4. **Retries handle transient failures**: Automatic retry logic
5. **XCom enables data passing**: Share data between tasks
6. **Prometheus integration**: Export metrics for monitoring
7. **Scheduling is flexible**: Cron expressions or intervals

## Production Best Practices

### 1. Idempotent Tasks
```python
def idempotent_task(**context):
    """Task that can be safely re-run"""
    # Check if already completed
    if check_completion():
        print("Already done, skipping...")
        return

    # Do work
    process_data()
    mark_completed()
```

### 2. Task Timeouts
```python
train = PythonOperator(
    task_id='train_model',
    python_callable=train_model,
    execution_timeout=timedelta(hours=4),
)
```

### 3. Resource Management
```python
from airflow.models import Pool

# Create pool in UI or via CLI
# airflow pools set gpu_pool 2 "GPU instances"

train = PythonOperator(
    task_id='train_model',
    python_callable=train_model,
    pool='gpu_pool',
)
```

### 4. Error Handling
```python
def safe_task(**context):
    try:
        process_data()
    except SpecificError as e:
        # Log and handle gracefully
        print(f"Known error: {e}")
        send_alert()
        raise  # Re-raise to mark task as failed
    except Exception as e:
        # Unexpected error
        print(f"Unexpected error: {e}")
        raise
```

## Next Steps

1. **Learn advanced features**:
   - Sensors (wait for events)
   - SubDAGs (nested workflows)
   - TaskGroups (organize tasks)
   - Dynamic task mapping

2. **Explore executors**:
   - CeleryExecutor (distributed)
   - KubernetesExecutor (scalable)
   - DaskExecutor (parallel Python)

3. **Study integrations**:
   - AWS (S3, EMR, SageMaker)
   - GCP (BigQuery, Dataflow)
   - Spark, dbt, Great Expectations

4. **Production deployment**:
   - Kubernetes deployment
   - High availability setup
   - Security and authentication
   - CI/CD for DAGs

## Resources

- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [Airflow Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)
- [Astronomer Guides](https://docs.astronomer.io/)
- [Awesome Apache Airflow](https://github.com/jghoman/awesome-apache-airflow)

## Clean Up

```bash
# Stop all services
docker-compose down

# Remove volumes (data will be lost)
docker-compose down -v
```

---

**Congratulations!** You've learned workflow orchestration with Apache Airflow and how to monitor data pipelines. You can now build, schedule, and monitor complex ML workflows!
