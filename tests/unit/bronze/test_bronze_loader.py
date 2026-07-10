"""
Unit tests for the Bronze layer.

This module validates the expected behavior of the Bronze layer,
ensuring that raw CSV files are correctly discovered and converted
to Parquet while preserving the original dataset without applying
business transformations.

Test coverage:
- Raw CSV file discovery.
- Missing raw directory validation.
- CSV to Parquet conversion.
- Data preservation during Bronze ingestion.
"""

from pathlib import Path

import pandas as pd
import pytest

from src.processing.bronze.bronze_loader import (
    list_raw_csv_files,
    load_csv_to_bronze,
)

# =============================================================================
# Constants
# =============================================================================

# =============================================================================
# Fixtures
# =============================================================================

# =============================================================================
# Tests
# =============================================================================


def test_list_raw_csv_files_returns_only_csv_files(tmp_path: Path) -> None:
    """Verify that only CSV files are returned from the raw directory."""
    raw_path = tmp_path / "raw"
    raw_path.mkdir()

    csv_file = raw_path / "train.csv"
    txt_file = raw_path / "notes.txt"

    csv_file.write_text("id,name\n1,Ana\n", encoding="utf-8")
    txt_file.write_text("not a csv", encoding="utf-8")

    result = list_raw_csv_files(raw_path)

    assert len(result) == 1
    assert result[0].name == "train.csv"


def test_list_raw_csv_files_raises_error_when_directory_does_not_exist(
    tmp_path: Path,
) -> None:
    """Verify that a missing raw directory raises FileNotFoundError."""
    missing_path = tmp_path / "missing"

    with pytest.raises(FileNotFoundError):
        list_raw_csv_files(missing_path)


def test_load_csv_to_bronze_creates_parquet_file(tmp_path: Path) -> None:
    """Verify that a raw CSV file is successfully converted to Parquet."""
    raw_path = tmp_path / "raw"
    bronze_path = tmp_path / "bronze"

    raw_path.mkdir()

    csv_file = raw_path / "train.csv"
    csv_file.write_text(
        "id,name\n1,Ana\n2,Bia\n",
        encoding="utf-8",
    )

    output_file = load_csv_to_bronze(csv_file, bronze_path)

    assert output_file.exists()
    assert output_file.name == "train.parquet"

    dataframe = pd.read_parquet(output_file)

    assert dataframe.shape == (2, 2)
    assert list(dataframe.columns) == ["id", "name"]
    assert dataframe["id"].astype(str).tolist() == ["1", "2"]