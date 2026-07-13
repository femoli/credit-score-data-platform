"""Unit tests for the Google Cloud Storage uploader."""

from pathlib import Path
from unittest.mock import Mock

import pytest

from src.storage.gcs_uploader import (
    build_blob_name,
    find_uploadable_files,
    normalize_prefix,
    upload_gold_layer,
)


def test_normalize_prefix_removes_slashes() -> None:
    assert normalize_prefix("/credit-score-data-platform/") == (
        "credit-score-data-platform"
    )


def test_build_blob_name_preserves_structure(
    tmp_path: Path,
) -> None:
    source_directory = tmp_path / "gold"
    file_path = source_directory / "train" / "dim_customer.parquet"

    file_path.parent.mkdir(parents=True)
    file_path.touch()

    result = build_blob_name(
        file_path=file_path,
        source_directory=source_directory,
        prefix="credit-score-data-platform",
    )

    assert result == (
        "credit-score-data-platform/"
        "gold/train/dim_customer.parquet"
    )


def test_find_uploadable_files_returns_supported_files(
    tmp_path: Path,
) -> None:
    parquet_file = tmp_path / "data.parquet"
    csv_file = tmp_path / "data.csv"
    text_file = tmp_path / "notes.txt"

    parquet_file.touch()
    csv_file.touch()
    text_file.touch()

    result = find_uploadable_files(tmp_path)

    assert result == sorted([csv_file, parquet_file])


def test_find_uploadable_files_rejects_missing_directory(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        FileNotFoundError,
        match="Source directory does not exist",
    ):
        find_uploadable_files(tmp_path / "missing")


def test_find_uploadable_files_rejects_empty_directory(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        ValueError,
        match="No Parquet or CSV files found",
    ):
        find_uploadable_files(tmp_path)


def test_upload_gold_layer_uploads_all_files(
    tmp_path: Path,
) -> None:
    source_directory = tmp_path / "gold"
    train_directory = source_directory / "train"
    train_directory.mkdir(parents=True)

    dimension_file = train_directory / "dim_customer.parquet"
    fact_file = train_directory / "fact_credit_profile.parquet"

    dimension_file.touch()
    fact_file.touch()

    blob = Mock()
    bucket = Mock()
    bucket.blob.return_value = blob

    client = Mock()
    client.bucket.return_value = bucket

    result = upload_gold_layer(
        source_directory=source_directory,
        project_id="test-project",
        bucket_name="test-bucket",
        prefix="project",
        client=client,
    )

    assert result == [
        "project/gold/train/dim_customer.parquet",
        "project/gold/train/fact_credit_profile.parquet",
    ]

    assert blob.upload_from_filename.call_count == 2
    client.bucket.assert_called_with("test-bucket")


def test_upload_gold_layer_requires_bucket(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        ValueError,
        match="GCS_BUCKET_NAME",
    ):
        upload_gold_layer(
            source_directory=tmp_path,
            project_id="test-project",
            bucket_name="",
            client=Mock(),
        )