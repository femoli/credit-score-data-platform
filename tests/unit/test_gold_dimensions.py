"""
Unit tests for Gold layer dimension builders.
"""

import pandas as pd
import pytest

from src.processing.gold.dimensions import (
    build_credit_score_dimension,
    build_date_dimension,
    build_occupation_dimension,
)


def test_build_occupation_dimension_returns_unique_sorted_values():
    dataframe = pd.DataFrame(
        {
            "occupation": [
                "Engineer",
                "Architect",
                "Engineer",
                "Developer",
            ]
        }
    )

    result = build_occupation_dimension(dataframe)

    expected = pd.DataFrame(
        {
            "occupation_key": [1, 2, 3],
            "occupation": [
                "Architect",
                "Developer",
                "Engineer",
            ],
        }
    )

    pd.testing.assert_frame_equal(result, expected)


def test_build_occupation_dimension_ignores_null_values():
    dataframe = pd.DataFrame(
        {
            "occupation": [
                "Engineer",
                None,
                "Architect",
            ]
        }
    )

    result = build_occupation_dimension(dataframe)

    assert result["occupation"].tolist() == [
        "Architect",
        "Engineer",
    ]


def test_build_credit_score_dimension_adds_business_attributes():
    dataframe = pd.DataFrame(
        {
            "credit_score": [
                "Good",
                "Poor",
                "Standard",
                "Good",
            ]
        }
    )

    result = build_credit_score_dimension(dataframe)

    expected = pd.DataFrame(
        {
            "credit_score_key": [1, 2, 3],
            "credit_score": [
                "Poor",
                "Standard",
                "Good",
            ],
            "risk_level": [
                "High",
                "Medium",
                "Low",
            ],
            "score_order": [1, 2, 3],
        }
    )

    pd.testing.assert_frame_equal(result, expected)


def test_build_credit_score_dimension_rejects_unexpected_category():
    dataframe = pd.DataFrame(
        {
            "credit_score": [
                "Good",
                "Unknown",
            ]
        }
    )

    with pytest.raises(
        ValueError,
        match="Unexpected credit score categories",
    ):
        build_credit_score_dimension(dataframe)


def test_build_date_dimension_creates_calendar_attributes():
    dataframe = pd.DataFrame(
        {
            "month": [
                "March",
                "January",
                "July",
                "January",
            ]
        }
    )

    result = build_date_dimension(dataframe)

    expected = pd.DataFrame(
        {
            "date_key": [1, 2, 3],
            "month_number": [1, 3, 7],
            "month_name": [
                "January",
                "March",
                "July",
            ],
            "quarter": [1, 1, 3],
            "semester": [1, 1, 2],
        }
    )

    pd.testing.assert_frame_equal(result, expected)


@pytest.mark.parametrize(
    "builder",
    [
        build_occupation_dimension,
        build_credit_score_dimension,
        build_date_dimension,
    ],
)
def test_dimension_builder_rejects_missing_required_column(
    builder,
):
    dataframe = pd.DataFrame(
        {
            "unrelated_column": ["value"],
        }
    )

    with pytest.raises(
        ValueError,
        match="Missing required columns",
    ):
        builder(dataframe)