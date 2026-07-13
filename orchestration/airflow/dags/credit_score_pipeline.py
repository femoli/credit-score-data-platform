"""
Apache Airflow DAG for the Credit Score Data Platform.

This workflow orchestrates the complete ETL pipeline from Kaggle ingestion
through the Medallion Architecture layers and Google Cloud Storage upload.
"""

from datetime import datetime, timedelta

from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.sdk import dag, task

from orchestration.airflow.tasks.credit_score_tasks import (
    execute_bronze,
    execute_gcs_upload,
    execute_gold,
    execute_ingestion,
    execute_silver,
)


DEFAULT_ARGS = {
    "owner": "data-engineering",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}


@dag(
    dag_id="credit_score_pipeline",
    description=(
        "Orchestrates the end-to-end credit score ETL pipeline through "
        "Raw, Bronze, Silver, Gold, and Google Cloud Storage."
    ),
    default_args=DEFAULT_ARGS,
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    dagrun_timeout=timedelta(minutes=30),
    max_active_runs=1,
    tags=["etl", "medallion", "credit-score"],
    doc_md="""
# Credit Score Data Pipeline

Orchestrates the complete Credit Score Data Platform workflow:

1. Downloads the dataset from Kaggle.
2. Loads raw CSV files into the Bronze layer.
3. Cleans, validates, types, and anonymizes data in the Silver layer.
4. Builds dimensional and fact tables in the Gold layer.
5. Uploads Gold datasets to Google Cloud Storage.

The DAG runs manually and allows only one active execution at a time.
""",
)
def credit_score_pipeline():
    """Define the end-to-end credit score data workflow."""

    start = EmptyOperator(task_id="start")

    @task(task_id="ingestion")
    def ingestion() -> None:
        """Execute the Kaggle ingestion task."""
        execute_ingestion()

    @task(task_id="bronze")
    def bronze() -> list[str]:
        """Execute the Bronze layer task."""
        return execute_bronze()

    @task(task_id="silver")
    def silver() -> list[str]:
        """Execute the Silver layer task."""
        return execute_silver()

    @task(task_id="gold")
    def gold() -> list[str]:
        """Execute the Gold layer task."""
        return execute_gold()

    @task(task_id="gcs_upload")
    def gcs_upload() -> list[str]:
        """Execute the Google Cloud Storage upload task."""
        return execute_gcs_upload()

    end = EmptyOperator(task_id="end")

    ingestion_task = ingestion()
    bronze_task = bronze()
    silver_task = silver()
    gold_task = gold()
    gcs_upload_task = gcs_upload()

    (
        start
        >> ingestion_task
        >> bronze_task
        >> silver_task
        >> gold_task
        >> gcs_upload_task
        >> end
    )


credit_score_pipeline()