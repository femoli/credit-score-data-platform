"""Unit tests for Airflow task adapters."""

from unittest.mock import patch

from orchestration.airflow.tasks.credit_score_tasks import (
    execute_bronze,
    execute_gcs_upload,
    execute_gold,
    execute_ingestion,
    execute_silver,
)


@patch(
    "orchestration.airflow.tasks.credit_score_tasks.run_ingestion_pipeline"
)
def test_execute_ingestion(
    mock_pipeline,
):
    execute_ingestion()

    mock_pipeline.assert_called_once()


@patch(
    "orchestration.airflow.tasks.credit_score_tasks.run_bronze_pipeline"
)
def test_execute_bronze(
    mock_pipeline,
):
    mock_pipeline.return_value = ["bronze"]

    assert execute_bronze() == ["bronze"]


@patch(
    "orchestration.airflow.tasks.credit_score_tasks.run_silver_pipeline"
)
def test_execute_silver(
    mock_pipeline,
):
    mock_pipeline.return_value = ["silver"]

    assert execute_silver() == ["silver"]


@patch(
    "orchestration.airflow.tasks.credit_score_tasks.run_gold_pipeline"
)
def test_execute_gold(
    mock_pipeline,
):
    mock_pipeline.return_value = ["gold"]

    assert execute_gold() == ["gold"]


@patch(
    "orchestration.airflow.tasks.credit_score_tasks.run_gcs_upload_pipeline"
)
def test_execute_gcs_upload(
    mock_pipeline,
):
    mock_pipeline.return_value = ["uploaded"]

    assert execute_gcs_upload() == ["uploaded"]