"""
Gold layer dimension builders.

This module contains pure transformation functions responsible for
building the dimensional tables used by the Gold layer star schema.
"""

import pandas as pd


REQUIRED_CUSTOMER_COLUMNS = {
    "customer_id",
    "age",
    "annual_income",
}

REQUIRED_OCCUPATION_COLUMNS = {"occupation"}
REQUIRED_CREDIT_SCORE_COLUMNS = {"credit_score"}
REQUIRED_DATE_COLUMNS = {"month"}

MONTH_ORDER = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12,
}

CREDIT_SCORE_ATTRIBUTES = {
    "Poor": {
        "risk_level": "High",
        "score_order": 1,
    },
    "Standard": {
        "risk_level": "Medium",
        "score_order": 2,
    },
    "Good": {
        "risk_level": "Low",
        "score_order": 3,
    },
}


def _validate_required_columns(
    dataframe: pd.DataFrame,
    required_columns: set[str],
    dimension_name: str,
) -> None:
    """Validate whether the source DataFrame contains all required columns."""
    missing_columns = required_columns - set(dataframe.columns)

    if missing_columns:
        raise ValueError(
            f"Cannot build {dimension_name}. "
            f"Missing required columns: {sorted(missing_columns)}"
        )


def build_customer_dimension(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Build the customer dimension."""
    _validate_required_columns(
        dataframe=dataframe,
        required_columns=REQUIRED_CUSTOMER_COLUMNS,
        dimension_name="customer dimension",
    )

    dimension = (
        dataframe[
            [
                "customer_id",
                "age",
                "annual_income",
            ]
        ]
        .sort_values("customer_id")
        .groupby("customer_id", as_index=False)
        .first()
    )

    dimension.insert(
        0,
        "customer_key",
        range(1, len(dimension) + 1),
    )

    return dimension


def build_occupation_dimension(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Build the occupation dimension."""
    _validate_required_columns(
        dataframe=dataframe,
        required_columns=REQUIRED_OCCUPATION_COLUMNS,
        dimension_name="occupation dimension",
    )

    dimension = (
        dataframe.loc[:, ["occupation"]]
        .dropna()
        .drop_duplicates()
        .sort_values("occupation")
        .reset_index(drop=True)
    )

    dimension.insert(
        loc=0,
        column="occupation_key",
        value=dimension.index + 1,
    )

    return dimension


def build_credit_score_dimension(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Build the credit score dimension."""
    _validate_required_columns(
        dataframe=dataframe,
        required_columns=REQUIRED_CREDIT_SCORE_COLUMNS,
        dimension_name="credit score dimension",
    )

    credit_scores = (
        dataframe.loc[:, ["credit_score"]]
        .dropna()
        .drop_duplicates()
        .copy()
    )

    credit_scores["credit_score"] = (
        credit_scores["credit_score"].astype(str)
    )

    unexpected_scores = (
        set(credit_scores["credit_score"])
        - set(CREDIT_SCORE_ATTRIBUTES)
    )

    if unexpected_scores:
        raise ValueError(
            "Unexpected credit score categories found: "
            f"{sorted(unexpected_scores)}"
        )

    dimension = credit_scores.reset_index(drop=True)

    dimension["risk_level"] = dimension["credit_score"].map(
        lambda value: CREDIT_SCORE_ATTRIBUTES[value]["risk_level"]
    )

    dimension["score_order"] = (
        dimension["credit_score"]
        .map(
            lambda value: CREDIT_SCORE_ATTRIBUTES[value]["score_order"]
        )
        .astype(int)
    )

    dimension = (
        dimension.sort_values("score_order")
        .reset_index(drop=True)
    )

    dimension.insert(
        loc=0,
        column="credit_score_key",
        value=dimension.index + 1,
    )

    return dimension


def build_date_dimension(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Build the monthly date dimension."""
    _validate_required_columns(
        dataframe=dataframe,
        required_columns=REQUIRED_DATE_COLUMNS,
        dimension_name="date dimension",
    )

    dimension = (
        dataframe.loc[:, ["month"]]
        .dropna()
        .drop_duplicates()
        .copy()
    )

    dimension["month"] = dimension["month"].astype(str)

    unexpected_months = (
        set(dimension["month"])
        - set(MONTH_ORDER)
    )

    if unexpected_months:
        raise ValueError(
            "Unexpected month values found: "
            f"{sorted(unexpected_months)}"
        )

    dimension["month_number"] = (
        dimension["month"]
        .map(MONTH_ORDER)
        .astype(int)
    )

    dimension = (
        dimension.sort_values("month_number")
        .reset_index(drop=True)
    )

    dimension["quarter"] = (
        ((dimension["month_number"] - 1) // 3) + 1
    )

    dimension["semester"] = (
        ((dimension["month_number"] - 1) // 6) + 1
    )

    dimension = dimension.rename(
        columns={"month": "month_name"}
    )

    dimension.insert(
        loc=0,
        column="date_key",
        value=dimension.index + 1,
    )

    return dimension[
        [
            "date_key",
            "month_number",
            "month_name",
            "quarter",
            "semester",
        ]
    ]