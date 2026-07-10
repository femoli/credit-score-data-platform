"""
Gold layer validation.

Validates dimensional tables and fact table before persisting them.
"""

import pandas as pd


def validate_gold_dataframes(
    customer_dimension: pd.DataFrame,
    occupation_dimension: pd.DataFrame,
    credit_score_dimension: pd.DataFrame,
    date_dimension: pd.DataFrame,
    fact_dataframe: pd.DataFrame,
    expected_row_count: int,
) -> None:
    """
    Validate Gold dimensional model.

    Raises:
        ValueError: If any validation rule fails.
    """

    # =========================================================================
    # Dimension primary keys
    # =========================================================================

    dimensions = [
        ("customer_key", customer_dimension),
        ("occupation_key", occupation_dimension),
        ("credit_score_key", credit_score_dimension),
        ("date_key", date_dimension),
    ]

    for key_column, dataframe in dimensions:

        if dataframe[key_column].isna().any():
            raise ValueError(
                f"Null values found in {key_column}."
            )

        if not dataframe[key_column].is_unique:
            raise ValueError(
                f"Duplicate values found in {key_column}."
            )

    # =========================================================================
    # Fact foreign keys
    # =========================================================================

    required_keys = [
        "customer_key",
        "credit_score_key",
        "date_key",
    ]

    for key_column in required_keys:

        if fact_dataframe[key_column].isna().any():
            raise ValueError(
                f"Null values found in fact column {key_column}."
            )

    # occupation_key is allowed to contain null values because
    # the original dataset contains customers without occupation.

    # =========================================================================
    # Row count
    # =========================================================================

    if len(fact_dataframe) != expected_row_count:
        raise ValueError(
            "Fact table row count does not match source dataframe."
        )