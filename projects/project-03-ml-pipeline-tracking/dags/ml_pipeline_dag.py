"""
Airflow DAG for ML Training Pipeline

This DAG orchestrates the complete ML pipeline from data ingestion to model registration.

Learning Objectives:
- Design Airflow DAGs with proper task dependencies
- Implement PythonOperators for ML tasks
- Use XCom for inter-task communication
- Handle errors and retries
- Schedule pipelines

TODO: Complete all sections marked with TODO
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
import sys
from pathlib import Path

# TODO: Add project source to Python path
# Hint: sys.path.insert(0, '/path/to/src')

import logging

logger = logging.getLogger(__name__)


# ============================================================================
# DAG Configuration
# ============================================================================

# TODO: Define default_args for all tasks
default_args = {
    'owner': 'ml-team',
    'depends_on_past': False,
    'email': ['mlops@example.com'],  # TODO: Update with your email
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,  # TODO: Set appropriate retry count
    'retry_delay': timedelta(minutes=5),  # TODO: Set retry delay
    # TODO: Add execution_timeout
    # 'execution_timeout': timedelta(hours=2),
}

# TODO: Define pipeline configuration
PIPELINE_CONFIG = {
    'raw_data_path': '/opt/airflow/data/raw',
    'processed_data_path': '/opt/airflow/data/processed',
    'model_save_path': '/opt/airflow/models',
    'artifacts_path': '/opt/airflow/artifacts',
    'mlflow_tracking_uri': 'http://mlflow:5000',
    'experiment_name': 'image_classification_pipeline',
}


# ============================================================================
# Task Functions
# ============================================================================

def ingest_data(**context):
    """
    Task: Ingest data from source.

    TODO:
    1. Import DataIngestion class
    2. Initialize with configuration
    3. Ingest data from CSV (or API, database)
    4. Save raw data
    5. Push data path to XCom for next task
    6. Return success message
    """
    logger.info("Starting data ingestion...")

    # TODO: Import DataIngestion
    # from src.data_ingestion import DataIngestion

    # TODO: Initialize ingestion
    # ingestion = DataIngestion(PIPELINE_CONFIG)

    # TODO: Ingest data
    # Example: df = ingestion.ingest_from_csv('/opt/airflow/data/source/dataset.csv')

    # TODO: Save raw data
    # output_path = ingestion.save_raw_data(df, 'raw_dataset.csv')

    # TODO: Push path to XCom
    # context['task_instance'].xcom_push(key='raw_data_path', value=str(output_path))

    logger.info("Data ingestion complete")
    return "Data ingestion successful"


def validate_data(**context):
    """
    Task: Validate data quality with Great Expectations.

    TODO:
    1. Pull raw data path from XCom
    2. Load data
    3. Initialize DataValidator
    4. Create expectation suite
    5. Run validation
    6. Raise error if validation fails
    7. Return validation result
    """
    logger.info("Starting data validation...")

    # TODO: Pull data path from previous task
    # raw_data_path = context['task_instance'].xcom_pull(
    #     task_ids='ingest_data',
    #     key='raw_data_path'
    # )

    # TODO: Load data
    # import pandas as pd
    # df = pd.read_csv(raw_data_path)

    # TODO: Import and initialize validator
    # from src.data_validation import DataValidator
    # validator = DataValidator()

    # TODO: Create expectations
    # validator.create_expectation_suite("data_quality_suite")

    # TODO: Validate
    # validation_passed = validator.validate_data(df, "data_quality_suite")

    # TODO: Raise error if validation fails
    # if not validation_passed:
    #     raise ValueError("Data validation failed! Check validation report.")

    logger.info("Data validation passed")
    return "Data validation successful"


def preprocess_data(**context):
    """
    Task: Preprocess data (clean, encode, split).

    TODO:
    1. Pull raw data path from XCom
    2. Load data
    3. Initialize DataPreprocessor
    4. Run preprocessing pipeline
    5. Push completion status to XCom
    6. Return success message
    """
    logger.info("Starting data preprocessing...")

    # TODO: Pull data path
    # raw_data_path = context['task_instance'].xcom_pull(
    #     task_ids='ingest_data',
    #     key='raw_data_path'
    # )

    # TODO: Load data
    # import pandas as pd
    # df = pd.read_csv(raw_data_path)

    # TODO: Import and initialize preprocessor
    # from src.preprocessing import DataPreprocessor
    # preprocessor = DataPreprocessor(PIPELINE_CONFIG)

    # TODO: Run pipeline
    # train, val, test = preprocessor.run_pipeline(df, label_column='label')

    # TODO: Push status to XCom
    # context['task_instance'].xcom_push(key='preprocessing_complete', value=True)

    logger.info("Data preprocessing complete")
    return "Preprocessing successful"


def version_data_dvc(**context):
    """
    Task: Version processed data with DVC.

    TODO:
    1. Run dvc add on processed data directory
    2. Commit DVC file to git
    3. Push to DVC remote
    4. Tag with version
    5. Return success message

    Note: This requires DVC and Git to be set up in the Airflow container
    """
    logger.info("Versioning data with DVC...")

    # TODO: Import subprocess
    # import subprocess

    # TODO: Add processed data to DVC
    # try:
    #     subprocess.run(['dvc', 'add', 'data/processed'], check=True)
    #     subprocess.run(['dvc', 'push'], check=True)
    #     subprocess.run(['git', 'add', 'data/processed.dvc', '.gitignore'], check=True)
    #     subprocess.run(
    #         ['git', 'commit', '-m', f'Data version {datetime.now().isoformat()}'],
    #         check=True
    #     )
    # except subprocess.CalledProcessError as e:
    #     logger.error(f"DVC versioning failed: {e}")
    #     raise

    logger.info("Data versioning complete")
    return "DVC versioning successful"


def train_model(**context):
    """
    Task: Train ML model with MLflow tracking.

    TODO:
    1. Initialize MLflowTracker
    2. Load preprocessed data
    3. Create data loaders
    4. Define training parameters
    5. Initialize ModelTrainer
    6. Run training
    7. Push best validation accuracy to XCom
    8. Return success message
    """
    logger.info("Starting model training...")

    # TODO: Import required classes
    # from src.training import MLflowTracker, ModelTrainer
    # import pandas as pd

    # TODO: Initialize MLflow tracker
    # tracker = MLflowTracker(
    #     tracking_uri=PIPELINE_CONFIG['mlflow_tracking_uri'],
    #     experiment_name=PIPELINE_CONFIG['experiment_name']
    # )

    # TODO: Load processed data
    # train_df = pd.read_csv(f"{PIPELINE_CONFIG['processed_data_path']}/train.csv")
    # val_df = pd.read_csv(f"{PIPELINE_CONFIG['processed_data_path']}/val.csv")

    # TODO: Create data loaders
    # Note: You'll need to implement a Dataset class for your data
    # train_loader = ...
    # val_loader = ...

    # TODO: Define training parameters
    params = {
        'model_name': 'resnet18',
        'num_epochs': 10,
        'batch_size': 32,
        'learning_rate': 0.001,
        'optimizer': 'adam',
        'lr_step_size': 5,
        'lr_gamma': 0.1,
        'early_stopping_patience': 3
    }

    # TODO: Initialize trainer
    # trainer = ModelTrainer(PIPELINE_CONFIG, tracker)

    # TODO: Run training
    # model, best_val_acc = trainer.train(
    #     train_loader=train_loader,
    #     val_loader=val_loader,
    #     num_classes=4,
    #     params=params
    # )

    # TODO: Push metrics to XCom
    # context['task_instance'].xcom_push(key='best_val_acc', value=best_val_acc)

    logger.info("Model training complete")
    return "Training successful"


def evaluate_model(**context):
    """
    Task: Evaluate model on test set.

    TODO:
    1. Load test data
    2. Load best model
    3. Initialize ModelEvaluator
    4. Run evaluation
    5. Push test metrics to XCom
    6. Return success message
    """
    logger.info("Starting model evaluation...")

    # TODO: Import required classes
    # from src.evaluation import ModelEvaluator
    # import pandas as pd
    # import torch

    # TODO: Load test data
    # test_df = pd.read_csv(f"{PIPELINE_CONFIG['processed_data_path']}/test.csv")

    # TODO: Create test data loader
    # test_loader = ...

    # TODO: Load best model
    # model_path = f"{PIPELINE_CONFIG['model_save_path']}/best_model.pth"
    # model = torch.load(model_path)

    # TODO: Initialize evaluator
    # class_names = ['cat', 'dog', 'bird', 'fish']
    # evaluator = ModelEvaluator(PIPELINE_CONFIG, class_names)

    # TODO: Run evaluation
    # metrics = evaluator.evaluate(model, test_loader)

    # TODO: Push metrics to XCom
    # context['task_instance'].xcom_push(key='test_metrics', value=metrics)

    logger.info("Model evaluation complete")
    return "Evaluation successful"


def register_model(**context):
    """
    Task: Register model in MLflow Model Registry if it meets criteria.

    TODO:
    1. Pull test metrics from XCom
    2. Check if model meets production criteria (e.g., accuracy >= 85%)
    3. If yes, register model in MLflow
    4. Transition to Staging stage
    5. Return registration result
    """
    logger.info("Starting model registration...")

    # TODO: Pull test metrics
    # test_metrics = context['task_instance'].xcom_pull(
    #     task_ids='evaluate_model',
    #     key='test_metrics'
    # )

    # TODO: Check production criteria
    # accuracy_threshold = 0.85
    # if test_metrics['test_accuracy'] >= accuracy_threshold:
    #     # TODO: Import MLflow
    #     import mlflow
    #
    #     # TODO: Get latest run ID
    #     experiment = mlflow.get_experiment_by_name(PIPELINE_CONFIG['experiment_name'])
    #     runs = mlflow.search_runs(
    #         experiment_ids=[experiment.experiment_id],
    #         order_by=["start_time DESC"],
    #         max_results=1
    #     )
    #     run_id = runs.iloc[0]['run_id']
    #
    #     # TODO: Register model
    #     model_uri = f"runs:/{run_id}/model"
    #     result = mlflow.register_model(
    #         model_uri=model_uri,
    #         name="image_classifier"
    #     )
    #
    #     # TODO: Transition to Staging
    #     client = mlflow.tracking.MlflowClient()
    #     client.transition_model_version_stage(
    #         name="image_classifier",
    #         version=result.version,
    #         stage="Staging"
    #     )
    #
    #     logger.info(f"Registered model version {result.version}")
    #     return f"Model registered: version {result.version}"
    # else:
    #     logger.info(f"Model did not meet criteria (accuracy: {test_metrics['test_accuracy']:.2%})")
    #     return "Model not registered - did not meet criteria"

    return "Model registration complete"


# ============================================================================
# DAG Definition
# ============================================================================

# TODO: Create the DAG
dag = DAG(
    dag_id='ml_training_pipeline',
    default_args=default_args,
    description='End-to-end ML training pipeline with MLflow tracking',
    # TODO: Set schedule (weekly on Sundays at midnight)
    schedule_interval='@weekly',
    start_date=days_ago(1),
    catchup=False,  # Don't run for past dates
    max_active_runs=1,  # Only one run at a time
    tags=['ml', 'training', 'production'],
)

# TODO: Define tasks
with dag:
    # Task 1: Ingest Data
    task_ingest = PythonOperator(
        task_id='ingest_data',
        python_callable=ingest_data,
        # TODO: Add provide_context=True if using Airflow < 2.0
    )

    # Task 2: Validate Data
    task_validate = PythonOperator(
        task_id='validate_data',
        python_callable=validate_data,
    )

    # Task 3: Preprocess Data
    task_preprocess = PythonOperator(
        task_id='preprocess_data',
        python_callable=preprocess_data,
    )

    # Task 4: Version Data with DVC
    task_dvc = PythonOperator(
        task_id='version_data_dvc',
        python_callable=version_data_dvc,
    )

    # Task 5: Train Model
    task_train = PythonOperator(
        task_id='train_model',
        python_callable=train_model,
    )

    # Task 6: Evaluate Model
    task_evaluate = PythonOperator(
        task_id='evaluate_model',
        python_callable=evaluate_model,
    )

    # Task 7: Register Model
    task_register = PythonOperator(
        task_id='register_model',
        python_callable=register_model,
    )

    # Task 8: Send Success Email
    task_notify = EmailOperator(
        task_id='send_success_email',
        to='mlops@example.com',  # TODO: Update email
        subject='[SUCCESS] ML Training Pipeline - {{ ds }}',
        html_content="""
        <h3>ML Training Pipeline Completed Successfully</h3>
        <p><strong>Execution Date:</strong> {{ ds }}</p>
        <p><strong>Status:</strong> SUCCESS</p>
        <p>View results in MLflow: <a href="http://mlflow:5000">MLflow UI</a></p>
        <p>View pipeline: <a href="http://airflow:8080/dags/ml_training_pipeline/grid">Airflow DAG</a></p>
        """,
    )

    # TODO: Define task dependencies
    # The pipeline should flow as:
    # ingest → validate → preprocess → version → train → evaluate → register → notify

    task_ingest >> task_validate >> task_preprocess >> task_dvc
    task_dvc >> task_train >> task_evaluate >> task_register >> task_notify


# ============================================================================
# DAG Testing (for local development)
# ============================================================================

if __name__ == "__main__":
    """
    Test the DAG structure without running tasks.

    TODO:
    1. Print DAG information
    2. Verify task dependencies
    3. Check for cycles
    """
    print(f"DAG: {dag.dag_id}")
    print(f"Schedule: {dag.schedule_interval}")
    print(f"Tasks: {len(dag.tasks)}")
    print("\nTask Dependencies:")
    for task in dag.tasks:
        print(f"  {task.task_id}: upstream={task.upstream_task_ids}, downstream={task.downstream_task_ids}")
