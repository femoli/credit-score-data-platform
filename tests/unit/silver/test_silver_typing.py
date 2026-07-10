"""
Unit tests for Silver layer type conversion.

This module validates the expected behavior of Silver typing functions,
ensuring that cleaned Bronze data is converted into the correct trusted
Silver data types.

Test coverage:
- Nullable integer conversion.
- Nullable float conversion.
- Category conversion.
- Invalid numeric values converted to missing values.
"""

import pandas as pd

from src.processing.silver.typing import (
    convert_category_columns,
    convert_float_columns,
    convert_integer_columns,
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


def test_convert_integer_columns_converts_to_nullable_integer() -> None:
    """Verify that integer columns are converted to pandas nullable Int64."""
    dataframe = pd.DataFrame(
        {
            "age": ["25", "30", "45"],
        }
    )

    result = convert_integer_columns(dataframe, ["age"])

    assert str(result["age"].dtype) == "Int64"
    assert result["age"].tolist() == [25, 30, 45]


def test_convert_integer_columns_converts_invalid_values_to_missing() -> None:
    """Verify that invalid integer values are converted to missing values."""
    dataframe = pd.DataFrame(
        {
            "age": ["25", "invalid", "45"],
        }
    )

    result = convert_integer_columns(dataframe, ["age"])

    assert str(result["age"].dtype) == "Int64"
    assert result["age"].isna().sum() == 1


def test_convert_float_columns_converts_to_nullable_float() -> None:
    """Verify that float columns are converted to pandas nullable Float64."""
    dataframe = pd.DataFrame(
        {
            "interest_rate": ["10", "20", "30"],
        }
    )

    result = convert_float_columns(dataframe, ["interest_rate"])

    assert str(result["interest_rate"].dtype) == "Float64"
    assert result["interest_rate"].tolist() == [10.0, 20.0, 30.0]


def test_convert_float_columns_converts_decimal_values() -> None:
    """Verify that decimal string values are converted to floats."""
    dataframe = pd.DataFrame(
        {
            "annual_income": ["1000.50", "2500.75", "3000.00"],
        }
    )

    result = convert_float_columns(dataframe, ["annual_income"])

    assert str(result["annual_income"].dtype) == "Float64"
    assert result["annual_income"].tolist() == [1000.50, 2500.75, 3000.00]


def test_convert_float_columns_converts_invalid_values_to_missing() -> None:
    """Verify that invalid float values are converted to missing values."""
    dataframe = pd.DataFrame(
        {
            "monthly_balance": ["100.50", "invalid", "300.00"],
        }
    )

    result = convert_float_columns(dataframe, ["monthly_balance"])

    assert str(result["monthly_balance"].dtype) == "Float64"
    assert result["monthly_balance"].isna().sum() == 1


def test_convert_category_columns_converts_to_category() -> None:
    """Verify that categorical columns are converted to category type."""
    dataframe = pd.DataFrame(
        {
            "credit_score": ["Good", "Standard", "Poor"],
        }
    )

    result = convert_category_columns(dataframe, ["credit_score"])

    assert str(result["credit_score"].dtype) == "category"
    assert result["credit_score"].tolist() == ["Good", "Standard", "Poor"]