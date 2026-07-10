"""
Unit tests for Silver layer validation.

This module validates the expected behavior of Silver validation functions,
ensuring that schema, nullability, allowed values, and numeric ranges are
enforced before data is published to downstream layers.

Test coverage:
- Expected column validation.
- Missing required column detection.
- Unexpected column detection.
- Optional column support.
- Nullable rule validation.
- Allowed values validation.
- Numeric range validation.
"""

import pandas as pd
import pytest

from src.processing.silver.validator import (
    validate_allowed_values,
    validate_expected_columns,
    validate_nullable_rules,
    validate_numeric_ranges,
    validate_silver_dataframe,
)

# =============================================================================
# Constants
# =============================================================================

TEST_SCHEMA = {
    "record_id": {
        "type": "string",
        "nullable": False,
    },
    "age": {
        "type": "Int64",
        "nullable": False,
        "min": 0,
        "max": 120,
    },
    "credit_score": {
        "type": "category",
        "nullable": False,
        "allowed_values": ["Good", "Standard", "Poor"],
    },
}

EXPECTED_COLUMNS = [
    "record_id",
    "age",
    "credit_score",
]

REQUIRED_COLUMNS = [
    "record_id",
    "age",
]

# =============================================================================
# Fixtures
# =============================================================================

# =============================================================================
# Tests
# =============================================================================


def test_validate_expected_columns_accepts_valid_columns() -> None:
    """Verify that valid expected columns do not raise errors."""
    dataframe = pd.DataFrame(
        {
            "record_id": ["1"],
            "age": [30],
            "credit_score": ["Good"],
        }
    )

    validate_expected_columns(dataframe, REQUIRED_COLUMNS, EXPECTED_COLUMNS)


def test_validate_expected_columns_accepts_missing_optional_column() -> None:
    """Verify that missing optional columns do not raise errors."""
    dataframe = pd.DataFrame(
        {
            "record_id": ["1"],
            "age": [30],
        }
    )

    validate_expected_columns(dataframe, REQUIRED_COLUMNS, EXPECTED_COLUMNS)


def test_validate_expected_columns_raises_error_for_missing_required_column() -> None:
    """Verify that missing required columns raise ValueError."""
    dataframe = pd.DataFrame(
        {
            "record_id": ["1"],
            "credit_score": ["Good"],
        }
    )

    with pytest.raises(ValueError, match="Missing required columns"):
        validate_expected_columns(dataframe, REQUIRED_COLUMNS, EXPECTED_COLUMNS)


def test_validate_expected_columns_raises_error_for_unexpected_columns() -> None:
    """Verify that unexpected columns raise ValueError."""
    dataframe = pd.DataFrame(
        {
            "record_id": ["1"],
            "age": [30],
            "credit_score": ["Good"],
            "extra_column": ["unexpected"],
        }
    )

    with pytest.raises(ValueError, match="Unexpected columns found"):
        validate_expected_columns(dataframe, REQUIRED_COLUMNS, EXPECTED_COLUMNS)


def test_validate_nullable_rules_accepts_non_null_required_columns() -> None:
    """Verify that non-nullable columns pass when they do not contain nulls."""
    dataframe = pd.DataFrame(
        {
            "record_id": ["1"],
            "age": [30],
            "credit_score": ["Good"],
        }
    )

    validate_nullable_rules(dataframe, TEST_SCHEMA)


def test_validate_nullable_rules_ignores_missing_optional_columns() -> None:
    """Verify that missing optional columns are ignored by nullable validation."""
    dataframe = pd.DataFrame(
        {
            "record_id": ["1"],
            "age": [30],
        }
    )

    validate_nullable_rules(dataframe, TEST_SCHEMA)


def test_validate_nullable_rules_raises_error_for_null_required_column() -> None:
    """Verify that null values in non-nullable columns raise ValueError."""
    dataframe = pd.DataFrame(
        {
            "record_id": ["1"],
            "age": [pd.NA],
            "credit_score": ["Good"],
        }
    )

    with pytest.raises(ValueError, match="contains null values"):
        validate_nullable_rules(dataframe, TEST_SCHEMA)


def test_validate_allowed_values_accepts_valid_values() -> None:
    """Verify that allowed categorical values pass validation."""
    dataframe = pd.DataFrame(
        {
            "record_id": ["1", "2"],
            "age": [30, 45],
            "credit_score": ["Good", "Poor"],
        }
    )

    validate_allowed_values(dataframe, TEST_SCHEMA)


def test_validate_allowed_values_ignores_missing_optional_columns() -> None:
    """Verify that missing optional columns are ignored by domain validation."""
    dataframe = pd.DataFrame(
        {
            "record_id": ["1"],
            "age": [30],
        }
    )

    validate_allowed_values(dataframe, TEST_SCHEMA)


def test_validate_allowed_values_raises_error_for_invalid_values() -> None:
    """Verify that invalid categorical values raise ValueError."""
    dataframe = pd.DataFrame(
        {
            "record_id": ["1"],
            "age": [30],
            "credit_score": ["Invalid"],
        }
    )

    with pytest.raises(ValueError, match="contains invalid values"):
        validate_allowed_values(dataframe, TEST_SCHEMA)


def test_validate_numeric_ranges_accepts_valid_values() -> None:
    """Verify that values within configured numeric ranges pass validation."""
    dataframe = pd.DataFrame(
        {
            "record_id": ["1", "2"],
            "age": [0, 120],
            "credit_score": ["Good", "Poor"],
        }
    )

    validate_numeric_ranges(dataframe, TEST_SCHEMA)


def test_validate_numeric_ranges_raises_error_below_minimum() -> None:
    """Verify that values below minimum raise ValueError."""
    dataframe = pd.DataFrame(
        {
            "record_id": ["1"],
            "age": [-1],
            "credit_score": ["Good"],
        }
    )

    with pytest.raises(ValueError, match="below minimum"):
        validate_numeric_ranges(dataframe, TEST_SCHEMA)


def test_validate_numeric_ranges_raises_error_above_maximum() -> None:
    """Verify that values above maximum raise ValueError."""
    dataframe = pd.DataFrame(
        {
            "record_id": ["1"],
            "age": [121],
            "credit_score": ["Good"],
        }
    )

    with pytest.raises(ValueError, match="above maximum"):
        validate_numeric_ranges(dataframe, TEST_SCHEMA)


def test_validate_silver_dataframe_runs_all_validations() -> None:
    """Verify that the full Silver validation pipeline accepts valid data."""
    dataframe = pd.DataFrame(
        {
            "record_id": ["1"],
            "age": [30],
            "credit_score": ["Standard"],
        }
    )

    validate_silver_dataframe(
        dataframe,
        TEST_SCHEMA,
        REQUIRED_COLUMNS,
        EXPECTED_COLUMNS,
    )


def test_validate_silver_dataframe_accepts_missing_optional_column() -> None:
    """Verify that full validation accepts missing optional columns."""
    dataframe = pd.DataFrame(
        {
            "record_id": ["1"],
            "age": [30],
        }
    )

    validate_silver_dataframe(
        dataframe,
        TEST_SCHEMA,
        REQUIRED_COLUMNS,
        EXPECTED_COLUMNS,
    )