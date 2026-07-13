"""
Credit score pipeline orchestration facade.

This module exposes stable entry points for external orchestrators, such as
Apache Airflow, while delegating the processing logic to the existing
application modules.
"""

from src.ingestion.downloader import main as run_ingestion
from src.processing.bronze.bronze_loader import run_bronze_layer
from src.processing.gold.gold_loader import run_gold_layer
from src.processing.silver.silver_loader import run_silver_layer
from src.storage.gcs_uploader import upload_gold_layer


def run_ingestion_pipeline() -> None:
    """Run the Kaggle dataset ingestion stage."""
    run_ingestion()


def run_bronze_pipeline() -> list[str]:
    """Run the Bronze stage and return generated file paths."""
    generated_files = run_bronze_layer()

    return [str(file_path) for file_path in generated_files]


def run_silver_pipeline() -> list[str]:
    """Run the Silver stage and return generated file paths."""
    generated_files = run_silver_layer()

    return [str(file_path) for file_path in generated_files]


def run_gold_pipeline() -> list[str]:
    """Run the Gold stage and return generated directory paths."""
    generated_directories = run_gold_layer()

    return [str(directory_path) for directory_path in generated_directories]


def run_gcs_upload_pipeline() -> list[str]:
    """Upload Gold datasets and return uploaded GCS object names."""
    return upload_gold_layer()