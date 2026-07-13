"""Unit tests for the Gold layer loader."""

from pathlib import Path
from unittest.mock import Mock, call

import pandas as pd
import pytest

from src.processing.gold import gold_loader


# =============================================================================
# list_silver_parquet_files
# =============================================================================


def test_list_silver_parquet_files_raises_when_directory_does_not_exist(
    tmp_path: Path,
) -> None:
    """Raise an error when the Silver directory does not exist."""
    missing_directory = tmp_path / "silver"

    with pytest.raises(
        FileNotFoundError,
        match="Silver data directory not found",
    ):
        gold_loader.list_silver_parquet_files(missing_directory)


def test_list_silver_parquet_files_raises_when_train_file_does_not_exist(
    tmp_path: Path,
) -> None:
    """Raise an error when train.parquet is missing."""
    silver_directory = tmp_path / "silver"
    silver_directory.mkdir()

    with pytest.raises(
        FileNotFoundError,
        match="Train dataset not found",
    ):
        gold_loader.list_silver_parquet_files(silver_directory)


def test_list_silver_parquet_files_returns_only_train_file(
    tmp_path: Path,
) -> None:
    """Return only the Silver training dataset."""
    silver_directory = tmp_path / "silver"
    silver_directory.mkdir()

    train_file = silver_directory / "train.parquet"
    test_file = silver_directory / "test.parquet"

    train_file.touch()
    test_file.touch()

    result = gold_loader.list_silver_parquet_files(silver_directory)

    assert result == [train_file]


# =============================================================================
# build_gold_dimensions
# =============================================================================


