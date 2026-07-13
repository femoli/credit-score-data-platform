"""
Integration tests for the Medallion pipeline.

These tests execute the Bronze, Silver, and Gold pipelines using the
same module entry points used by the application.

The integration test is skipped automatically when the raw Kaggle
dataset is not available.
"""

import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

from src.config.settings import (
    BRONZE_DATA_PATH,
    GOLD_DATA_PATH,
    RAW_DATA_PATH,
    SILVER_DATA_PATH,
)


RAW_FILES = (
    RAW_DATA_PATH / "train.csv",
    RAW_DATA_PATH / "test.csv",
)

BRONZE_FILES = (
    BRONZE_DATA_PATH / "train.parquet",
    BRONZE_DATA_PATH / "test.parquet",
)

SILVER_FILES = (
    SILVER_DATA_PATH / "train.parquet",
    SILVER_DATA_PATH / "test.parquet",
)


def raw_dataset_is_available() -> bool:
    """
    Check whether all raw files required by the pipeline are available.

    Returns:
        bool: True when all expected raw files exist.
    """
    return all(file_path.exists() for file_path in RAW_FILES)


def run_pipeline_module(module_name: str) -> None:
    """
    Execute a pipeline module using the current Python interpreter.

    Args:
        module_name: Fully qualified Python module name.
    """
    result = subprocess.run(
        [sys.executable, "-m", module_name],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, (
        f"Pipeline module failed: {module_name}\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )


def assert_valid_parquet(file_path: Path) -> None:
    """
    Validate whether a Parquet file exists and contains records.

    Args:
        file_path: Path to the Parquet file being validated.
    """
    assert file_path.exists(), (
        f"Expected file was not created: {file_path}"
    )

    assert file_path.stat().st_size > 0, (
        f"File is empty: {file_path}"
    )

    dataframe = pd.read_parquet(file_path)

    assert not dataframe.empty, (
        f"Dataset contains no records: {file_path}"
    )

    assert len(dataframe.columns) > 0, (
        f"Dataset contains no columns: {file_path}"
    )


@pytest.mark.integration
@pytest.mark.skipif(
    not raw_dataset_is_available(),
    reason="Raw Kaggle dataset is not available.",
)
def test_medallion_pipeline_creates_expected_datasets() -> None:
    """
    Execute the complete Medallion pipeline and validate its outputs.

    The test verifies that:

    - the Bronze pipeline creates valid Parquet files;
    - the Silver pipeline creates valid curated datasets;
    - the Gold pipeline creates analytics-ready datasets.
    """
    run_pipeline_module(
        "src.processing.bronze.bronze_loader"
    )

    for bronze_file in BRONZE_FILES:
        assert_valid_parquet(bronze_file)

    run_pipeline_module(
        "src.processing.silver.silver_loader"
    )

    for silver_file in SILVER_FILES:
        assert_valid_parquet(silver_file)

    run_pipeline_module(
        "src.processing.gold.gold_loader"
    )

    gold_files = sorted(
        GOLD_DATA_PATH.rglob("*.parquet")
    )

    assert gold_files, (
        f"No Gold Parquet datasets were created in "
        f"{GOLD_DATA_PATH}"
    )

    for gold_file in gold_files:
        assert_valid_parquet(gold_file)