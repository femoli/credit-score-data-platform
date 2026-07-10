"""
Unit tests for Silver layer cleaning.

This module validates the expected behavior of Silver cleaning functions,
ensuring that Bronze data is standardized before type conversion and
validation.

Test coverage:
- Column name standardization.
- Invalid value replacement.
- Numeric text cleaning.
- PII column removal.
"""

import pandas as pd

from src.processing.silver.cleaning import (
    clean_numeric_text,
    remove_pii_columns,
    replace_invalid_values,
    standardize_column_names,
    replace_out_of_range_values,
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


def test_standardize_column_names_renames_columns() -> None:
    """Verify that Bronze column names are renamed to Silver column names."""
    dataframe = pd.DataFrame(
        {
            "ID": ["1"],
            "Customer_ID": ["CUS_001"],
            "Annual_Income": ["1000"],
        }
    )

    rename_mapping = {
        "ID": "record_id",
        "Customer_ID": "customer_id",
        "Annual_Income": "annual_income",
    }

    result = standardize_column_names(dataframe, rename_mapping)

    assert list(result.columns) == [
        "record_id",
        "customer_id",
        "annual_income",
    ]


def test_replace_invalid_values_converts_known_invalid_values_to_missing() -> None:
    """Verify that known invalid values are replaced with missing values."""
    dataframe = pd.DataFrame(
        {
            "occupation": ["Engineer", "_______", "Teacher"],
            "payment_behaviour": ["Low_spent", "!@9#%8", "High_spent"],
            "monthly_balance": [
                "100.50",
                "__-333333333333333333333333333__",
                "200.00",
            ],
        }
    )

    result = replace_invalid_values(dataframe)

    assert result.isna().sum().sum() == 3


def test_clean_numeric_text_removes_underscores_commas_and_spaces() -> None:
    """Verify that numeric text is cleaned before type conversion."""
    series = pd.Series(
        [
            " 1,000.50 ",
            "2500_",
            "_3000",
        ]
    )

    result = clean_numeric_text(series)

    assert result.tolist() == [
        "1000.50",
        "2500",
        "3000",
    ]


def test_remove_pii_columns_removes_sensitive_columns() -> None:
    """Verify that PII columns are removed from the dataframe."""
    dataframe = pd.DataFrame(
        {
            "record_id": ["1"],
            "name": ["Ana"],
            "ssn": ["123-45-6789"],
            "age": ["30"],
        }
    )

    result = remove_pii_columns(dataframe, ["name", "ssn"])

    assert "name" not in result.columns
    assert "ssn" not in result.columns
    assert list(result.columns) == ["record_id", "age"]


def test_remove_pii_columns_ignores_missing_columns() -> None:
    """Verify that missing PII columns do not raise errors."""
    dataframe = pd.DataFrame(
        {
            "record_id": ["1"],
            "age": ["30"],
        }
    )

    result = remove_pii_columns(dataframe, ["name", "ssn"])

    assert list(result.columns) == ["record_id", "age"]
    

def test_replace_out_of_range_values_converts_invalid_ranges_to_missing() -> None:
    """Verify that numeric values outside configured ranges become missing."""
    dataframe = pd.DataFrame(
        {
            "age": [-1, 30, 121],
            "annual_income": [-100.0, 1000.0, 2000.0],
        }
    )

    schema = {
        "age": {"min": 0, "max": 120},
        "annual_income": {"min": 0},
    }

    result = replace_out_of_range_values(dataframe, schema)

    assert result["age"].isna().sum() == 2
    assert result["annual_income"].isna().sum() == 1