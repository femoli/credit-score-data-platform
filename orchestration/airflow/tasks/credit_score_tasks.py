"""
Apache Airflow task adapters.

This module bridges Airflow tasks and the application pipeline layer.
"""

from src.observability.logger import get_logger
from src.pipeline.credit_score_pipeline import (
    run_bronze_pipeline,
    run_gcs_upload_pipeline,
    run_gold_pipeline,
    run_ingestion_pipeline,
    run_silver_pipeline,
)

logger = get_logger(__name__)


def execute_ingestion() -> None:
    """Execute dataset ingestion."""
    logger.info("Starting ingestion task.")

    run_ingestion_pipeline()

    logger.info("Ingestion task completed.")


def execute_bronze() -> list[str]:
    """Execute Bronze layer."""
    logger.info("Starting Bronze task.")

    result = run_bronze_pipeline()

    logger.info("Bronze task completed.")

    return result


def execute_silver() -> list[str]:
    """Execute Silver layer."""
    logger.info("Starting Silver task.")

    result = run_silver_pipeline()

    logger.info("Silver task completed.")

    return result


def execute_gold() -> list[str]:
    """Execute Gold layer."""
    logger.info("Starting Gold task.")

    result = run_gold_pipeline()

    logger.info("Gold task completed.")

    return result


def execute_gcs_upload() -> list[str]:
    """Upload Gold layer to Google Cloud Storage."""
    logger.info("Starting GCS upload task.")

    result = run_gcs_upload_pipeline()

    logger.info("GCS upload task completed.")

    return result