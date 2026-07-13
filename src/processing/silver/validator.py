"""
Silver layer validation functions.

Validates whether Silver dataframes comply with the declared Silver schema.

Architecture notes:
Validation ensures that the Silver layer behaves as a trusted data layer,
catching schema, nullability, domain, and range issues before data is
published to Gold.
"""

import pandas as pd

# =============================================================================
# Functions
# =============================================================================


def validate_expected_columns(
    dataframe: pd.DataFrame,
    required_columns: list[str],
    expected_columns: list[str],
) -> None:
    """Validate required columns and reject unexpected columns."""
    actual_columns = list(dataframe.columns)

    missing_columns = set(required_columns) - set(actual_columns)
    unexpected_columns = set(actual_columns) - set(expected_columns)

    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

    if unexpected_columns:
        raise ValueError(f"Unexpected columns found: {sorted(unexpected_columns)}")


def validate_nullable_rules(
    dataframe: pd.DataFrame,
    schema: dict[str, dict],
) -> None:
    """Validate non-nullable columns."""
    for column, rules in schema.items():
        if column not in dataframe.columns:
            continue

        if not rules.get("nullable", True) and dataframe[column].isna().any():
            raise ValueError(f"Column '{column}' contains null values.")


def validate_allowed_values(
    dataframe: pd.DataFrame,
    schema: dict[str, dict],
) -> None:
    """Validate allowed values for categorical/domain columns."""
    for column, rules in schema.items():
        if column not in dataframe.columns:
            continue

        allowed_values = rules.get("allowed_values")

        if not allowed_values:
            continue

        valid_values = dataframe[column].dropna()
        invalid_values = valid_values.loc[
            ~valid_values.isin(allowed_values)
        ].unique().tolist()

        if invalid_values:
            raise ValueError(
                f"Column '{column}' contains invalid values: "
                f"{sorted(invalid_values)}"
            )


def validate_numeric_ranges(
    dataframe: pd.DataFrame,
    schema: dict[str, dict],
) -> None:
    """Validate numeric minimum and maximum rules."""
    for column, rules in schema.items():
        if column not in dataframe.columns:
            continue

        minimum = rules.get("min")
        maximum = rules.get("max")
        values = dataframe[column].dropna()

        if minimum is not None and (values < minimum).any():
            raise ValueError(
                f"Column '{column}' contains values below minimum {minimum}."
            )

        if maximum is not None and (values > maximum).any():
            raise ValueError(
                f"Column '{column}' contains values above maximum {maximum}."
            )


def validate_silver_dataframe(
    dataframe: pd.DataFrame,
    schema: dict[str, dict],
    required_columns: list[str],
    expected_columns: list[str],
) -> None:
    """Run all Silver dataframe validations."""
    validate_expected_columns(dataframe, required_columns, expected_columns)
    validate_nullable_rules(dataframe, schema)
    validate_allowed_values(dataframe, schema)
    validate_numeric_ranges(dataframe, schema)