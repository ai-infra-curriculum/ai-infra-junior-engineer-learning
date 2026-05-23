"""Scheduled retraining DAG.

This DAG runs the full training pipeline on a recurring schedule, gated by data
quality checks. It is intentionally separate from ``ml_pipeline_dag.py`` so that
ad-hoc / triggered runs and scheduled retraining can have different policies
(schedule interval, alerting, promotion rules).

Schedule
--------
- Weekly retraining on Sunday at 02:00 UTC.
- Triggered retraining on data drift detection (sensor task).

Promotion policy
----------------
After training and evaluation, a candidate model is promoted to "Staging" in the
MLflow Model Registry only if it meets all thresholds in ``dvc/params.yaml``.
A separate human-gated approval step (not shown) moves Staging -> Production.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

import mlflow
from airflow import DAG
from airflow.exceptions import AirflowFailException
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.sensors.python import PythonSensor


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PARAMS_FILE = PROJECT_ROOT / "dvc" / "params.yaml"
EVAL_FILE = PROJECT_ROOT / "models" / "current" / "evaluation.json"

DEFAULT_ARGS = {
    "owner": "ml-platform",
    "depends_on_past": False,
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=10),
    "execution_timeout": timedelta(hours=3),
}


def detect_drift(**_context) -> bool:
    """Sensor: returns True when retraining should proceed.

    In production this would query a drift monitor (e.g., Evidently, Arize, or
    a custom Prometheus rule). For the curriculum project we keep a
    placeholder that returns True on the scheduled cadence.
    """
    # TODO: replace with real drift check, e.g.:
    # return drift_client.psi(feature="amount", window="7d") > 0.2
    return True


def promote_to_staging(**_context) -> None:
    """Promote the just-trained model to MLflow's Staging stage iff it passes thresholds."""
    import yaml

    if not EVAL_FILE.exists():
        raise AirflowFailException("evaluation.json not produced by training stage")

    eval_results = json.loads(EVAL_FILE.read_text())
    thresholds = yaml.safe_load(PARAMS_FILE.read_text())["evaluate"]["thresholds"]

    failed = [
        f"{metric} = {eval_results.get(metric):.4f} < min {threshold}"
        for metric, threshold in (
            ("roc_auc", thresholds["roc_auc_min"]),
            ("precision", thresholds["precision_min"]),
            ("recall", thresholds["recall_min"]),
        )
        if eval_results.get(metric, 0) < threshold
    ]
    if failed:
        raise AirflowFailException("Promotion blocked: " + "; ".join(failed))

    run_id = eval_results["mlflow_run_id"]
    client = mlflow.MlflowClient()
    model_version = client.create_model_version(
        name="fraud-detector",
        source=f"runs:/{run_id}/model",
        run_id=run_id,
    )
    client.transition_model_version_stage(
        name="fraud-detector",
        version=model_version.version,
        stage="Staging",
        archive_existing_versions=True,
    )
    print(f"Promoted version {model_version.version} to Staging.")


with DAG(
    dag_id="model_retraining",
    description="Weekly retraining with drift-triggered runs and gated promotion",
    schedule="0 2 * * 0",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    default_args=DEFAULT_ARGS,
    tags=["ml", "retraining", "project-03"],
) as dag:

    drift_check = PythonSensor(
        task_id="drift_check",
        python_callable=detect_drift,
        poke_interval=60,
        timeout=60 * 60,
        mode="reschedule",
    )

    ingest = BashOperator(
        task_id="ingest",
        bash_command=f"cd {PROJECT_ROOT} && dvc repro ingest",
    )

    preprocess = BashOperator(
        task_id="preprocess",
        bash_command=f"cd {PROJECT_ROOT} && dvc repro preprocess",
    )

    validate = BashOperator(
        task_id="validate_with_great_expectations",
        bash_command=f"cd {PROJECT_ROOT} && dvc repro validate",
    )

    train = BashOperator(
        task_id="train",
        bash_command=f"cd {PROJECT_ROOT} && dvc repro train",
    )

    evaluate = BashOperator(
        task_id="evaluate",
        bash_command=f"cd {PROJECT_ROOT} && dvc repro evaluate",
    )

    promote = PythonOperator(
        task_id="promote_to_staging",
        python_callable=promote_to_staging,
    )

    drift_check >> ingest >> preprocess >> validate >> train >> evaluate >> promote
