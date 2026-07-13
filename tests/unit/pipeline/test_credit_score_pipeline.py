"""Unit tests for the credit score pipeline facade."""

from pathlib import Path
from unittest.mock import patch

from src.pipeline.credit_score_pipeline import (
    run_bronze_pipeline,
    run_gcs_upload_pipeline,
    run_gold_pipeline,
    run_ingestion_pipeline,
    run_silver_pipeline,
)


@patch("src.pipeline.credit_score_pipeline.run_ingestion")
def test_run_ingestion_pipeline_calls_ingestion(
    mock_run_ingestion,
) -> None:
    """Ensure the ingestion stage delegates to the ingestion module."""
    run_ingestion_pipeline()

    mock_run_ingestion.assert_called_once_with()


@patch("src.pipeline.credit_score_pipeline.run_bronze_layer")
def test_run_bronze_pipeline_returns_string_paths(
    mock_run_bronze_layer,
) -> None:
    """Ensure Bronze output paths are converted to strings."""
    mock_run_bronze_layer.return_value = [
        Path("data/bronze/train.parquet"),
        Path("data/bronze/test.parquet"),
    ]

    result = run_bronze_pipeline()

    assert result == [
        "data/bronze/train.parquet",
        "data/bronze/test.parquet",
    ]
    mock_run_bronze_layer.assert_called_once_with()


@patch("src.pipeline.credit_score_pipeline.run_silver_layer")
def test_run_silver_pipeline_returns_string_paths(
    mock_run_silver_layer,
) -> None:
    """Ensure Silver output paths are converted to strings."""
    mock_run_silver_layer.return_value = [
        Path("data/silver/train.parquet"),
    ]

    result = run_silver_pipeline()

    assert result == ["data/silver/train.parquet"]
    mock_run_silver_layer.assert_called_once_with()


@patch("src.pipeline.credit_score_pipeline.run_gold_layer")
def test_run_gold_pipeline_returns_string_paths(
    mock_run_gold_layer,
) -> None:
    """Ensure Gold output directories are converted to strings."""
    mock_run_gold_layer.return_value = [
        Path("data/gold/train"),
    ]

    result = run_gold_pipeline()

    assert result == ["data/gold/train"]
    mock_run_gold_layer.assert_called_once_with()


@patch("src.pipeline.credit_score_pipeline.upload_gold_layer")
def test_run_gcs_upload_pipeline_returns_uploaded_objects(
    mock_upload_gold_layer,
) -> None:
    """Ensure the GCS stage returns uploaded object names."""
    mock_upload_gold_layer.return_value = [
        "credit-score/gold/train/dim_customer.parquet",
        "credit-score/gold/train/fact_credit_profile.parquet",
    ]

    result = run_gcs_upload_pipeline()

    assert result == [
        "credit-score/gold/train/dim_customer.parquet",
        "credit-score/gold/train/fact_credit_profile.parquet",
    ]
    mock_upload_gold_layer.assert_called_once_with()