def test_build_gold_dimensions_calls_all_dimension_builders(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Build and return every Gold dimension."""
    source_dataframe = pd.DataFrame({"customer_id": ["customer-1"]})

    customer_dimension = pd.DataFrame({"customer_key": [1]})
    occupation_dimension = pd.DataFrame({"occupation_key": [1]})
    credit_score_dimension = pd.DataFrame({"credit_score_key": [1]})
    date_dimension = pd.DataFrame({"date_key": [20260101]})

    customer_builder = Mock(return_value=customer_dimension)
    occupation_builder = Mock(return_value=occupation_dimension)
    credit_score_builder = Mock(return_value=credit_score_dimension)
    date_builder = Mock(return_value=date_dimension)

    monkeypatch.setattr(
        gold_loader,
        "build_customer_dimension",
        customer_builder,
    )
    monkeypatch.setattr(
        gold_loader,
        "build_occupation_dimension",
        occupation_builder,
    )
    monkeypatch.setattr(
        gold_loader,
        "build_credit_score_dimension",
        credit_score_builder,
    )
    monkeypatch.setattr(
        gold_loader,
        "build_date_dimension",
        date_builder,
    )

    result = gold_loader.build_gold_dimensions(source_dataframe)

    assert result == {
        "dim_customer": customer_dimension,
        "dim_occupation": occupation_dimension,
        "dim_credit_score": credit_score_dimension,
        "dim_date": date_dimension,
    }

    customer_builder.assert_called_once_with(source_dataframe)
    occupation_builder.assert_called_once_with(source_dataframe)
    credit_score_builder.assert_called_once_with(source_dataframe)
    date_builder.assert_called_once_with(source_dataframe)


# =============================================================================
# load_parquet_to_gold
# =============================================================================


def test_load_parquet_to_gold_creates_gold_datasets(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Read Silver data, validate the model and write Gold datasets."""
    silver_file = tmp_path / "silver" / "train.parquet"
    silver_file.parent.mkdir()
    silver_file.touch()

    gold_directory = tmp_path / "gold"

    source_dataframe = pd.DataFrame(
        {
            "customer_id": ["customer-1", "customer-2"],
            "credit_score": ["Good", "Poor"],
        }
    )

    dimensions = {
        "dim_customer": pd.DataFrame(
            {
                "customer_key": [1, 2],
                "customer_id": ["customer-1", "customer-2"],
            }
        ),
        "dim_occupation": pd.DataFrame(
            {
                "occupation_key": [1],
                "occupation": ["Engineer"],
            }
        ),
        "dim_credit_score": pd.DataFrame(
            {
                "credit_score_key": [1, 2],
                "credit_score": ["Good", "Poor"],
            }
        ),
        "dim_date": pd.DataFrame(
            {
                "date_key": [20260101],
                "year": [2026],
            }
        ),
    }

    fact_dataframe = pd.DataFrame(
        {
            "customer_key": [1, 2],
            "occupation_key": [1, 1],
            "credit_score_key": [1, 2],
            "date_key": [20260101, 20260101],
        }
    )

    read_parquet_mock = Mock(return_value=source_dataframe)
    dimensions_mock = Mock(return_value=dimensions)
    fact_builder_mock = Mock(return_value=fact_dataframe)
    validator_mock = Mock()

    monkeypatch.setattr(
        gold_loader.pd,
        "read_parquet",
        read_parquet_mock,
    )
    monkeypatch.setattr(
        gold_loader,
        "build_gold_dimensions",
        dimensions_mock,
    )
    monkeypatch.setattr(
        gold_loader,
        "build_credit_profile_fact",
        fact_builder_mock,
    )
    monkeypatch.setattr(
        gold_loader,
        "validate_gold_dataframes",
        validator_mock,
    )

    result = gold_loader.load_parquet_to_gold(
        parquet_file_path=silver_file,
        gold_data_path=gold_directory,
    )

    expected_output_directory = gold_directory / "train"

    assert result == expected_output_directory
    assert expected_output_directory.is_dir()

    expected_files = {
        "dim_customer.parquet",
        "dim_occupation.parquet",
        "dim_credit_score.parquet",
        "dim_date.parquet",
        "fact_credit_profile.parquet",
    }

    assert {
        file_path.name
        for file_path in expected_output_directory.glob("*.parquet")
    } == expected_files

    read_parquet_mock.assert_called_once_with(silver_file)
    dimensions_mock.assert_called_once_with(source_dataframe)

    fact_builder_mock.assert_called_once_with(
        dataframe=source_dataframe,
        customer_dimension=dimensions["dim_customer"],
        occupation_dimension=dimensions["dim_occupation"],
        credit_score_dimension=dimensions["dim_credit_score"],
        date_dimension=dimensions["dim_date"],
    )

    validator_mock.assert_called_once_with(
        customer_dimension=dimensions["dim_customer"],
        occupation_dimension=dimensions["dim_occupation"],
        credit_score_dimension=dimensions["dim_credit_score"],
        date_dimension=dimensions["dim_date"],
        fact_dataframe=fact_dataframe,
        expected_row_count=2,
    )


# =============================================================================
# run_gold_layer
# =============================================================================


def test_run_gold_layer_returns_empty_list_when_no_files_are_found(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Return an empty list when no Silver files are available."""
    monkeypatch.setattr(
        gold_loader,
        "list_silver_parquet_files",
        Mock(return_value=[]),
    )

    load_mock = Mock()
    monkeypatch.setattr(
        gold_loader,
        "load_parquet_to_gold",
        load_mock,
    )

    result = gold_loader.run_gold_layer()

    assert result == []
    load_mock.assert_not_called()


def test_run_gold_layer_processes_every_silver_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Process every file returned by the Silver file listing."""
    first_file = tmp_path / "train.parquet"
    second_file = tmp_path / "another-train.parquet"

    first_output = tmp_path / "gold" / "train"
    second_output = tmp_path / "gold" / "another-train"

    list_files_mock = Mock(
        return_value=[first_file, second_file]
    )
    load_mock = Mock(
        side_effect=[first_output, second_output]
    )

    monkeypatch.setattr(
        gold_loader,
        "list_silver_parquet_files",
        list_files_mock,
    )
    monkeypatch.setattr(
        gold_loader,
        "load_parquet_to_gold",
        load_mock,
    )

    result = gold_loader.run_gold_layer()

    assert result == [first_output, second_output]

    list_files_mock.assert_called_once_with()
    assert load_mock.call_args_list == [
        call(first_file),
        call(second_file),
    ]
