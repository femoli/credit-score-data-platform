"""
Unit tests for Gold layer validator.
"""

import pandas as pd
import pytest

from src.processing.gold.validator import validate_gold_dataframes


def create_dimension(
    key_name: str,
    values: list[int],
) -> pd.DataFrame:
    """Create a simple dimension dataframe."""
    return pd.DataFrame(
        {
            key_name: values,
        }
    )


def create_fact() -> pd.DataFrame:
    """Create a valid fact dataframe."""
    return pd.DataFrame(
        {
            "customer_key": [1, 2],
            "occupation_key": [1, None],
            "credit_score_key": [1, 2],
            "date_key": [1, 2],
        }
    )


def test_validate_gold_dataframes_passes_for_valid_model():
    validate_gold_dataframes(
        customer_dimension=create_dimension(
            "customer_key",
            [1, 2],
        ),
        occupation_dimension=create_dimension(
            "occupation_key",
            [1, 2],
        ),
        credit_score_dimension=create_dimension(
            "credit_score_key",
            [1, 2],
        ),
        date_dimension=create_dimension(
            "date_key",
            [1, 2],
        ),
        fact_dataframe=create_fact(),
        expected_row_count=2,
    )


def test_validate_gold_dataframes_rejects_duplicate_dimension_key():
    customer_dimension = create_dimension(
        "customer_key",
        [1, 1],
    )

    with pytest.raises(
        ValueError,
        match="Duplicate values found",
    ):
        validate_gold_dataframes(
            customer_dimension=customer_dimension,
            occupation_dimension=create_dimension(
                "occupation_key",
                [1, 2],
            ),
            credit_score_dimension=create_dimension(
                "credit_score_key",
                [1, 2],
            ),
            date_dimension=create_dimension(
                "date_key",
                [1, 2],
            ),
            fact_dataframe=create_fact(),
            expected_row_count=2,
        )


def test_validate_gold_dataframes_rejects_null_fact_key():
    fact = create_fact()

    fact.loc[0, "customer_key"] = None

    with pytest.raises(
        ValueError,
        match="Null values found",
    ):
        validate_gold_dataframes(
            customer_dimension=create_dimension(
                "customer_key",
                [1, 2],
            ),
            occupation_dimension=create_dimension(
                "occupation_key",
                [1, 2],
            ),
            credit_score_dimension=create_dimension(
                "credit_score_key",
                [1, 2],
            ),
            date_dimension=create_dimension(
                "date_key",
                [1, 2],
            ),
            fact_dataframe=fact,
            expected_row_count=2,
        )


def test_validate_gold_dataframes_rejects_invalid_row_count():
    with pytest.raises(
        ValueError,
        match="row count",
    ):
        validate_gold_dataframes(
            customer_dimension=create_dimension(
                "customer_key",
                [1, 2],
            ),
            occupation_dimension=create_dimension(
                "occupation_key",
                [1, 2],
            ),
            credit_score_dimension=create_dimension(
                "credit_score_key",
                [1, 2],
            ),
            date_dimension=create_dimension(
                "date_key",
                [1, 2],
            ),
            fact_dataframe=create_fact(),
            expected_row_count=10,
        )